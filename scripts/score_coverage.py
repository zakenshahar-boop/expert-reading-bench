"""Score a model's note against a paper's gold answers, from a file of matches.

The matches (which gold answer each entry of the note states) are judgments. They live
in runs/<run>/coverage.<paper_id>.json and say who made them. This script only counts.

    python3 scripts/score_coverage.py pone.0360061 runs/qwen3-4b-4bit-prompt2 runs/opus-5-5-text
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def score(gold: dict, cov: dict) -> dict:
    """Full match = 1 point, partial = 0.5. A correct answer in the wrong slot ("misplaced") = 0.5, no flag.
    An answer that two or more entries of its own slot state between them ("joined") = 1 point
    (labeler decision, 2026-11-22). Flags are claims that say more than the paper does; a flag
    whose type ends in "(mild)" is counted separately from the serious ones."""
    slots = gold["slots"]
    acceptable = {a["id"]: (s, a) for s, b in slots.items() for a in b["acceptable"]}
    points, flags, empty, slots_hit, unlisted = {}, [], 0, 0, 0
    caught = set()
    loose = {}
    for slot, entries in cov["entries"].items():
        hit = False
        for e in entries:
            full = [i for i in e.get("match", []) if acceptable[i][0] == slot]
            for i in full:
                points[i] = 1.0
            for i in e.get("partial", []) + e.get("misplaced", []):
                points[i] = max(points.get(i, 0), 0.5)
            for i in e.get("ungrounded", []):
                loose[i] = 1.0
            flags += e.get("flags", [])
            caught.update(e.get("catches", []))
            credited = bool(full) or bool(e.get("partial")) or bool(e.get("misplaced"))
            hit = hit or credited
            unlisted += bool(e.get("unlisted"))
            empty += not credited and not e.get("unlisted") and not e.get("neutral")
        slots_hit += hit

    strict = dict(points)
    for i in cov.get("joined", []):
        if i in acceptable:
            points[i] = 1.0
    mild = sum(1 for f in flags if "(mild)" in f["type"])

    def total(ids):
        return f"{sum(points.get(i, 0) for i in ids):g}/{len(ids)}"

    by = lambda test: [i for i, (s, a) in acceptable.items() if test(s, a)]  # noqa: E731
    kinds = sorted({f["type"] for f in flags})
    out = {"slots with any credit": f"{slots_hit}/{len(slots)}",
           "core findings": total(by(lambda s, a: s == "key_findings" and a.get("tier") == "core")),
           "required evidence": total(by(lambda s, a: a.get("required"))),
           "primary framework named": total(by(lambda s, a: a.get("tier") == "primary")),
           "acceptable answers, points": total(list(acceptable)),
           "  if answers split across entries counted in full": total(list(acceptable)),
           "  strict (an answer split across entries earns half)": f"{sum(strict.get(i, 0) for i in acceptable):g}/{len(acceptable)}",
           "  if claims without a faithful quote counted": f"{sum(max(points.get(i, 0), loose.get(i, 0)) for i in acceptable):g}/{len(acceptable)}",
           "risk flags": f"{len(flags)}" + (f" ({', '.join(kinds)})" if kinds else ""),
           "serious flags": str(len(flags) - mild),
           "mild flags": str(mild),
           "critical catches (bonus)": f"{len(caught)}/{len(gold.get('critical_catches', []))}",
           "true but not in the gold": str(unlisted),
           "other entries with no credit": str(empty)}
    for s in slots:
        out[f"  {s}"] = total(by(lambda slot, a, s=s: slot == s))
    return out


def main(paper_id: str, runs: list[str]) -> None:
    gold = json.loads((ROOT / "gold" / f"{paper_id}.json").read_text())
    results = {Path(r).name: score(gold, json.loads((Path(r) / f"coverage.{paper_id}.json").read_text()))
               for r in runs}
    names = list(results)
    print(f"{'':44}" + "".join(f"{n:>26}" for n in names))
    for key in results[names[0]]:
        print(f"{key:44}" + "".join(f"{results[n][key]:>26}" for n in names))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
