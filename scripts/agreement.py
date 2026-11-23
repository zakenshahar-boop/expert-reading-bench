"""Agreement between the human labeler and the two matchings on a labeling sample.

    python3 scripts/agreement.py labeling/sample1
"""

import json
import sys
from collections import Counter


def kappa(a: list, b: list) -> tuple[float, float]:
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in set(a) | set(b))
    return po, (po - pe) / (1 - pe) if pe < 1 else 1.0


def report(stem: str) -> dict:
    key = json.load(open(stem + "_key.json"))["items"]
    labels = json.load(open(stem + "_labels.json"))["labels"]
    human = [labels[str(i["n"])]["credit"] for i in key]
    out = {"items": len(key), "human labels": dict(Counter(human))}
    for judge, name in (("agent", "Claude Opus 5.5 agents"), ("hand", "the assistant's hand matching")):
        other = [i[judge] for i in key]
        po, k = kappa(human, other)
        out[name] = {"same label": f"{sum(x == y for x, y in zip(human, other))}/{len(key)} = {po:.0%}", "Cohen's kappa": round(k, 2),
                     "judge stricter than human": sum(y < x for x, y in zip(human, other)),
                     "judge more generous than human": sum(y > x for x, y in zip(human, other))}
    split = [(h, i["agent"], i["hand"]) for h, i in zip(human, key) if i["agent"] != i["hand"]]
    out["where the two matchings disagreed"] = {"items": len(split), "human sided with the agents": sum(h == a for h, a, _ in split),
                                                "human sided with the hand matching": sum(h == m for h, _, m in split)}
    return out


if __name__ == "__main__":
    print(json.dumps(report(sys.argv[1]), indent=1))
