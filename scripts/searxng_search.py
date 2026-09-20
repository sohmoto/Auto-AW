#!/usr/bin/env python3

import argparse
import html
import json
import os
import sys
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class SearXNGResultsParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.results = []
        self._article_depth = 0
        self._current = None
        self._in_heading = False
        self._capture_title = False
        self._capture_content = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = set(attributes.get("class", "").split())

        if tag == "article" and "result" in classes:
            self._article_depth = 1
            self._current = {"title": "", "url": "", "snippet": ""}
            return

        if not self._current:
            return

        if tag == "article":
            self._article_depth += 1
        elif tag == "h3":
            self._in_heading = True
        elif tag == "a" and self._in_heading:
            href = attributes.get("href", "")
            if href.startswith(("http://", "https://")):
                self._current["url"] = href
                self._capture_title = True
        elif tag == "p" and "content" in classes:
            self._capture_content = True

    def handle_endtag(self, tag):
        if not self._current:
            return

        if tag == "a":
            self._capture_title = False
        elif tag == "h3":
            self._in_heading = False
        elif tag == "p":
            self._capture_content = False
        elif tag == "article":
            self._article_depth -= 1
            if self._article_depth == 0:
                result = {key: " ".join(value.split()) for key, value in self._current.items()}
                if result["title"] and result["url"]:
                    self.results.append(result)
                self._current = None
                self._in_heading = False
                self._capture_title = False
                self._capture_content = False

    def handle_data(self, data):
        if not self._current:
            return
        if self._capture_title:
            self._current["title"] += data
        elif self._capture_content:
            self._current["snippet"] += data


def parse_args():
    parser = argparse.ArgumentParser(description="Search the workflow-local SearXNG instance.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--page", type=int, default=1, choices=range(1, 11))
    parser.add_argument("--language", default="all")
    parser.add_argument("--time-range", choices=("day", "month", "year"))
    parser.add_argument("--categories", default="general")
    parser.add_argument("--limit", type=int, default=10, choices=range(1, 21))
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main():
    args = parse_args()
    base_url = os.environ.get("SEARXNG_URL", "http://host.docker.internal:8080").rstrip("/")
    if base_url not in {"http://host.docker.internal:8080", "http://127.0.0.1:8888"}:
        print(f"Unsupported SEARXNG_URL: {base_url}", file=sys.stderr)
        return 2

    parameters = {
        "q": args.query,
        "pageno": args.page,
        "language": args.language,
        "categories": args.categories,
        "safesearch": 1,
    }
    if args.time_range:
        parameters["time_range"] = args.time_range

    request = Request(
        f"{base_url}/search?{urlencode(parameters)}",
        headers={"Accept": "text/html", "User-Agent": "Auto-AW/1.0"},
    )

    try:
        with urlopen(request, timeout=45) as response:
            content = response.read().decode(response.headers.get_content_charset() or "utf-8")
    except (HTTPError, URLError, TimeoutError) as error:
        print(f"SearXNG request failed: {error}", file=sys.stderr)
        return 1

    parser = SearXNGResultsParser()
    parser.feed(content)
    results = parser.results[: args.limit]

    if not results:
        print("SearXNG returned no parseable results.", file=sys.stderr)
        return 1

    if args.as_json:
        print(json.dumps({"query": args.query, "results": results}, ensure_ascii=False, indent=2))
        return 0

    print(f"# Search results: {html.escape(args.query)}")
    for index, result in enumerate(results, 1):
        print(f"\n## {index}. {result['title']}")
        print(result["url"])
        if result["snippet"]:
            print(result["snippet"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
