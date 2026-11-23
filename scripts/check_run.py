"""Run the deterministic checks on saved replies.

    python3 scripts/check_run.py runs/opus-5-5-text-prompt3 runs/haiku-5-5-text-prompt3
    python3 scripts/check_run.py --paper pone.0360061 --items runs/opus-5-5-text-prompt3

Prints one column per run, summed over its papers, and writes checks.json in each run.
Gold-quote overlap is computed only for papers that have a gold file.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb import checks  # noqa: E402
from grb.extract import pdf_pages  # noqa: E402
from grb.task import parse_output  # noqa: E402

GROUPS = ("numbers in claims", "strength of claim", "attribution (interlocutor slot)",
          "overlap with gold quotes", "where quotes come from")


def run_checks(run: Path, only: str | None) -> dict:
    per_paper = {}
    for f in sorted(run.glob("pone.*.json")):
        rec = json.loads(f.read_text())
        pid = rec["paper_id"]
        if only and pid != only:
            continue
        folder = ROOT / "data" / "plos" / pid
        pages, xml = pdf_pages(folder / "paper.pdf"), (folder / "paper.xml").read_text()
        note, _ = parse_output(rec["raw"])
        r = {GROUPS[0]: checks.number_check(note, pages),
             GROUPS[1]: checks.strength_check(note),
             GROUPS[2]: checks.attribution_check(note, pages, xml),
             GROUPS[4]: checks.location_check(note, pages, xml)}
        gold = ROOT / "gold" / f"{pid}.json"
        if gold.exists():
            r[GROUPS[3]] = checks.gold_overlap(note, pages, json.loads(gold.read_text()))
        per_paper[pid] = r
    return per_paper


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+")
    ap.add_argument("--paper")
    ap.add_argument("--items", action="store_true", help="also print each flagged item")
    args = ap.parse_args()
    results = {}
    for r in args.runs:
        results[Path(r).name] = run_checks(Path(r), args.paper)
        if not args.paper:
            (Path(r) / "checks.json").write_text(json.dumps(results[Path(r).name], indent=2, ensure_ascii=False))
    names = list(results)
    print(f"{'':40}" + "".join(f"{n[:24]:>26}" for n in names))
    print(f"{'papers':40}" + "".join(f"{len(results[n]):>26}" for n in names))
    for group in GROUPS:
        keys = []
        for n in names:
            for paper in results[n].values():
                for k, v in paper.get(group, {}).items():
                    if isinstance(v, (int, bool)) and k not in keys:
                        keys.append(k)
        if not keys:
            continue
        print(group)
        for k in keys:
            print(f"  {k:38}" + "".join(
                f"{sum(p.get(group, {}).get(k, 0) for p in results[n].values()):>26}" for n in names))
    if args.items:
        for n in names:
            for pid, paper in results[n].items():
                for group, r in paper.items():
                    for item in r.get("items", []):
                        print(f"\n[{n} | {pid} | {group}] {json.dumps(item, ensure_ascii=False)}")
                    if r.get("missed"):
                        print(f"\n[{n} | {pid} | {group}] no overlap: {' '.join(r['missed'])}")


if __name__ == "__main__":
    main()
