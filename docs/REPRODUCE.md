# Reproducing the results

There are three levels. The first needs no model and no key.

## 1. Recompute every table from the saved files

Needs Python 3.11 and poppler's `pdftotext` (version 26.03 was used; `brew install poppler`).

```bash
python3 -m pytest -q tests                 # 45 tests
python3 scripts/results.py                 # every result table (also in docs/RESULTS.md)
python3 scripts/agreement.py labeling/sample1   # the judge against the human labels
```

To recompute the quote checks themselves from the raw replies:

```bash
python3 scripts/score_run.py runs/opus-5-5-text-prompt3        # any run folder
python3 scripts/check_run.py runs/opus-5-5-text-prompt3        # the six screens
python3 scripts/check_gold.py gold/pone.0360061.json           # every gold quote is in its paper
```

Each run folder holds the raw reply for each paper (`pone.<id>.json`, with the model id the
service reported, the settings sent and the token counts), the quote checks (`scores.json`)
and the matches to the gold (`agent_coverage.pone.<id>.json`, or `coverage.pone.<id>.json`
where only the agents matched the note).

## 2. Produce new replies

Install `requirements.txt`. Keys are read from the environment (`ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`); none is stored in this repository. API models are not deterministic, so
new replies will differ from the saved ones; three runs per model moved coverage by at most
four points.

| Result | Command |
|---|---|
| Claude Opus 5.5 | `python scripts/run_anthropic.py --model claude-opus-5-5 --name <folder>` |
| Claude Haiku 5.5 | `python scripts/run_anthropic.py --model claude-haiku-5-5 --name <folder>` |
| GPT-6.2 Astra | `python scripts/run_openai.py --model gpt-6.2-astra --name <folder>` |
| GPT-6.2 Sol | `python scripts/run_openai.py --model gpt-6.2-sol --name <folder>` |
| GPT-4o | `python scripts/run_openai.py --model gpt-4o --name <folder>` |
| Qwen3 4B (local, Apple silicon) | `python scripts/run_mlx.py --model mlx-community/Qwen3-4B-Instruct-2507-4bit --name <folder> --max-tokens 6000` |

Settings used, all recorded in each reply file:

| Model | Served as | Settings |
|---|---|---|
| claude-opus-5-5, claude-haiku-5-5 | same id | effort high, max 16,000 output tokens, no temperature set, no fallback model |
| gpt-6.2-astra, gpt-6.2-sol | same id | reasoning effort high, max 16,000 completion tokens |
| gpt-4o | gpt-4o-2024-08-06 | temperature 0 (it does not take a reasoning effort), max 16,000 completion tokens |
| Qwen3-4B-Instruct-2507, 4-bit, mlx | local | three runs with `--temp 0.7 --top-p 0.8 --top-k 20 --seed 1` (then 2, 3), max 6,000 tokens; one earlier run at temperature 0, the starting point of its harness rows |

Every model gets the same prompt (`grb/task.py`, prompt version 3): the paper as text with
`[page N]` markers, taken from the PDF with `pdftotext`.

Harness settings (`grb/harness.py`), each starting from a saved run:

| Setting | Command |
|---|---|
| Quotes confirmed | `python scripts/run_harness.py --provider <mlx/anthropic/openai> --model <id> --name <folder> --from-run runs/<base run>` |
| ... claims re-checked | add `--recheck 2`, with `--from-run` pointing at the quotes-confirmed folder |
| ... asked for more | add `--expand` |
| ... key findings too | add `--more-findings`, with `--from-run` pointing at the asked-for-more folder |
| Thin entries completed (off by default) | add `--complete` |

Each harness reply file also holds a `trace`: every model call and every decision the
harness made (found, page corrected, repaired, dropped, rewritten, added).

## 3. Judge new notes

A new note has to be matched to the gold before it has a coverage score. The matching in
this repository was done by Claude Opus 5.5 agents with the brief in `docs/JUDGE_BRIEF.md`,
under the rules in `docs/LABELING_PROTOCOL.md`. A person can do the same job with
`python3 scripts/show_note.py <run> <paper id>` and the gold sheet `gold/<paper id>.md`.
The file format is described in `docs/JUDGE_BRIEF.md` and checked by
`python3 scripts/score_coverage.py <paper id> <run>`.

Agreement of the judge with a human labeler is in `docs/RESULTS.md`.

## Run folders

| Folder | What it is |
|---|---|
| `<model>-text-prompt3`, `-run2`, `-run3` | The three runs of each model on the task |
| `<model>-harness-confirm` | Quotes confirmed |
| `<model>-harness-confirm-recheck2` | Quotes confirmed, claims re-checked |
| `<model>-harness-expand` | Quotes confirmed, asked for more |
| `<model>-harness-expand-findings` | Asked for more, key findings too |
| `<model>-harness-expand-complete` | Thin entries completed (tested, not adopted) |
| `qwen3-4b-harness-slots`, `-slots2`, `-recheck`, `-slots2-recheck2` | Harness variants that were tested and not adopted |
| `qwen3-4b-4bit-prompt1`, `-prompt2`, `opus-5-5-text` | Runs with earlier prompt versions, kept for the record |

In folders of the first run, `coverage.pone.<id>.json` is the assistant's earlier hand
matching, kept only for the comparison of judges; the scores use `agent_coverage`.
