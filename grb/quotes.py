"""Whole-span quote matching against the pages of a document.

Ported from PDF IDE (src/shared/grounding.ts). The rule is the same: the complete
quotation must occur in the source. A matching opening never authenticates the rest.
Two things differ. The unit is the page instead of the text block, and normalization
also undoes what PDF typesetting does to text (ligatures, soft hyphens, words broken
across lines, typographic quotes and dashes).
"""

from __future__ import annotations

import re
import unicodedata

MIN_QUOTE_CHARS = 3

_INVISIBLE = dict.fromkeys(map(ord, "­​‌‍⁠﻿"))
_QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "‛": "'",
                         "“": '"', "”": '"', "„": '"', "‟": '"'})
_DASHES = re.compile(r"\s*[-‐‑‒–—―−]\s*")


def normalize_text(s: str) -> str:
    """Lowercase, collapse whitespace, and remove typesetting artifacts.

    Hyphens and dashes are dropped together with the whitespace around them, so
    "associ-\\nated", "associated", "self-attention" and "self-\\nattention" compare as
    intended, and a model that types a hyphen for an en dash is not penalized.
    """
    s = unicodedata.normalize("NFKC", s).translate(_INVISIBLE).translate(_QUOTES)
    s = _DASHES.sub("", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def _index(pages: list[str]) -> tuple[str, list[tuple[int, int, int]]]:
    doc, spans = "", []
    for number, text in enumerate(pages, start=1):
        n = normalize_text(text)
        if not n:
            continue
        start = len(doc)
        doc += n + " "
        spans.append((start, start + len(n), number))
    return doc, spans


def locate_quote(pages: list[str], quote: str) -> list[list[int]]:
    """Every place the whole quote occurs, each as the 1-based pages it covers.

    Returns [] when the quote is absent or too short. A quote that runs over a page
    break yields two pages for that occurrence.
    """
    q = normalize_text(quote)
    if len(q) < MIN_QUOTE_CHARS:
        return []
    doc, spans = _index(pages)
    found, pos = [], doc.find(q)
    while pos != -1:
        end = pos + len(q)
        found.append([n for start, stop, n in spans if start < end and stop > pos])
        pos = doc.find(q, pos + 1)
    return found


def find_ranges(pages: list[str], quote: str) -> list[tuple[int, int]]:
    """Character ranges of every whole occurrence of the quote in the normalized document,
    for comparing where two quotes sit. The second value of the result of
    doc_length(pages) is the scale these positions are on."""
    q = normalize_text(quote)
    if len(q) < MIN_QUOTE_CHARS:
        return []
    doc, _ = _index(pages)
    out, pos = [], doc.find(q)
    while pos != -1:
        out.append((pos, pos + len(q)))
        pos = doc.find(q, pos + 1)
    return out


def doc_length(pages: list[str]) -> int:
    return len(_index(pages)[0])


def verify_quote(pages: list[str], quote: str, page: object) -> bool:
    """True when the whole quote occurs at a place that includes the stated page."""
    if isinstance(page, bool) or not isinstance(page, int) or not 1 <= page <= len(pages):
        return False
    return any(page in occurrence for occurrence in locate_quote(pages, quote))


def token_score(query: str, text: str) -> int:
    """How many of the query's words (longer than two characters) appear in the text."""
    tokens = [t for t in re.split(r"[^a-z0-9]+", query.lower()) if len(t) > 2]
    haystack = text.lower()
    return sum(1 for t in tokens if t in haystack)
