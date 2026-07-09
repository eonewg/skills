# Static personal site visual refactor notes

Use this when updating a deployed personal/static homepage and the user gives visual direction like “make the whole site feel like the first page/hero”.

## Workflow
1. Pull the deployed HTML/CSS and inspect the existing section structure.
2. Preserve useful content, but move decorative hero-side cards out of the hero if the user wants a cleaner first screen.
3. Convert moved content into a semantic downstream section such as `#status`, using the same visual language as the hero: white/near-white backgrounds, generous whitespace, soft rounded cards, subtle shadows, and restrained color.
4. Add real external profile links where provided (for example GitHub) in every relevant contact/action area, not just in copy.
5. If a bottom dock/floating nav competes with the requested clean style or overlaps content after scrolling, remove it unless the user explicitly wants that UI pattern.
6. Deploy with a backup and verify:
   - public `curl`/text checks for expected strings and removed elements;
   - browser open with cache-busting query string;
   - screenshot of first viewport;
   - scroll to next section and screenshot again;
   - browser console errors.

## Pitfalls
- DOM/a11y snapshots can say the right elements exist while the visual page is wrong because reveal animations, fixed nav, or floating elements overlap after scroll.
- Full-page screenshots can make fixed elements appear in the middle of a long image; inspect both current viewport screenshots and scrolled viewport screenshots.
- A user saying “move the three small cards to later pages/sections” means preserve their information, not delete it.
- A user saying “make the whole thing like the first page after removing the cards” usually means propagate the clean hero design language across sections, not keep a contrasting dark/cinematic section.
