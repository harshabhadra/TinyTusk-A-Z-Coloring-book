# TinyTusk launch website

A static launch page for **My First A to Z Animals: Copy Coloring Book**. Plain HTML, CSS and JavaScript with no build step.

```
website/
  index.html      page content
  styles.css      design tokens (book palette) + layout
  app.js          A–Z gallery, page viewer, coloring demo, sign-up form
  assets/
    cover-front.webp / .jpg   front cover (hero + social share image)
    animals/A–Z.webp          colored animals (gallery, studio reference)
    pages/*.webp              page previews (viewer, "what's inside")
    lineart/*.png             black & white art for the coloring demo
    downloads/tinytusk-free-sample-pages.pdf   name page + A, E, L, P
```

## Preview locally

```bash
cd website && python3 -m http.server 8000
```

Then open http://localhost:8000.

## Before launch: things to fill in

1. **Email sign-up**: in `index.html`, set `data-action="YOUR_FORM_ACTION_URL"` on `#notify-form` to your form endpoint (for example a Formspree URL `https://formspree.io/f/xxxx`, or a Mailchimp/ConvertKit form action). Until then the form validates the email and shows a "sign-ups open soon" message, but sends nothing.
2. **Buy link on launch day**: replace the "Coming soon to Amazon" pill and the "Tell me when it launches" button in the hero with your Amazon link, and update the "When and where can I buy it?" FAQ answer.
3. **Social image**: `og:image` is relative. When the site has a domain, change it to the full URL (for example `https://yourdomain.com/assets/cover-front.jpg`).

## Deploy

It's a folder of static files, so any static host works:

- **GitHub Pages**: Pages can only serve a branch's root or `/docs` folder, so either rename `website/` to `docs/` (then Settings → Pages → deploy from branch `website`, folder `/docs`) or use a GitHub Actions Pages workflow that uploads `website/`.
- **Netlify / Cloudflare Pages / Vercel**: set the publish directory to `website` with no build command.

## Updating images

The images were generated from the book files (`cover.pdf`, `colored/`, `pages/`, `clean/`). If you redo an animal, regenerate its `animals/X.webp` and `pages/X.webp` at the same sizes (420 px max for animals, 850 × 1100 for pages).

Fonts (Baloo 2 and Fredoka, the same fonts as the book) load from Google Fonts.
