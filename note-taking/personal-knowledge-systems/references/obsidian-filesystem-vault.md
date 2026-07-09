---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `~/.hermes/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

For the user's local wiki, `~/wiki` is the default formal knowledge base. It is not necessarily an Obsidian vault, but the same markdown file-tool practices apply; follow the wiki schema/index/log rules from `personal-knowledge-systems` when writing there.

For the user's Obsidian vault, the default resolved path is `/mnt/e/Obsidian/Warehouse/Study`. Treat it as a front-stage scratch/handwritten-note/browsing layer, not the canonical long-term knowledge backend. Routing rule: when the user says “整理 / 入库 / 沉淀 / 文章 / 书摘 / wiki / 知识库”, default to `~/wiki`; when he explicitly says “Obsidian / 草稿 / 随手记 / 放到笔记里”, write under `/mnt/e/Obsidian/Warehouse/Study`; when he asks to formalize an Obsidian draft, extract the durable model into the wiki.

When the user asks whether Obsidian is available/usable, distinguish the Obsidian app from the vault: check `command -v obsidian`, `OBSIDIAN_VAULT_PATH`, Obsidian config such as `~/.config/obsidian/obsidian.json`, and the fallback `~/Documents/Obsidian Vault`. If the app exists but no env-var vault is configured, say it can still be used filesystem-first once a vault path is known, and offer either to locate existing vaults or to treat `~/wiki` as an Obsidian-compatible vault. Do not claim Obsidian is unusable merely because the env var/default vault is missing.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
