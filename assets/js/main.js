/* ==========================================================================
   Coach website: interactions
   No dependencies. Everything you need to customise is in CONFIG below.
   ========================================================================== */

const CONFIG = {
  // WhatsApp number in international format, digits only (no +, spaces or leading 0).
  whatsappNumber: "33600000000",
  whatsappMessage: "Hi Alex! I'd like to book my free intro session.",

  // Leave empty to use Netlify Forms (works automatically when hosted on Netlify).
  // On Vercel or elsewhere, create a free form at https://formspree.io and paste its URL:
  // e.g. "https://formspree.io/f/abcdwxyz"
  formEndpoint: "",

  // Stripe Payment Links (Stripe Dashboard → Payment Links → New). One per plan & billing period.
  // Leave a link empty ("") and the button scrolls to the booking form with the plan preselected.
  paymentLinks: {
    single:  { monthly: "", quarterly: "" }, // e.g. "https://buy.stripe.com/xxxx"
    monthly: { monthly: "", quarterly: "" },
    premium: { monthly: "", quarterly: "" },
  },

  // Optional Google Analytics 4 ID, loaded ONLY after cookie consent. e.g. "G-XXXXXXXXXX"
  analyticsId: "",
};

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* Small wrapper: localStorage can throw in private mode / blocked storage */
const store = {
  get(key) { try { return localStorage.getItem(key); } catch { return null; } },
  set(key, val) { try { localStorage.setItem(key, val); } catch { /* ignore */ } },
};

/* ---------- Header: solid background after scrolling ---------- */
const header = $("#header");
const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 20);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

/* ---------- Mobile menu ---------- */
const burger = $("#burger");
const mobileMenu = $("#mobile-menu");

function setMenu(open) {
  burger.setAttribute("aria-expanded", String(open));
  burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  mobileMenu.classList.toggle("is-open", open);
  mobileMenu.setAttribute("aria-hidden", String(!open));
  document.body.style.overflow = open ? "hidden" : "";
}
burger.addEventListener("click", () => setMenu(burger.getAttribute("aria-expanded") !== "true"));
$$("a", mobileMenu).forEach((a) => a.addEventListener("click", () => setMenu(false)));
document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

/* ---------- Fade-in on scroll ---------- */
const revealObserver = new IntersectionObserver(
  (entries) => entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("is-visible");
      revealObserver.unobserve(entry.target);
    }
  }),
  { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
);
$$(".reveal").forEach((el) => revealObserver.observe(el));

/* ---------- Highlight the nav link of the section in view ---------- */
const navLinks = $$(".nav__link");
const sectionObserver = new IntersectionObserver(
  (entries) => entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    navLinks.forEach((link) =>
      link.classList.toggle("is-active", link.getAttribute("href") === `#${entry.target.id}`)
    );
  }),
  { rootMargin: "-45% 0px -50% 0px" }
);
["about", "services", "pricing", "results", "contact"].forEach((id) => {
  const el = document.getElementById(id);
  if (el) sectionObserver.observe(el);
});

/* ---------- Sticky mobile CTA: show after the hero, hide at the form ---------- */
const mobileCta = $("#mobile-cta");
let pastHero = false;
let atContact = false;
const updateMobileCta = () => mobileCta.classList.toggle("is-visible", pastHero && !atContact);

new IntersectionObserver(([e]) => { pastHero = !e.isIntersecting; updateMobileCta(); }, { threshold: 0.2 })
  .observe($("#top"));
new IntersectionObserver(([e]) => { atContact = e.isIntersecting; updateMobileCta(); }, { threshold: 0.1 })
  .observe($("#contact"));

/* ---------- WhatsApp click-to-chat ---------- */
const waUrl = (text = CONFIG.whatsappMessage) =>
  `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent(text)}`;
$$(".js-whatsapp").forEach((a) => { a.href = waUrl(); });

/* ---------- Any CTA with data-plan preselects that plan in the form ---------- */
const planSelect = $("#plan");
document.addEventListener("click", (e) => {
  const trigger = e.target.closest("[data-plan]");
  if (!trigger || !planSelect) return;
  const option = [...planSelect.options].find((o) => o.text === trigger.dataset.plan);
  if (option) planSelect.value = option.value;
});

/* ---------- Pricing: monthly / 3-month toggle ---------- */
let billing = "monthly";

function applyBilling(period) {
  billing = period;
  $$(".billing-toggle button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.billing === period)));
  // Every element with data-monthly / data-quarterly swaps its text.
  $$("#pricing [data-monthly]").forEach((el) => { el.textContent = el.dataset[period]; });
  // Point Subscribe buttons to the matching Stripe link (if configured).
  $$("#pricing .plan").forEach((plan) => {
    const btn = $(".js-subscribe", plan);
    const link = CONFIG.paymentLinks[plan.dataset.planId]?.[period];
    if (link) {
      btn.href = link;
      btn.target = "_blank";
      btn.rel = "noopener";
    } else {
      btn.href = "#contact";
      btn.removeAttribute("target");
    }
  });
}
$$(".billing-toggle button").forEach((b) => b.addEventListener("click", () => applyBilling(b.dataset.billing)));
applyBilling(billing);

/* ---------- FAQ accordion (one item open at a time) ---------- */
$$(".faq__q").forEach((btn) => {
  btn.addEventListener("click", () => {
    const item = btn.closest(".faq__item");
    const willOpen = !item.classList.contains("is-open");
    $$(".faq__item").forEach((other) => {
      other.classList.remove("is-open");
      $(".faq__q", other).setAttribute("aria-expanded", "false");
    });
    item.classList.toggle("is-open", willOpen);
    btn.setAttribute("aria-expanded", String(willOpen));
  });
});

/* ---------- Booking form ---------- */
const form = $("#booking-form");
const statusEl = $("#form-status");

function setStatus(msg, type) {
  statusEl.innerHTML = msg;
  statusEl.className = `form__status ${type ? `is-${type}` : ""}`;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  if (!form.checkValidity()) {
    form.reportValidity();
    setStatus("Please fill in the required fields.", "error");
    return;
  }

  const submitBtn = $("button[type=submit]", form);
  const data = new FormData(form);
  submitBtn.disabled = true;
  submitBtn.textContent = "Sending…";
  setStatus("", "");

  try {
    let res;
    if (CONFIG.formEndpoint) {
      // Formspree (or any endpoint that accepts multipart form data)
      res = await fetch(CONFIG.formEndpoint, { method: "POST", body: data, headers: { Accept: "application/json" } });
    } else {
      // Netlify Forms expects a url-encoded POST to the page
      res = await fetch("/", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams(data).toString(),
      });
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    // Offer an instant WhatsApp follow-up with the details pre-filled.
    const wa = waUrl(
      `Hi Alex! I just booked via your website.\nName: ${data.get("name")}\nGoal: ${data.get("goal")}\nPlan: ${data.get("plan")}`
    );
    setStatus(
      `✅ Thanks ${escapeHtml(String(data.get("name")).split(" ")[0])}! Your request is in. I'll contact you within 24h. ` +
      `Want a faster reply? <a href="${wa}" target="_blank" rel="noopener" style="text-decoration:underline">Message me on WhatsApp</a>.`,
      "success"
    );
    form.reset();
  } catch (err) {
    setStatus(
      `Something went wrong sending your request. Please <a href="${waUrl()}" target="_blank" rel="noopener" style="text-decoration:underline">message me on WhatsApp</a> instead.`,
      "error"
    );
    console.error("Form submission failed:", err);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Book my free session";
  }
});

function escapeHtml(str) {
  return str.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

/* ---------- Cookie consent ---------- */
const cookieBanner = $("#cookie-banner");
const CONSENT_KEY = "cookie-consent"; // "accepted" | "rejected"

function loadAnalytics() {
  if (!CONFIG.analyticsId || window.gtag) return;
  const s = document.createElement("script");
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${CONFIG.analyticsId}`;
  document.head.appendChild(s);
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  window.gtag("config", CONFIG.analyticsId, { anonymize_ip: true });
}

const consent = store.get(CONSENT_KEY);
if (consent === "accepted") loadAnalytics();
if (!consent) setTimeout(() => { cookieBanner.hidden = false; }, 1200);

$$("[data-cookie]", cookieBanner).forEach((btn) =>
  btn.addEventListener("click", () => {
    const choice = btn.dataset.cookie === "accept" ? "accepted" : "rejected";
    store.set(CONSENT_KEY, choice);
    cookieBanner.hidden = true;
    if (choice === "accepted") loadAnalytics();
  })
);
$$(".js-cookie-settings").forEach((b) => b.addEventListener("click", () => { cookieBanner.hidden = false; }));

/* ---------- Footer year ---------- */
const yearEl = $("#year");
if (yearEl) yearEl.textContent = new Date().getFullYear();
