# Ozi Realty: Design Refresh Guide for the Wix Editor

This refresh keeps your current layout, page structure and colours, and rebuilds every element (buttons, cards, forms, headers and spacing) in the style used by leading Australian agency sites in 2026, such as Ray White, Belle Property, McGrath and boutique Adelaide agencies.

The live prototype is `redesign/index.html`. Open it in a browser to see each element before you rebuild it in the Editor.

## 1. Apply your colours (Site Design → Colours)
Map your existing palette onto these 5 roles. Use the same values in the `:root` tokens of `index.html` so the prototype matches your site.

| Role | Used for | Prototype default |
|---|---|---|
| Primary | Top bar, dark buttons, appraisal panel, footer | `#0F2A44` |
| Accent | Main CTA buttons, eyebrows, icons, stars | `#C8A15A` |
| Surface | Alternating section backgrounds | `#F7F6F3` |
| Text | Body text | `#14181F` |
| Muted | Secondary text and addresses | `#5B6472` |
| Line | Card borders and dividers | `#E6E3DD` |

Rule: the accent colour covers about 10% of a page at most. Use it for actions and nothing else.

## 2. Typography (Site Design → Text)
- **Headings:** Fraunces (or Playfair Display / Cormorant if Fraunces is unavailable), weight 500, tight line height 1.15.
- **Body & UI:** Inter (or DM Sans / Poppins), 16px, line height 1.6.
- **Eyebrow labels:** 12px, bold, uppercase, letter-spacing 14%, in the accent colour, placed above every section heading.
- Sizes: H1 64px desktop / 36px mobile · H2 42 / 28 · H3 20.

## 3. Component specs (rebuild these)
| Element | Spec |
|---|---|
| Buttons | Pill shape (radius 999), 48px tall, 22px side padding, semibold 15px. Primary = accent fill. Secondary = 1px Line border, transparent. Hover = lift 1px. |
| Header | Sticky, 76px, white at 88% opacity with blur, 1px bottom border. Thin primary-colour top bar with phone and email. "Free appraisal" CTA always visible. |
| Hero | Full-bleed photo with a dark gradient at the bottom, left-aligned headline, and a **floating white search card** with Buy / Rent / Sold tabs, location, type, price and a Search button. |
| Trust strip | 4 stats under the hero: Google rating, sale-to-list %, days on market, properties managed. **Use only your real numbers.** |
| Listing card | Radius 14, 1px border, 4:3 image, status badge (New / Auction / Sold), heart (save) icon, inspection-time label on the photo, bold price, muted address, bed/bath/car icon row. Hover = shadow + 3px lift + 4% image zoom. |
| Service cards | 3 cards, radius 14, soft accent-tinted icon tile, short copy, underlined arrow link. |
| Appraisal CTA | Full-width primary-colour panel with the lead form on a white card inside it. This is the #1 lead generator on AU agency sites, so repeat it on Sell and Property Management pages. |
| Team cards | 4:5 portrait photos with consistent lighting and background, name, role, and Call / Email buttons. |
| Reviews | Large aggregate score card plus a 2×2 grid of quotes. Connect real Google reviews via the Wix app if possible. |
| Footer | Dark primary colour, 4 columns, **Acknowledgement of Country**, RLA licence number, privacy links. |
| Mobile | Sticky bottom bar with **Call** and **Free appraisal**, and 16px side margins. |

## 4. Spacing & effects
- Section padding 88px desktop / 56px mobile; content max width 1240px.
- Corner radius: cards 14, inputs 12, buttons pill.
- Shadow: soft only (`0 8px 24px rgba(16,24,40,.06)`). Never use dark drop shadows.
- Photography: bright, natural daylight, wide angle. Avoid stock images with people in suits.

## 5. 2026 AU real-estate trend checklist
- [ ] Search-first hero (portal-style) instead of a slideshow
- [ ] Free appraisal CTA in the header, hero and mid-page, plus a mobile sticky bar
- [ ] Inspection times and auction dates shown on every listing card
- [ ] Social proof near the top (rating, results)
- [ ] Suburb or market insight content (Wix Blog is already installed)
- [ ] Acknowledgement of Country and RLA licence number in the footer
- [ ] Click-to-call phone numbers everywhere
- [ ] Fast images (WebP, lazy loading) and sufficient contrast
- [ ] Booking for appraisals via Wix Bookings (already installed)
