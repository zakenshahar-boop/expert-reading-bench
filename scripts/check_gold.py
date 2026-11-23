"""Check a gold file against its PDF and write a readable review sheet.

Every span in the gold file must occur, whole, on the page it names. Prints one line
per failure and a table of counts per slot, and writes gold/<paper_id>.md.

    python3 scripts/check_gold.py gold/pone.0360061.json
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb.extract import pdf_pages  # noqa: E402
from grb.quotes import locate_quote, verify_quote  # noqa: E402


def main(gold_path: str) -> int:
    gold = json.loads(Path(gold_path).read_text())
    pid = gold["paper_id"]
    pages = pdf_pages(ROOT / "data" / "plos" / pid / "paper.pdf")
    failures, rows = 0, []
    md = [f"# Gold answers: {gold['title']}", "",
          f"Paper `{pid}`, {len(pages)} pages. Status: {gold['status']}.", "",
          "Origin codes: R1 to R4 are reviewers with the review round in parentheses, "
          "AR1 and AR2 are the author responses, ED is the editor, and `paper` means the "
          "answer comes from the published paper alone.", ""]

    def check(item_id: str, span: dict) -> None:
        nonlocal failures
        if not verify_quote(pages, span["text"], span["page"]):
            failures += 1
            where = locate_quote(pages, span["text"])
            print(f"FAIL {item_id} p{span['page']} (found on {where or 'no page'}): {span['text'][:70]}")

    for slot, body in gold["slots"].items():
        acc, rej, bord = body["acceptable"], body["rejected"], body["borderline"]
        backed = sum(1 for a in acc if not any(o.startswith(("paper", "model-suggested", "labeler")) for o in a["origin"]))
        rows.append((slot, len(acc), backed, len(rej), len(bord)))
        md += [f"## {slot.replace('_', ' ').capitalize()}", "", "Acceptable:", ""]
        if body.get("not_stated_is_acceptable"):
            md.append("- **not stated** is an acceptable answer for this slot.")
        for a in acc:
            tag = "".join(f" [{a[k]}]" for k in ("tier", "part") if k in a)
            md.append(f"- **{a['id']}**{tag} {a['answer']} ({', '.join(a['origin'])})")
            for s in a["spans"]:
                check(a["id"], s)
                md.append(f"  - p. {s['page']}: \"{s['text']}\"")
        for title, items in (("Rejected", rej), ("Neutral: no credit, no penalty", body.get("neutral", [])),
                             ("Borderline, needs a decision", bord)):
            if not items:
                continue
            md += ["", f"{title}:", ""]
            for r in items:
                md.append(f"- **{r['id']}** {r['answer']} ({', '.join(r['origin'])})")
                note = r.get("why") or r.get("question_for_labeler")
                md.append(f"  - {note}")
                for s in [r["counter_span"]] if "counter_span" in r else r.get("spans", []):
                    check(r["id"], s)
                    md.append(f"  - p. {s['page']}: \"{s['text']}\"")
        md.append("")

    Path(gold_path).with_suffix(".md").write_text("\n".join(md))
    print(f"{'slot':26}{'acceptable':>11}{'from review':>12}{'rejected':>9}{'borderline':>11}")
    for r in rows:
        print(f"{r[0]:26}{r[1]:>11}{r[2]:>12}{r[3]:>9}{r[4]:>11}")
    t = [sum(r[i] for r in rows) for i in range(1, 5)]
    print(f"{'total':26}{t[0]:>11}{t[1]:>12}{t[2]:>9}{t[3]:>11}")
    print(f"span failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
