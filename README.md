# Ozi Realty website (modern rebuild)

A modern rebuild of www.ozirealty.com.au. It keeps the same pages, URLs, copy, images and brand colours, and is deployed to the Wix Headless site `69fed271-bb73-4ade-b57a-6db7f55c7b59`.

- `tools/extract.py`: turns saved live-site HTML into `content/content.json` (sections, copy, images, forms).
- `tools/posts_meta.py`: blog post dates and categories go into `content/posts-meta.json`.
- `tools/build.py`: renders `content/*.json` into the static site in `site/`.
- `site/assets/site.css` and `site/assets/site.js` hold the design system and behaviour.

Rebuild: `python3 tools/build.py`. Then drop the `site/` folder onto the Wix headless site.
Enquiry forms validate the input, then open the visitor's email app addressed to the matching department mailbox (sell@, rent@, buy@, oversea@, support@).
