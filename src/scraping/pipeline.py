"""Scraper backbone for imot.bg apartment sales in Sofia (1-, 2-, 3-room).

This module is designed for incremental, restart-friendly scraping:
- iterate paginated result pages per room category
- extract detail URLs
- fetch + parse each listing
- append each row immediately to a CSV so crashes do not lose work

Selectors and patterns are conservative; adjust after inspecting real HTML during
the pilot run. Network calls can be rate-limited to remain polite, but the website doesn't seem to have a rate limiter so we won't be using it.
"""
from __future__ import annotations

import csv
import re
import time
from pathlib import Path
from typing import Dict, Any, Iterator, Iterable

import requests
from bs4 import BeautifulSoup

BASE_URLS: dict[int, str] = {
    # 1: "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/ednostaen?type_home=2~3~", for all
    1: "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/ednostaen",
    2: "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/dvustaen",
    3: "https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/tristaen",
}

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/118.0 Safari/537.36"
)

RAW_COLUMNS = [
    "url",
    "listing_id",
    "source",
    "price_raw",
    "area_raw",
    "rooms",
    "district_raw",
    "floor_raw",
    "max_floor_raw",
    "heat_raw",
    "construction_raw",
    "year_raw",
    "desc_text",
]

def _session() -> requests.Session:
    ses = requests.Session()
    ses.headers.update({"User-Agent": USER_AGENT})
    return ses

def _decode_html(resp: requests.Response) -> str:
    """Decode response bytes, choosing encoding with most Cyrillic characters."""
    candidates: list[str] = []
    if resp.encoding:
        candidates.append(resp.encoding)
    if resp.apparent_encoding and resp.apparent_encoding not in candidates:
        candidates.append(resp.apparent_encoding)
    for enc in ("utf-8", "cp1251"):
        if enc not in candidates:
            candidates.append(enc)

    best_html = None
    best_score = -1
    for enc in candidates:
        try:
            html = resp.content.decode(enc, errors="ignore")
        except Exception:
            continue
        score = sum(1 for ch in html if "\u0400" <= ch <= "\u04FF")
        if score > best_score:
            best_score = score
            best_html = html
    return best_html or resp.text

def _extract_next_page_url(html: str, current_url: str) -> str | None:
    """Attempt to find the next-page URL from pagination links.

    This uses `<a rel="next">`, Bulgarian "Следваща" text, or a general `page=`
    parameter. Adjust selectors after inspecting live markup.
    """
    soup = BeautifulSoup(html, "html.parser")

    link_tag = soup.find("link", rel="next")
    if link_tag and link_tag.get("href"):
        return requests.compat.urljoin(current_url, link_tag["href"])

    a_link = soup.find("a", rel="next")
    if a_link and a_link.get("href"):
        return requests.compat.urljoin(current_url, a_link["href"])

    for a in soup.find_all("a"):
        text = (a.get_text(strip=True) or "").lower()
        if "следващ" in text and a.get("href"):
            return requests.compat.urljoin(current_url, a["href"])

    if "page=" in current_url:
        try:
            current_page = int(re.search(r"page=(\d+)", current_url).group(1))
            return re.sub(r"page=\d+", f"page={current_page + 1}", current_url)
        except Exception:
            return None
    path_match = re.search(r"/p-(\d+)", current_url)
    if path_match:
        current_page = int(path_match.group(1))
        return re.sub(r"/p-\d+", f"/p-{current_page + 1}", current_url)
    if "?" in current_url:
        return f"{current_url}&page=2"
    return f"{current_url}?page=2"

def iter_result_pages(rooms: int, *, delay_seconds: float = 1.0, max_pages: int | None = None,
                      session: requests.Session | None = None) -> Iterator[str]:
    """Yield HTML for each search-results page for the given room count.

    Pagination uses `/p-{n}` path segments used by imot.bg (p-1, p-2, ...).
    Stops when `max_pages` is reached.
    """
    if rooms not in BASE_URLS:
        raise ValueError(f"Unsupported rooms={rooms}; expected one of {list(BASE_URLS)}")

    ses = session or _session()
    base_url = BASE_URLS[rooms]
    prefix, q = (base_url.split("?", 1) + [""])[:2]
    page_num = 1
    while True:
        url = prefix if page_num == 1 else f"{prefix}/p-{page_num}"
        if q:
            url = f"{url}?{q}"
        resp = ses.get(url, timeout=15)
        resp.raise_for_status()
        html = _decode_html(resp)
        print(f"[rooms={rooms}] GET {url} status={resp.status_code} bytes={len(resp.content)}")
        yield html

        if max_pages is not None and page_num >= max_pages:
            break
        page_num += 1
        time.sleep(delay_seconds)

def extract_listing_cards(results_page: str) -> list[dict[str, Any]]:
    """Parse the results page and return listing cards (url + headline info).

    Rules from sample HTML:
    - listings live under <div class="ads2023">
    - actual offers are <div class="item ..."> (e.g., item BEST, item TOP)
    - link is inside div.text > div.zaglavie > a.title
    We also capture the item id, headline price, and district if present.
    """
    soup = BeautifulSoup(results_page, "html.parser")
    container = soup.find("div", class_="ads2023")
    if not container:
        print("[warn] ads2023 container not found on results page")
        return []

    cards: list[dict[str, Any]] = []
    for item in container.find_all("div", class_=re.compile(r"\bitem\b")):
        title_tag = item.select_one("div.text div.zaglavie a.title[href]")
        if not title_tag:
            continue

        href = title_tag["href"]
        if "/obiava-" not in href:
            continue
        url = requests.compat.urljoin("https://www.imot.bg", href)
        listing_id = item.get("id")

        district_raw = None
        loc_tag = title_tag.find("location")
        if loc_tag:
            district_raw = loc_tag.get_text(strip=True)

        price_raw = None
        price_div = item.select_one("div.price div")
        if price_div:
            price_raw = price_div.get_text(" ", strip=True)

        cards.append({
            "url": url,
            "listing_id": listing_id,
            "district_raw": district_raw,
            "price_raw": price_raw,
        })
    return cards

def fetch_listing_detail(url: str, *, session: requests.Session | None = None) -> str:
    """Return raw HTML for a listing detail page (polite pacing applied externally)."""
    ses = session or _session()
    resp = ses.get(url, timeout=15)
    resp.raise_for_status()
    return _decode_html(resp)

def _text_search(text: str, patterns: Iterable[str]) -> str | None:
    for pat in patterns:
        match = re.search(pat, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return None

def parse_listing_detail(raw_page: str, *, rooms: int) -> Dict[str, Any]:
    """Extract structured fields from a listing detail page.

    Fields: url (to be added by caller), price_raw, area_raw, rooms, district_raw,
    floor_raw, max_floor_raw, heat_raw, construction_raw, year_raw, desc_text.
    Parsing follows the observed imot.bg DOM (ad2023 / contactsBox / adParams).
    """
    soup = BeautifulSoup(raw_page, "html.parser")

    listing_id = None
    district_raw = None
    price_raw = None
    area_raw = None
    floor_raw = None
    max_floor_raw = None
    heat_raw: str | None = None
    heat_raw_entries: list[str] = []
    construction_raw = None
    year_raw = None
    desc_text = None
    text_main = soup.get_text(" ", strip=True)

    contacts = soup.select_one("div.ad2023 div.right div.sticky div.contactsBox")
    if contacts:
        ob_title = contacts.select_one("div.obTitle h1")
        if ob_title:
            heading_text = ob_title.get_text(" ", strip=True)
            rooms_match = re.search(r"Продава\\s+(\\d)", heading_text)
            if rooms_match:
                rooms = int(rooms_match.group(1))
            district_div = ob_title.find("div")
            if district_div:
                district_raw = district_div.get_text(strip=True)
            id_span = ob_title.find("span")
            if id_span:
                id_text = id_span.get_text(strip=True)
                id_match = re.search(r"Обява:\\s*(\\w+)", id_text)
                if id_match:
                    listing_id = id_match.group(1)

        price_block = contacts.find("div", class_=re.compile(r"Price", re.IGNORECASE))
        if price_block:
            lines = [l.strip() for l in price_block.get_text("\\n", strip=True).split("\\n") if l.strip()]
            euro_line = next((ln for ln in lines if "€" in ln or "EUR" in ln), None)
            price_raw = euro_line or (lines[0] if lines else None)

    params = soup.find("div", class_="adParams")
    if params:
        for box in params.find_all("div", recursive=False):
            full = box.get_text(" ", strip=True)
            if ":" in full:
                label, val = full.split(":", 1)
            else:
                label, val = full, ""
            label = label.strip()
            val = val.strip()
            if label == "Площ":
                area_raw = val
            elif label == "Етаж":
                fl_match = re.search(r"(\d+)", val)
                if fl_match:
                    floor_raw = fl_match.group(1)
                max_match = re.search(r"(?:от|/)\s*(\d+)", val)
                if max_match:
                    max_floor_raw = max_match.group(1)
            elif label and "Строителство" in label:
                cons_match = re.search(r"(Тухла|Панел|ЕПК|ПК)", val, flags=re.IGNORECASE)
                if cons_match:
                    construction_raw = cons_match.group(1)
                year_match = re.search(r"(19\d{2}|20\d{2})", val)
                if year_match and not year_raw:
                    year_raw = year_match.group(1)
            elif label in {"Газ", "ТEЦ", "ТЕЦ"}:
                heat_raw_entries.append(f"{label}: {val}")

    if heat_raw_entries:
        heat_raw = "; ".join(heat_raw_entries)
    else:
        heat_raw = _text_search(text_main, [r"ТЕЦ", r"газ", r"електр", r"клим", r"парно"])

    desc_box = soup.find("div", class_="borderBox")
    if desc_box:
        desc_text = desc_box.get_text(" ", strip=True)
    else:
        desc_text = text_main[:2000]

    if not year_raw:
        yr_match = re.search(r"(19\\d{2}|20\\d{2})", desc_text or "")
        if yr_match:
            year_raw = yr_match.group(1)

    return {
        "url": None,
        "listing_id": listing_id,
        "source": "imot.bg",
        "price_raw": price_raw,
        "area_raw": area_raw,
        "rooms": rooms,
        "district_raw": district_raw,
        "floor_raw": floor_raw,
        "max_floor_raw": max_floor_raw,
        "heat_raw": heat_raw,
        "construction_raw": construction_raw,
        "year_raw": year_raw,
        "desc_text": desc_text,
    }

def append_row(row: dict[str, Any], *, output_path: str) -> None:
    """Append a single listing row to a CSV (restart-friendly)."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RAW_COLUMNS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def _load_seen_urls(output_path: str) -> set[str]:
    path = Path(output_path)
    if not path.exists():
        return set()
    urls: set[str] = set()
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            url_val = row.get("url")
            if url_val:
                urls.add(url_val)
    return urls

def crawl_room_category(
    rooms: int,
    *,
    output_path: str,
    delay_seconds: float = 1.0,
    max_pages: int | None = None,
    log_every: int = 10,
) -> None:
    """Driver to crawl one room-count category and append listings incrementally.

    Steps:
    - iterate result pages
    - extract detail URLs
    - fetch details (optional per-listing delay)
    - parse and append immediately to disk for crash resilience
    - skip already-seen URLs when restarting (read existing output)
    """
    seen = _load_seen_urls(output_path)
    ses = _session()
    processed = 0
    page_idx = 0
    for page_html in iter_result_pages(rooms, delay_seconds=delay_seconds, max_pages=max_pages, session=ses):
        page_idx += 1
        print(f"[rooms={rooms}] page {page_idx} fetched")
        cards = extract_listing_cards(page_html)
        print(f"[rooms={rooms}] page {page_idx} cards found: {len(cards)} (seen so far: {len(seen)})")
        for card in cards:
            url = card["url"]
            if url in seen:
                continue
            try:
                raw_detail = fetch_listing_detail(url, session=ses)
                parsed = parse_listing_detail(raw_detail, rooms=rooms)
                parsed.update({
                    "url": url,
                    "listing_id": card.get("listing_id"),
                    "price_raw": parsed.get("price_raw") or card.get("price_raw"),
                    "district_raw": parsed.get("district_raw") or card.get("district_raw"),
                })
                append_row(parsed, output_path=output_path)
                seen.add(url)
                processed += 1
                if processed % log_every == 0:
                    print(f"[rooms={rooms}] processed {processed} listings so far")
            except Exception as exc:
                print(f"[warn] Failed to process {url}: {exc}")
            time.sleep(delay_seconds)
    print(f"[rooms={rooms}] done. new listings processed: {processed}")
