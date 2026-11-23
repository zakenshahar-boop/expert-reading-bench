"""PDF to a list of page texts, in reading order, with running heads and feet removed."""

from __future__ import annotations

import re
import subprocess
from collections import Counter
from pathlib import Path


def _key(line: str) -> str:
    return re.sub(r"\d+", "#", line.strip())


def strip_running_lines(pages: list[str], min_share: float = 0.5) -> list[str]:
    """Drop lines that recur, apart from their digits, on at least min_share of pages.

    Without this a quote that crosses a page break never matches, because the page
    footer sits between its two halves.
    """
    if len(pages) < 4:
        return pages
    counts = Counter(k for p in pages for k in {_key(l) for l in p.splitlines() if l.strip()})
    running = {k for k, c in counts.items() if c >= min_share * len(pages)}
    return ["\n".join(l for l in p.splitlines() if _key(l) not in running) for p in pages]


def pdf_pages(path: str | Path) -> list[str]:
    """Page texts from poppler's pdftotext. Index 0 is page 1."""
    out = subprocess.run(["pdftotext", str(path), "-"], check=True, capture_output=True).stdout
    pages = out.decode("utf-8", errors="replace").split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return strip_running_lines(pages)
