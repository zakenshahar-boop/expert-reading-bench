import json

from grb import harness

PAGES = ["Alpha beta gamma delta epsilon zeta eta theta iota kappa.", "The ad raised belief in public service motives among Democrats in the sample."]


def test_confirm_keeps_found_quotes_fixes_pages_and_drops_the_rest():
    note = {"slots": {"key_findings": [
        {"claim": "found", "quotes": [{"text": "beta gamma delta epsilon zeta", "page": 2}]},
        {"claim": "repairable", "quotes": [{"text": "the ad raised belief in civic motives a lot", "page": 2}]},
        {"claim": "hopeless", "quotes": []}]}}
    replies = iter(['{"text": "The ad raised belief in public service motives", "page": 2}', '{"text": null}'])
    trace = []
    out = harness.confirm_quotes(lambda prompt, with_paper: next(replies), PAGES, note, trace)
    kept = out["slots"]["key_findings"]
    assert [e["claim"] for e in kept] == ["found", "repairable"]
    assert kept[0]["quotes"][0]["page"] == 1
    assert kept[1]["quotes"][0]["text"].startswith("The ad raised")
    assert any(t["step"] == "drop" for t in trace)


def test_recheck_drops_unsupported_and_rewrites_wrong_direction():
    q = [{"text": "The ad raised belief in public service motives", "page": 2}]
    note = {"slots": {"key_findings": [{"claim": "The ad lowered belief.", "quotes": q}, {"claim": "Unrelated.", "quotes": q}, {"claim": "Fine.", "quotes": q}]}}
    replies = iter([json.dumps({"supported": "partly", "direction": "no", "attribution": "none", "claim": "The ad raised belief."}),
                    json.dumps({"supported": "no", "direction": "none", "attribution": "none", "claim": ""}),
                    json.dumps({"supported": "yes", "direction": "yes", "attribution": "none", "claim": "Fine."})])
    out = harness.recheck_claims(lambda prompt, with_paper: next(replies), PAGES, note, [])
    assert [e["claim"] for e in out["slots"]["key_findings"]] == ["The ad raised belief.", "Fine."]


def test_reply_with_malformed_quotes_is_read_loosely():
    raw = '[{"claim": "A.", "quotes": ["beta gamma delta epsilon zeta", "page": 1]}, {"claim": "B.", "quotes": [{"text": "x y", "page": 2}]}]'
    entries, how = harness.read_entries(raw)
    assert how == "read loosely"
    assert entries[0] == {"claim": "A.", "quotes": [{"text": "beta gamma delta epsilon zeta", "page": 1}]}
    assert entries[1]["quotes"] == [{"text": "x y", "page": 2}]


def test_recheck_2_asks_narrow_questions_and_rewrites_direction():
    q = [{"text": "The ad raised belief in public service motives", "page": 2}]
    note = {"slots": {"key_findings": [{"claim": "The ad decreased belief in public service motives.", "quotes": q}, {"claim": "Unrelated.", "quotes": q}],
                      "interlocutor_claim": [{"claim": "Prior research said the ad does nothing.", "quotes": q}]}}
    replies = iter(["yes", "opposite", "The ad raised belief in public service motives.", "No.", "yes", "no"])
    trace = []
    out = harness.recheck_claims_2(lambda prompt, with_paper: next(replies), PAGES, note, trace)
    assert [e["claim"] for e in out["slots"]["key_findings"]] == ["The ad raised belief in public service motives."]
    assert out["slots"]["interlocutor_claim"] == "not stated"
    assert [t["verdict"] for t in trace] == ["rewritten", "dropped", "dropped"]


def test_expand_adds_only_new_confirmed_claims():
    note = {"slots": {"scope_and_limits": [{"claim": "Old limit.", "quotes": [{"text": "Alpha beta gamma delta epsilon", "page": 1}]}]}}
    more = '[{"claim": "Old limit.", "quotes": [{"text": "Alpha beta gamma delta epsilon", "page": 1}]}, {"claim": "New limit.", "quotes": [{"text": "raised belief in public service motives", "page": 2}]}]'
    replies = {"scope_and_limits": more}
    def ask(prompt, with_paper):
        for slot, reply in replies.items():
            if f'Slot "{slot}"' in prompt:
                return reply
        return "[]" if "empty list" in prompt else "{}"
    out = harness.expand_note(ask, PAGES, note, [])
    assert [e["claim"] for e in out["slots"]["scope_and_limits"]] == ["Old limit.", "New limit."]
    assert out["slots"]["evidence"] == "not stated"


def test_complete_accepts_a_grounded_rewrite_and_rejects_a_loose_number():
    q = [{"text": "The ad raised belief in public service motives", "page": 2}]
    note = {"slots": {"key_findings": [{"claim": "The ad changed beliefs.", "quotes": q}, {"claim": "Something else.", "quotes": q}]}}
    reply = json.dumps([{"entry": 0, "claim": "The ad raised belief in public service motives among Democrats.", "quotes": [{"text": "public service motives among Democrats in the sample", "page": 2}]},
                        {"entry": 1, "claim": "Something else, by 42 points.", "quotes": []}])
    trace = []
    out = harness.complete_entries(lambda prompt, with_paper: reply if 'Slot "key_findings"' in prompt else "[]", PAGES, note, trace)
    kept = out["slots"]["key_findings"]
    assert kept[0]["claim"].startswith("The ad raised") and len(kept[0]["quotes"]) == 2
    assert kept[1]["claim"] == "Something else."
    assert [t["result"] for t in trace if t["step"] == "complete"] == ["rewritten", "rejected: number not in its quotes: 42"]
