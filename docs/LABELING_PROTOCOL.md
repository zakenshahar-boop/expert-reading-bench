# Labeling protocol (draft 1)

How the gold answers for one paper are built. Written after labeling one paper
(`gold/pone.0360061.json`), so expect it to change as more papers are done.

## Principle

The gold for a slot is a **set of acceptable answers**, not one answer. The set comes
from people who read the paper for a reason other than this benchmark: its reviewers,
its editor and its authors replying to them. The labeler collects and checks. The
labeler does not decide what the paper's main points are.

## Materials

- The published PDF. It is the only authority on what the paper says.
- The published peer review history: every review round, the author responses and the
  editor's letters.

## Steps

1. Read the review history first, before the paper. For each slot, copy out every
   passage where a reviewer, the editor or the authors state what the paper asks,
   claims, uses, finds, cannot show, builds on or argues with.
2. Read the published paper. For each candidate answer, find the sentence that states
   it and record the verbatim span and its page.
3. Sort each candidate into one of three lists (rules below).
4. Add answers that the paper states plainly and no one in the review mentioned. Mark
   their origin as `paper`.
5. Run `python3 scripts/check_gold.py gold/<paper>.json`. Every span must match.

## The lists

**Acceptable.** The published paper states it, and a span shows it.

**Rejected.** Someone in the review history said the paper claims it, and the published
paper does not, or says the opposite. Each needs a counter-span from the published
paper. These are kept because they are the wrong answers a model is most likely to
give: they are what the paper nearly said.

**Neutral.** The paper says it, but too slightly to count: for example a result
mentioned only in the limitations. A model that gives it gets no credit and no penalty.

**Borderline.** The labeler cannot place it by the rules. Each carries a written
question. A second coder answers the question independently, and the rule that
settles it is added to this protocol.

## Rules

1. **The published paper wins.** Reviews describe the submitted draft. A reviewer's
   restatement is a candidate, never an answer, until a span in the published paper
   supports it. In the first paper, Reviewer 4 summarized a finding (hostile users are
   influential within their networks) that the published text explicitly disclaims.
2. **Record the origin of every answer**: which reviewer and round, which author
   response, the editor, or `paper`. The share of answers with a review origin is
   reported per slot. It measures how much of the gold rests on the labeler alone.
3. **Critique becomes limits.** An objection the authors accepted, and wrote into the
   paper, is a scope-and-limits answer. An objection they rebutted without changing
   the text is not.
4. **Claims toned down in revision become rejected answers** in the slot where the
   strong version would have gone.
5. **Key findings have two tiers.** Core: restated independently by at least two
   reviewers. Secondary: stated by one reviewer, or by the paper only. Coverage is
   scored against core findings; secondary findings are accepted and not required.
6. **Evidence has one required element**, the data source, and optional ones (sample,
   measures, models).
7. **Theoretical positioning has two parts**, framework and stance, labeled
   separately. A theory the paper cites and discusses without adopting goes in
   rejected, with the span where the authors decline it.
8. **Not stated.** A slot is `not stated` only when the labeler finds no acceptable
   answer after step 4. Then any filled answer from a model is an error.
9. **Spans.** Verbatim, one or two sentences, from the body or abstract. Not from
   figure captions, tables, references or the margin metadata. Avoid spans that cross
   a page break.
10. **Paraphrase is expected.** Answers are written in the labeler's words. A model's
    answer matches when it says the same thing as any one acceptable answer; the gold
    wording is not a target string.

## Decisions from the first paper

- A moderator with its own theory section counts as a second framework (T5).
- A self-citation can count as an interlocutor, but the first candidate (I-x1) was
  rejected on the two rules below.
- An interlocutor claim is one the paper's argument engages: it motivates the question
  or the expectations. A study cited in the limitations to illustrate a caveat is not one.
- Gold answers keep the paper's strength of claim. An association is not restated as
  influence or effect. This binds the labeler as much as the model.
- Where a paper has a main theoretical perspective, that framework is tagged `primary`
  and the others `secondary`. Naming the primary one earns extra credit (T2). Whether
  a conditional-context framework such as T5 also earns extra credit is not settled.
- A result the paper mentions only in its limitations is neutral, not a finding (F-b1).
- Numbers the paper reports separately are not joined in a gold answer. The first draft
  of E2 said the 9.25 million posts came from the 2,567 linked panelists; the paper
  never says so.

## Scoring a model's note against the gold (decided on the first paper)

- A claim that states a gold answer earns 1 point. A claim that gets the substance and
  inflates or distorts it earns 0.5 and a **risk flag**.
- Risk flags mark claims a reader should not trust as written: an association stated as
  an effect, a qualified result stated without its qualification, a wrong stance toward
  another literature. Each flag names the rejected gold answer it resembles. Flags are
  counted and reported on their own, because a note can cover everything and still
  mislead.
- An accurate statement with overclaiming wording around it (for example a correct list
  of controls said to "isolate the effects") earns nothing for the wording and one flag.

- A correct answer placed in the wrong slot earns 0.5 and no flag.
- A flag can be marked mild when the claim keeps the substance and only tilts the
  wording. The claim keeps its credit; mild flags are counted with the others and
  labeled.
- A claim earns credit only if at least one of its quotes is faithful. A correct claim
  with no quote, or only quotes that fail, is recorded as ungrounded and reported in a
  second total. (Confirmed by the labeler, 2026-11-20.)

## Answers suggested by a model

- The gold is never extended with an answer a model under test suggested, even a true
  one. Doing so tilts the gold toward that model. (Decided 2026-11-20, after two such
  answers were added and then removed.)
- Such an entry is recorded as "true but not in the gold": no credit, no penalty. The
  count is reported, since a high count means the gold is missing things.

## What the next four papers added (drafted 2026-11-21, not yet confirmed by the labeler)

- **An author response is a candidate too.** In one paper the authors told the reviewers
  the paper now states a caveat ("with only three schools we cannot statistically
  disentangle...") that the published text does not contain. Letters are checked
  against the paper exactly as reviews are.
- **A review can describe the wrong paper.** One round 2 review cites tables, sections
  and claims that are not in the manuscript, and the authors say so. Such a review
  supplies rejected answers only.
- **A rejected answer may have no counter-span.** When the paper is simply silent (a
  criticism the authors never conceded, or draft material removed in revision), the
  rejected answer carries a reason and no quote. A model that gives it is reporting
  something the paper does not say.
- **Unconceded criticism is a rejected limit.** "The authors acknowledge X" is wrong when
  only a reviewer said X. Three of the four papers have such cases.
- **A slot can be legitimately empty.** One paper names no theory at all; its draft had
  two, both removed after review. "Not stated" is marked acceptable there.

## Decisions of 2026-11-21

- **True to the paper is enough.** When a paper states a strong claim in one place and
  hedges it in another, a model that repeats the paper's own strong wording is credited
  and not flagged. A version stronger than anything in the paper stays rejected.
- **A paper with no theory.** Saying that the paper names no theoretical framework is the
  primary answer and earns extra credit. Describing the empirical literatures it sits in
  is also acceptable.
- **Rejected answers come only from the review history.** The labeler does not add
  mistakes they merely foresee. This keeps the method consistent.
- **An interlocutor is a peer.** A claim counts for slot 7 only if the paper attributes
  it to other scholars or studies. A party's strategy or a public figure's position does
  not; it is neutral.
- **A theory the paper only mentions.** One rule for all cases (social pressure, motivated
  reasoning, prospect theory): a hedged mention reported as a suggestion earns secondary
  credit; the same theory reported as the paper's framework is flagged as an unsupported
  attribution. The labeler notes that calls of this kind are subjective, which is why a
  second coder's agreement on tiers, neutral items and flags must be measured.
- **Unsupported attribution** is a flag type: saying a paper is grounded in a theory it
  only mentions. A hedged mention reported as a hedged mention is credited.
- **Gap statements keep the paper's hedge.** "Little research had examined X" is not
  "no research examined X".
- **Critical catches earn a bonus.** When a paper contradicts itself (the abstract says
  significant in both countries, the results say not significant in one), a note that
  repeats either statement is true to the paper and is credited. A note that points out
  the contradiction shows critical reading and earns a bonus. Catches are listed per
  paper under `critical_catches`, each with the two passages. They are found by the
  labeler while checking, so the list is not complete; a model can only gain from it.
  How much the bonus is worth is open.
- **A statement the paper makes without analysis behind it** (an effect "after
  controlling for other factors" with no such analysis reported) is neutral: no credit,
  no penalty.
- **An author's interpretation of a finding** earns no credit beyond the finding itself.
  Reported as a suggestion it is neutral; reported as a result it is the rejected claim.
- **Merged findings (2026-11-22).** When one gold finding only says where another's
  exception occurred, it becomes a detail of that finding and earns no second point.
- **A limitation needs its consequence.** "Cross-sectional" alone earns no credit; the
  note must say what inference the design limits.
- **Stance words are checked like claims.** A paper that tests whether a finding
  generalizes has not revised the theory it uses.

## Scoring decisions of 2026-11-22 (labeler)

- **An answer split across entries counts in full.** When no single entry states a whole
  gold answer, but two or more entries in the answer's own slot state it between them,
  the answer earns one point. The matcher lists such answers under `joined`. The strict
  figure (half a point) is still reported beside it for reference.
- **Reported statistics are detail.** "A strong negative correlation with vaccination" is a
  full answer without r = -0.77. A number is required only when it is the finding.
- **The critical reading bonus is its own count.** It is reported as catches out of the
  contradictions listed for the paper and is not part of coverage.
- **A catch means pointing the contradiction out.** Reporting the correct figure where the
  abstract says something else is an accurate answer, not a catch.
- **"Names no theory" stays the primary answer** on papers that name none.
- **Serious and mild flags are counted apart.** A flag whose type ends in "(mild)" is a
  small overstatement. Serious flags are wrong directions, invented claims or quotes,
  unsupported attributions, wrong stances and unqualified overclaims.
- **The judge.** Notes are matched to the gold by an LLM judge (Claude Opus 5.5 agents, one
  per paper) working from this protocol, the gold file and the paper. The labeler checks a
  sample; agreement is reported.

## Open questions



- Slot 7 gets little help from reviews. Reviewers name the literatures a paper argues
  with, and rarely the specific claim. Most slot 7 answers will rest on the paper.

## Known weaknesses

- One labeler so far. Origin codes reduce what the labeler decides, and do not remove it.
- Assigning an origin is itself a judgment (did the reviewer really say this?). A second
  coder should recheck origins on a subsample.
- Reviewer quality varies, and some reviews may be machine-written. An answer is never
  accepted on a reviewer's word alone (rule 1), which limits the damage.
