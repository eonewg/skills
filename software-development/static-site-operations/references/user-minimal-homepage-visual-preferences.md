# the user minimalist homepage visual preferences

Captured from homepage iteration on the Baidu VM static Nginx site.

## Preferences

- Ordinary content sections should not look like cards, boxes, panels, or tinted bands.
- Avoid light beige/gray alternating section backgrounds for normal text blocks.
- Avoid visible outer section borders/frames such as `border-top` on every section when they create a boxed feeling.
- Keep the page white and calm; use typography, whitespace, and occasional internal divider lines to structure content.
- Card UI is only for genuinely high-emphasis modules, not for every section.
- GitHub should appear intentionally, not repeatedly across sections.

## CSS pitfall observed

A rule like this made the “想做的事” line-list area look framed/tinted:

```css
.quiet-section {
  padding: 118px 0;
  border-top: 1px solid var(--border-light);
  background: var(--bg);
}
.quiet-section:nth-of-type(even) {
  background: linear-gradient(180deg, var(--bg) 0%, var(--bg-warm) 100%);
}
```

Preferred minimal version:

```css
.quiet-section {
  padding: 118px 0;
  background: var(--bg);
}
```

Keep internal list dividers if they aid scanning, e.g. `border-bottom` between rows, but avoid an outer frame around the entire section.

## Deployment note

When SSH reports `Exceeded MaxStartups` or resets during rapid repeated deploy commands, avoid opening multiple SSH/SCP sessions. Retry with backoff and, if possible, combine backup + upload + verification into one SSH session by streaming the file over stdin.
