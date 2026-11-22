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
    downloads/tinytusk-<book>-free-sample.pdf  samples for the other three books
    books/<book>/                    cover + 4 preview pages per book (More TinyTusk books section)
```

## Preview locally

```bash
cd website && python3 -m http.server 8000
```

Then open http://localhost:8000.

## Before launch: things to fill in

1. **Email sign-up**: in `index.html`, set `data-action="YOUR_FORM_ACTION_URL"` on `#notify-form` to your form endpoint (for example a Formspree URL `https://formspree.io/f/xxxx`, or a Mailchimp/ConvertKit form action). Until then the form validates the email and shows a "sign-ups open soon" message, but sends nothing.
2. **Buy links on launch day**: at the top of `app.js`, paste each Amazon link:
   - `AMAZON_URL` is the A to Z Animals Copy Coloring Book. The hero, menu and FAQ switch to "Buy on Amazon".
   - `BOOK_LINKS` holds the other three books (`color-by-number`, `abc-tracing`, `trace-write`). Each card in "More TinyTusk books" switches from "Coming soon" to "Now on Amazon" with a buy button.
3. **Custom domain** (optional): if you move to your own domain, update `og:image` and `og:url` in `index.html` to the new address.

## Deploy

The site is live on GitHub Pages at https://harshabhadra.github.io/TinyTusk-A-Z-Coloring-book/

Pushing changes under `website/` to the `website` branch runs `.github/workflows/deploy-site.yml`, which copies the folder to the `gh-pages` branch. Pages serves that branch (Settings → Pages → Deploy from a branch → `gh-pages`, `/ (root)`). A new version is usually live within a minute or two.

## Updating images

The images were generated from the book files (`cover.pdf`, `colored/`, `pages/`, `clean/`). If you redo an animal, regenerate its `animals/X.webp` and `pages/X.webp` at the same sizes (420 px max for animals, 850 × 1100 for pages).

Fonts (Baloo 2 and Fredoka, the same fonts as the book) load from Google Fonts.
