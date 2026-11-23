"""What each run cost, from the token counts saved with each reply and docs/prices.json.

    python3 scripts/costs.py

API models: dollars per paper at the listed standard rates. Local models: minutes per paper.
Output tokens include a model's reasoning tokens, which are billed as output.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRICES = json.loads((ROOT / "docs" / "prices.json").read_text())["models"]


def usage(run: str) -> dict:
    """Totals over the papers of one run folder."""
    t = dict(papers=0, input=0, output=0, seconds=0.0, calls=0, model=None)
    for f in sorted((ROOT / "runs" / run).glob("pone.*.json")):
        d = json.loads(f.read_text())
        t["papers"] += 1
        t["input"] += d.get("input_tokens") or d.get("prompt_tokens") or 0
        t["output"] += d.get("output_tokens") or 0
        t["seconds"] += d.get("seconds") or 0
        t["calls"] += d.get("model_calls", 1)
        t["model"] = d.get("model")
    return t


def dollars(u: dict) -> float | None:
    p = PRICES.get(u["model"])
    return None if p is None else (u["input"] * p["input"] + u["output"] * p["output"]) / 1e6


def per_paper(runs: list[str]) -> dict:
    """Mean over several run folders, per paper. Costs add when a result needs several steps."""
    us = [usage(r) for r in runs]
    n = us[0]["papers"] or 1
    cost = [dollars(u) for u in us]
    return {"dollars": None if None in cost else sum(cost) / n, "input": sum(u["input"] for u in us) / n,
            "output": sum(u["output"] for u in us) / n, "minutes": sum(u["seconds"] for u in us) / n / 60,
            "calls": sum(u["calls"] for u in us) / n}


if __name__ == "__main__":
    for run in sys.argv[1:]:
        print(run, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in per_paper([run]).items()})
