#!/usr/bin/env python3
"""
Command line entrypoint for the Public Libraries News scraper.
"""

import argparse
import sys
from .scraper import PLNScraper

def main():
    parser = argparse.ArgumentParser(
        description="Scrape and parse weekly news posts from Public Libraries News."
    )
    parser.add_argument(
        "--mode",
        choices=["incremental", "backfill"],
        default="incremental",
        help="Scraping mode: 'incremental' (checks latest page) or 'backfill' (paginates through archives)."
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=None,
        help="Maximum pages to process in backfill mode."
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=None,
        help="Number of posts per page request."
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Seconds to wait between paginated requests (default: 1.5)."
    )

    args = parser.parse_args()

    scraper = PLNScraper(rate_limit_delay=args.delay)

    if args.mode == "incremental":
        per_page = args.per_page or 10
        count = scraper.run_incremental(per_page=per_page)
        print(f"Incremental run completed. Updated {count} post(s).")
    elif args.mode == "backfill":
        per_page = args.per_page or 50
        count = scraper.run_backfill(max_pages=args.pages, per_page=per_page)
        print(f"Backfill run completed. Processed {count} post(s).")

if __name__ == "__main__":
    main()
