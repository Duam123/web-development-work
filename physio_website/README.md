# Restore Motion — Physiotherapy Hospital Website

A 4-page site for a physiotherapy hospital: Home, Services, About, and
Contact (with an appointment request form). Built as its own distinct
project — different structure, palette, and layout patterns from the
skin clinic sites built earlier in this conversation.

## Structure

```
restore_motion_physio/
├── index.html        # Home — split-screen hero with ROM device, conditions, recovery journey, testimonials
├── services.html      # Sticky tab-nav + treatment list panels, grouped by condition category
├── about.html         # Story, values, team, hospital snapshot
├── contact.html       # Appointment form, map, contact info, FAQ
├── css/style.css      # All design tokens + styles
└── js/script.js       # Nav toggle, service tab switching, FAQ accordion, form logic
```

## Running it locally

```bash
cd restore_motion_physio
python -m http.server 8000
# then visit http://localhost:8000
```

## Design notes

- **Positioning**: "measure the recovery, don't just hope for it" — a
  physiotherapy hospital that tracks range-of-motion and strength as
  actual numbers, not vague progress reports.
- **Palette**: warm sand/cream base, deep brown-black ink, terracotta for
  CTAs, and a calm sky-blue secondary accent — a genuinely different
  combination from the sage/gold, coral/teal/navy, and rose/plum palettes
  used in the other three clinic sites in this thread.
- **Type**: Newsreader (warm literary serif) + Figtree — not reused
  elsewhere in this conversation.
- **Signature element**: a hero "range-of-motion" device — an animated
  goniometer-style arc with a sweeping needle and a live-looking degree
  readout (e.g. "Knee Flexion — 138°"), which is literally what a
  physiotherapy assessment measures.
- **Distinct layout choices**: split-screen hero (not centered), a
  services page built as sticky category tabs + expandable treatment
  rows (not a card grid), and an alternating left/right "recovery
  journey" timeline instead of equal-width process columns.

## Things to personalize before launch

1. **Everything here is placeholder** — clinic name ("Restore Motion"),
   address (14-C Gulberg III, Lahore), phone, email, therapist names, and
   testimonials are all fictional. Replace before publishing.
2. **Google Maps embed** — swap the `iframe src` in `contact.html` for
   your real address once available.
3. **Team photos** — replace the gradient initials avatars in
   `about.html` with real photos.
4. **Services & pricing** — adjust `services.html` and the `contact.html`
   condition dropdown to your real offerings and PKR pricing.

## Connecting the contact form to something real

Same situation as the other sites in this conversation: the form
validates client-side and shows a success message, but isn't wired to
send anywhere. Fastest fix is Formspree or Web3Forms (~10 minutes) — or
I can build a real backend if you want this connected to email or a
booking database.
