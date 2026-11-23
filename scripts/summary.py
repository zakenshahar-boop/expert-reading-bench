"""One table for all papers and runs: coverage points, risk flags, bonus catches.

    python3 scripts/summary.py runs/qwen3-4b-4bit-prompt3 runs/haiku-5-5-text-prompt3 runs/opus-5-5-text-prompt3
    python3 scripts/summary.py --matcher=agent_coverage runs/...   # use another set of matches where a run has one
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from score_coverage import score  # noqa: E402


def frac(text: str) -> tuple[float, float]:
    a, b = text.split("/")
    return float(a), float(b)


def main(runs: list[str]) -> None:
    matcher = "coverage"
    if runs and runs[0].startswith("--matcher="):
        matcher, runs = runs[0].split("=", 1)[1], runs[1:]
    papers = sorted(p.stem for p in (ROOT / "gold").glob("pone.*.json"))
    for r in runs:
        run = Path(r)
        fid = json.loads((run / "scores.json").read_text())
        tot = dict(pts=0.0, strict=0.0, serious=0, mild=0, joined=0.0, loose=0.0, n=0.0, core=0.0, ncore=0.0, flags=0, faithful=0, located=0, quotes=0, prim=0.0, catch=0.0, ncatch=0.0)
        print(f"\n{run.name}")
        print(f"{'paper':<14}{'points':>10}{'no quote':>10}{'core':>8}{'flags':>7}{'quotes ok':>11}{'pages ok':>10}")
        for pid in papers:
            f = run / f"{matcher}.{pid}.json"
            if not f.exists():
                f = run / f"coverage.{pid}.json"
            if not f.exists():
                continue
            s = score(json.loads((ROOT / "gold" / f"{pid}.json").read_text()), json.loads(f.read_text()))
            pts, n = frac(s["acceptable answers, points"])
            loose, _ = frac(s["  if claims without a faithful quote counted"])
            joined, _ = frac(s["  if answers split across entries counted in full"])
            strict, _ = frac(s["  strict (an answer split across entries earns half)"])
            tot["strict"] += strict
            tot["serious"] += int(s["serious flags"])
            tot["mild"] += int(s["mild flags"])
            core, ncore = frac(s["core findings"])
            flags = int(s["risk flags"].split()[0])
            q = fid.get(pid, {})
            print(f"{pid:<14}{pts:>6g}/{n:<3g}{loose:>7g}/{n:<3g}{core:>4g}/{ncore:<3g}{flags:>5}{q.get('faithful', 0):>7}/{q.get('quotes', 0):<3}{q.get('located', 0):>6}/{q.get('quotes', 0):<3}")
            c, nc = frac(s["critical catches (bonus)"])
            p1, _ = frac(s["primary framework named"])
            for k, v in dict(pts=pts, joined=joined, loose=loose, n=n, core=core, ncore=ncore, flags=flags, faithful=q.get("faithful", 0),
                             located=q.get("located", 0), quotes=q.get("quotes", 0), prim=p1, catch=c, ncatch=nc).items():
                tot[k] += v
        t = tot
        print(f"{'all':<14}{t['pts']:>6g}/{t['n']:<3g}{t['loose']:>7g}/{t['n']:<3g}{t['core']:>4g}/{t['ncore']:<3g}{t['flags']:>5}{t['faithful']:>7}/{t['quotes']:<3}{t['located']:>6}/{t['quotes']:<3}")
        print(f"flags: {t['serious']} serious, {t['mild']} mild   strict rule (split answers half): {t['strict']:g}/{t['n']:g} = {t['strict'] / t['n']:.0%}")
        print(f"coverage {t['pts'] / t['n']:.0%}   primary framework {t['prim']:g}/5   bonus catches {t['catch']:g}/{t['ncatch']:g}")


if __name__ == "__main__":
    main(sys.argv[1:])
