from grb.checks import (_expand, attribution_check, gold_overlap, location_check, number_check,
                        numbers, strength_check)
from grb.paperxml import references, sections

PAGES = ["Abstract text says hostility is positively associated with engagement among users.",
         "We scraped 9,250,180 posts. We linked 2567 panelists. Engagement may be associated "
         "with hostility [3]. Smith argued that engagement is good [1,2]. As shown before [4–6].",
         "The association was 0.306 for interest.\nReferences\n1. Smith A. 2. Jones B."]
XML = """<article><front><abstract><p>Abstract text says hostility is positively associated with
engagement among users.</p></abstract></front><body>
<sec><title>Introduction</title><p>Smith argued that engagement is good [1,2].</p></sec>
<sec><title>Theory of things</title><p>As shown before.</p></sec>
<sec><title>Materials and methods</title><p>We scraped 9,250,180 posts. We linked 2567 panelists.</p></sec>
<sec><title>Results</title><p>The association was 0.306 for interest. Engagement may be associated with hostility.</p></sec>
</body><back><ref-list>
<ref id="r1"><label>1</label><name><surname>Smith</surname></name></ref>
<ref id="r2"><label>2</label><name><surname>Jones</surname></name></ref>
<ref id="r3"><label>3</label><name><surname>Brown</surname></name></ref>
</ref-list></back><sub-article><body><sec><title>Review</title><p>x</p></sec></body></sub-article></article>"""


def note(**slots):
    return {"slots": slots}


def entry(claim, *quotes):
    return [{"claim": claim, "quotes": [{"text": q, "page": 1} for q in quotes]}]


def test_numbers_parse_scale_and_commas():
    assert numbers("about 9.25 million posts, 2,567 users, r = .59")[0] == (9250000.0, 5000.0)
    assert [v for v, _ in numbers("about 9.25 million posts, 2,567 users, r = .59")] == [9250000.0, 2567.0, 0.59]


def test_number_check_places_each_number():
    n = note(evidence=entry("About 9.25 million posts from 2,567 users, r = 0.306, and 4,000 bots.",
                            "We scraped 9,250,180 posts."))
    r = number_check(n, PAGES)
    assert (r["numbers"], r["in own quotes"], r["elsewhere in paper"], r["nowhere"]) == (4, 1, 2, 1)


def test_exact_integers_do_not_match_neighbours():
    n = note(evidence=entry("2,568 panelists", "We linked 2567 panelists."))
    assert number_check(n, PAGES)["nowhere"] == 1


def test_strength_flags_causal_word_and_dropped_hedge():
    n = note(central_claim=entry("Engagement causes hostility.", "Engagement may be associated with hostility"),
             key_findings=entry("The result is not causal.", "does not establish causal effects"),
             evidence=entry("Engagement may relate to hostility.", "Engagement may be associated with hostility"))
    r = strength_check(n)
    assert (r["entries with quotes"], r["causal word not in quote"], r["hedge dropped"]) == (3, 1, 1)


def test_sections_and_references_ignore_the_review_history():
    names = [s[0] for s in sections(XML)]
    assert names == ["abstract", "introduction", "background", "methods", "results"]
    assert references(XML) == {1: {"Smith"}, 2: {"Jones"}, 3: {"Brown"}}


def test_expand_citation_ranges():
    assert _expand("before [4–6] and [1,2]") == "before [4,5,6] and [1,2]"


def test_attribution():
    good = note(interlocutor_claim=entry("Smith said engagement is good.", "Smith argued that engagement is good"))
    bad = note(interlocutor_claim=entry("Brown said engagement is good.", "Smith argued that engagement is good"))
    assert attribution_check(good, PAGES, XML)["all named authors cited at the quote"] == 1
    assert attribution_check(bad, PAGES, XML)["none"] == 1


def test_gold_overlap():
    gold = {"slots": {"key_findings": {"acceptable": [
        {"id": "F1", "tier": "core", "spans": [{"page": 3, "text": "The association was 0.306 for interest"}]},
        {"id": "F2", "spans": [{"page": 2, "text": "We linked 2567 panelists"}]}]}}}
    n = note(central_claim=entry("c", "association was 0.306 for interest"))
    r = gold_overlap(n, PAGES, gold)
    assert (r["overlapped, same slot"], r["overlapped, any slot"], r["core findings overlapped"]) == (0, 1, 1)
    assert r["missed"] == ["F2"]


def test_location():
    n = note(question=entry("q", "hostility is positively associated with engagement"),
             key_findings=entry("f", "The association was 0.306 for interest"),
             evidence=entry("e", "this quote is not in the paper at all"))
    r = location_check(n, PAGES, XML)
    assert (r["faithful quotes"], r["abstract"], r["results"]) == (2, 1, 1)
    assert (r["first third"], r["last third"]) == (1, 1)


def test_negated_causal_word_is_not_flagged():
    n = note(scope_and_limits=entry("The study does not show that engagement causes hostility.",
                                    "should be interpreted as associational"),
             key_findings=entry("Results are not simply driven by volume.", "the main results are robust"))
    assert strength_check(n)["causal word not in quote"] == 0


def test_xml_citations_read_like_the_pdf():
    xml = '<article><body><sec><title>Results</title><p>As found [<xref rid="r1">1</xref>,<xref rid="r2">2</xref>] in <italic>vivo</italic>.</p></sec></body></article>'
    assert "as found [1,2] in vivo." in sections(xml)[0][2]
