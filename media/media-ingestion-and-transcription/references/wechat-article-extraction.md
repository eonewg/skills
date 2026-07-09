# WeChat public account article extraction

Use this when the user sends a `mp.weixin.qq.com/s/...` article and wants Markdown, summary, notes, or wiki ingestion.

## Local fixed tool path

Installed working checkout:

```bash
~/.hermes/tools/wechat-article-for-ai
```

Convenience wrapper:

```bash
~/.hermes/scripts/wechat_article_to_md.sh "https://mp.weixin.qq.com/s/xxxx"
```

Default output directory:

```text
~/.hermes/data/wechat-articles
```

## Verified capability

A real WeChat public-account article was successfully extracted to Markdown, preserving title, author, publish time, body text, and code blocks.

## Known local fixes / pitfalls

- Camoufox/uBlock can fail with `manifest.json is missing` when the extension directory is empty. Re-download/restore the uBlock extension directory before blaming WeChat anti-bot behavior.
- The upstream extractor hit a `NoneType is not callable` crash on articles containing code blocks. The local checkout has been patched; if the error reappears after updating the tool, inspect the code-block parsing path first.
- Verify the generated Markdown file exists and has substantial body text before summarizing or writing downstream notes.
- A first `Page.goto ... Timeout 30000ms exceeded` from the wrapper is often transient because the wrapper retries internally. Do not treat the first timeout line as failure if the run later logs `Title:` and `Saved:`; judge success by the saved Markdown artifact and body length.
- Sometimes the wrapper logs `Could not extract article title` even though the debug HTML contains a valid short WeChat text article (`item_show_type=10`) with `#js_text_title`, `#js_text_desc`, and `#publish_time`. Before declaring CAPTCHA failure, inspect the debug HTML under `~/.hermes/data/wechat-articles/debug/`; if it does **not** contain `环境异常` and has `id="js_content"` / `id="js_text_desc"`, extract the text from those DOM nodes (e.g. with BeautifulSoup), preserve a note in raw frontmatter, and continue ingestion. If debug HTML only contains the verification page, stop and ask for pasted/exported content.

## Standard flow

0. For the user, a bare `mp.weixin.qq.com/s/...` link usually means: extract it, assess signal density, and ingest useful information into the local wiki according to `personal-knowledge-systems/references/the user-filesystem-wiki.md` -- not just return a chat summary. Only stop at summary if the user explicitly asks for summary-only.
1. Run the wrapper with the WeChat URL.
2. Inspect the output Markdown title and body length.
3. If the log contains an early timeout but later `Saved: ...`, continue normally after verifying the saved Markdown.
4. If the wrapper fails with title extraction but writes debug HTML, inspect the debug HTML before giving up; valid short-text WeChat pages can be recovered from `#js_text_title`, `#js_text_desc`, and `#publish_time`.
5. Use the Markdown artifact or recovered debug-HTML text for summary, critique, knowledge extraction, or wiki ingestion.
