/* ==========================================================================
   Coach website: interactions
   No dependencies. Everything you need to customise is in CONFIG below.
   ========================================================================== */

const CONFIG = {
  // WhatsApp number in international format, digits only (no +, spaces or leading 0).
  whatsappNumber: "212655911650",

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

/* ---------- Text shown by scripts, per page language (index.html = en, ar/index.html = ar) ---------- */
const STRINGS = {
  en: {
    whatsappMessage: "Hi Abdelhalim! I'd like to book my free intro session.",
    whatsappBooked: (d) => `Hi Abdelhalim! I just booked via your website.\nName: ${d.name}\nGoal: ${d.goal}\nPlan: ${d.plan}`,
    openMenu: "Open menu",
    closeMenu: "Close menu",
    required: "Please fill in the required fields.",
    sending: "Sending…",
    submit: "Book my free session",
    success: (name, wa) => `✅ Thanks ${name}! Your request is in. I'll contact you within 24h. ` +
      `Want a faster reply? <a href="${wa}" target="_blank" rel="noopener" style="text-decoration:underline">Message me on WhatsApp</a>.`,
    error: (wa) => `Something went wrong sending your request. Please <a href="${wa}" target="_blank" rel="noopener" style="text-decoration:underline">message me on WhatsApp</a> instead.`,
  },
  ar: {
    whatsappMessage: "مرحباً عبد الحليم! أرغب في حجز حصتي التعريفية المجانية.",
    whatsappBooked: (d) => `مرحباً عبد الحليم! قمت بالحجز للتو عبر موقعك.\nالاسم: ${d.name}\nالهدف: ${d.goal}\nالخطة: ${d.plan}`,
    openMenu: "فتح القائمة",
    closeMenu: "إغلاق القائمة",
    required: "يرجى ملء الحقول المطلوبة.",
    sending: "جارٍ الإرسال…",
    submit: "احجز حصتي المجانية",
    success: (name, wa) => `✅ شكراً ${name}! تم استلام طلبك، وسأتواصل معك خلال 24 ساعة. ` +
      `تريد رداً أسرع؟ <a href="${wa}" target="_blank" rel="noopener" style="text-decoration:underline">راسلني على واتساب</a>.`,
    error: (wa) => `حدث خطأ أثناء إرسال طلبك. يرجى <a href="${wa}" target="_blank" rel="noopener" style="text-decoration:underline">مراسلتي على واتساب</a> بدلاً من ذلك.`,
  },
};
const LANG = document.documentElement.lang === "ar" ? "ar" : "en";
const T = STRINGS[LANG];
const RTL = document.documentElement.dir === "rtl";

const $ = (sel, ctx = document) => ctx.querySelector(sel);
const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

/* Small wrapper: localStorage can throw in private mode / blocked storage */
const store = {
  get(key) { try { return localStorage.getItem(key); } catch { return null; } },
  set(key, val) { try { localStorage.setItem(key, val); } catch { /* ignore */ } },
};

/* ---------- Splash screen ---------- */
const splash = $("#splash");
if (splash && !document.documentElement.classList.contains("no-splash")) {
  const start = performance.now();
  // Safety net: the CSS fade-out ends by ~3.3s, so the element can always go by 3.4s
  setTimeout(() => splash.remove(), 3400);
  const finish = () => {
    setTimeout(() => {
      // After 2.75s the CSS fade has started on its own; restarting it would flash the splash back
      if (!splash.isConnected || performance.now() - start >= 2750) return;
      splash.classList.add("is-done");
      setTimeout(() => splash.remove(), 550);
    }, Math.max(0, 2000 - (performance.now() - start))); // logo stays at least 2s
  };
  if (document.readyState === "complete") finish();
  else window.addEventListener("load", finish, { once: true });
} else if (splash) {
  splash.remove();
}

/* ---------- Header: solid background after scrolling ---------- */
const header = $("#header");
const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 20);
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

/* ---------- Mobile menu ---------- */
const burger = $("#burger");
const mobileMenu = $("#mobile-menu");

function setMenu(open) {
  const wasOpen = burger.getAttribute("aria-expanded") === "true";
  burger.setAttribute("aria-expanded", String(open));
  burger.setAttribute("aria-label", open ? T.closeMenu : T.openMenu);
  mobileMenu.classList.toggle("is-open", open);
  mobileMenu.inert = !open; // closed menu can't be tabbed into
  document.body.style.overflow = open ? "hidden" : "";
  if (open) $("a", mobileMenu).focus();
  else if (wasOpen && mobileMenu.contains(document.activeElement)) burger.focus();
}
burger.addEventListener("click", () => setMenu(burger.getAttribute("aria-expanded") !== "true"));
$$("a", mobileMenu).forEach((a) => a.addEventListener("click", () => setMenu(false)));
document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });
// Close the menu if the screen is resized to desktop width while it's open.
window.matchMedia("(min-width: 960px)").addEventListener("change", (e) => { if (e.matches) setMenu(false); });

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
["about", "services", "pricing", "gallery", "contact"].forEach((id) => {
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
const waUrl = (text = T.whatsappMessage) =>
  `https://wa.me/${CONFIG.whatsappNumber}?text=${encodeURIComponent(text)}`;
$$(".js-whatsapp").forEach((a) => { a.href = waUrl(); });

/* ---------- Any CTA with data-plan preselects that plan in the form ---------- */
const planSelect = $("#plan");
document.addEventListener("click", (e) => {
  const trigger = e.target.closest("[data-plan]");
  if (!trigger || !planSelect) return;
  // data-plan holds the option's English value, so it works on both language versions
  const option = [...planSelect.options].find((o) => o.value === trigger.dataset.plan);
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

/* ---------- Parallax on the group-classes photo (skipped with "reduce motion") ---------- */
const classesPhoto = $(".classes__photo");
if (classesPhoto && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  const img = $("img", classesPhoto);
  let ticking = false;
  const update = () => {
    const r = classesPhoto.getBoundingClientRect();
    // -1 when the photo enters at the bottom of the screen, +1 when it leaves at the top
    const progress = Math.max(-1, Math.min(1, (window.innerHeight / 2 - (r.top + r.height / 2)) / window.innerHeight));
    // The image is 115% tall: it can move up to 15/115 ≈ 13% of its own height without showing a gap
    img.style.setProperty("--parallax", `${(-6.5 + progress * 6.5).toFixed(2)}%`);
    ticking = false;
  };
  window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
  update();
}

/* ---------- Group classes: tabs + animated charts ---------- */
const classTabs = $$(".class-tabs [role=tab]");
const drawChart = (panel) => {
  const chart = $(".class-chart", panel);
  if (!chart) return;
  chart.classList.remove("is-drawn");
  void chart.offsetWidth; // restart the animation
  chart.classList.add("is-drawn");
};
function selectClass(tab, focus) {
  classTabs.forEach((t) => {
    const on = t === tab;
    t.setAttribute("aria-selected", String(on));
    t.tabIndex = on ? 0 : -1;
    const panel = document.getElementById(t.getAttribute("aria-controls"));
    panel.hidden = !on;
    panel.classList.toggle("is-active", on);
    if (on) drawChart(panel);
  });
  if (focus) tab.focus();
}
classTabs.forEach((tab, i) => {
  tab.addEventListener("click", () => selectClass(tab));
  tab.addEventListener("keydown", (e) => {
    const step = { ArrowRight: RTL ? -1 : 1, ArrowLeft: RTL ? 1 : -1 }[e.key];
    if (step) { e.preventDefault(); selectClass(classTabs[(i + step + classTabs.length) % classTabs.length], true); }
  });
});
// Draw the first chart when it scrolls into view
const firstChart = $(".class-panel.is-active .class-chart");
if (firstChart) {
  new IntersectionObserver((entries, obs) => {
    if (entries[0].isIntersecting) { firstChart.classList.add("is-drawn"); obs.disconnect(); }
  }, { threshold: 0.25 }).observe(firstChart);
}

/* ---------- Gallery photo viewer ---------- */
const lightbox = $("#lightbox");
const lightboxImg = $(".lightbox__img", lightbox);
const tiles = $$(".gallery__item");
let current = 0;

function showPhoto(i) {
  current = (i + tiles.length) % tiles.length;
  const img = $("img", tiles[current]);
  lightboxImg.src = img.currentSrc || img.src;
  lightboxImg.alt = img.alt;
}
tiles.forEach((tile, i) => tile.addEventListener("click", () => {
  showPhoto(i);
  lightbox.showModal();
  document.body.style.overflow = "hidden";
}));
lightbox.addEventListener("close", () => { document.body.style.overflow = ""; tiles[current].focus(); });
lightbox.addEventListener("click", (e) => {
  const action = e.target.dataset.lightbox;
  if (action === "prev") showPhoto(current - 1);
  else if (action === "next") showPhoto(current + 1);
  else if (action === "close" || e.target === lightbox) lightbox.close(); // click on backdrop closes
});
lightbox.addEventListener("keydown", (e) => {
  // In right-to-left Arabic, "next" is to the left
  if (e.key === "ArrowLeft") showPhoto(current + (RTL ? 1 : -1));
  if (e.key === "ArrowRight") showPhoto(current + (RTL ? -1 : 1));
});
// Swipe left / right on phones
let touchX = null;
lightbox.addEventListener("touchstart", (e) => { touchX = e.touches[0].clientX; }, { passive: true });
lightbox.addEventListener("touchend", (e) => {
  if (touchX === null) return;
  const dx = e.changedTouches[0].clientX - touchX;
  if (Math.abs(dx) > 50) showPhoto(current + ((dx < 0) !== RTL ? 1 : -1));
  touchX = null;
});

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
    setStatus(T.required, "error");
    return;
  }

  const submitBtn = $("button[type=submit]", form);
  const data = new FormData(form);
  submitBtn.disabled = true;
  submitBtn.textContent = T.sending;
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
    const wa = waUrl(T.whatsappBooked({ name: data.get("name"), goal: data.get("goal"), plan: data.get("plan") }));
    setStatus(T.success(escapeHtml(String(data.get("name")).split(" ")[0]), wa), "success");
    form.reset();
  } catch (err) {
    setStatus(T.error(waUrl()), "error");
    console.error("Form submission failed:", err);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = T.submit;
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
