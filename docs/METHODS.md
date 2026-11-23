# Methods

## 1. What the benchmark tests

A model reads one research paper and reports what the paper says: what it asks, what it claims, on what evidence, within what limits, and against whose earlier work. The benchmark asks two questions of that report.

- Does it find what an expert reader would find?
- Does it say only what the paper says?

The second question matters as much as the first. A reading assistant that covers everything and overstates one result in ten is not one a researcher can rely on.

## 2. The task

### The note

The model fills a note with seven parts.

| Part | What goes in it |
|---|---|
| Question | What the paper asks or argues against |
| Central claim | The main argument or finding |
| Evidence | The data, cases or method, and what they consist of |
| Key findings | The three to five most important findings |
| Scope and limits | What the authors say the paper does not show |
| Theoretical positioning | The framework the authors place the paper in, and their stance toward it |
| Interlocutor claim | A specific claim the paper attributes to other scholars and then disputes or builds on |

Every part except key findings takes as many entries as the paper supports. A part the paper does not address is answered "not stated".

The seven parts follow the questions a researcher asks of a paper before citing it. The last two are there because they are the hardest: they ask how the paper relates to other work, which a summary of the abstract does not reveal.

### Quotes

Each entry is a claim in the model's own words plus one or more quotes copied from the paper, each with its page number. A quote is 5 to 60 words. A claim with no quote counts as an error.

The quote requirement does two jobs. It lets code check part of the note with no judgment involved. And it gives a human reader a way to verify any claim in seconds, which is what makes a reading note usable in practice.

### What the model receives

The model gets the paper as text, extracted from the PDF with `pdftotext`, with each page marked `[page N]`. It gets one prompt (version 3, in `grb/task.py`) and writes the whole note in one reply. It is told to use only the paper and nothing it remembers about it. It never sees the review history.

## 3. The review history as an expert record

This is the idea the benchmark rests on.

### The problem it solves

A reading benchmark needs an answer key, and for scholarly papers the usual sources are weak.

- The abstract is the authors' own pitch. It is what a model can copy, and it sometimes claims more than the results show.
- Annotators hired for the benchmark know they are writing an answer key, and are rarely experts in the paper's field.
- Answers written by a model make the benchmark circular.

What is needed is a record left by experts who read the paper closely, for a reason of their own, and who wrote down both what it shows and what it does not.

### What a review history is

Some journals publish, beside each paper, its full peer review history: every reviewer report in every round, the authors' replies, and the editor's letters. PLOS ONE does this under the same open license as the paper.

Reviewers are specialists who read the paper to judge it. They restate its findings to show they understood it. They object to claims that go too far. The authors reply, concede some points and rebut others, and the published text changes as a result. That exchange is a record of expert reading that was made for another purpose and already exists.

### How it becomes an answer key

| In the review history | In the gold answers |
|---|---|
| A reviewer, the editor or the authors restate what the paper asks, uses, finds or builds on | A candidate accepted answer |
| Two or more reviewers independently restate the same finding | A core finding |
| A reviewer objects, and the authors write the caveat into the paper | An accepted answer under scope and limits |
| A reviewer objects, and the authors tone the claim down or remove it | A rejected answer: the strong version the paper no longer makes |
| A reviewer criticizes, and the authors never concede it | A rejected limit: "the authors acknowledge X" is false |
| A reviewer describes something the published paper does not contain | A rejected answer |

Two properties follow.

First, importance is not decided by the labeler. A finding is core because two reviewers restated it, not because the person building the benchmark thought it mattered.

Second, the wrong answers are realistic. A rejected answer is something the paper nearly said: a claim from the draft, or a reading a reviewer actually arrived at. These are the mistakes a model is most likely to make, and no one had to imagine them.

### The published paper always wins

Reviews describe the submitted draft, and reviewers make mistakes. So a restatement in a review is only a candidate. It becomes an accepted answer when a sentence in the published paper supports it, and that sentence is recorded word for word with its page. Author replies are checked the same way: in one paper the authors told reviewers they had added a caveat that the published text does not contain.

### How much of the gold it supplies

Across the five papers there are 187 accepted answers, 47 rejected and 7 neutral. Of the accepted answers, 161 (86%) trace to the review history. The rest were added by the labeler from the paper alone and are marked as such. All 47 rejected answers come from the review history; the labeler does not add mistakes they merely foresee.

| Part | Accepted answers with a review origin |
|---|---|
| Central claim | 10 of 10 |
| Evidence | 33 of 33 |
| Theoretical positioning | 20 of 21 |
| Scope and limits | 35 of 40 |
| Key findings | 29 of 38 |
| Interlocutor claim | 22 of 29 |
| Question | 12 of 16 |

Every answer carries a code for where it came from (for example `R1(1)` for reviewer 1 in round 1, `AR2` for the authors' second reply, `ED` for the editor, `paper`, `labeler`), so these shares can be recomputed.

### Relation to earlier work

Peer reviews are widely used in NLP, mostly to study or imitate reviewing.

- PeerRead [1], NLPeer [2] and Peer Review Analyze [3] are datasets of reviews for studying peer review itself. NLPeer's second version includes reviews from PLOS journals.
- ClaimCheck [4] is the closest relative. It takes reviews from OpenReview, has experts link each reviewer weakness to the paper claim it disputes, and tests models on making that link and on verifying claims.
- LimitGen [5] uses limitations written by human reviewers as a target for models that generate limitations.
- Peerify [6] builds a claim verification benchmark from NeurIPS and ICLR review data.
- A group of recent benchmarks compare model-written reviews with human ones [7, 8, 9].

All of these evaluate a model as a reviewer: can it find weaknesses, score a paper, or judge a claim. We use reviews for a different purpose: as an expert record of what a paper says and does not say, to score models as readers. Three things in our use are, as far as we know, not in that work.

1. Reviewer restatements are used as the positive answer key, not only reviewer criticisms.
2. Claims withdrawn between rounds are recovered and scored as negatives.
3. The whole record is used, including author replies and editor letters, not only first-round reports.

We are not aware of earlier work that builds a reading-comprehension answer key this way. This rests on a search of the literature that was not exhaustive.

### Where it falls short

- Reviewers comment on what they choose to. The gold reflects their attention, and an accurate entry outside it earns nothing.
- Reviews are uneven. One second-round review in our set describes tables and claims that are not in the manuscript. The rule that the published paper wins limits the damage.
- Reviews help least with the interlocutor part. Reviewers name the literatures a paper argues with and rarely the specific claim.
- Some reviews may have been written with the help of a language model. The surveys cited above report this as a growing share [7]. Our papers are recent, so we cannot rule it out, and we did not test for it.
- The method needs journals that publish review histories, which narrows the fields and venues it can cover.

## 4. Building the gold answers

### The papers

Five open-access research articles from PLOS ONE, each with its published peer review history, all under CC BY 4.0.

### Steps

1. The review history is read first, before the paper. For each part of the note, every passage is copied out where a reviewer, the editor or the authors say what the paper asks, claims, uses, finds, cannot show, builds on or argues with.
2. The published paper is read. For each candidate, the sentence that states it is found and recorded word for word with its page.
3. Each candidate is sorted into accepted, rejected or neutral.
4. Answers the paper states plainly and no reviewer mentioned are added, with origin `paper`.
5. `scripts/check_gold.py` confirms that every recorded sentence is in the paper on the page given.

An AI assistant wrote the first draft of each gold file. The labeler then reviewed every answer, corrected or removed many, and decided every case that the rules did not settle. Each decision and its reason is in `docs/LABELING_PROTOCOL.md`.

### The three lists

- Accepted: the published paper states it, and a recorded sentence shows it.
- Rejected: someone in the review history said the paper claims it, and the published paper does not, or says the opposite.
- Neutral: the paper says it, too slightly to count, for example a result mentioned only in the limitations. No credit and no penalty.

### Tiers

- Key findings are core (restated by at least two reviewers) or secondary. There are 14 core findings.
- Evidence has one required element per paper, the data source.
- Theoretical positioning marks one framework as primary. On a paper that names no theory, saying so is the primary answer.

### Rules that keep the gold honest

- Accepted answers keep the paper's strength of claim. An association is not rewritten as an effect. This binds the labeler as much as the model.
- True to the paper is enough. Where a paper states a claim strongly in one place and hedges it in another, repeating the paper's own strong wording is credited. Only a version stronger than anything in the paper is rejected.
- The gold is never extended with an answer that a model under test suggested, even a true one, because that would tilt the gold toward that model. Such entries are counted as "true but not in the gold".

### Contradictions inside a paper

While checking, the labeler found five places where a paper disagrees with itself, such as an abstract that reports a result as significant in both countries when the results section says it is not in one. These are listed per paper as critical catches. The list is not complete, and it can only add to a model's result.

## 5. What we measure and why

There are six measures and one composite. They are kept apart because they fail differently: a note can cover everything and still mislead, or be perfectly accurate and say very little.

### Quote fidelity

What: the share of quotes that occur in the paper, whole and word for word.

How: code. The complete quote must be found in the paper's text. A matching opening does not authenticate the rest. Before comparing, both sides are lowercased and stripped of what typesetting does to text: ligatures, soft hyphens, words broken across lines, typographic quotes and dashes.

Why: it is the one check that needs no judgment, and an invented quote is the most serious failure a reading tool can have, because it looks like proof.

### Page accuracy

What: the share of quotes that are on the page the note gives.

How: code.

Why: a page number is what lets a reader find the passage. It is reported separately from fidelity because a real quote on the wrong page is a small error and an invented quote is not.

### Coverage

What: the share of accepted answers the note states.

How: the judge decides, for each entry, which accepted answers it states. The points are then counted by code.

| Case | Points |
|---|---|
| An entry states the answer, in the right part of the note | 1 |
| An entry states part of the answer | 0.5 |
| An entry states the answer in the wrong part of the note | 0.5 |
| Two or more entries in the right part state the answer between them | 1 |
| The claim is right and none of its quotes is in the paper | 0 |

Matching is strict about substance and lenient about wording. A reported statistic is detail: "a strong negative correlation" is a full answer without the coefficient, unless the number is the finding.

Why: it is the main measure of whether a model reads as an expert does. Credit depends on a real quote because a claim the reader cannot check is not worth more than no claim. Split answers count in full because how a model divides its entries is a matter of format. The stricter figure, where a split answer earns half, is reported beside it.

What it does not show: an accurate entry that no reviewer mentioned earns nothing. Coverage is a floor on how much a note gets right.

### Core findings

What: how many of the 14 findings that at least two reviewers restated the note states.

Why: coverage treats all answers alike. This asks the narrower question of whether the note got the main results, as independent experts identified them. A model limited to five findings should spend them here.

### Flags

What: the number of entries that say more than the paper does, or get it wrong.

How: the judge checks each entry against the paper and the rejected answers. A flag names its type and, where there is one, the rejected answer it matches.

- Serious: a wrong direction, an invented claim or quote, an attribution the paper does not make, a wrong stance toward another literature, an overclaim without its qualification.
- Mild: the substance is right and the wording tilts it.

Why: this is the other half of the benchmark. Flags are counted on their own and never subtracted from coverage, so a reader can see how much a model finds and how much of it can be trusted as two separate facts. Serious and mild are kept apart because one wrong direction should not be hidden among, or weighed like, several small overstatements.

### Critical reading bonus

What: how many of the listed contradictions the note points out.

How: the judge credits a catch only when the entry explicitly says the paper contradicts itself. Reporting the correct figure where the abstract says otherwise is an accurate answer and not a catch.

Why: noticing that a paper disagrees with itself is what a critical reader does beyond accurate reporting. It is its own count and not part of coverage, because the task does not ask for it. Asking for it would invite models to invent contradictions.

### Reading score

What: one number per model, for the headline figure.

How: coverage multiplied by the share of a note's entries that are sound.

    reading score = coverage × (1 − (serious flags + quotes not in the paper) / entries)

Why: a single figure is needed to place models on one line, and coverage alone ranks a model that invents quotes level with one that does not. The discount is proportional, so a long accurate note is not penalized for its length.

What it does not show: it mixes two things that the other measures keep apart, and the weighting is a choice. Every component is reported beside it.

### Also reported

- "True but not in the gold": entries accurate to the paper that match no gold answer. A high count means the gold is missing things.
- Entries with no credit and no flag.
- Six deterministic screens in `grb/checks.py`, which count things a reader should look at and decide nothing.

## 6. The judge

### Who judges

Matching an entry to a gold answer is a judgment about meaning, so code cannot do it. It is done by an LLM judge: Claude Opus 5.5 agents, one per paper, each working from the gold file, the labeling protocol, the paper and a written brief (`docs/JUDGE_BRIEF.md`). The judge writes a match file for each note. Everything after that is counting.

Later agents were first shown two notes an earlier agent had matched for the same paper and told to apply the same strictness, so that notes judged at different times are comparable.

### Checked against a human

The labeler labeled a blind sample of 60 answer-and-note pairs as full, half or none, without seeing any other label. The sample was weighted toward hard cases: pairs where two earlier sets of matches disagreed, and pairs both had scored as nothing.

| | Same label as the human | Cohen's kappa |
|---|---|---|
| The judge | 52 of 60 (87%) | 0.79 |
| Hand matching by the AI assistant that built the scripts | 34 of 60 (57%) | 0.37 |

Where the judge and the human differed, the judge was stricter in 7 cases and more generous in 1. The usual miss was the judge giving nothing where the human gave half. So the judge lowers every model's coverage slightly, and by a similar amount.

The first scores in this project came from the assistant's hand matching. The sample showed that matching was too generous, and all scores were moved to the judge.

### The judge and the models it scores

The judge is Claude Opus 5.5, and two of the six models it scores are Claude models, one of them Opus 5.5 itself. A judge could favour notes written the way it writes. Three things bear on that.

- Quote fidelity and page accuracy are checked by code. The judge has no say in them.
- The results do not show a tilt. Claude Opus 5.5 leads the two GPT-6.2 models by three points of coverage, which is inside the variation between runs, and Claude Haiku 5.5 scores 38%.
- The human sample measured the judge's accuracy overall. It was not designed to compare notes from different model families, so it does not rule a tilt out.

A labeled sample balanced across model families would settle the question, and is planned.

## 7. Models and runs

| Model | Settings |
|---|---|
| Claude Opus 5.5, Claude Haiku 5.5 | Effort high, up to 16,000 output tokens |
| GPT-6.2 Astra, GPT-6.2 Sol | Reasoning effort high |
| GPT-4o (served as gpt-4o-2024-08-06) | Temperature 0 |
| Qwen3 4B Instruct, 4-bit, on a laptop with mlx-lm | Temperature 0.7, top-p 0.8, top-k 20, seeds 1 to 3, up to 6,000 output tokens |

Each model was run three times on all five papers. The reported score is the mean, and the range over runs is given. The local model's three runs use sampling with different seeds, since at temperature 0 it gives the same reply every time. One earlier run at temperature 0 is kept as the starting point for its harness results.

Three runs are there to say which differences are real. Across runs an API model's overall coverage moved by at most four points, and a single paper's by up to eight. Differences smaller than that are not interpreted. The local model moved by 14 points, because in some runs it loops on one part of the note and writes nothing else.

A reply that is not valid JSON is read part by part where possible, and marked as repaired. A model is not scored down for a formatting slip that leaves its content readable.

## 8. The harness

The harness is code around a model that checks and extends its note. It never sees the gold answers or the review history. It uses the same model throughout; no stronger model helps.

It was built from what the benchmark showed. Models fell short in three different ways, and each setting answers one.

| Failure | Setting | What it does |
|---|---|---|
| Quotes that are not in the paper | Quotes confirmed | Checks every quote, corrects a wrong page, sends a failed quote back once with the closest pages for repair, and drops a claim that ends with no real quote |
| Claims that go beyond the passage | Claims re-checked | Shows the model each claim beside its quoted passage and asks one narrow question at a time: does the passage support it, is the direction right, is the attribution in the passage, is causal wording warranted |
| Stopping early | Asked for more | Shows the model its own entries for each part and asks what else the paper states, then asks it to re-read the pages no entry quotes |

Harness notes are scored exactly as unassisted notes are, by the same judge. Harness results so far start from each model's first run and are single runs.

Two ideas were tested and not adopted: asking for one part of the note at a time, which made a small model write more claims and more errors, and asking a model to complete its own thin entries, which was safe and changed little.

## 9. Cost

Cost per paper is input and output tokens, as reported by the provider for each call, multiplied by the provider's standard rates on 22 November 2026 (`docs/prices.json`). Prompt caching is not applied. For the local model, the cost is time on a laptop. One figure, GPT-4o with the fullest harness setting, is an estimate.

Cost is reported because the practical question is often which model is good enough for the price, and because the harness trades more calls for better notes.

## 10. Limits of the method

- Five papers, one journal, neighbouring fields. Enough to separate tiers of models, too few to rank models within a tier.
- One labeler. Origin codes reduce what the labeler decides and do not remove it. Assigning an origin is itself a judgment.
- The judge is a model, checked on 60 items. Individual scores were not checked one by one.
- The gold reflects what reviewers chose to comment on.
- Some reviews may be machine-assisted.
- The list of contradictions is incomplete.
- Some models could have seen two of the papers in training. See the section below.
- Models read extracted text. Figures are not seen, and tables only as text.

## 11. Could the models have seen the papers?

The papers are new. All five were published in 2026, and three of them after the training cutoff of every model tested.

| Paper | Published |
|---|---|
| Vaccine hesitancy and regional political climate (pone.0342063) | 3 February 2026 |
| Partisan polarization during COVID-19 (pone.0347327) | 20 April 2026 |
| Lose the label (pone.0355933) | 27 August 2026 |
| Online political hostility (pone.0360061) | 11 November 2026 |
| Adolescent social networks (pone.0362373) | 17 November 2026 |

| Model | Training cutoff, as reported | Papers published before it |
|---|---|---|
| GPT-4o | October 2023 | none |
| Qwen3 4B Instruct (2507) | released July 2025 | none |
| GPT-6.2 Astra | 18 May 2026 | 2 |
| GPT-6.2 Sol | 1 June 2026 | 2 |
| Claude Opus 5.5, Claude Haiku 5.5 | June 2026 | 2 |

So the question is open only for the two earliest papers and the four newest models. On those, the scores show no advantage:

| Model | Coverage on the two earlier papers | Coverage on the three later papers |
|---|---|---|
| Claude Opus 5.5 | 80% | 76% |
| GPT-6.2 Astra | 71% | 77% |
| GPT-6.2 Sol | 71% | 76% |
| Claude Haiku 5.5 | 38% | 38% |

Two further points limit what memory could contribute. A claim earns credit only with a word-for-word quote on the right page, which a model cannot supply from a general recollection of a paper. And the part that matters most is the review history, since the answer key is built from it; PLOS ONE publishes it together with the paper, so it is no older than the paper.

What this does not cover: the GPT-6.2 cutoffs come from secondary sources and were not confirmed on OpenAI's own pages, and we did not check whether earlier preprints of the papers exist.

## References

1. Kang, Ammar, Dalvi, van Zuylen, Kohlmeier, Hovy and Schwartz. A Dataset of Peer Reviews (PeerRead): Collection, Insights and NLP Applications. NAACL 2018. https://arxiv.org/abs/1804.09635
2. Dycke, Kuznetsov and Gurevych. NLPeer: A Unified Resource for the Computational Study of Peer Review. ACL 2023. https://aclanthology.org/2023.acl-long.277/ (second version: https://tudatalib.ulb.tu-darmstadt.de/items/d4a4061b-e4e3-4b1e-a90d-d48a3d69e3c0/full)
3. Ghosal, Kumar, Bharti and Ekbal. Peer review analyze: A novel benchmark resource for computational analysis of peer reviews. PLOS ONE 17(1), 2022. https://doi.org/10.1371/journal.pone.0259238
4. Ou, Walden, Sanders, Jiang, Sun, Cheng, Jurayj, Wanner, Liang, Morgan, Han, Wang, May, Recknor, Khashabi and Van Durme. CLAIMCHECK: How Grounded are LLM Critiques of Scientific Papers? Findings of EMNLP 2025. https://aclanthology.org/2025.findings-emnlp.1185/
5. Xu, Zhao, Patwardhan, Vig and Cohan. Can LLMs Identify Critical Limitations within Scientific Research? A Systematic Evaluation on AI Research Papers (LimitGen). ACL 2025. https://aclanthology.org/2025.acl-long.1009
6. Daghighfarsoodeh, Ebrahimi, Ghorbanpour, Sadeghian, Cheraghi, Arabzadeh and Bagheri. Peerify: Benchmarking Peer-Review Claim Verification. arXiv preprint, 2026. https://arxiv.org/abs/2609.25046
7. Nguyen and Ahmadi. LLM-Based Scientific Peer Review: Methods, Benchmarks, and Reliability Challenges. arXiv preprint, 2026. https://arxiv.org/abs/2606.25057
8. Zubeldia, Bolliet, Villaescusa-Navarro, Villanueva-Domingo and Cranmer. Auditing AI peer reviewers: a benchmark on real scientific papers. NeurIPS 2026. https://arxiv.org/abs/2611.17052
9. Żurawicki, Farganus, Gaweł, Bystroński and Kajdanowicz. PRAIB: Peer Review AI Benchmark of Behaviour of LLM-Assisted Reviewing. arXiv preprint, 2026. https://arxiv.org/abs/2605.29815
