#!/usr/bin/env python3
"""
Download Organic Maps (.mwm) files from omaps.webfreak.org
Usage: python download_maps.py [--output-dir ./maps] [--workers 3] [--filter France]
"""

import re
import sys
import time
import argparse
import threading
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urljoin, unquote
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

INDEX_URL = "https://omaps.webfreak.org/maps/260310/"


# ── helpers ───────────────────────────────────────────────────────────────────

def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": "OrganicMaps-Downloader/1.0"})
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_mwm_links(html: str, base_url: str) -> list:
    """
    Extract all .mwm hrefs from the page, handling both relative and absolute URLs.
    Returns list of (filename, full_url).
    """
    # Match href="..." where the value ends in .mwm (relative or absolute)
    pattern = r'href="([^"]+\.mwm)"'
    results = []
    for href in re.findall(pattern, html):
        full_url = urljoin(base_url, href)   # resolves relative paths correctly
        filename = unquote(full_url.split("/")[-1])
        results.append((filename, full_url))
    return results


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ── download one file ─────────────────────────────────────────────────────────

_print_lock = threading.Lock()

def log(msg: str):
    with _print_lock:
        print(msg, flush=True)


def download_file(filename: str, url: str, dest_dir: Path, retries: int = 3) -> bool:
    dest = dest_dir / filename

    if dest.exists() and dest.stat().st_size > 0:
        log(f"  ✓ skipped  {filename}  (already exists)")
        return True

    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers={"User-Agent": "OrganicMaps-Downloader/1.0"})
            with urlopen(req, timeout=60) as resp:
                downloaded = 0
                chunk_size = 1 << 16  # 64 KiB
                tmp = dest.with_suffix(".part")
                with open(tmp, "wb") as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                tmp.rename(dest)
                log(f"  ✓ done     {filename}  ({human_size(downloaded)})")
                return True

        except (URLError, HTTPError, OSError) as e:
            log(f"  ✗ attempt {attempt}/{retries} failed for {filename}: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)

    log(f"  ✗ FAILED   {filename}  (gave up after {retries} attempts)")
    return False


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Download Organic Maps .mwm files from omaps.webfreak.org"
    )
    parser.add_argument("--output-dir", default="./maps",
                        help="Directory to save .mwm files (default: ./maps)")
    parser.add_argument("--workers", type=int, default=3,
                        help="Parallel download threads (default: 3)")
    parser.add_argument("--filter", default="",
                        help="Only download files whose name contains this string "
                             "(case-insensitive), e.g. --filter France")
    args = parser.parse_args()

    dest_dir = Path(args.output_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching index from {INDEX_URL} …")
    html = fetch_text(INDEX_URL)
    links = parse_mwm_links(html, INDEX_URL)

    if not links:
        print("ERROR: No .mwm links found. The page layout may have changed.")
        sys.exit(1)

    if args.filter:
        links = [(f, u) for f, u in links if args.filter.lower() in f.lower()]
        if not links:
            print(f"No files match filter '{args.filter}'.")
            sys.exit(0)

    total = len(links)
    print(f"Found {total} map file(s) to download → {dest_dir.resolve()}\n")

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(download_file, fname, url, dest_dir): fname
            for fname, url in links
        }
        for future in as_completed(futures):
            if future.result():
                ok += 1
            else:
                fail += 1

    print(f"\n{'='*50}")
    print(f"  Completed: {ok}/{total}   Failed: {fail}/{total}")
    print(f"  Files saved to: {dest_dir.resolve()}")


if __name__ == "__main__":
    main()
