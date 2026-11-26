# Expert Reading Bench

*Grounded reading notes, scored against peer review.*

I built this as part of a longer effort to make myself a reliable reading assistant and interlocutor for research. Frontier models have become very good readers. I wanted to know where they still fall short, and what it takes to make smaller models dependable at the same job.

## The task

A model reads a research paper and writes a structured note with seven parts: the question, the central claim, the evidence, the key findings, the limits, the theory, and the earlier work the paper argues with. Every claim must carry a word-for-word quote from the paper and the number of the page it is on.

## The answers

Notes are scored against answers drawn from each paper's published peer review: what reviewers said the paper shows, and what they told the authors it does not. A reviewer restating a finding is evidence that the finding is central. A reviewer objecting to a claim, and the authors withdrawing it, marks a claim a careful reader should not repeat.

I used the review chain as an interpretable chain of evidence from which we could draw good answers and get a deeper understanding of the paper.

The set is five open-access papers from PLOS ONE with their full review histories, 187 accepted answers and 47 rejected ones. A human labeler reviewed and corrected every answer.

## What is measured

| Score | What it asks | Who checks |
|---|---|---|
| Quote fidelity | Is each quote in the paper, word for word? | Code |
| Page accuracy | Is it on the page the note says? | Code |
| Coverage | How many of the accepted answers does the note state, with a real quote behind them? | Judge |
| Core findings | Does it state the results that at least two reviewers restated? | Judge |
| Flags | Does it say more than the paper does? Serious: a wrong direction, an invented claim or quote, a wrong attribution. Mild: a small overstatement. | Judge |
| Critical reading bonus | Does it point out a place where the paper contradicts itself? | Judge |
| Reading score | Coverage, discounted by the share of a note's entries that are wrong or unquotable | Computed |

The reading score is coverage multiplied by the share of a note's entries that carry no serious flag and rest on a quote that is really in the paper. A model that finds many answers and also invents quotes scores lower than its coverage alone.

The judge is an LLM (Claude Opus 5.5 agents) working from written rules, the gold answers and the paper. On a blind sample of 60 answers weighted toward hard cases, it gave the same label as the human labeler on 52 (87%, Cohen's kappa 0.79). Where the two differed, the judge was usually the stricter.

The results also cover a harness: code around the model that checks and extends a note, and never sees the gold answers. It grew in three steps, each from a failure the benchmark exposed: first rejecting any claim whose quote is not in the paper, then having the model re-check its own claims, then asking it for more, part by part. What is good about it is that each setting targets one way of falling short, and the right one takes Claude Haiku 5.5 from 37% to 69% coverage for about three cents a paper, with no serious flags. It could still use improvement: its results are single runs, claim re-checking removes correct claims from an accurate model, and two further ideas were tested and dropped. The settings and the full table are in [The harness](#the-harness).

## Results

![Reading score by model](docs/figures/reading_score.svg?v=1a1896a559f5)

Each large point is a model's mean over its runs. The small points are single papers in single runs, so the spread of a row shows how much a model varies from paper to paper. The diamond is the same model with its best harness setting.

Here are the results for all the models tested so far. Rows marked local are open-weight models on a single machine. Qwen3 4B ran on a laptop; the other six local setups were run by [Ellian-Eorwyn](https://github.com/Ellian-Eorwyn) on one RTX 3090 (24 GB) and judged here by the same judge. I will add more soon.

| Model | Runs | Reading score | Coverage | Range over runs | Core findings (of 14) | Quotes in the paper | Serious flags per run | Cost per paper |
|---|---|---|---|---|---|---|---|---|
| Claude Opus 5.5 | 3 | 77 | 78% | 76 to 79 | 12.7 | 664 of 664 | 0.7 | $0.29 |
| GPT-6.2 Astra | 3 | 75 | 75% | 73 to 76 | 13.8 | 1,064 of 1,065 | 0 | $0.42 |
| GPT-6.2 Sol | 3 | 74 | 75% | 72 to 76 | 13.8 | 1,231 of 1,234 | 0.3 | $0.14 |
| Qwen3.8 27B, thinking low (local) | 3 | 46 | 48% | 45 to 51 | 10.8 | 348 of 354 | 1.3 | not timed |
| Claude Haiku 5.5 | 3 | 37 | 38% | 37 to 40 | 10.2 | 253 of 255 | 0.7 | $0.006 |
| Gemma 4 31B (local, QAT 4-bit) | 3 | 32 | 33% | 32 to 34 | 10.0 | 220 of 222 | 2.3 | 3.3 minutes, at most $0.005 |
| Qwen3.8 27B, thinking off (local) | 3 | 30 | 39% | 38 to 40 | 9.3 | 320 of 367 | 2 | not timed |
| Muse Glimmer 30B (local, 4-bit) | 3 | 26 | 29% | 24 to 32 | 9.3 | 204 of 220 | 1 | 0.9 minutes, at most $0.001 |
| GPT-4o | 3 | 17 | 21% | 21 to 22 | 8.0 | 133 of 161 | 1 | $0.06 |
| Gemma 4 26B-A4B (local, QAT 4-bit) | 3 | 17 | 22% | 21 to 24 | 4.5 | 136 of 162 | 3 | 15 seconds, at most $0.0004 |
| Qwen3.6 35B-A3B (local, 4-bit) | 3 | 9 | 31% | 28 to 36 | 8.2 | 186 of 301 | 2.7 | 0.4 minutes, at most $0.0005 |
| Qwen3 4B (local, 4-bit) | 3 | 9 | 17% | 9 to 23 | 6.2 | 261 of 437 | 14.3 | 4.4 minutes on a laptop |

A model that fits on one 24 GB graphics card now reads better than the cheapest API model. Qwen3.8 27B with thinking on covers 48% against 38% for Claude Haiku 5.5, and quotes almost as faithfully. Turning its thinking off costs nine points of coverage and one quote in eight.

The reading score separates models that coverage puts together. Qwen3.6 35B-A3B covers 31%, close to Gemma 4 31B, but more than a third of its quotes are not in the paper, so its reading score is 9 where Gemma's is 32. GPT-4o and Qwen3 4B are four points apart on coverage and further apart on the reading score for the same reason.

Qwen3 4B is the only unstable model. Its runs are sampled, and in four of its fifteen notes it repeated one sentence pattern dozens of times in a single part and never reached the rest. That is why its range is 14 points. The contributed local setups are sampled too, and the widest of their ranges is 8 points.

The contributed runs come with what served each model (file, quantization, sha256, engine, sampling) in [docs/local-runs-2026-11-25/](docs/local-runs-2026-11-25/). Each model used the sampling recommended for it, so settings differ between rows. The two Qwen3.8 rows ran on a server that was doing other work, with its own sampling and no seed, so they are not timed and cannot be repeated exactly.

### Coverage by paper and by part of the note

![Coverage by paper and by part of the note](docs/figures/coverage_grids.svg?v=58828cea8861)

The strong models are even across papers. The parts of the note tell them apart: the GPT-6.2 models are nearly complete on evidence and limits and name few of the earlier works a paper argues with, where Claude Opus 5.5 names most of them.

### Quotes and flags

![Quotes found in the paper, and flags per run](docs/figures/quotes_and_flags.svg?v=890e265cc428)

### Cost

![Cost per paper against coverage](docs/figures/cost.svg?v=6bb353280170)

API costs use the providers' standard rates on 22 November 2026 ([docs/prices.json](docs/prices.json)), without prompt caching.

The cost of a local model is electricity only, and is not the same kind of number as an API price. It is the time the requests took on one RTX 3090, charged as if the card drew its full 420 W limit throughout, at an example rate of $0.20 per kWh. That makes it an upper bound for the card: by the contributor's account it stays under 350 W, which would lower every figure by a sixth. The rest of the machine, idle time and the price of the hardware are not counted. On those terms the full harness on Qwen3.6 35B-A3B reaches 59% coverage for a fifth of a cent a paper, and Gemma 4 31B, the slowest of the four, takes 17 minutes and two and a half cents. The two Qwen3.8 setups shared their GPU with other work, so they have no time or cost. The contributor's full table is in [docs/local-runs-2026-11-25/gpu-time.md](docs/local-runs-2026-11-25/gpu-time.md). Every table is in [docs/RESULTS.md](docs/RESULTS.md), and the figures are redrawn from the saved results by `python3 scripts/make_figures.py`.

## What we found

1. Newer models quote faithfully; older and smaller ones do not. GPT-4o invents about one quote in five, in every run. The current models almost never do.
2. The strongest models form one tier. Claude Opus 5.5 and the two GPT-6.2 models are three points apart, which is inside the variation between runs.
3. Models differ in how they fall short, not only in how far. Some misquote, some stop early, some overstate. Each needs a different fix.
4. A cheap model with the right harness lands near the expensive ones. Claude Haiku 5.5 goes from 37% to 69% coverage for about three cents a paper, and a local Qwen3.8 27B goes from 51% to 74% on one graphics card. The local models pay for it in flags, where Haiku does not.
5. No model volunteered a contradiction. The papers contain five places where they disagree with themselves, such as an abstract that claims more than the results show. The task does not ask for these, and no model pointed one out in any run.

## The harness

The benchmark showed three ways of falling short, so the harness has a setting for each. It is code around the model that checks and extends a note. It never sees the gold answers.

![Coverage and serious flags under each harness setting](docs/figures/harness.svg?v=76ed18a656cd)

| Setting | What it does | Who it is for |
|---|---|---|
| Quotes confirmed | Checks every quote against the paper, sends a failed quote back with the page text for repair, and drops a claim that ends with no real quote | Any model; it only acts when a quote is wrong |
| Claims re-checked | Shows the model each claim beside its quoted passage and asks narrow questions: is this what the passage says, is the direction right, does it name a source the passage names | Small models that make many errors |
| Asked for more | Shows the model its own list for each part and asks what else the paper states, then asks it to re-read the pages no entry quotes | Models that are accurate and stop early |

| Model | Setting | Coverage | Core findings | Serious flags | Cost per paper |
|---|---|---|---|---|---|
| Qwen3 4B | alone | 21% | 7 | 15 | 3.7 minutes |
| | quotes confirmed | 32% | 10 | 8 | about 2 minutes more |
| | plus claims re-checked | 23% | 8 | 1 | about 3 minutes more |
| GPT-4o | alone | 21% | 8 | 1 | $0.06 |
| | quotes confirmed | 24% | 9.5 | 2 | $0.06 |
| | asked for more | 38% | 10 | 3 | about $0.35 |
| Claude Haiku 5.5 | alone | 37% | 10.5 | 0 | $0.006 |
| | quotes confirmed | 37% | 10.5 | 0 | $0.006 |
| | plus claims re-checked | 31% | 7 | 0 | $0.008 |
| | asked for more | 69% | 13 | 0 | $0.035 |

The six contributed local setups, each through the same four settings. Each cell is coverage, with serious flags in brackets.

| Model (local) | Alone | Quotes confirmed | Plus claims re-checked | Asked for more |
|---|---|---|---|---|
| Qwen3.8 27B, thinking low | 51% (2) | 52% (2) | 39% (1) | 74% (4) |
| Qwen3.8 27B, thinking off | 38% (2) | 43% (2) | 33% (0) | 68% (5) |
| Qwen3.6 35B-A3B | 28% (4) | 36% (3) | 24% (2) | 59% (6) |
| Gemma 4 31B | 34% (2) | 34% (2) | 32% (2) | 53% (2) |
| Muse Glimmer 30B | 24% (2) | 25% (2) | 16% (0) | 49% (3) |
| Gemma 4 26B-A4B | 24% (2) | 28% (2) | 25% (2) | 49% (4) |

The pattern from the API models holds. Confirming quotes helps exactly the models that misquote: Qwen3.6 35B-A3B, which had 53 of 95 quotes in the paper, gains eight points. Asking for more adds 19 to 31 points for every one of them. Re-checking claims costs coverage each time. What is new is that asking for more also raises the serious flags of five of the six, by one to three, where Claude Haiku 5.5 stayed at none.

Each harness row starts from the model's first run. For Qwen3 4B that is a run at temperature 0, which scored 21% and did not loop; its three sampled runs in the table above average 17%. "Asked for more" here covers every part of the note, key findings included. The last GPT-4o cost is an estimate.

How we got here, in short. The first idea was the obvious one: reject any claim whose quote is not in the paper. That helped the small model at once, because its wrong claims were disproportionately the ones it could not find a quote for. The second idea was to have the model check its own claims. It removed nearly all of the small model's serious errors, and it removed correct claims from an accurate model, so it is a setting for models that make many errors and stays off for the rest. The third came from looking at where the mid-sized models lost points: they were rarely wrong, they just wrote a third as much as the strong models. Asking for more, part by part, recovered most of that.

Two ideas were tested and dropped. Asking a small model for one part of the note at a time produced more claims and more errors, with no gain in coverage. Asking models to complete their own thin entries was safe but changed little, because a model does not know which half of an answer it left out.

## What this does not show yet

- Five papers from one journal and one field. That is enough to separate tiers of models and too few to rank models within a tier. A single model's score on a single paper moves by up to eight points between runs.
- The harness results are single runs. The unassisted scores vary by up to four points across runs, so smaller differences should not be read into.
- The judge is a model. It agreed with a human on 87% of a hard-case sample and errs slightly strict, which lowers every model's score by a similar amount. Individual scores were not checked one by one.
- The gold answers start from what reviewers chose to comment on. That was only the baseline: a human labeler reviewed and corrected every answer. A note can be accurate and useful beyond them.
- The six contributed local setups were run on someone else's machine. The replies and model settings are saved and the quote checks reproduce here exactly, but the runs themselves were not repeated here, and the harness ran with different output allowances than for the other models.
- Costs are without prompt caching, which would lower the harness's cost, since it sends the same paper several times.

## How it was built

The six local setups on one RTX 3090 (Gemma 4, Qwen3.6, Qwen3.8 and Muse Glimmer) were run and documented by [Ellian-Eorwyn](https://github.com/Ellian-Eorwyn), who also added the harness's provider for OpenAI-compatible servers.

A human labeler reviewed every gold answer, set every scoring rule, and validated the automated judge on a blind sample. Most of the code and the first drafts of the gold answers were written with an AI assistant.

The full method, including how the review history becomes an answer key and why each score was chosen, is in [docs/METHODS.md](docs/METHODS.md). The rules, with each decision and the reason for it, are in [docs/LABELING_PROTOCOL.md](docs/LABELING_PROTOCOL.md). The brief the judge worked from is in [docs/JUDGE_BRIEF.md](docs/JUDGE_BRIEF.md). The labeling sample, the labels and the key are in [labeling/](labeling/).

## Reproduce

Every table can be recomputed from the files in this repository, with no model and no key. It needs Python 3.11 and poppler's `pdftotext`.

```bash
python3 -m pytest -q tests
python3 scripts/results.py
python3 scripts/make_figures.py
```

[docs/REPRODUCE.md](docs/REPRODUCE.md) gives the command and the settings for every model run and every harness setting, and says how to judge a new note.

## What is in the repository

| Path | Contents |
|---|---|
| `data/plos/` | The five papers (PDF and XML) and their review histories |
| `gold/` | The accepted, rejected and neutral answers for each paper, with the source of each and its quotes |
| `grb/` | The task prompt, the quote checker, the six deterministic screens and the harness |
| `scripts/` | Runners for each provider, the scorers, the result tables |
| `runs/` | Every reply, its quote checks and its matches to the gold |
| `labeling/` | The human labeling sample |
| `docs/` | The labeling protocol, the judge's brief, the reproduction guide, the result tables and the figures |

## The papers

All five are open access under CC BY 4.0, published in PLOS ONE with their peer review histories.

- Political engagement and online political hostility among American X/Twitter users. doi:10.1371/journal.pone.0360061
- Regional political climate's moderating role in the association between political conservatism and COVID-19 vaccine hesitancy in the United States. doi:10.1371/journal.pone.0342063
- Lose the label: Messaging effects on Democrats' perceptions of individuals with criminal records and representation. doi:10.1371/journal.pone.0355933
- Regional and temporal patterns of partisan polarization during the COVID-19 pandemic in the United States and Canada. doi:10.1371/journal.pone.0347327
- Beyond generalizations: Understanding adolescent social networks in American Indian communities. doi:10.1371/journal.pone.0362373

## License

The code is under the MIT License ([LICENSE](LICENSE)). The gold answers, labels, matches and result tables are under CC BY 4.0 ([LICENSE-DATA.md](LICENSE-DATA.md)). The papers and their review histories belong to their authors and reviewers and are redistributed under their CC BY 4.0 license.
