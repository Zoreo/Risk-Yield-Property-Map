"""Run a pilot scrape for imot.bg Sofia apartments (1/2/3-room).

Usage:
  python run_pilot_scrape.py --pages 2 --delay 1.0 --output-prefix data/raw/raw_room

Logs progress per page and every N listings; reports HTTP/parse errors.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.scraping.pipeline import crawl_room_category


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pilot scrape imot.bg Sofia apartments")
    parser.add_argument("--pages", type=int, default=2, help="Max pages per room (None for all)")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests (seconds)")
    parser.add_argument(
        "--output-prefix",
        default="data/raw/raw_room",
        help="Prefix for output CSVs; rooms will append 1/2/3 and _pilot.csv",
    )
    parser.add_argument("--log-every", type=int, default=10, help="Log every N listings")
    args = parser.parse_args(argv)

    rooms_list = [1, 2, 3]
    for r in rooms_list:
        output_path = f"{args.output_prefix}{r}_pilot.csv"
        print(f"[start] rooms={r} -> {output_path}, pages={args.pages}, delay={args.delay}s")
        try:
            crawl_room_category(
                rooms=r,
                output_path=output_path,
                delay_seconds=args.delay,
                max_pages=args.pages,
                log_every=args.log_every,
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[error] rooms={r} failed: {exc}")
    print("[done] pilot scrape finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
