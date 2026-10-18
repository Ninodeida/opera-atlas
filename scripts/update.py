#!/usr/bin/env python3
"""Daily updater for Opera Atlas. Standard library only.

Reads public RSS feeds, keeps the newest opera headlines and every mention of
Nino Surguladze, and writes feed.json. Also stamps data.json with today's date.
A feed that fails is skipped; the script never deletes existing items.
"""
import json
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_ITEMS = 80

NINO_RE = re.compile(r"surguladze|сургуладзе|сургуладзе|სურგულაძე|surgouladze", re.I)


def gnews(query, hl="en", gl="US"):
    q = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={gl}:{hl}"


# (label, url, nino_only) - edit freely.
FEEDS = [
    ("OperaWire", "https://operawire.com/feed/", False),
    ("Google News", gnews('"Nino Surguladze"'), True),
    ("Google News (IT)", gnews('"Nino Surguladze"', "it", "IT"), True),
    ("Google News (RU)", gnews('"Нино Сургуладзе"', "ru", "RU"), True),
    ("Google News (KA)", gnews('"ნინო სურგულაძე"', "ka", "GE"), True),
    ("Google News", gnews("opera premiere 2026 new production"), False),
]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "OperaAtlasBot/1.0 (+github pages)"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def parse_rss(xml_bytes, label):
    items = []
    root = ET.fromstring(xml_bytes)
    for it in root.iter("item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not title or not link:
            continue
        date = ""
        raw = it.findtext("pubDate")
        if raw:
            try:
                date = parsedate_to_datetime(raw).astimezone(timezone.utc).date().isoformat()
            except (TypeError, ValueError):
                pass
        src = it.findtext("source") or label
        items.append({"title": title, "link": link, "date": date, "source": src.strip()})
    return items


def main():
    feed_path = ROOT / "feed.json"
    try:
        old = json.loads(feed_path.read_text(encoding="utf-8")).get("items", [])
    except (OSError, ValueError):
        old = []
    seen = {i["link"]: i for i in old}
    for label, url, nino_only in FEEDS:
        try:
            got = parse_rss(fetch(url), label)
        except Exception as exc:  # network, parse, anything
            print(f"skip {label}: {exc}", file=sys.stderr)
            continue
        for it in got:
            is_nino = bool(NINO_RE.search(it["title"]))
            if nino_only and not is_nino and label.startswith("Google News"):
                # Google returns loose matches; keep only real name hits.
                continue
            it["nino"] = is_nino
            seen.setdefault(it["link"], it)
    items = sorted(seen.values(), key=lambda i: i.get("date", ""), reverse=True)[:MAX_ITEMS]
    today = datetime.now(timezone.utc).date().isoformat()
    feed_path.write_text(json.dumps({"updated": today, "items": items}, ensure_ascii=False, indent=1), encoding="utf-8")

    data_path = ROOT / "data.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    data["updated"] = today
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"feed.json: {len(items)} items; data.json stamped {today}")


if __name__ == "__main__":
    main()
