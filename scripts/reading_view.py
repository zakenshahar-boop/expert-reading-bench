"""Print a paper's review history without journal boilerplate, or its pages without the
reference list, for a labeler to read.

    python3 scripts/reading_view.py reviews pone.0342063
    python3 scripts/reading_view.py paper pone.0342063
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb.extract import pdf_pages  # noqa: E402

BOILER = re.compile(
    r"editorialmanager|protocols\.io|PACE|NAAS|figures@plos|plosone@plos|ORCID|press office|"
    r"onepress@|billing|invoice|phishing|customercare|style requirements|Data Availability|"
    r"data availability|what does this mean|Do you want your identity|identity will remain|"
    r"marked-up copy|unmarked version|rebuttal letter|letter that responds|financial disclosure|"
    r"PLOS LaTeX|Supporting Information files|retracted|HTML markup|View Attachments|"
    r"production (team|department)|We look forward|Kind regards|judged scientifically suitable|"
    r"formally accepted|properly (cited|typeset)|supporting information is included|"
    r"PLOS Data policy|Privacy Policy|^\*+$|^Reviewer #\d+: (Yes|No|Partly|N/A|I Don't Know|\(No Response\))\s*$|"
    r"submission guidelines|recommended-repositories|Before we proceed|code sharing|"
    r"Journal Requirements|additional requirements|Submitted filename|^Attachment$|"
    r"^\d+\. (Is the manuscript|Has the statistical|Have the authors made|If the authors have)", re.I)


def main(kind: str, pid: str) -> None:
    folder = ROOT / "data" / "plos" / pid
    if kind == "reviews":
        for line in (folder / "reviews.md").read_text().splitlines():
            if line.strip() and not BOILER.search(line):
                print(line)
    else:
        for i, page in enumerate(pdf_pages(folder / "paper.pdf"), start=1):
            m = re.search(r"^\s*References\s*$", page, re.M)
            print(f"\n=== PAGE {i} ===\n{page[:m.start()] if m else page}")
            if m:
                break


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
