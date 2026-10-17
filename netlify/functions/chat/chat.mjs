/*
 * "Ask A2B" chat endpoint: POST /api/chat
 *
 * Runs as a Netlify Function (server side), so the Anthropic API key never reaches the browser.
 * Set ANTHROPIC_API_KEY in Netlify: Site configuration → Environment variables.
 *
 * Request body:  { "messages": [{ "role": "user" | "assistant", "content": "..." }, ...] }
 * Response:      the assistant's reply as a plain-text stream. A reply that ends with
 *                "[[ERROR]]" or "[[REFUSAL]]" tells the widget to show its fallback message.
 */
import Anthropic from "@anthropic-ai/sdk";
import { SYSTEM_PROMPT } from "./knowledge.mjs";

// ---- Limits that protect your API bill ----
const MAX_MESSAGES = 16;          // only the latest 16 messages of a conversation are sent
const MAX_MESSAGE_CHARS = 800;    // longer visitor messages are rejected
const MAX_TOTAL_CHARS = 12000;    // whole conversation
const RATE_LIMIT = 30;            // requests per visitor (IP address) ...
const RATE_WINDOW_MS = 10 * 60e3; // ... per 10 minutes

// Best-effort rate limit: kept in the function's memory, so it resets when Netlify starts a new
// instance. Your real safety net is the monthly spend limit you set in the Anthropic Console.
const hits = new Map();
function rateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < RATE_WINDOW_MS);
  recent.push(now);
  hits.set(ip, recent);
  if (hits.size > 5000) hits.clear(); // keep memory bounded
  return recent.length > RATE_LIMIT;
}

const text = (body, status) =>
  new Response(body, { status, headers: { "Content-Type": "text/plain; charset=utf-8" } });

/** Checks the conversation sent by the browser and returns it as API messages, or null if invalid. */
function cleanMessages(input) {
  if (!Array.isArray(input) || input.length === 0) return null;
  const messages = input.slice(-MAX_MESSAGES);
  while (messages.length && messages[0]?.role !== "user") messages.shift(); // must start with the visitor
  let total = 0;
  for (const [i, m] of messages.entries()) {
    const expected = i % 2 === 0 ? "user" : "assistant";
    if (!m || m.role !== expected || typeof m.content !== "string") return null;
    const content = m.content.trim();
    if (!content || (m.role === "user" && content.length > MAX_MESSAGE_CHARS)) return null;
    total += content.length;
  }
  if (!messages.length || messages.at(-1).role !== "user" || total > MAX_TOTAL_CHARS) return null;
  return messages.map((m) => ({ role: m.role, content: m.content.trim() }));
}

/** Streams Claude's reply for a cleaned conversation. Exported separately so it can be tested. */
export function streamReply(client, messages) {
  const encoder = new TextEncoder();
  return new ReadableStream({
    async start(controller) {
      try {
        const stream = client.beta.messages.stream({
          model: "claude-opus-5-5",
          max_tokens: 4000, // cost cap: replies are short, this leaves room for the model's reasoning
          output_config: { effort: "low" }, // quick, inexpensive replies, which suit a chat
          // If Claude's safety check declines a message, retry it automatically on the model
          // Anthropic recommends instead of failing.
          betas: ["server-side-fallback-2026-07-01"],
          fallbacks: "default",
          system: [{ type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } }],
          messages,
        });
        for await (const event of stream) {
          if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
            controller.enqueue(encoder.encode(event.delta.text));
          }
        }
        const final = await stream.finalMessage();
        if (final.stop_reason === "refusal") controller.enqueue(encoder.encode("[[REFUSAL]]"));
      } catch (err) {
        if (err instanceof Anthropic.AuthenticationError) {
          console.error("Ask A2B: ANTHROPIC_API_KEY is missing or invalid");
        } else if (err instanceof Anthropic.RateLimitError) {
          console.error("Ask A2B: Anthropic rate limit reached");
        } else if (err instanceof Anthropic.APIError) {
          console.error(`Ask A2B: API error ${err.status}: ${err.message}`);
        } else {
          console.error("Ask A2B: unexpected error", err);
        }
        controller.enqueue(encoder.encode("[[ERROR]]"));
      } finally {
        controller.close();
      }
    },
  });
}

let client; // created on first use, reused while the function instance stays warm

export default async (req, context) => {
  if (req.method !== "POST") return text("Method not allowed", 405);

  // Only accept requests coming from this website
  const origin = req.headers.get("origin");
  if (origin && origin !== new URL(req.url).origin && origin !== process.env.URL) {
    return text("Forbidden", 403);
  }
  if (rateLimited(context?.ip || "unknown")) return text("Too many messages, please try again later.", 429);

  let body;
  try {
    body = await req.json();
  } catch {
    return text("Invalid JSON", 400);
  }
  const messages = cleanMessages(body?.messages);
  if (!messages) return text("Invalid conversation", 400);

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error("Ask A2B: set ANTHROPIC_API_KEY in Netlify → Site configuration → Environment variables");
    return text("[[ERROR]]", 200);
  }
  client ??= new Anthropic();

  return new Response(streamReply(client, messages), {
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
};

export const config = { path: "/api/chat" };
