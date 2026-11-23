"""A harness around a small model, after the rule PDF IDE applies to its own agent:
nothing is accepted unless its quote is found whole in the source, a rejected quote goes
back to the model with the reason and the source text, and what cannot be repaired is
dropped.

Three steps, each usable on its own so their effects can be measured separately:

1. `extract_by_slot`: ask for one slot of the note at a time.
2. `confirm_quotes`: check every quote against the paper; ask for a repair; drop failures.
3. `recheck_claims`: show the model one claim beside the page its quote is on and ask
   fixed questions about it; rewrite or drop the claim on a bad answer.

The harness never sees gold answers. `ask(prompt, with_paper)` is any function that sends
text to the model and returns its reply.
"""

from __future__ import annotations

import json
import re

from .quotes import locate_quote, normalize_text
from .task import MAX_QUOTE_WORDS, MIN_QUOTE_WORDS, NOT_STATED, SLOTS, _salvage

RULES = f"""Rules:
- Each entry has a "claim", written in your own words, and "quotes": one or more passages
  copied from the paper exactly, character for character, each with the number of the
  page it is on. Pages are marked in the text as [page N].
- A quote is {MIN_QUOTE_WORDS} to {MAX_QUOTE_WORDS} words long. Do not join separate passages with "..." and do not
  correct or shorten the wording.
- Give every answer the paper supports, one entry per distinct point. Never repeat an
  entry, and never add a point the paper does not make.
- A claim with no quote counts as an error.
- Use only the paper above. Do not use anything you remember about it."""


def paper_block(pages: list[str]) -> str:
    """The paper as the start of every prompt that needs it, so a model can read it once."""
    body = "\n\n".join(f"[page {i}]\n{p.strip()}" for i, p in enumerate(pages, start=1))
    return "You will read a scholarly paper and then do one task about it.\n\nThe paper:\n\n" + body + "\n\n---\n"


RULES_2 = f"""Rules:
- Each entry has a "claim", written in your own words, and "quotes": one or more passages
  copied from the paper exactly, character for character, each with the number of the
  page it is on. Pages are marked in the text as [page N].
- A quote is {MIN_QUOTE_WORDS} to {MAX_QUOTE_WORDS} words long. Do not join separate passages with "..." and do not
  correct or shorten the wording.
- One entry per distinct point. Give only what the paper clearly says: a short list of
  well-supported entries is better than a long one. Never repeat an entry.
- Keep the paper's own strength of wording. If it reports an association, do not write
  that one thing causes, drives, influences or leads to another.
- Do not invent a position for the paper to argue against. Name another view only if the
  paper itself describes it and says who holds it.
- Use only the paper above. Do not use anything you remember about it."""


def slot_prompt(slot: str, version: int = 1) -> str:
    extra = " Give the three to five most important." if slot == "key_findings" else ""
    if version == 2:
        return (f"Task: fill one slot of a structured reading note about the paper above.\n\n"
                f"Slot \"{slot}\": {SLOTS[slot]}{extra}\n\n{RULES_2}\n\n"
                f"Reply with one JSON list and nothing else. Every quote is an object with \"text\" and \"page\":\n"
                f'[{{"claim": "...", "quotes": [{{"text": "...", "page": 1}}]}}]\n'
                f'If the paper does not address this slot, reply with the string "{NOT_STATED}".')
    return (f"Task: fill one slot of a structured reading note about the paper above.\n\n"
            f"Slot \"{slot}\": {SLOTS[slot]}{extra}\n\n{RULES}\n\n"
            f"Go through the whole paper and list each distinct answer as its own entry.\n\n"
            f"Reply with one JSON list and nothing else, in this shape:\n"
            f'[{{"claim": "...", "quotes": [{{"text": "...", "page": 1}}]}}, {{"claim": "...", "quotes": [{{"text": "...", "page": 2}}]}}]\n'
            f'If the paper does not address this slot, reply with the string "{NOT_STATED}".')


def answer_part(raw: str) -> str:
    """A reply without the reasoning some models write first, between <think> tags."""
    text = re.sub(r"<think>.*?</think>", "", raw, flags=re.S)
    return text.split("</think>")[-1] if "</think>" in text else text


def _read_json(raw: str, opener: str):
    """The first JSON value starting with `opener` in a reply, repaired if it was cut off."""
    text = answer_part(raw)
    start = text.find(opener)
    if start == -1:
        return None
    try:
        value, _ = json.JSONDecoder().raw_decode(text[start:])
        return value
    except json.JSONDecodeError:
        got = _salvage('{"slots": {"x": ' + text[start:])
        return got["slots"].get("x") if got else None


def _entries(value) -> list[dict]:
    out = []
    for e in value if isinstance(value, list) else []:
        if isinstance(e, dict) and isinstance(e.get("claim"), str) and e["claim"].strip():
            quotes = e.get("quotes") if isinstance(e.get("quotes"), list) else []
            out.append({"claim": e["claim"].strip(), "quotes": quotes})
    return out


_STRING = re.compile(r'"((?:[^"\\\\]|\\\\.)*)"')


def _loose_entries(raw: str) -> list[dict]:
    """Entries from a reply that is not valid JSON, typically because a quote was written
    as `["words", "page": 3]`. Each claim is taken with the strings and page numbers that
    follow it, up to the next claim."""
    out = []
    for part in re.split(r'"claim"\s*:', answer_part(raw))[1:]:
        first = _STRING.search(part)
        if not first:
            continue
        claim = json.loads(first.group(0))
        quotes = []
        for m in _STRING.finditer(part, first.end()):
            text = json.loads(m.group(0))
            if text in ("quotes", "text", "page") or part[m.end():m.end() + 3].lstrip().startswith(":"):
                continue
            page = re.match(r'\s*[,}]?\s*"page"\s*:\s*(\d+)', part[m.end():])
            quotes.append({"text": text, "page": int(page.group(1)) if page else None})
        if claim.strip():
            out.append({"claim": claim.strip(), "quotes": quotes})
    return out


def read_entries(raw: str) -> tuple[list[dict], str]:
    entries = _entries(_read_json(raw, "["))
    if entries:
        return entries, "read"
    entries = _loose_entries(raw)
    return entries, "read loosely" if entries else "nothing readable"


def extract_by_slot(ask, pages: list[str], trace: list, replies: dict | None = None, version: int = 1) -> dict:
    """Ask for each slot in turn. `replies` (slot -> an earlier reply) skips the asking."""
    note = {}
    for slot in SLOTS:
        raw = replies[slot] if replies else ask(slot_prompt(slot, version), True)
        entries, how = read_entries(raw)
        trace.append({"step": "extract", "slot": slot, "entries": len(entries), "how": how, "raw": raw})
        note[slot] = entries if entries else NOT_STATED
    return {"slots": note}


def _where(pages: list[str], text: str) -> list[int] | None:
    """The pages a quote is found on, or None when it is not in the paper or the wrong length."""
    if not isinstance(text, str) or not MIN_QUOTE_WORDS <= len(text.split()) <= MAX_QUOTE_WORDS:
        return None
    found = locate_quote(pages, text)
    return found[0] if found else None


def _closest_pages(pages: list[str], text: str, stated, n: int = 2) -> list[int]:
    words = {w for w in normalize_text(text).split() if len(w) > 3}
    scored = sorted(((sum(1 for w in words if w in normalize_text(p)), -i) for i, p in enumerate(pages, start=1)), reverse=True)
    picks = [-i for _, i in scored[:n]]
    if isinstance(stated, int) and 1 <= stated <= len(pages) and stated not in picks:
        picks = [stated] + picks[:n - 1]
    return sorted(picks)


def repair_prompt(pages: list[str], claim: str, quote: str | None, page_numbers: list[int]) -> str:
    problem = (f'This quote was given for it, but it is not in the paper word for word, or it is not '
               f'{MIN_QUOTE_WORDS} to {MAX_QUOTE_WORDS} words long:\n"{quote}"' if quote else "No quote was given for it.")
    text = "\n\n".join(f"[page {n}]\n{pages[n - 1].strip()}" for n in page_numbers)
    return (f"A reading note about a paper contains this claim:\n\"{claim}\"\n\n{problem}\n\n"
            f"Here is the text of the most likely pages:\n\n{text}\n\n---\n"
            f"Copy one passage of {MIN_QUOTE_WORDS} to {MAX_QUOTE_WORDS} consecutive words from the text above, exactly as written, "
            f"that supports the claim. Reply with JSON only: {{\"text\": \"...\", \"page\": 1}}\n"
            f"If no passage above supports the claim, reply {{\"text\": null}}.")


def confirm_quotes(ask, pages: list[str], note: dict, trace: list, tries: int = 2) -> dict:
    """Keep quotes found in the paper (with the page they are really on), ask for a repair
    of the others, and drop a claim left with no confirmed quote."""
    out = {}
    for slot, entries in note["slots"].items():
        if slot not in SLOTS:
            continue
        if not isinstance(entries, list):
            out[slot] = entries
            continue
        kept, seen = [], set()
        for e in entries:
            claim = e.get("claim") if isinstance(e, dict) else (e if isinstance(e, str) else None)
            if not isinstance(claim, str) or not claim.strip() or normalize_text(claim) in seen:
                continue
            seen.add(normalize_text(claim))
            raw_quotes = e.get("quotes") if isinstance(e, dict) and isinstance(e.get("quotes"), list) else []
            good, bad = [], []
            for q in raw_quotes:
                text = q.get("text") if isinstance(q, dict) else q
                stated = q.get("page") if isinstance(q, dict) else None
                on = _where(pages, text)
                if on:
                    page = stated if stated in on else on[0]
                    good.append({"text": text, "page": page})
                    trace.append({"step": "confirm", "slot": slot, "result": "found" if stated in on else "page corrected"})
                else:
                    bad.append((text if isinstance(text, str) else None, stated))
            if not good:
                for text, stated in (bad[:1] or [(None, None)]):
                    for attempt in range(tries):
                        near = _closest_pages(pages, (text or "") + " " + claim, stated)
                        raw = ask(repair_prompt(pages, claim, text, near), False)
                        reply = _read_json(raw, "{")
                        new = reply.get("text") if isinstance(reply, dict) else None
                        on = _where(pages, new)
                        trace.append({"step": "repair", "slot": slot, "attempt": attempt + 1, "result": "repaired" if on else "failed", "raw": raw})
                        if on:
                            good.append({"text": new, "page": on[0]})
                            break
                        if new is None:
                            break
                        text = new
            if good:
                kept.append({"claim": claim.strip(), "quotes": good})
            else:
                trace.append({"step": "drop", "slot": slot, "why": "no confirmed quote", "claim": claim})
        out[slot] = kept if kept else NOT_STATED
    return {"slots": out}


def recheck_prompt(pages: list[str], claim: str, page_numbers: list[int]) -> str:
    text = "\n\n".join(f"[page {n}]\n{pages[n - 1].strip()}" for n in page_numbers)
    return (f"Check one claim from a reading note against the page of the paper it cites.\n\n{text}\n\n---\n"
            f"Claim: \"{claim}\"\n\n"
            f"Answer using only the text above.\n"
            f"1. \"supported\": does the text say what the claim says? \"yes\", \"partly\" or \"no\".\n"
            f"2. \"direction\": if the claim says something is higher, lower, more, less, rose or fell, is that the same "
            f"direction as in the text? \"yes\", \"no\", or \"none\" if the claim has no direction.\n"
            f"3. \"attribution\": if the claim says who said or found something, does the text name that same source for it? "
            f"\"yes\", \"no\", or \"none\" if the claim names no source.\n"
            f"4. \"claim\": the claim, rewritten if needed so that it says only what the text supports. Repeat it unchanged if it is already right.\n\n"
            f"Reply with JSON only: {{\"supported\": \"...\", \"direction\": \"...\", \"attribution\": \"...\", \"claim\": \"...\"}}")


def recheck_claims(ask, pages: list[str], note: dict, trace: list) -> dict:
    """Ask the model fixed questions about each claim beside its cited page. "no" on support
    drops the claim; any other bad answer replaces it with the model's rewritten version."""
    out = {}
    for slot, entries in note["slots"].items():
        if not isinstance(entries, list):
            out[slot] = entries
            continue
        kept = []
        for e in entries:
            near = sorted({q["page"] for q in e["quotes"]})[:2]
            raw = ask(recheck_prompt(pages, e["claim"], near), False)
            reply = _read_json(raw, "{")
            reply = reply if isinstance(reply, dict) else {}
            answers = {k: str(reply.get(k, "")).strip().lower() for k in ("supported", "direction", "attribution")}
            new = reply.get("claim") if isinstance(reply.get("claim"), str) else ""
            if answers["supported"] == "no":
                verdict = "dropped"
            elif (answers["supported"] == "partly" or "no" in (answers["direction"], answers["attribution"])) and new.strip() \
                    and normalize_text(new) != normalize_text(e["claim"]):
                verdict = "rewritten"
                kept.append({"claim": new.strip(), "quotes": e["quotes"]})
            else:
                verdict = "kept"
                kept.append(e)
            trace.append({"step": "recheck", "slot": slot, "verdict": verdict, **answers, "claim": e["claim"],
                          "new_claim": new if verdict == "rewritten" else None})
        out[slot] = kept if kept else NOT_STATED
    return {"slots": out}


# ---------- re-check, second version: one narrow question per call ----------

_DIRECTION = re.compile(r"\b(increas\w*|decreas\w*|higher|lower|fewer|greater|reduc\w*|rais\w*|rose|fell|worsen\w*|improv\w*|"
                        r"stronger|weaker|more likely|less likely|more hesitant|less hesitant)\b", re.I)
_OTHER_VIEW = re.compile(r"\b(prior (research|work|studies)|previous (research|work|studies)|earlier (research|work|studies)|"
                         r"disputes?|challenges?|refutes?|argues? against|rejects?|the (claim|idea|notion|assumption|view) that)\b", re.I)


def passage(pages: list[str], quote: dict, around: int = 700) -> str:
    """The text around a confirmed quote on its page."""
    page = pages[quote["page"] - 1]
    words = quote["text"].split()[:6]
    m = re.search(r"\s+".join(re.escape(w) for w in words), page) if words else None
    if not m:
        return page.strip()
    return page[max(0, m.start() - around):m.end() + len(quote["text"]) + around].strip()


def _first_word(raw: str) -> str:
    m = re.search(r"[a-z]+", answer_part(raw).lower())
    return m.group(0) if m else ""


def _one_line(raw: str) -> str:
    text = answer_part(raw).strip().strip('"').strip()
    return text.splitlines()[0].strip().strip('"') if text else ""


def recheck_claims_2(ask, pages: list[str], note: dict, trace: list) -> dict:
    """One narrow question per call, each beside the passage around the claim's quote.
    Support is asked of every claim. Direction is asked only when the claim has a direction
    word, another view only when the claim speaks of one, and causal wording is rewritten
    only when the claim has a causal word and its quotes have none."""
    from .checks import CAUSAL, _asserted_causal
    out = {}
    for slot, entries in note["slots"].items():
        if not isinstance(entries, list):
            out[slot] = entries
            continue
        kept = []
        for e in entries:
            claim = e["claim"]
            text = "\n\n".join(f"[page {q['page']}] {passage(pages, q)}" for q in e["quotes"][:2])
            head = f"A passage from a paper:\n\n{text}\n\n---\nA claim about the paper: \"{claim}\"\n\n"
            log = {"step": "recheck2", "slot": slot, "claim": claim, "asked": []}
            verdict = "kept"
            raw = ask(head + "Does the passage say what the claim says? Answer with one word: yes or no.", False)
            log["asked"].append(["support", _first_word(raw)])
            if _first_word(raw) == "no":
                verdict = "dropped"
            if verdict == "kept" and (slot == "interlocutor_claim" or _OTHER_VIEW.search(claim)):
                raw = ask(head + "The claim says the paper responds to a view or finding of someone else. Does the passage itself describe "
                          "that view or finding as someone else's? Answer with one word: yes or no.", False)
                log["asked"].append(["other view", _first_word(raw)])
                if _first_word(raw) == "no":
                    verdict = "dropped"
            if verdict == "kept" and _DIRECTION.search(claim):
                raw = ask(head + "The claim says something is higher or lower, more or less, rose or fell. Is that the same direction as in "
                          "the passage? Answer with one word: same, opposite or unclear.", False)
                log["asked"].append(["direction", _first_word(raw)])
                if _first_word(raw) == "opposite":
                    new = _one_line(ask(head + "The direction in the claim is the opposite of the passage. Rewrite the claim so that it "
                                        "matches the passage. Reply with the rewritten claim only, in one sentence.", False))
                    if new and normalize_text(new) != normalize_text(claim):
                        claim, verdict = new, "rewritten"
            causal = _asserted_causal(claim)
            if verdict != "dropped" and causal and not CAUSAL.search(" ".join(q["text"] for q in e["quotes"])):
                new = _one_line(ask(head + f"The claim uses the causal wording \"{causal.group(0)}\", and the quoted passage does not. "
                                    "Rewrite the claim so that it describes the relationship in the passage's own terms, for example "
                                    "\"is associated with\". Change nothing else. Reply with the rewritten claim only, in one sentence.", False))
                log["asked"].append(["causal wording", causal.group(0)])
                if new and normalize_text(new) != normalize_text(claim):
                    claim, verdict = new, "rewritten"
            log["verdict"], log["new_claim"] = verdict, claim if verdict == "rewritten" else None
            trace.append(log)
            if verdict != "dropped":
                kept.append({"claim": claim, "quotes": e["quotes"]})
        out[slot] = kept if kept else NOT_STATED
    return {"slots": out}


# ---------- a setting for models that are accurate but stop early: ask for more ----------

MORE_SLOTS = ("question", "evidence", "scope_and_limits", "theoretical_positioning", "interlocutor_claim")


def more_prompt(slot: str, claims: list[str]) -> str:
    desc = "Findings the paper reports, each a separate entry with its own quote." if slot == "key_findings" else SLOTS[slot]
    have = "\n".join(f"- {c}" for c in claims) or "(nothing yet)"
    return (f"Task: add to one slot of a structured reading note about the paper above.\n\n"
            f"Slot \"{slot}\": {desc}\n\nThe note already has these entries for this slot:\n{have}\n\n"
            f"Papers usually support several answers for this slot. Read the paper again for answers that are not in the "
            f"list above, and give only those. Do not repeat or rephrase an entry that is already listed.\n\n{RULES_2}\n\n"
            f"Reply with one JSON list and nothing else. Every quote is an object with \"text\" and \"page\":\n"
            f'[{{"claim": "...", "quotes": [{{"text": "...", "page": 1}}]}}]\n'
            f"If the paper supports nothing more for this slot, reply with an empty list: []")


def body_pages(pages: list[str]) -> list[int]:
    """Page numbers up to the reference list."""
    for i, p in enumerate(pages, start=1):
        if re.search(r"^\s*References\s*$", p, flags=re.M):
            return list(range(1, i + 1))
    return list(range(1, len(pages) + 1))


def pages_prompt(unread: list[int]) -> str:
    slots = "\n".join(f"- {name}: {desc}" for name, desc in SLOTS.items() if name != "key_findings")
    listed = ", ".join(str(n) for n in unread)
    return (f"Task: add to a structured reading note about the paper above.\n\nThe note so far quotes nothing from these pages: {listed}.\n"
            f"Read those pages again. For each slot below, give any answer those pages support that a careful reader would want in the note.\n\n"
            f"{slots}\n\n{RULES_2}\n- Every quote must come from one of the pages listed above.\n\n"
            f"Reply with one JSON object and nothing else, with only the slots you are adding to:\n"
            f'{{"scope_and_limits": [{{"claim": "...", "quotes": [{{"text": "...", "page": 1}}]}}], "evidence": [...]}}\n'
            f"If those pages add nothing, reply with an empty object: {{}}")


def expand_note(ask, pages: list[str], note: dict, trace: list, more_slots=MORE_SLOTS, unread_pages: bool = True) -> dict:
    """Ask for answers the note lacks: once per list-like slot, then once for the pages no
    entry quotes. Every addition must pass `confirm_quotes` like any other claim."""
    slots = {k: (list(v) if isinstance(v, list) else []) for k, v in note["slots"].items()}
    for slot in SLOTS:
        slots.setdefault(slot, [])

    def add(slot: str, entries: list[dict], step: str) -> None:
        have = {normalize_text(e["claim"]) for e in slots[slot]}
        fresh = [e for e in entries if normalize_text(e["claim"]) not in have]
        checked = confirm_quotes(ask, pages, {"slots": {slot: fresh}}, trace)["slots"][slot]
        checked = checked if isinstance(checked, list) else []
        trace.append({"step": step, "slot": slot, "offered": len(entries), "added": len(checked)})
        slots[slot] += checked

    for slot in more_slots:
        raw = ask(more_prompt(slot, [e["claim"] for e in slots[slot]]), True)
        entries, _ = read_entries(raw)
        trace.append({"step": "more: asked", "slot": slot, "raw": raw})
        add(slot, entries, "more: by slot")
    quoted = {q["page"] for entries in slots.values() for e in entries for q in e["quotes"]}
    unread = [n for n in body_pages(pages) if n not in quoted]
    if unread and unread_pages:
        raw = ask(pages_prompt(unread), True)
        reply = _read_json(raw, "{")
        trace.append({"step": "more: asked", "slot": "unquoted pages", "pages": unread, "raw": raw})
        for slot, value in (reply.items() if isinstance(reply, dict) else []):
            if slot in SLOTS and slot != "key_findings":
                add(slot, _entries(value), "more: unquoted pages")
    return {"slots": {k: (v if v else NOT_STATED) for k, v in slots.items()}}


# ---------- complete thin entries: same entries, fuller claims ----------

COMPLETE_SLOTS = ("central_claim", "evidence", "key_findings")


def complete_prompt(slot: str, claims: list[str]) -> str:
    listed = "\n".join(f"[{k}] {c}" for k, c in enumerate(claims))
    return (f"Task: complete the entries of one slot of a structured reading note about the paper above.\n\n"
            f"Slot \"{slot}\": {SLOTS[slot]}\n\nThe entries so far:\n{listed}\n\n"
            f"For each entry, check four things against the paper:\n"
            f"1. Direction: if it reports a difference or a relationship, does it say which way it goes?\n"
            f"2. Comparison: does it say compared with what, or among whom?\n"
            f"3. Size: if the paper gives a number for it, does the entry give that number?\n"
            f"4. Conditions: if the paper attaches a condition, an exception or a qualification to it, does the entry say so?\n\n"
            f"Rewrite only the entries where something is missing, adding what the paper states. Keep each entry to one or two "
            f"sentences about the same point. Keep the paper's own strength of wording and its hedges. Never combine numbers that "
            f"the paper reports for different things. Do not add new entries.\n\n"
            f"For each entry you rewrite, give one or two quotes of {MIN_QUOTE_WORDS} to {MAX_QUOTE_WORDS} words, copied exactly from the paper with their "
            f"page, that contain the detail you added.\n\n"
            f"Reply with one JSON list and nothing else, with only the entries you rewrote:\n"
            f'[{{"entry": 0, "claim": "...", "quotes": [{{"text": "...", "page": 1}}]}}]\n'
            f"If no entry needs completing, reply with an empty list: []")


def complete_entries(ask, pages: list[str], note: dict, trace: list) -> dict:
    """Ask the model to fill in what an entry leaves out (direction, comparison, size,
    conditions). A rewrite replaces the entry only if its new quotes are in the paper,
    every number in it is in the entry's quotes or was in the old claim, and it does not
    drop a hedge or add causal wording."""
    from .checks import CAUSAL, HEDGE, _asserted_causal, _has, numbers
    slots = dict(note["slots"])
    for slot in COMPLETE_SLOTS:
        entries = slots.get(slot)
        if not isinstance(entries, list) or not entries:
            continue
        raw = ask(complete_prompt(slot, [e["claim"] for e in entries]), True)
        reply = _read_json(raw, "[")
        trace.append({"step": "complete: asked", "slot": slot, "raw": raw})
        new_entries = list(entries)
        for r in reply if isinstance(reply, list) else []:
            k, claim = (r.get("entry"), r.get("claim")) if isinstance(r, dict) else (None, None)
            if not isinstance(k, int) or not 0 <= k < len(entries) or not isinstance(claim, str) or not claim.strip():
                continue
            old = entries[k]
            if normalize_text(claim) == normalize_text(old["claim"]):
                continue
            quotes = list(old["quotes"])
            for q in r.get("quotes") if isinstance(r.get("quotes"), list) else []:
                text = q.get("text") if isinstance(q, dict) else q
                on = _where(pages, text)
                if on and all(normalize_text(text) != normalize_text(x["text"]) for x in quotes):
                    stated = q.get("page") if isinstance(q, dict) else None
                    quotes.append({"text": text, "page": stated if stated in on else on[0]})
            pool = numbers(" ".join(q["text"] for q in quotes) + " " + old["claim"])
            loose = [v for v, tol in numbers(claim) if not _has(v, tol, pool)]
            joined = " ".join(q["text"] for q in quotes)
            why = None
            if loose:
                why = f"number not in its quotes: {loose[0]:g}"
            elif HEDGE.search(old["claim"]) and not HEDGE.search(claim):
                why = "hedge dropped"
            elif _asserted_causal(claim) and not _asserted_causal(old["claim"]) and not CAUSAL.search(joined):
                why = "causal wording added"
            trace.append({"step": "complete", "slot": slot, "entry": k, "result": "rejected: " + why if why else "rewritten",
                          "old_claim": old["claim"], "new_claim": claim.strip(), "quotes added": len(quotes) - len(old["quotes"])})
            if not why:
                new_entries[k] = {"claim": claim.strip(), "quotes": quotes}
        slots[slot] = new_entries
    return {"slots": slots}
