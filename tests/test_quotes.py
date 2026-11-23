from grb.extract import strip_running_lines
from grb.quotes import locate_quote, normalize_text, token_score, verify_quote

PAGES = [
    "The transformer architecture relies on self-attention.",
    "It scales quadratically with sequence length, a known limitation.",
    "We propose a linear-attention variant.",
]


# --- ported from PDF IDE test/grounding.test.ts ---

def test_normalize_collapses_whitespace_and_lowercases():
    assert normalize_text("  The   QUICK\nBrown  ") == "the quick brown"


def test_locates_a_quote_on_one_page():
    assert locate_quote(PAGES, "self-attention") == [[1]]


def test_case_and_whitespace_insensitive():
    assert locate_quote(PAGES, "  SELF-ATTENTION  ") == [[1]]


def test_spans_the_pages_a_quote_crosses():
    assert locate_quote(PAGES, "a known limitation. We propose") == [[2, 3]]


def test_absent_quote():
    assert locate_quote(PAGES, "quantum entanglement") == []


def test_too_short_quote():
    assert locate_quote(PAGES, "ab") == []


def test_rejects_an_invented_conclusion_after_a_real_opening():
    pages = ["Self-attention lets the model weigh all positions in the sequence when "
             "encoding each token, which is powerful but expensive."]
    drifted = ("Self-attention lets the model weigh all positions in the sequence when "
               "encoding each token, which is powerful but cheap.")
    assert locate_quote(pages, drifted) == []


def test_token_score():
    assert token_score("linear attention variant", "We propose a linear-attention variant.") == 3
    assert token_score("a to in", "a to in anything") == 0
    assert token_score("TRANSFORMER", "the transformer architecture") == 1
    assert token_score("quantum", "classical mechanics") == 0


def test_verify_requires_the_whole_quote_on_the_stated_page():
    assert verify_quote(PAGES, "a known limitation. We propose", 2)
    assert verify_quote(PAGES, "a known limitation. We propose", 3)
    assert not verify_quote(PAGES, "self-attention", 2)
    assert not verify_quote(PAGES, "We propose a linear-attention variant that cures cancer.", 3)


def test_verify_rejects_invalid_pages():
    for page in [0, -1, 0.5, 999, None, "1", True]:
        assert not verify_quote(PAGES, "self-attention", page)


# --- PDF typesetting ---

def test_word_broken_across_lines():
    pages = ["such engagement may also be associ-\nated with more polarized behavior"]
    assert locate_quote(pages, "may also be associated with more polarized") == [[1]]


def test_real_hyphen_at_a_line_break():
    pages = ["a deprivation or personality-\nbased explanation"]
    assert locate_quote(pages, "personality-based explanation") == [[1]]


def test_soft_hyphen_and_zero_width_characters():
    pages = ["cross-­sectional and panel analyses at Aarhus, ‌‌Denmark"]
    assert locate_quote(pages, "cross-sectional and panel analyses at Aarhus, Denmark") == [[1]]


def test_ligatures_quotes_and_dashes():
    pages = ["the “political hate” vector; a Benjamini–Hochberg correction; eﬃcacy; user’s"]
    assert locate_quote(pages, '"political hate" vector') == [[1]]
    assert locate_quote(pages, "Benjamini-Hochberg correction") == [[1]]
    assert locate_quote(pages, "efficacy; user's") == [[1]]


def test_every_occurrence_is_reported():
    pages = ["hostility is associated with engagement", "nothing", "hostility is associated with engagement"]
    assert locate_quote(pages, "associated with engagement") == [[1], [3]]
    assert verify_quote(pages, "associated with engagement", 3)
    assert not verify_quote(pages, "associated with engagement", 2)


def test_changed_number_fails():
    pages = ["from around 420 to around 900"]
    assert locate_quote(pages, "from around 420 to around 950") == []


def test_running_footer_removed_so_cross_page_quotes_match():
    pages = [f"body text of page {w} ends here\nJournal | doi.org/x  {i} / 4"
             for i, w in enumerate(["one", "two", "three", "four"], start=1)]
    cleaned = strip_running_lines(pages)
    assert all("Journal" not in p for p in cleaned)
    assert locate_quote(cleaned, "page one ends here body text of page two") == [[1, 2]]
