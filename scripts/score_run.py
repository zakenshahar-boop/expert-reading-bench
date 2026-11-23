"""Score saved replies for quote fidelity and locator accuracy.

    python3 scripts/score_run.py runs/qwen3-4b-4bit
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb.extract import pdf_pages  # noqa: E402
from grb.score import score_note  # noqa: E402
from grb.task import parse_output  # noqa: E402


def main(run_dir: str) -> None:
    run = Path(run_dir)
    total = {"quotes": 0, "faithful": 0, "located": 0}
    print(f"{'paper':14}{'reply':>11}{'filled':>7}{'n/s':>5}{'entries':>8}{'quotes':>7}"
          f"{'faithful':>9}{'located':>8}{'bad len':>8}")
    scores = {}
    for f in sorted(run.glob("pone.*.json")):
        rec = json.loads(f.read_text())
        pages = pdf_pages(ROOT / "data" / "plos" / rec["paper_id"] / "paper.pdf")
        note, how = parse_output(rec["raw"])
        s = score_note(note, pages)
        s["parsed"] = how
        scores[rec["paper_id"]] = s
        for k in total:
            total[k] += s[k]
        print(f"{rec['paper_id']:14}{s['parsed']:>11}{s['slots_filled']:>7}"
              f"{s['slots_not_stated']:>5}{s['entries']:>8}{s['quotes']:>7}"
              f"{s['faithful']:>9}{s['located']:>8}{s['bad_length']:>8}")
    q = total["quotes"] or 1
    print(f"\nquote fidelity   {total['faithful']}/{total['quotes']} = {total['faithful'] / q:.2f}")
    print(f"locator accuracy {total['located']}/{total['quotes']} = {total['located'] / q:.2f}")
    (run / "scores.json").write_text(json.dumps(scores, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
