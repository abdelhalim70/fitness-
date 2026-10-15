# Boxing & Fitness Coach Website

A fast, mobile-first one-page website for a private boxing and fitness coach. It is plain HTML, CSS and JavaScript, with no framework and no build step.

```
index.html            → the one-page site (all sections + copy)
privacy.html          → privacy policy, cookies, terms of sale, legal notice
assets/css/styles.css → all styles (colours & fonts at the top in :root)
assets/js/main.js     → interactions + CONFIG (WhatsApp, form, Stripe, analytics)
assets/img/           → favicon, before/after placeholders, review avatars
```

## 1. Preview locally

```bash
python3 -m http.server 8000
# open http://localhost:8000
```

The booking form only *sends* once deployed (Netlify) or once `formEndpoint` is set (Formspree). When it can't send, it shows a fallback that offers WhatsApp.

## 2. Personalise (checklist)

**Already filled in from the CV:** name (Abdelhalim Benhaddi), logo (A2B), location (Abu Dhabi, UAE), phone / WhatsApp (+212 655 911650), email, experience, titles and certifications.

**Still to replace (find & replace across all files):**

| Placeholder | Replace with |
|---|---|
| `your-domain.com` | Your domain (canonical URL, Open Graph) |
| `yourhandle` / `yourpage` | Instagram, TikTok and Facebook handles |
| `[add your licence number]` | UAE trade / freelance licence number (privacy.html) |
| `+212 655 911650` / `212655911650` | Your UAE number, once you have one (index.html, privacy.html, main.js) |

**In [assets/js/main.js](assets/js/main.js), edit `CONFIG`:**
- `whatsappNumber`: digits only, international format (e.g. `33612345678`).
- `formEndpoint`: leave empty on Netlify; set a Formspree URL on Vercel.
- `paymentLinks`: your Stripe Payment Links (see section 4).
- `analyticsId`: optional GA4 ID. It only loads after cookie consent.

**Prices:** each price in `index.html` has `data-monthly` and `data-quarterly` attributes, and the toggle switches between them. Update both values and the visible default text.

**Accent colour:** change `--accent`, `--accent-hover` and `--accent-soft` at the top of `styles.css` (gold `#d4a017`, electric orange `#ff5a1f`). The red hover border on cards is `rgba(225,6,0,.5)`. Search for `225,6,0` to update it too.

**Photos:** the stock photos come from Unsplash (free licence) as placeholders. Replace them with your own:
1. Put your images in `assets/img/` (compress them to WebP/JPG under ~250 KB at https://squoosh.app).
2. Update the `src` (and the hero `<link rel="preload">`) in `index.html`.
3. Keep the `alt` text descriptive. It helps SEO and accessibility.
4. Add `assets/img/og-image.jpg` (1200×630). This is the preview shown when the link is shared on WhatsApp or Instagram.

Hero video: the hero has a commented-out `<video>` snippet. Keep the file small (under 3 MB, 720p, no audio).

**Results & testimonials:** the before/after images and reviews are placeholders. Replace them with real client photos and quotes, and only with each client's written permission.

## 3. Booking form → email

- **Netlify (recommended, zero config):** the form already has `data-netlify="true"`. After the first deploy, go to *Site → Forms → booking → Form notifications → Add notification → Email*. Each booking then arrives in your inbox. Spam protection uses a honeypot field.
- **Vercel / other hosts:** create a free form at [formspree.io](https://formspree.io), copy its endpoint into `CONFIG.formEndpoint`, and set your email in Formspree.

After a successful submit, the visitor is offered a WhatsApp message pre-filled with their details.

## 4. Payments (Stripe)

1. Create a [Stripe](https://stripe.com) account.
2. *Product catalogue → Add product* for each plan:
   - Single session: one-off AED 300, and a 3-pack at AED 825
   - Fighter plan: recurring AED 2,000/month, and AED 5,400 every 3 months
   - Champion plan: recurring AED 3,500/month, and AED 9,450 every 3 months
3. For each price, *Create payment link*, then paste the URLs into `CONFIG.paymentLinks`.
4. In the payment link settings, set the success redirect to `https://your-domain.com/#contact` (or a thank-you page).

When a link is empty, its button scrolls to the booking form with that plan preselected. You can go live before Stripe is set up.

PayPal alternative: create PayPal "Buy Now" or "Subscribe" button links and paste them into the same fields.

## 5. Instagram feed

Instagram doesn't allow a free official feed without an API app. The easiest option is a widget service:
1. Sign up at [behold.so](https://behold.so), [SnapWidget](https://snapwidget.com) or [Elfsight](https://elfsight.com) and connect your account.
2. Paste the embed code they give you inside `<div id="instagram-feed"></div>` in the Gallery section.

## 6. Deploy

**Netlify (recommended because forms work out of the box)**
1. Push this folder to GitHub.
2. Go to [app.netlify.com](https://app.netlify.com), choose *Add new site → Import from Git*, and pick the repo.
3. Leave the build command empty and set the publish directory to `/`. Then deploy.
   (Or drag and drop the folder onto https://app.netlify.com/drop.)
4. Add your domain under *Domain management*. HTTPS is automatic.
5. Turn on the form email notification (section 3).

**Vercel**
1. Push to GitHub, then go to [vercel.com/new](https://vercel.com/new) and import the repo.
2. Framework preset: *Other*. No build command. Deploy.
3. Set `CONFIG.formEndpoint` to your Formspree URL, because Netlify Forms won't work on Vercel.

## 7. Before going live

- [ ] All placeholders replaced (search for `your-domain`, `yourhandle`, `00 00`)
- [ ] Real photos, results and testimonials (with consent)
- [ ] Form tested end-to-end and the email notification received
- [ ] WhatsApp button opens a chat with the right number
- [ ] Stripe links tested in test mode, then switched to live
- [ ] Privacy policy reviewed for UAE law (PDPL), licence number added
- [ ] Submit `https://your-domain.com` to Google Search Console and create a Google Business Profile (big win for local search)
