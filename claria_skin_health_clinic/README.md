# Claria Skin Health — Skin Health Center Website

A 4-page site for a modern skin health center: Home, Services, About, and
Contact (with an appointment request form). Built as a **separate,
distinct project** from the "Fresh & Glow" skincare clinic and "Ivory"
dental studio sites — same underlying tech, deliberately different brand
and visual language.

## Structure

```
claria_skin_health/
├── index.html        # Home — hero with diagnostic scan device, services, process, testimonials
├── services.html      # Full service menu, grouped by category
├── about.html         # Story, values, team, center snapshot
├── contact.html       # Appointment form, map, contact info, FAQ
├── css/style.css      # All design tokens + styles (single stylesheet)
└── js/script.js       # Nav toggle, scan/metrics animation, FAQ accordion, form logic
```

## Running it locally

No build step — plain HTML/CSS/JS. Open `index.html` directly, or serve it:

```bash
cd claria_skin_health
python -m http.server 8000
# then visit http://localhost:8000
```

## What makes this different from the other two clinic sites

This was explicitly meant to feel like a **health-tech diagnostic center**,
not a spa or boutique — a deliberate contrast in every layer:

- **Palette**: cool porcelain-grey base, navy-charcoal text, a vivid coral
  accent for action, and teal for data/metrics — vs. the botanical
  sage/gold of Fresh & Glow or the dark champagne/serif of Ivory Dental.
- **Type**: Space Grotesk + Inter, an all-sans pairing (no serif anywhere)
  to read as "software product" rather than "boutique atelier." Small
  stats and the metric readout use JetBrains Mono for a clinical,
  data-panel feel.
- **Signature element**: the hero's "diagnostic scan" device — a scanning
  line sweeps across a skin-texture swatch, then four metric bars
  (Hydration, Texture, Tone Evenness, UV Protection) animate in, framed
  like an AI skin-analysis readout. This replaces the drag-slider or
  shade-guide devices used on the other two sites with something that
  fits a "diagnose first" health-tech positioning.

## Things to personalize before launch

1. **Real contact details** — address, phone, email, and hours (currently
   220 Bay Street, Toronto placeholders) throughout the footer and on
   `contact.html`.
2. **Google Maps embed** — swap the `iframe src` in `contact.html` for
   your real address once you have one (Google Maps → Share → Embed a map).
3. **Team names/photos** — replace the initials avatars in `about.html`
   with real photos once available.
4. **Services & pricing** — everything in `services.html` and the
   `contact.html` concern dropdown is a reasonable placeholder for a
   Canadian dermatology practice; adjust to your real offerings and CAD
   pricing (or your local currency).

## Connecting the contact form to something real

Same situation as the other two sites: the form validates client-side and
shows a success message, but isn't wired to send anywhere yet. Fastest
options:

- **Formspree / Web3Forms** — a 10-minute no-code fix, just point the
  `<form>` at their endpoint.
- **A real backend** (Flask/Node) — happy to build one if you want this
  connected to email or a booking database.
