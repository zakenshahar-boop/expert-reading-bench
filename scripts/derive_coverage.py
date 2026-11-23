"""Carry matches over from one note to a later version of it made by the harness, which only
drops claims or repairs their quotes. Claims are paired by their text.

    python3 scripts/derive_coverage.py <source run> <source matches name> <target run> <target matches name>

A claim missing from the target is removed with its flags. A claim that was "ungrounded"
in the source (no quote found in the paper) and survives in the target now has a confirmed
quote, so its answers count: as a match in their own slot, as misplaced in another.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb.quotes import normalize_text  # noqa: E402
from grb.task import parse_output  # noqa: E402


def claims(note: dict, slot: str) -> list[str]:
    value = note["slots"].get(slot)
    return [(e.get("claim") if isinstance(e, dict) else e) or "" for e in value] if isinstance(value, list) else []


def main(src: str, src_name: str, dst: str, dst_name: str) -> None:
    for f in sorted(Path(src).glob(f"{src_name}.pone.*.json")):
        pid = f.name.split(".", 1)[1].rsplit(".", 1)[0]
        gold = json.loads((ROOT / "gold" / f"{pid}.json").read_text())
        slot_of = {a["id"]: s for s, b in gold["slots"].items() for a in b["acceptable"]}
        cov = json.loads(f.read_text())
        old, _ = parse_output(json.loads((Path(src) / f"{pid}.json").read_text())["raw"])
        new, _ = parse_output(json.loads((Path(dst) / f"{pid}.json").read_text())["raw"])
        out, dropped, lost_flags = {}, 0, 0
        for slot, entries in cov["entries"].items():
            before = claims(old, slot)
            if len(before) != len(entries):
                raise SystemExit(f"{pid} {slot}: {len(entries)} matches for {len(before)} claims")
            after = [normalize_text(c) for c in claims(new, slot)]
            by_claim = {}
            for c, e in zip(before, entries):
                by_claim.setdefault(normalize_text(c), e)
            dropped += sum(1 for c in before if normalize_text(c) not in after)
            lost_flags += sum(len(e.get("flags", [])) for c, e in zip(before, entries) if normalize_text(c) not in after)
            out[slot] = []
            for c in after:
                e = dict(by_claim.get(c, {"match": [], "note": "No match carried over for this claim."}))
                loose = e.pop("ungrounded", [])
                if loose:
                    e["match"] = list(e.get("match", [])) + [i for i in loose if slot_of.get(i) == slot]
                    wrong_slot = [i for i in loose if i in slot_of and slot_of[i] != slot]
                    if wrong_slot:
                        e["misplaced"] = list(e.get("misplaced", [])) + wrong_slot
                    e["note"] = (e.get("note", "") + " Quote repaired by the harness; credit carried over from the claim.").strip()
                out[slot].append(e)
        result = {"paper_id": pid, "judged_by": f"Carried over from {Path(src).name}/{src_name} ({cov.get('judged_by', '')}) Claims the harness dropped are removed; repaired quotes were not judged for support.", "entries": out}
        (Path(dst) / f"{dst_name}.{pid}.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(pid, "claims dropped", dropped, "flags removed with them", lost_flags)


if __name__ == "__main__":
    main(*sys.argv[1:5])
