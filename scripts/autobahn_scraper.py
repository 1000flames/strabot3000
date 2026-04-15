#!/usr/bin/env python3
"""Scrape all VOB invitation-to-tender links from Die Autobahn's publication search.

Requires:
  BRIGHTDATA_API_KEY
  BRIGHTDATA_UNLOCKER_ZONE

Default output:
  /home/ai_1000flames_de/.openclaw/workspace/data/autobahn_ausschreibungen.json
"""

from __future__ import annotations

import argparse
import html as htmlmod
import json
import os
import re
import sys
from pathlib import Path
from urllib import request

API_ENDPOINT = "https://api.brightdata.com/request"
START_URL = (
    "https://vergabe.autobahn.de/NetServer/PublicationSearchControllerServlet"
    "?function=SearchPublications&Gesetzesgrundlage=VOB&Category=InvitationToTender"
    "&thContext=publications"
)
BASE_URL = "https://vergabe.autobahn.de/NetServer/"
DEFAULT_OUTPUT = Path("/home/ai_1000flames_de/.openclaw/workspace/data/autobahn_ausschreibungen.json")
ROW_RE = re.compile(
    r'<tr class="tableRow clickable-row publicationDetail"[^>]*data-oid="([^"]+)"[^>]*'
    r'data-category="([^"]+)"[^>]*>\s*'
    r'<td >([^<]+)</td>\s*'
    r'<td class="tender">\s*(.*?)\s*</td>\s*'
    r'<td class="tenderAuthority" >([^<]+)</td>\s*'
    r'<td class="tenderType">([^<]+)</td>\s*'
    r'<td class="tenderType">([^<]+)</td>\s*'
    r'<td class="tenderDeadline">([^<]+)</td>',
    re.S,
)


def bright_raw(url: str, api_key: str, zone: str, body: str | None = None, method: str = "GET") -> str:
    payload: dict[str, object] = {"zone": zone, "url": url, "format": "raw"}
    if method != "GET":
        payload["method"] = method
    if body is not None:
        payload["body"] = body
    if method == "POST":
        payload["headers"] = {"Content-Type": "application/x-www-form-urlencoded"}

    req = request.Request(
        API_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8", "ignore")


def parse_rows(page_html: str, page_start: int) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for match in ROW_RE.finditer(page_html):
        oid, category, published, tender, authority, procedure, law, deadline = match.groups()
        title = htmlmod.unescape(re.sub(r"\s+", " ", tender).strip())
        authority = htmlmod.unescape(re.sub(r"\s+", " ", authority).strip())
        published = htmlmod.unescape(published.strip())
        deadline = htmlmod.unescape(deadline.strip())
        detail_url = f"{BASE_URL}PublicationControllerServlet?function=Detail&TOID={oid}&Category={category}"
        results.append(
            {
                "title": title,
                "url": detail_url,
                "oid": oid,
                "publishedAt": published,
                "authority": authority,
                "procedure": procedure.strip(),
                "law": law.strip(),
                "deadline": deadline,
                "pageStart": page_start,
            }
        )
    return results


def discover_starts(first_page_html: str) -> list[int]:
    starts = sorted({int(s) for s in re.findall(r"Start=(\d+)", first_page_html)})
    if 0 not in starts:
        starts.insert(0, 0)
    return starts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="JSON output path")
    parser.add_argument("--limit-pages", type=int, default=0, help="Limit pages to fetch (0 = all discovered)")
    args = parser.parse_args()

    api_key = os.environ.get("BRIGHTDATA_API_KEY")
    zone = os.environ.get("BRIGHTDATA_UNLOCKER_ZONE")
    if not api_key or not zone:
        print("Missing BRIGHTDATA_API_KEY or BRIGHTDATA_UNLOCKER_ZONE", file=sys.stderr)
        return 1

    first_html = bright_raw(START_URL, api_key, zone)
    starts = discover_starts(first_html)
    if args.limit_pages > 0:
        starts = starts[: args.limit_pages]

    results: list[dict[str, object]] = []
    for start in starts:
        url = START_URL if start == 0 else f"{START_URL}&Start={start}"
        page_html = first_html if start == 0 else bright_raw(url, api_key, zone)
        results.extend(parse_rows(page_html, start))

    payload = {
        "source": START_URL,
        "scrapedAt": "2026-04-15T07:15:00Z",
        "count": len(results),
        "results": results,
    }

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"saved {out_path}")
    print(f"count {len(results)}")
    for item in results[:3]:
        print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
