# Brief given to the judge

Each note was matched to the gold answers by a Claude Opus 5.5 agent, one agent per paper,
working in this repository with read access to the gold file, the protocol and the paper.
The text below is the brief, with the paper id and the list of notes filled in per agent.
The first agents (2026-11-22) had no calibration paragraph; later agents were told to read
two notes the first agents had matched for the same paper and to apply the same strictness.

Where a note had already been matched by hand, the agent was told not to open that file.

---

You are a careful judge for a reading benchmark. Work in the root directory of this checkout. Your paper id is PID = <paper id>.

Background: models read a scholarly paper and write a structured note with seven slots (question, central_claim, evidence, key_findings, scope_and_limits, theoretical_positioning, interlocutor_claim). Each entry is a claim plus quotes. A human-reviewed gold file lists, per slot, "acceptable" answers (ids like Q1, C2, E3, F1, L4, T2, I5), "rejected" answers (ids like C-x1, F-x2: things a note must NOT say) and sometimes "neutral" answers (no credit, no penalty). You judge which gold answers each entry of a note states. You only write the match files named below; never edit gold files, notes, scripts or anything else, and do not run git.

An earlier judge (another Claude Opus 5.5 agent) already matched other notes for this paper. Your matches will be compared with theirs, so apply the same strictness. Before you start, read for calibration: runs/haiku-5-5-harness-expand-findings/coverage.PID.json together with `python3 scripts/show_note.py runs/haiku-5-5-harness-expand-findings PID`, and runs/qwen3-4b-harness-slots/coverage.PID.json together with `python3 scripts/show_note.py runs/qwen3-4b-harness-slots PID`. Notice when that judge gave a full match, a partial, a misplaced credit, a flag, or nothing, and do the same in like cases.

Read first:
1. gold/PID.json in full (answers with their "why", "decided" and "note" fields, tiers, rejected and neutral lists, "critical_catches").
2. docs/LABELING_PROTOCOL.md (scoring rules and the decisions lists).
3. The paper: `python3 scripts/reading_view.py paper PID` (pages are marked). For author names of numbered references, look in data/plos/PID/paper.xml.

Matching rules:
- "match": the entry states that acceptable answer and the answer belongs to the entry's own slot. "partial": own slot, but only part of the answer. "misplaced": the entry states an acceptable answer that belongs to another slot (half credit). An entry may list several ids. Strict about substance, lenient about wording.
- "flags": the entry says more than the paper does or gets it wrong. Each is {"type", "gold": rejected or related id or null, "text": what the note said and what the paper says}. Types: "overclaim", "overclaim (mild)", "wrong direction", "made up", "unsupported detail", "unsupported attribution", "wrong stance". An entry stating a rejected gold answer gets a flag naming it. Check every flag against the paper. Wording the paper itself uses is not flagged even when strong; only a version stronger than anything in the paper is.
- "unlisted": true when the entry is accurate to the paper but matches no gold answer. "neutral": true when it matches a neutral gold item. "catches": a critical_catches id only if the entry explicitly points out that contradiction inside the paper.
- These notes' quotes are all confirmed to be in the paper unless show_note marks one "NOT IN PAPER"; an entry with no quote in the paper earns no credit and its ids go in "ungrounded" instead.
- Add a short "note" wherever a call is not obvious.

Split answers: after matching a note, add a top-level key "joined": the acceptable ids for which no single entry earned a full match, but two or more entries in the answer's own slot, each credited partial for it, together state the whole gold answer (every part, including any qualification it carries). Reported statistics such as an r value are detail, not a required part. Empty list if none.

Output per note: {"paper_id": "PID", "judged_by": "Matched by a Claude Opus 5.5 agent on 2026-11-22; not yet checked by the labeler.", "joined": [...], "entries": {slot: [one object per printed entry, in order, each with "match" (list, may be empty) and optionally "partial", "misplaced", "ungrounded", "flags", "unlisted", "neutral", "catches", "note"]}} with all seven slots.

Task. For each note listed: print it with `python3 scripts/show_note.py <run> <paper id>`,
write `<run>/coverage.<paper id>.json` (or `agent_coverage.<paper id>.json` where a hand-made
`coverage` file already exists), validate it with `python3 scripts/score_coverage.py`, and
check that each slot's list has one object per printed entry. Report the entries, points,
flags and joined ids, and every call you were unsure about.
