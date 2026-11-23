"""The two deterministic scores: quote fidelity and locator accuracy."""

from __future__ import annotations

from .quotes import locate_quote
from .task import MAX_QUOTE_WORDS, MIN_QUOTE_WORDS, NOT_STATED, SLOTS


def score_note(note: dict | None, pages: list[str]) -> dict:
    """Counts for one paper. A quote is faithful when all of it occurs in the paper and
    its length is within the limits. It is located when one occurrence includes the
    stated page."""
    out = {"parsed": note is not None, "slots_filled": 0, "slots_not_stated": 0,
           "slots_missing": 0, "entries": 0, "entries_without_quote": 0, "quotes": 0,
           "faithful": 0, "located": 0, "bad_length": 0, "per_quote": []}
    if note is None:
        out["slots_missing"] = len(SLOTS)
        return out
    for slot in SLOTS:
        value = note["slots"].get(slot)
        if isinstance(value, str) and value.strip().lower() == NOT_STATED:
            out["slots_not_stated"] += 1
            continue
        if isinstance(value, dict):
            value = [value]
        if not isinstance(value, list) or not value:
            out["slots_missing"] += 1
            continue
        out["slots_filled"] += 1
        for entry in value:
            out["entries"] += 1
            quotes = entry.get("quotes") if isinstance(entry, dict) else None
            if not isinstance(quotes, list) or not quotes:
                out["entries_without_quote"] += 1
                continue
            for q in quotes:
                text = q.get("text", "") if isinstance(q, dict) else q  # a bare string has no page
                page = q.get("page") if isinstance(q, dict) else None
                text = text if isinstance(text, str) else ""
                words = len(text.split())
                length_ok = MIN_QUOTE_WORDS <= words <= MAX_QUOTE_WORDS
                found = locate_quote(pages, text)
                faithful = bool(found) and length_ok
                located = faithful and isinstance(page, int) and any(page in o for o in found)
                out["quotes"] += 1
                out["bad_length"] += not length_ok
                out["faithful"] += faithful
                out["located"] += located
                out["per_quote"].append({"slot": slot, "page": page, "words": words,
                                         "found_on": found, "faithful": faithful,
                                         "located": located, "text": text})
    return out
