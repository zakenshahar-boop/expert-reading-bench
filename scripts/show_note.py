"""Print a model's note for one paper, one numbered entry per line, with its quotes.

    python3 scripts/show_note.py runs/<run> pone.0360061
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb.extract import pdf_pages  # noqa: E402
from grb.quotes import locate_quote  # noqa: E402
from grb.task import SLOTS, parse_output  # noqa: E402

run, pid = Path(sys.argv[1]), sys.argv[2]
note, how = parse_output(json.loads((run / f"{pid}.json").read_text())["raw"])
pages = pdf_pages(ROOT / "data" / "plos" / pid / "paper.pdf")
print(f"{run.name} {pid} (reply read as: {how})")
for slot in SLOTS:
    entries = note["slots"].get(slot)
    print(f"\n## {slot}")
    if not isinstance(entries, list):
        print(f"  {entries!r}")
        continue
    for k, e in enumerate(entries):
        claim = e.get("claim") if isinstance(e, dict) else e
        print(f"  [{k}] {claim}")
        for q in (e.get("quotes") or []) if isinstance(e, dict) else []:
            text = q.get("text") if isinstance(q, dict) else q
            page = q.get("page") if isinstance(q, dict) else None
            print(f"        {'in paper' if locate_quote(pages, text or '') else 'NOT IN PAPER'} p.{page}: {text}")
