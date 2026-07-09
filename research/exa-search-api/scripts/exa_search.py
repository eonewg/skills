#!/usr/bin/env python3
"""CLI wrapper for Exa direct APIs.

Supports:
- POST https://api.exa.ai/search
- POST https://api.exa.ai/contents

Uses x-api-key auth and local .env loading. Never prints the key.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from urllib import error, request

BASE_URL = "https://api.exa.ai"
SKILL_DIR = Path(__file__).resolve().parents[1]
HERMES_ENV = Path.home() / ".hermes" / ".env"
DEEP_TYPES = {"deep-lite", "deep", "deep-reasoning"}
CATEGORY_FILTER_LIMITED = {"company", "people"}
SECTIONS = ["header", "navigation", "banner", "body", "sidebar", "footer", "metadata"]


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key:
            values[key] = val
    return values


def get_api_key(cli_key: str | None) -> str:
    if cli_key:
        return cli_key.strip()
    local = load_env_file(SKILL_DIR / ".env").get("EXA_API_KEY", "").strip()
    if local:
        return local
    hermes = load_env_file(HERMES_ENV).get("EXA_API_KEY", "").strip()
    if hermes:
        return hermes
    return os.environ.get("EXA_API_KEY", "").strip()


def parse_json_value(value: str | None, label: str) -> Any:
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON for {label}: {exc}") from exc


def load_json_arg(value: str | None, label: str) -> Any:
    """Parse JSON from a literal string or @path."""
    if not value:
        return None
    if value.startswith("@"):
        path = Path(value[1:]).expanduser()
        try:
            return json.loads(path.read_text())
        except OSError as exc:
            raise SystemExit(f"Cannot read {label} file {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise SystemExit(f"Invalid JSON in {label} file {path}: {exc}") from exc
    return parse_json_value(value, label)


def add_content_args(parser: argparse.ArgumentParser, *, nested: bool) -> None:
    parser.add_argument("--highlights", action="store_true", help="Return query-relevant highlights")
    parser.add_argument("--highlight-query", help="Custom query to guide highlights")
    parser.add_argument("--highlight-max", type=int, help="Max highlight characters per result")
    parser.add_argument("--text", action="store_true", help="Return page text as markdown")
    parser.add_argument("--text-max", type=int, help="Max text characters per result")
    parser.add_argument("--include-html-tags", action="store_true", help="Preserve HTML tags in text")
    parser.add_argument("--text-verbosity", choices=["compact", "standard", "full"], help="Text extraction verbosity")
    parser.add_argument("--include-section", action="append", choices=SECTIONS, help="Only include this page section; repeatable")
    parser.add_argument("--exclude-section", action="append", choices=SECTIONS, help="Exclude this page section; repeatable")
    parser.add_argument("--summary", nargs="?", const="", default=None, help="Return generic summary, or summary biased by this query")
    parser.add_argument("--summary-schema", help="JSON schema for per-result structured summary; literal JSON or @file")
    parser.add_argument("--livecrawl-timeout", type=int, help="Livecrawl timeout in milliseconds")
    parser.add_argument("--max-age-hours", type=int, help="Cache freshness: 0 always livecrawl, -1 cache only")
    parser.add_argument("--subpages", type=int, help="Number of subpages to crawl per result")
    parser.add_argument("--subpage-target", action="append", help="Keyword(s) to prioritize for subpages; repeatable")
    parser.add_argument("--extra-links", type=int, help="Number of URLs to extract from each page")
    parser.add_argument("--extra-image-links", type=int, help="Number of image URLs to extract from each page")
    if nested:
        parser.add_argument("--no-contents", action="store_true", help="Do not request contents; URLs/titles only")


def build_content_options(args: argparse.Namespace) -> dict[str, Any]:
    content: dict[str, Any] = {}
    if getattr(args, "highlights", False):
        content["highlights"] = True if not args.highlight_query and args.highlight_max is None else {
            k: v for k, v in {
                "query": args.highlight_query,
                "maxCharacters": args.highlight_max,
            }.items() if v is not None
        }
    if getattr(args, "text", False):
        text_obj: dict[str, Any] = {}
        if args.text_max is not None:
            text_obj["maxCharacters"] = args.text_max
        if args.include_html_tags:
            text_obj["includeHtmlTags"] = True
        if args.text_verbosity:
            text_obj["verbosity"] = args.text_verbosity
        if args.include_section:
            text_obj["includeSections"] = args.include_section
        if args.exclude_section:
            text_obj["excludeSections"] = args.exclude_section
        content["text"] = text_obj or True
    if args.summary is not None:
        summary_obj: Any = True if args.summary == "" else {"query": args.summary}
        schema = load_json_arg(args.summary_schema, "summary-schema")
        if schema is not None:
            if summary_obj is True:
                summary_obj = {}
            summary_obj["schema"] = schema
        content["summary"] = summary_obj
    if args.livecrawl_timeout is not None:
        content["livecrawlTimeout"] = args.livecrawl_timeout
    if args.max_age_hours is not None:
        content["maxAgeHours"] = args.max_age_hours
    if args.subpages is not None:
        content["subpages"] = args.subpages
    if args.subpage_target:
        content["subpageTarget"] = args.subpage_target if len(args.subpage_target) > 1 else args.subpage_target[0]
    if args.extra_links is not None or args.extra_image_links is not None:
        content["extras"] = {}
        if args.extra_links is not None:
            content["extras"]["links"] = args.extra_links
        if args.extra_image_links is not None:
            content["extras"]["imageLinks"] = args.extra_image_links
    return content


def validate_search_args(args: argparse.Namespace) -> None:
    if not (1 <= args.num_results <= 100):
        raise SystemExit("--num-results must be 1..100")
    if args.additional_query and args.type not in DEEP_TYPES:
        raise SystemExit("--additional-query is only supported for --type deep-lite, deep, or deep-reasoning")
    if args.category in CATEGORY_FILTER_LIMITED:
        bad = []
        if args.exclude_domain:
            bad.append("--exclude-domain")
        if args.start_published_date:
            bad.append("--start-published-date")
        if args.end_published_date:
            bad.append("--end-published-date")
        if bad:
            raise SystemExit(f"category '{args.category}' does not support {', '.join(bad)}")


def build_search_payload(args: argparse.Namespace) -> dict[str, Any]:
    validate_search_args(args)
    payload: dict[str, Any] = {
        "query": args.query,
        "type": args.type,
        "numResults": args.num_results,
    }
    if args.stream:
        payload["stream"] = True
    if args.category:
        payload["category"] = args.category
    if args.user_location:
        payload["userLocation"] = args.user_location
    if args.include_domain:
        payload["includeDomains"] = args.include_domain
    if args.exclude_domain:
        payload["excludeDomains"] = args.exclude_domain
    if args.start_published_date:
        payload["startPublishedDate"] = args.start_published_date
    if args.end_published_date:
        payload["endPublishedDate"] = args.end_published_date
    if args.moderation:
        payload["moderation"] = True
    if args.compliance:
        payload["compliance"] = args.compliance
    if args.additional_query:
        payload["additionalQueries"] = args.additional_query
    if args.system_prompt:
        payload["systemPrompt"] = args.system_prompt
    schema = load_json_arg(args.output_schema, "output-schema")
    if schema is not None:
        payload["outputSchema"] = schema

    contents = {} if args.no_contents else build_content_options(args)
    if contents:
        payload["contents"] = contents
    return payload


def build_contents_payload(args: argparse.Namespace) -> dict[str, Any]:
    if not args.url:
        raise SystemExit("contents requires at least one URL")
    payload: dict[str, Any] = {"urls": args.url}
    payload.update(build_content_options(args))
    return payload


def call_exa(path: str, payload: dict[str, Any], api_key: str, timeout: int) -> tuple[int, dict[str, str], str, int]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers={"Content-Type": "application/json", "x-api-key": api_key},
        method="POST",
    )
    start = time.time()
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            elapsed = round((time.time() - start) * 1000)
            return resp.status, dict(resp.headers), text, elapsed
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        elapsed = round((time.time() - start) * 1000)
        return exc.code, dict(exc.headers), text, elapsed


def print_markdown(data: dict[str, Any], elapsed_ms: int, title: str) -> None:
    results = data.get("results") or data.get("contents") or []
    print(f"## {title} ({len(results)} results, {elapsed_ms}ms)\n")
    if data.get("output") is not None:
        print("### Output\n")
        print(json.dumps(data["output"], ensure_ascii=False, indent=2) if not isinstance(data["output"], str) else data["output"])
        print("\n---\n")
    for idx, item in enumerate(results, 1):
        title_s = (item.get("title") or "").strip() or "(untitled)"
        url = (item.get("url") or item.get("id") or "").strip()
        score = item.get("score")
        score_s = f" — score {score:.3f}" if isinstance(score, (float, int)) else ""
        print(f"### {idx}. {title_s}{score_s}")
        if url:
            print(f"- **URL**: {url}")
        if item.get("publishedDate"):
            print(f"- **Published**: {item.get('publishedDate')}")
        if item.get("author"):
            print(f"- **Author**: {item.get('author')}")
        highlights = item.get("highlights") or []
        for hidx, highlight in enumerate(highlights[:3], 1):
            h = " ".join(str(highlight).split())
            print(f"- **Highlight {hidx}**: {h[:700]}{'...' if len(h) > 700 else ''}")
        summary = item.get("summary")
        if summary:
            s = summary if isinstance(summary, str) else json.dumps(summary, ensure_ascii=False)
            print(f"- **Summary**: {s[:900]}{'...' if len(s) > 900 else ''}")
        text = item.get("text")
        if text:
            t = "\n".join(str(text).splitlines()[:20])
            print("\n```text")
            print(t[:1600] + ("..." if len(t) > 1600 else ""))
            print("```")
        print()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Exa direct API CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="POST /search: find URLs and optionally retrieve contents")
    s.add_argument("query")
    s.add_argument("--api-key", default=None)
    s.add_argument("--num-results", "-n", type=int, default=5)
    s.add_argument("--type", default="auto", choices=["auto", "fast", "instant", "deep-lite", "deep", "deep-reasoning"])
    s.add_argument("--stream", action="store_true", help="Request SSE streaming mode; prints raw response")
    s.add_argument("--category", choices=["company", "people", "research paper", "news", "personal site", "financial report"])
    s.add_argument("--user-location", help="Two-letter ISO country code, e.g. US")
    s.add_argument("--include-domain", action="append")
    s.add_argument("--exclude-domain", action="append")
    s.add_argument("--start-published-date")
    s.add_argument("--end-published-date")
    s.add_argument("--moderation", action="store_true")
    s.add_argument("--compliance", choices=["hipaa"], help="Enterprise-only compliance mode")
    s.add_argument("--additional-query", action="append")
    s.add_argument("--system-prompt")
    s.add_argument("--output-schema", help="JSON schema for synthesized output; literal JSON or @file")
    add_content_args(s, nested=True)
    s.add_argument("--timeout", type=int, default=40)
    s.add_argument("--json", action="store_true", help="Print raw JSON response")

    c = sub.add_parser("contents", help="POST /contents: retrieve contents for known URLs")
    c.add_argument("url", nargs="+", help="URL(s) to fetch")
    c.add_argument("--api-key", default=None)
    add_content_args(c, nested=False)
    c.add_argument("--timeout", type=int, default=40)
    c.add_argument("--json", action="store_true", help="Print raw JSON response")

    args = parser.parse_args(argv)

    api_key = get_api_key(args.api_key)
    if not api_key:
        print("Missing EXA_API_KEY. Put it in this skill's .env, ~/.hermes/.env, env var, or pass --api-key.", file=sys.stderr)
        return 1

    try:
        if args.command == "search":
            path = "/search"
            payload = build_search_payload(args)
            md_title = "Exa Search Results"
        elif args.command == "contents":
            path = "/contents"
            payload = build_contents_payload(args)
            md_title = "Exa Contents Results"
        else:
            raise SystemExit(f"Unknown command: {args.command}")
    except SystemExit as exc:
        print(str(exc), file=sys.stderr)
        return 2

    status, _headers, body, elapsed_ms = call_exa(path, payload, api_key, args.timeout)
    if status < 200 or status >= 300:
        print(f"Exa {args.command} failed HTTP {status} ({elapsed_ms}ms)", file=sys.stderr)
        print(body[:2000], file=sys.stderr)
        return 1
    if getattr(args, "stream", False):
        print(body)
        return 0
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        print(body)
        return 0
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_markdown(data, elapsed_ms, md_title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
