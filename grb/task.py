"""The task: prompt text, output parsing, and the slot list."""

from __future__ import annotations

import json
import re

SLOTS = {
    "question": "What the paper asks or argues against.",
    "central_claim": "The main argument or finding.",
    "evidence": "The data, cases or method, and what they consist of.",
    "key_findings": "Three to five findings, each a separate entry with its own quote.",
    "scope_and_limits": "What the authors say the paper does not show.",
    "theoretical_positioning": (
        "The tradition or framework the authors place the paper in, and their stance "
        "toward it: extends, combines, revises or rejects. The quote must show the "
        "authors placing themselves, not only naming a theorist."),
    "interlocutor_claim": (
        "One specific claim the paper attributes to someone else and then disputes or "
        "builds on. Say whose claim it is."),
}
ABSTRACT_LEVEL = ("question", "central_claim", "evidence")
MIN_QUOTE_WORDS, MAX_QUOTE_WORDS = 5, 60
NOT_STATED = "not stated"
PROMPT_VERSION = 3

PROMPT = """You will read a scholarly paper and fill in a structured reading note.

The note has seven slots:
{slots}

Rules:
- Each entry has a "claim", written in your own words, and "quotes": one or more passages
  copied from the paper exactly, character for character, each with the number of the
  page it is on. Pages are marked in the text as [page N].
- A quote is {lo} to {hi} words long. Do not join separate passages with "..." and do not
  correct or shorten the wording.
- Give every answer the paper supports, one entry per distinct point. There is no limit on
  entries, except key_findings, which takes the three to five most important. Never
  repeat an entry, and never add a point the paper does not make.
- Every quote is an object with "text" and "page", as in the shape below. A claim with no
  quote counts as an error.
- If the paper does not address a slot, give the string "{ns}" for that slot. Do not guess.
- Use only the paper below. Do not use anything you remember about it.

Reply with one JSON object and nothing else, in this shape:
{{"slots": {{"question": [{{"claim": "...", "quotes": [{{"text": "...", "page": 1}}]}}],
"central_claim": [...], "evidence": [...], "key_findings": [...],
"scope_and_limits": [...], "theoretical_positioning": [...], "interlocutor_claim": [...]}}}}

The paper:

{paper}
"""


def build_prompt(pages: list[str]) -> str:
    slots = "\n".join(f"- {name}: {desc}" for name, desc in SLOTS.items())
    paper = "\n\n".join(f"[page {i}]\n{p.strip()}" for i, p in enumerate(pages, start=1))
    return PROMPT.format(slots=slots, lo=MIN_QUOTE_WORDS, hi=MAX_QUOTE_WORDS,
                         ns=NOT_STATED, paper=paper)


def _salvage(text: str) -> dict | None:
    """Close a reply that was cut off, keeping everything up to its last complete value."""
    stack, cuts, in_string, escape = [], [], False, False
    for i, ch in enumerate(text):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]" and stack:
            stack.pop()
            cuts.append((i, "".join(reversed(stack))))
    for i, closers in reversed(cuts[-400:]):
        try:
            obj = json.loads(text[:i + 1] + closers)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("slots"), dict):
            return obj
    return None


def _by_slot(text: str) -> dict | None:
    """Read each slot on its own, for a reply whose brackets do not balance (a stray or
    missing brace between slots). Each slot's value is read from its key to the next key."""
    marks = sorted((m.start(), m.end(), m.group(1)) for name in SLOTS
                   for m in [re.search(r'"(%s)"\s*:' % name, text)] if m)
    slots = {}
    for k, (_, after, name) in enumerate(marks):
        piece = text[after:marks[k + 1][0] if k + 1 < len(marks) else len(text)].lstrip()
        try:
            slots[name], _ = json.JSONDecoder().raw_decode(piece)
        except json.JSONDecodeError:
            got = _salvage('{"slots": {"x": ' + piece)
            if got and got["slots"].get("x"):
                slots[name] = got["slots"]["x"]
    return {"slots": slots} if slots else None


def parse_output(raw: str) -> tuple[dict | None, str]:
    """The note and how it was read: "complete", "partial" (the reply did not finish and
    was closed after its last complete value), "repaired" (the brackets did not balance, so
    each slot was read on its own) or "unreadable"."""
    text = re.sub(r"<think>.*?</think>", "", raw, flags=re.S)
    if "</think>" in text:  # reasoning whose opening tag was part of the prompt
        text = text.split("</think>")[-1]
    start, end = text.find("{"), text.rfind("}")
    if start == -1:
        return None, "unreadable"
    try:
        obj = json.loads(text[start:end + 1])
        if isinstance(obj, dict) and isinstance(obj.get("slots"), dict):
            return obj, "complete"
    except json.JSONDecodeError:
        pass
    obj = _salvage(text[start:])
    loose = _by_slot(text[start:])
    if loose and len(loose["slots"]) > len(obj["slots"] if obj else {}):
        return loose, "repaired"
    return (obj, "partial") if obj else (None, "unreadable")
