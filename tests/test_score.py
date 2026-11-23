from grb.score import score_note
from grb.task import build_prompt, parse_output

PAGES = ["Hostility is positively associated with political interest among users.",
         "The findings should be interpreted as associational rather than causal."]


def note(slots):
    return {"slots": slots}


def test_faithful_and_located():
    s = score_note(note({"central_claim": [{"claim": "c", "quotes": [
        {"text": "positively associated with political interest among users", "page": 1}]}]}), PAGES)
    assert (s["quotes"], s["faithful"], s["located"]) == (1, 1, 1)


def test_wrong_page_is_faithful_but_not_located():
    s = score_note(note({"central_claim": [{"claim": "c", "quotes": [
        {"text": "positively associated with political interest among users", "page": 2}]}]}), PAGES)
    assert (s["faithful"], s["located"]) == (1, 0)


def test_altered_quote_fails_both():
    s = score_note(note({"central_claim": [{"claim": "c", "quotes": [
        {"text": "negatively associated with political interest among users", "page": 1}]}]}), PAGES)
    assert (s["faithful"], s["located"]) == (0, 0)


def test_too_short_quote_fails_even_if_present():
    s = score_note(note({"central_claim": [{"claim": "c", "quotes": [
        {"text": "political interest", "page": 1}]}]}), PAGES)
    assert (s["faithful"], s["bad_length"]) == (0, 1)


def test_not_stated_and_missing_slots():
    s = score_note(note({"question": "not stated", "evidence": [{"claim": "no quote"}]}), PAGES)
    assert s["slots_not_stated"] == 1 and s["slots_filled"] == 1
    assert s["slots_missing"] == 5 and s["entries_without_quote"] == 1


def test_unparsed_reply():
    assert parse_output("sorry, I cannot") == (None, "unreadable")
    assert score_note(None, PAGES)["slots_missing"] == 7


def test_parse_strips_fences_and_thinking():
    raw = '<think>hmm {"x": 1}</think>```json\n{"slots": {"question": "not stated"}}\n```'
    assert parse_output(raw) == ({"slots": {"question": "not stated"}}, "complete")


def test_cut_off_reply_keeps_complete_entries():
    raw = ('{"slots": {"question": [{"claim": "a", "quotes": [{"text": "one } two", "page": 1}]}, '
           '{"claim": "b", "quotes": [{"text": "unfinished quo')
    note, how = parse_output(raw)
    assert how == "partial"
    assert note["slots"]["question"][0]["quotes"][0]["text"] == "one } two"


def test_bare_string_quote_is_scored_without_a_page():
    s = score_note(note({"central_claim": [{"claim": "c", "quotes": [
        "positively associated with political interest among users"]}]}), PAGES)
    assert (s["quotes"], s["faithful"], s["located"]) == (1, 1, 0)


def test_prompt_marks_pages():
    p = build_prompt(PAGES)
    assert "[page 1]" in p and "[page 2]" in p and "interlocutor_claim" in p


def test_reply_with_a_stray_brace_is_read_slot_by_slot():
    from grb.task import parse_output
    raw = '{"slots": {"question": [{"claim": "a", "quotes": [{"text": "q", "page": 1}}], "central_claim": [{"claim": "b", "quotes": []}]}}'
    note, how = parse_output(raw)
    assert how == "repaired"
    assert note["slots"]["question"][0]["claim"] == "a"
    assert note["slots"]["central_claim"][0]["claim"] == "b"


def test_reasoning_before_the_note_is_ignored():
    from grb.task import parse_output
    note = '{"slots": {"question": [{"claim": "a", "quotes": []}]}}'
    for raw in ("<think>plan {not json}</think>" + note, "plan {not json}</think>\n" + note):
        got, how = parse_output(raw)
        assert how == "complete" and got["slots"]["question"][0]["claim"] == "a"
