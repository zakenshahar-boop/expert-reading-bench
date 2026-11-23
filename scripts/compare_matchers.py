"""Compare two matchings of the same notes against the gold: credit per gold answer.

    python3 scripts/compare_matchers.py runs/haiku-5-5-text-prompt3 coverage agent_coverage
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def credit(gold: dict, cov: dict) -> tuple[dict, int]:
    slot_of = {a["id"]: s for s, b in gold["slots"].items() for a in b["acceptable"]}
    pts, flags = {i: 0.0 for i in slot_of}, 0
    for slot, entries in cov["entries"].items():
        for e in entries:
            for i in e.get("match", []):
                if i in pts:
                    pts[i] = max(pts[i], 1.0 if slot_of[i] == slot else 0.5)
            for i in e.get("partial", []) + e.get("misplaced", []):
                if i in pts:
                    pts[i] = max(pts[i], 0.5)
            flags += len(e.get("flags", []))
    return pts, flags


def main(run: str, a: str, b: str) -> None:
    same = n = 0
    exact_cells = {}
    ta = tb = fa = fb = 0
    for f in sorted(Path(run).glob(f"{b}.pone.*.json")):
        pid = f.name.split(".", 1)[1].rsplit(".", 1)[0]
        other = Path(run) / f"{a}.{pid}.json"
        if not other.exists():
            continue
        gold = json.loads((ROOT / "gold" / f"{pid}.json").read_text())
        pa, xa = credit(gold, json.loads(other.read_text()))
        pb, xb = credit(gold, json.loads(f.read_text()))
        agree = sum(pa[i] == pb[i] for i in pa)
        diff = [f"{i}:{pa[i]:g}/{pb[i]:g}" for i in pa if pa[i] != pb[i]]
        print(f"{pid}  {a} {sum(pa.values()):g}  {b} {sum(pb.values()):g}  of {len(pa)}   same credit on {agree}/{len(pa)}   flags {xa}/{xb}")
        print("   differ:", " ".join(diff) or "none")
        same, n = same + agree, n + len(pa)
        ta, tb, fa, fb = ta + sum(pa.values()), tb + sum(pb.values()), fa + xa, fb + xb
        for i in pa:
            key = (pa[i], pb[i])
            exact_cells[key] = exact_cells.get(key, 0) + 1
    if n:
        po = same / n
        cats = sorted({k for pair in exact_cells for k in pair})
        pe = sum((sum(v for (x, _), v in exact_cells.items() if x == c) / n) * (sum(v for (_, y), v in exact_cells.items() if y == c) / n) for c in cats)
        print(f"\nall: {a} {ta:g}, {b} {tb:g} of {n} answers; same credit on {same}/{n} = {po:.0%}; Cohen's kappa {(po - pe) / (1 - pe):.2f}; flags {fa} vs {fb}")
        both = sum(v for (x, y), v in exact_cells.items() if x > 0 and y > 0)
        either = sum(v for (x, y), v in exact_cells.items() if x > 0 or y > 0)
        print(f"answers credited by both / by either: {both}/{either}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
