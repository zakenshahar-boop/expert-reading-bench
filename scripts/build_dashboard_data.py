"""Write the dashboard's data files (dashboard/*.csv) from the scored runs.

    python3 scripts/build_dashboard_data.py

Every row uses the same judge: the matches made by Claude Opus 5.5 agents
(`agent_coverage.*.json`, or `coverage.*.json` in runs that only the agents matched).
"""

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from score_coverage import score  # noqa: E402

THREE = ("", "-run2", "-run3")
# Each model with its runs. The local model's three runs are sampled (temperature 0.7, seeds 1 to 3);
# its earlier run at temperature 0 is the starting point of its harness rows.
MODELS = [("qwen", "Qwen3 4B (local)", [f"qwen3-4b-4bit-prompt3-sample{i}" for i in (1, 2, 3)]),
          ("gpt4o", "GPT-4o", ["gpt-4o-text-prompt3" + x for x in THREE]),
          ("haiku", "Claude Haiku 5.5", ["haiku-5-5-text-prompt3" + x for x in THREE]),
          ("sol", "GPT-6.2 Sol", ["gpt-6.2-sol-text-prompt3" + x for x in THREE]),
          ("astra", "GPT-6.2 Astra", ["gpt-6.2-astra-text-prompt3" + x for x in THREE]),
          ("opus", "Claude Opus 5.5", ["opus-5-5-text-prompt3" + x for x in THREE])]
# Local models run by Ellian-Eorwyn (https://github.com/Ellian-Eorwyn) on one RTX 3090 (2026-11-25; docs/local-runs-2026-11-25/). Each has three runs and the
# four harness settings, started from its first run.
CONTRIBUTED = [("gemma31", "Gemma 4 31B (local)", "local-gemma4-31b-qat-q4_0"),
               ("qwen38", "Qwen3.8 27B, thinking low (local)", "local-qwen3.8-27b-default"),
               ("qwen38off", "Qwen3.8 27B, thinking off (local)", "local-qwen3.8-27b-default-nothink"),
               ("muse", "Muse Glimmer 30B (local)", "local-muse-glimmer-30b-q4km"),
               ("gemma26", "Gemma 4 26B-A4B (local)", "local-gemma4-26b-a4b-judge"),
               ("qwen36", "Qwen3.6 35B-A3B (local)", "local-qwen3.6-35b-a3b-q4km")]
MODELS += [(mid, name, [prefix + "-text-prompt3" + x for x in THREE]) for mid, name, prefix in CONTRIBUTED]
HARNESS = [
    ("Qwen3 4B (local)", "Model alone", "qwen3-4b-4bit-prompt3"),
    ("Qwen3 4B (local)", "Quotes confirmed", "qwen3-4b-harness-confirm"),
    ("Qwen3 4B (local)", "Quotes confirmed, claims re-checked", "qwen3-4b-harness-confirm-recheck2"),
    ("GPT-4o", "Model alone", "gpt-4o-text-prompt3"),
    ("GPT-4o", "Quotes confirmed", "gpt-4o-harness-confirm"),
    ("GPT-4o", "Quotes confirmed, claims re-checked", "gpt-4o-harness-confirm-recheck2"),
    ("GPT-4o", "Quotes confirmed, asked for more", "gpt-4o-harness-expand"),
    ("GPT-4o", "Asked for more, key findings too", "gpt-4o-harness-expand-findings"),
    ("Claude Haiku 5.5", "Model alone", "haiku-5-5-text-prompt3"),
    ("Claude Haiku 5.5", "Quotes confirmed", "haiku-5-5-harness-confirm"),
    ("Claude Haiku 5.5", "Quotes confirmed, claims re-checked", "haiku-5-5-harness-confirm-recheck2"),
    ("Claude Haiku 5.5", "Quotes confirmed, asked for more", "haiku-5-5-harness-expand"),
    ("Claude Haiku 5.5", "Asked for more, key findings too", "haiku-5-5-harness-expand-findings"),
]
HARNESS += [(name, setting, prefix + suffix) for _, name, prefix in CONTRIBUTED for setting, suffix in (
    ("Model alone", "-text-prompt3"), ("Quotes confirmed", "-harness-confirm"),
    ("Quotes confirmed, claims re-checked", "-harness-confirm-recheck2"),
    ("Quotes confirmed, asked for more", "-harness-expand"), ("Asked for more, key findings too", "-harness-expand-findings"))]
PAPERS = [("0360061", "Online hostility"), ("0342063", "Vaccine hesitancy"), ("0355933", "Criminal record labels"),
          ("0347327", "COVID polarization"), ("0362373", "Adolescent networks")]
SLOTS = [("question", "Question"), ("central_claim", "Central claim"), ("evidence", "Evidence"), ("key_findings", "Key findings"),
         ("scope_and_limits", "Scope and limits"), ("theoretical_positioning", "Theory"), ("interlocutor_claim", "Interlocutors")]


def frac(text):
    return [float(x) for x in text.split("/")]


def matches(run: str, pid: str) -> dict:
    for name in ("agent_coverage", "coverage"):
        f = ROOT / "runs" / run / f"{name}.pone.{pid}.json"
        if f.exists():
            return json.loads(f.read_text())
    raise SystemExit(f"no matches for {run} {pid}")


def write(name, rows):
    with open(ROOT / "dashboard" / f"{name}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(name, len(rows))


def one(run: str, pid: str) -> tuple[dict, dict, dict]:
    gold = json.loads((ROOT / "gold" / f"pone.{pid}.json").read_text())
    cov = matches(run, pid)
    s = score(gold, cov)
    q = json.loads((ROOT / "runs" / run / "scores.json").read_text())["pone." + pid]
    return s, q, cov


def main():
    res, slots, flags, catches, harness = [], {}, [], [], []
    for mid, mname, runs in MODELS:
        for rn, run in enumerate(runs, start=1):
            for pid, pname in PAPERS:
                s, q, cov = one(run, pid)
                pts, n = frac(s["acceptable answers, points"])
                strict, _ = frac(s["  strict (an answer split across entries earns half)"])
                loose, _ = frac(s["  if claims without a faithful quote counted"])
                core, ncore = frac(s["core findings"])
                c, nc = frac(s["critical catches (bonus)"])
                prim, _ = frac(s["primary framework named"])
                res.append(dict(key=f"{mid}.{pid}.{rn}", model_id=mid, model=mname, run=rn, paper_id=pid, paper=pname, points=pts,
                                points_strict=strict, points_no_quote=max(loose, pts), answers=n, core=core, core_total=ncore,
                                quotes=q["quotes"], verbatim=q["faithful"], page_correct=q["located"],
                                flags_serious=int(s["serious flags"]), flags_mild=int(s["mild flags"]), primary_framework=prim,
                                catches=c, catches_total=nc, not_in_gold=int(s["true but not in the gold"]), claims=q["entries"]))
                for sid, sname in SLOTS:
                    a, b = frac(s["  " + sid])
                    d = slots.setdefault((mid, sid), dict(key=f"{mid}.{sid}", model_id=mid, model=mname, slot_id=sid, slot=sname, points=0, answers=0))
                    d["points"] += a
                    d["answers"] += b
                for ents in cov["entries"].values():
                    for e in ents:
                        for f in e.get("flags", []):
                            flags.append(dict(id=f"f{len(flags) + 1}", model=mname, run=rn, paper=pname, type=f["type"],
                                              severity="mild" if "(mild)" in f["type"] else "serious", what=f["text"]))
    for k, (mname, setting, run) in enumerate(HARNESS):
        t = dict(points=0.0, joined=0.0, answers=0.0, core=0.0, core_total=0.0, flags=0, serious=0, mild=0, claims=0, quotes=0, verbatim=0)
        for pid, _ in PAPERS:
            s, q, _cov = one(run, pid)
            pts, n = frac(s["acceptable answers, points"])
            joined, _ = frac(s["  strict (an answer split across entries earns half)"])
            core, ncore = frac(s["core findings"])
            for key, v in dict(points=pts, joined=joined, answers=n, core=core, core_total=ncore, flags=int(s["risk flags"].split()[0]),
                               serious=int(s["serious flags"]), mild=int(s["mild flags"]),
                               claims=q["entries"], quotes=q["quotes"], verbatim=q["faithful"]).items():
                t[key] += v
        harness.append(dict(key=f"h{k}", model=mname, setting=setting, order=k, points=t["points"], points_strict=t["joined"],
                            answers=t["answers"], core=t["core"], core_total=t["core_total"], flags=t["flags"], flags_serious=t["serious"], flags_mild=t["mild"], claims=t["claims"],
                            quotes=t["quotes"], verbatim=t["verbatim"]))
    for pid, pname in PAPERS:
        for b in json.loads((ROOT / "gold" / f"pone.{pid}.json").read_text()).get("critical_catches", []):
            catches.append(dict(id=f"{pid}.{b['id']}", paper=pname, contradiction=b["catch"], caught_by="no model"))
    write("results", res)
    write("slots", list(slots.values()))
    write("flags", flags)
    write("catches", catches)
    write("harness", harness)


if __name__ == "__main__":
    main()
