# WordPress category/archive page ingestion

Use when the user explicitly asks to archive a WordPress category, tag, blog index, or other listing page rather than a single article.

## Pattern

1. Treat the page as a **source map / corpus entry**, not as one normal article.
2. Extract the archive page itself, then check whether the site exposes WordPress REST endpoints:
   - `/wp-json/wp/v2/categories?slug=<slug>` to resolve category id, count, description, and canonical link.
   - `/wp-json/wp/v2/posts?per_page=100&categories=<id>&_fields=date,link,title,excerpt,tags` to capture the post index without mirroring every article.
3. Preserve raw evidence as a compact corpus raw file under `raw/articles/` or `raw/sources/` containing:
   - source URL and canonical URL
   - category id / slug / count / description when available
   - extracted archive summaries for the first pages if useful
   - REST post index metadata
   - an explicit note that individual posts were not fully mirrored unless separately fetched
4. Create or patch one formal concept/entity page that captures the reusable intellectual map of the corpus.
   - For an author blog, prefer a concept like `<author>-<domain>-philosophy` or an entity page for the author if the person is the main reusable object.
   - Do not create one page per post unless the user asks for a deep corpus ingestion or a post is high-signal enough on its own.
5. Update index/hot/log/manifest and run lint/build/query verification as usual.

## Extraction heuristics

- Category pages may be long and summaries can truncate. The REST metadata is often more reliable for post coverage than a rendered category page.
- If the category has many posts, store metadata for up to the API/page limit and state the coverage. Do not imply the whole archive was fully read when only summaries/metadata were captured.
- If a category archive surfaces several themes across posts, formalize those themes as a compact map: recurring claims, tensions, vocabulary, and links to existing wiki concepts.

## Example shape

For `https://jondron.ca/category/blog/`, the WordPress API exposed category slug `blog`, id `4`, count `87`, and description “Original blog posts, as opposed to comments on bookmarked content”. The useful formal page is a map of Jon Dron’s education-technology philosophy rather than 87 separate post pages.
