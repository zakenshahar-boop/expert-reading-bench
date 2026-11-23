"""Deterministic checks on a reading note, beyond quote fidelity and page accuracy.

Each one is a screen: it counts things a reader should look at. None of them decides
whether a claim is right.
"""

from __future__ import annotations

import re
from collections import Counter

from .paperxml import references, sections
from .quotes import doc_length, find_ranges, normalize_text
from .task import NOT_STATED, SLOTS

# ---------- walking a note ----------


def entries(note: dict | None):
    """Yield (slot, claim, [quote texts]) for every entry of a parsed note."""
    if not note:
        return
    for slot in SLOTS:
        value = note["slots"].get(slot)
        if isinstance(value, str) and value.strip().lower() == NOT_STATED:
            continue
        if isinstance(value, dict):
            value = [value]
        if not isinstance(value, list):
            continue
        for e in value:
            if isinstance(e, str):
                yield slot, e, []
            elif isinstance(e, dict):
                quotes = e.get("quotes") or []
                texts = [q.get("text", "") if isinstance(q, dict) else q for q in quotes]
                yield slot, str(e.get("claim", "")), [t for t in texts if isinstance(t, str) and t]


# ---------- 1. numbers ----------

_NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?|\.\d+)\s*(million|billion|thousand)?", re.I)
_SCALE = {"thousand": 1e3, "million": 1e6, "billion": 1e9}


def numbers(text: str) -> list[tuple[float, float]]:
    """(value, half the unit of its last written digit) for each number in the text.
    "9.25 million" gives (9250000, 5000), so a rounded figure can match an exact one."""
    out = []
    for m in _NUM.finditer(text.replace("−", "-")):
        raw = m.group(1).replace(",", "")
        scale = _SCALE.get((m.group(2) or "").lower(), 1.0)
        decimals = len(raw.split(".")[1]) if "." in raw else 0
        out.append((float(raw) * scale, 0.5 * 10 ** -decimals * scale))
    return out


def _has(value: float, tolerance: float, pool: list[tuple[float, float]]) -> bool:
    exact = tolerance <= 0.5 and float(value).is_integer()
    return any(abs(v - value) <= (1e-9 if exact else tolerance + 1e-9) for v, _ in pool)


def number_check(note: dict | None, pages: list[str]) -> dict:
    """Where each number in a claim can be found: in the entry's own quotes, elsewhere
    in the paper, or nowhere."""
    paper = numbers("\n".join(pages))
    out = {"numbers": 0, "in own quotes": 0, "elsewhere in paper": 0, "nowhere": 0, "items": []}
    for slot, claim, quotes in entries(note):
        own = numbers("\n".join(quotes))
        for value, tol in numbers(claim):
            where = ("in own quotes" if _has(value, tol, own)
                     else "elsewhere in paper" if _has(value, tol, paper) else "nowhere")
            out["numbers"] += 1
            out[where] += 1
            if where != "in own quotes":
                out["items"].append({"slot": slot, "number": value, "where": where, "claim": claim})
    return out


# ---------- 2. strength of claim ----------

CAUSAL = re.compile(
    r"\b(caus\w+|effects? (?:of|on)|impacts?|affects?|driv(?:e|es|en|ing)|leads? to|led to|"
    r"results? in|resulted in|fuel(?:s|ed|ing)?|influenc\w+|due to|because of|determin(?:e|es|ed)|"
    r"produc(?:e|es|ed) (?:more|less|higher|lower))\b", re.I)
HEDGE = re.compile(
    r"\b(may|might|could|suggest\w*|partial\w*|partly|explorator\w+|tentative\w*|potential\w*|"
    r"appear\w*|seem\w*|likely|possibl\w+|not uniform\w*|inconsistent|to a lesser extent)\b", re.I)
_NEGATION = re.compile(r"\b(not|no|never|without|cannot|rather than|n't)\b[^.;]{0,40}$", re.I)


def _asserted_causal(text: str):
    """The first causal word that is not negated just before it ("does not cause")."""
    for m in CAUSAL.finditer(text):
        if not _NEGATION.search(text[:m.start()]):
            return m
    return None


def strength_check(note: dict | None) -> dict:
    """Entries whose claim uses a causal word when none of its quotes does, and entries
    whose quotes hedge when the claim does not."""
    out = {"entries with quotes": 0, "causal word not in quote": 0, "hedge dropped": 0, "items": []}
    for slot, claim, quotes in entries(note):
        if not quotes:
            continue
        out["entries with quotes"] += 1
        joined = " ".join(quotes)
        causal = _asserted_causal(claim)
        if causal and not CAUSAL.search(joined):
            out["causal word not in quote"] += 1
            out["items"].append({"slot": slot, "kind": "causal", "word": causal.group(0), "claim": claim})
        hedge = HEDGE.search(joined)
        if hedge and not HEDGE.search(claim):
            out["hedge dropped"] += 1
            out["items"].append({"slot": slot, "kind": "hedge", "word": hedge.group(0), "claim": claim})
    return out


# ---------- 3. attribution ----------

_RANGE = re.compile(r"(\d+)\s*[–—-]\s*(\d+)")
_CITE = re.compile(r"\[([\d,\s]+)(?:,\s*p\.[^\]]*)?\]")


def _expand(text: str) -> str:
    """Rewrite [13–15] as [13,14,15] so reference numbers survive normalization."""
    def inside(m):
        def rng(r):
            a, b = int(r.group(1)), int(r.group(2))
            return ",".join(map(str, range(a, b + 1))) if 0 < b - a < 50 else r.group(0)
        return "[" + _RANGE.sub(rng, m.group(1)) + "]"
    return re.sub(r"\[([^\]\[]{1,80})\]", inside, text)


def attribution_check(note: dict | None, pages: list[str], xml: str) -> dict:
    """For interlocutor entries that name authors from the reference list: are those
    authors cited in the sentences the quotes come from?"""
    refs = references(xml)
    surnames = {n for names in refs.values() for n in names if len(n) >= 3}
    expanded = [_expand(p) for p in pages]
    doc = " ".join(normalize_text(p) for p in expanded)
    out = {"entries": 0, "name authors": 0, "all named authors cited at the quote": 0,
           "some": 0, "none": 0, "items": []}
    for slot, claim, quotes in entries(note):
        if slot != "interlocutor_claim":
            continue
        out["entries"] += 1
        named = {n for n in surnames if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", claim)}
        named = {n for n in named if not any(n != m and n in m for m in named)}  # "Rasmussen" inside a longer name
        if not named:
            continue
        out["name authors"] += 1
        cited = set()
        for q in quotes:
            nq = normalize_text(_expand(q))
            pos = doc.find(nq) if len(nq) >= 3 else -1
            if pos == -1:
                continue
            start = max(doc.rfind(". ", 0, pos), 0)
            end = doc.find(". ", pos + len(nq))
            end = len(doc) if end == -1 else end
            # a citation often follows the full stop of the sentence it belongs to
            window = doc[start:end + 40]
            for m in _CITE.finditer(window):
                for n in re.findall(r"\d+", m.group(1)):
                    cited |= refs.get(int(n), set())
        hit = named & cited
        key = "all named authors cited at the quote" if hit == named else "some" if hit else "none"
        out[key] += 1
        if hit != named:
            out["items"].append({"named": sorted(named), "not cited at the quote": sorted(named - cited), "claim": claim})
    return out


# ---------- 4. overlap with gold quotes ----------


def gold_overlap(note: dict | None, pages: list[str], gold: dict, min_chars: int = 20) -> dict:
    """Which gold answers have a gold quote that one of the model's quotes overlaps.
    A lower bound on coverage: the same answer can be supported from another passage."""
    mine = {s: [] for s in SLOTS}
    for slot, _, quotes in entries(note):
        for q in quotes:
            mine[slot] += find_ranges(pages, q)
    everything = [r for ranges in mine.values() for r in ranges]

    def touches(ranges, span):
        return any(min(b, d) - max(a, c) >= min_chars for a, b in ranges for c, d in find_ranges(pages, span))

    out = {"gold answers": 0, "overlapped, same slot": 0, "overlapped, any slot": 0,
           "core findings": 0, "core findings overlapped": 0, "missed": []}
    for slot, body in gold["slots"].items():
        for a in body["acceptable"]:
            same = any(touches(mine[slot], s["text"]) for s in a["spans"])
            anywhere = same or any(touches(everything, s["text"]) for s in a["spans"])
            core = slot == "key_findings" and a.get("tier") == "core"
            out["gold answers"] += 1
            out["overlapped, same slot"] += same
            out["overlapped, any slot"] += anywhere
            out["core findings"] += core
            out["core findings overlapped"] += core and anywhere
            if not anywhere:
                out["missed"].append(a["id"])
    return out


# ---------- 5 and 6. where the quotes come from ----------


def _body_end(pages: list[str]) -> int:
    """Length of the normalized document up to the reference list."""
    for i, p in enumerate(pages):
        if re.search(r"^\s*References\s*$", p, re.M):
            head = p[:re.search(r"^\s*References\s*$", p, re.M).start()]
            return doc_length(pages[:i]) + len(normalize_text(head))
    return doc_length(pages)


def location_check(note: dict | None, pages: list[str], xml: str) -> dict:
    """The section each faithful quote sits in, and which third of the body."""
    secs = sections(xml)
    end = max(_body_end(pages), 1)
    by_section, thirds, found = Counter(), Counter(), 0
    for _, _, quotes in entries(note):
        for q in quotes:
            ranges = find_ranges(pages, q)
            if not ranges:
                continue
            found += 1
            nq = normalize_text(q)
            by_section[next((name for name, _, text in secs if nq in text), "unknown")] += 1
            thirds[("first third", "middle third", "last third")[min(int(3 * ranges[0][0] / end), 2)]] += 1
    out = {"faithful quotes": found}
    for name in ("abstract", "introduction", "background", "methods", "results", "discussion", "other", "unknown"):
        out[name] = by_section.get(name, 0)
    for name in ("first third", "middle third", "last third"):
        out[name] = thirds.get(name, 0)
    return out
