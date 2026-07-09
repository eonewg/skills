# Lightweight editorial HTML lesson design notes

Use this reference when a lesson page is too card-heavy, too UI-like, or not Claude/editorial enough.

## Durable visual preference

Teaching pages should feel like a readable editorial/long-form note, not a SaaS dashboard, PPT, or documentation-site component library.

Core direction:
- Warm page background remains `#faf9f5`.
- Accent remains sparse coral `#cc785c`.
- Teaching annotations stay inside a warm ink/brown scale: near-black, deep brown-gray, warm gray, warm brown, deep warm brown, light warm brown. Do not introduce bright blue/green/purple/red label colors.
- Prefer `<strong>`, `<em>`, font weight, italic, and typographic hierarchy before adding more color. Multiple emphasis levels are allowed, but they should be different warm-brown values, not different saturated hues.
- Use containers only when structure truly needs aggregation or interaction.
- Prefer typography, whitespace, and subtle left rules over rounded cards, pills, panels, and decorative gradients.

## Specific rules

### Hero

Avoid heavy hero treatment:
- No large colored hero background block.
- No decorative pseudo-element circles such as `hero::after`.
- No badge pills.
- No four-stat grid inside the hero.

Preferred:
- Plain text eyebrow with subject and topic.
- Serif h1 using `var(--font-serif)`.
- Height around 140–160px when possible.
- Move metadata (time, positioning, next step) to sidebar or a brief ordinary info line.

### Typography

- `.hero h1` and `.section h2` should use `var(--font-serif)`.
- Keep body text in sans for readability.
- Section number markers should be plain accent text, e.g. `01 —`, not square/rounded badges.

### Sections and rhythm

- Avoid boxing each section.
- Avoid dense `border-bottom` section separators.
- Use vertical whitespace for rhythm; default section padding around 48–60px.

### Callouts

Avoid full accent-colored blocks unless the content truly needs a card.
Preferred callout treatment:
- transparent background
- `border-left: 3px solid var(--accent)`
- left padding
- no full border, no rounded rectangle

### Formula and example blocks

Avoid full bordered rounded cards and title color bands.
Preferred:
- left `2–3px` accent rule plus indentation
- small accent heading line
- formula inner box may keep an ultra-light background, but radius should stay small, around 8px

### Steps

Avoid filled round/square number badges.
Preferred:
- serif italic accent numbers, e.g. `1.` / `2.` / `3.`
- transparent step background
- more breathing room between steps

### Quiz choices

Avoid app-like buttons:
- no hover translate/raise motion
- no heavy rounded rectangles

Preferred:
- list-style buttons with transparent background
- shallow bottom border
- hover changes text/border color only
- correct/wrong states include textual symbols `✓` / `✗` in addition to color for accessibility

### Sidebar / TOC

- Sidebar navigation should not be a card.
- Use same background as page, muted text, and accent hover/active color.
- Mobile must not hide TOC entirely; keep it as a normal block near the top or under hero.

## Verification checklist

Before sending a revised lesson after this kind of critique, verify computed styles or visually inspect that:
- hero background is transparent and border width is `0px`
- `hero::after` is `none`
- hero height is roughly 140–160px when layout allows
- h1/h2 font family resolves to the serif stack
- h2 number marker has transparent background
- callout/formula/example blocks use left border rather than full card border
- quiz correct/wrong states expose `✓` / `✗`
- KaTeX still renders and raw delimiters are not visible