# TinyTusk Books website

The TinyTusk Books site: all four books (A to Z Animals Copy Coloring Book and the three TinyTusk Learning Series books). Plain HTML, CSS and JavaScript with no build step.

```
website/
  index.html      page content
  styles.css      design tokens (book palette) + layout
  app.js          A–Z gallery, page viewer, coloring demo, sign-up form
  assets/
    cover-front.webp          A to Z Animals Copy Coloring Book cover
    books/<book>/             cover + 4 preview pages for each Learning Series book
    animals/A–Z.webp          colored animals (gallery, studio reference)
    pages/A–Z.webp            A to Z coloring pages (gallery viewer, A to Z book previews)
    lineart/*.png             black & white art for the coloring demo
    logo/                     logos from brand/ on main (horizontal, stacked, home-screen icon)
    favicon-32.png, favicon-48.png   round badge
    og-tinytusk-books.jpg     link-preview image with all four covers
    downloads/                one free sample PDF per book
```

## Preview locally

```bash
cd website && python3 -m http.server 8000
```

Then open http://localhost:8000.

## Before launch: things to fill in

1. **Email sign-up**: in `index.html`, set `data-action="YOUR_FORM_ACTION_URL"` on `#notify-form` to your form endpoint (for example a Formspree URL `https://formspree.io/f/xxxx`, or a Mailchimp/ConvertKit form action). Until then the form validates the email and shows a "sign-ups open soon" message, but sends nothing.
2. **Buy links**: at the top of `app.js`, paste each book's Amazon link into `BOOK_LINKS` (`az-coloring`, `color-by-number`, `abc-tracing`, `trace-write`). That book's card switches from "In review" / "Coming soon" to "Now on Amazon" with a Buy on Amazon button. Also update the "When and where can I buy them?" FAQ answer.
3. **Custom domain** (optional): if you move to your own domain, update `og:image` and `og:url` in `index.html` to the new address.

## Deploy

The site is live on GitHub Pages at https://harshabhadra.github.io/TinyTusk-A-Z-Coloring-book/

Pushing changes under `website/` to the `website` branch runs `.github/workflows/deploy-site.yml`, which copies the folder to the `gh-pages` branch. Pages serves that branch (Settings → Pages → Deploy from a branch → `gh-pages`, `/ (root)`). A new version is usually live within a minute or two.

## Updating images

The images were generated from the book files (`cover.pdf`, `colored/`, `pages/`, `clean/`). If you redo an animal, regenerate its `animals/X.webp` and `pages/X.webp` at the same sizes (420 px max for animals, 850 × 1100 for pages).

Fonts (Baloo 2 and Fredoka, the same fonts as the book) load from Google Fonts.
