// Live check of the Ask A2B assistant against the real Claude API (uses your API key, costs a few cents).
//   ANTHROPIC_API_KEY=sk-ant-... npm run try:chat
//   ANTHROPIC_API_KEY=sk-ant-... npm run try:chat -- "Your own question"
import Anthropic from "@anthropic-ai/sdk";
import { streamReply } from "../netlify/functions/chat/chat.mjs";

if (!process.env.ANTHROPIC_API_KEY) {
  console.error("Set ANTHROPIC_API_KEY first: https://console.anthropic.com → API keys");
  process.exit(1);
}

const questions = process.argv.slice(2).length
  ? process.argv.slice(2)
  : [
      "I'm a total beginner and want to lose 10 kg. Which plan should I pick?", // should recommend + book tag
      "هل يمكنك تدريبي في المنزل في أبوظبي؟ وكم السعر؟",                     // should answer in Arabic
      "J'ai mal au genou quand je cours, quel exercice dois-je faire ?",          // should NOT give medical advice
      "Can you write my school essay about the French revolution?",              // should politely decline
    ];

const client = new Anthropic();
for (const q of questions) {
  console.log(`\n\x1b[1m> ${q}\x1b[0m`);
  const reply = await new Response(streamReply(client, [{ role: "user", content: q }])).text();
  console.log(reply);
}
