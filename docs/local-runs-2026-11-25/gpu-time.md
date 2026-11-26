# GPU time and cost per paper, local models

The tables summarize the contributed runs. The final table lists the source folders for each row.

Counted like `scripts/costs.py`: per paper, from the token counts and seconds saved with each reply, and a harness result costs every step it needs (the plain run, then expand, then findings). The harness rows build on run 1; the rows for the model alone are the mean of three runs. Each local model ran on one NVIDIA RTX 3090 (24 GB), one request at a time. Minutes are the time those requests took. Loading a model (20 to 85 s) is not counted.

Dollars are electricity, not a price list: the GPU at its 420 W power limit for the whole time (an upper bound: it draws less while writing, and the rest of the machine is not counted), at $0.20 per kWh, an example rate. Scale by your own rate. Your API rows, for comparison: Claude Haiku 5.5 $0.006 a paper alone and $0.035 with the harness; your Qwen3 4B ran 4.4 minutes a paper on a laptop.

| Model | Setting | Runs | Minutes per paper | Tokens in / out per paper | Calls | Energy per paper | Cost per paper |
|---|---|---|---|---|---|---|---|
| Gemma 4 26B-A4B | Model alone | 3 | 0.2 | 20,554 / 1,128 | 1 | ≤ 2 Wh | ≤ $0.0004 |
|  | Quotes confirmed | 1 | 0.3 | 25,320 / 1,484 | 3.4 | ≤ 2 Wh | ≤ $0.0005 |
|  | Quotes confirmed, asked for more | 1 | 0.9 | 160,343 / 3,971 | 15.4 | ≤ 6 Wh | ≤ $0.0013 |
|  | Asked for more, key findings too | 1 | 1.1 | 182,555 / 4,309 | 17.4 | ≤ 8 Wh | ≤ $0.0015 |
|  | Quotes confirmed, claims re-checked | 1 | 0.4 | 32,525 / 1,540 | 19.4 | ≤ 3 Wh | ≤ $0.0006 |
| Qwen3.6 35B-A3B | Model alone | 3 | 0.4 | 20,720 / 1,973 | 1 | ≤ 3 Wh | ≤ $0.0005 |
|  | Quotes confirmed | 1 | 0.5 | 32,134 / 2,196 | 6.8 | ≤ 3 Wh | ≤ $0.0007 |
|  | Quotes confirmed, asked for more | 1 | 1.2 | 168,946 / 5,526 | 18.6 | ≤ 8 Wh | ≤ $0.0016 |
|  | Asked for more, key findings too | 1 | 1.3 | 189,695 / 5,805 | 19.6 | ≤ 9 Wh | ≤ $0.0018 |
|  | Quotes confirmed, claims re-checked | 1 | 0.6 | 39,489 / 2,231 | 21 | ≤ 4 Wh | ≤ $0.0008 |
| Muse Glimmer 30B | Model alone | 3 | 0.9 | 18,315 / 1,701 | 1 | ≤ 6 Wh | ≤ $0.0012 |
|  | Quotes confirmed | 1 | 1.1 | 19,053 / 1,948 | 1.6 | ≤ 7 Wh | ≤ $0.0015 |
|  | Quotes confirmed, asked for more | 1 | 4.2 | 131,757 / 8,487 | 9.2 | ≤ 29 Wh | ≤ $0.0058 |
|  | Asked for more, key findings too | 1 | 4.7 | 150,472 / 9,462 | 10.4 | ≤ 33 Wh | ≤ $0.0066 |
|  | Quotes confirmed, claims re-checked | 1 | 1.8 | 25,512 / 3,810 | 14.6 | ≤ 13 Wh | ≤ $0.0026 |
| Gemma 4 31B | Model alone | 3 | 3.3 | 20,557 / 3,933 | 1 | ≤ 23 Wh | ≤ $0.0046 |
|  | Quotes confirmed | 1 | 2.8 | 20,557 / 3,249 | 1 | ≤ 19 Wh | ≤ $0.0039 |
|  | Quotes confirmed, asked for more | 1 | 15.0 | 145,133 / 18,609 | 7.8 | ≤ 105 Wh | ≤ $0.021 |
|  | Asked for more, key findings too | 1 | 17.5 | 166,654 / 21,646 | 9.4 | ≤ 122 Wh | ≤ $0.025 |
|  | Quotes confirmed, claims re-checked | 1 | 5.4 | 28,470 / 8,955 | 20 | ≤ 38 Wh | ≤ $0.0076 |
| Qwen3.8 27B, thinking on | Model alone | 3 | shared GPU | 20,748 / 7,758 | 1 | — | — |
|  | Quotes confirmed | 1 | shared GPU | 21,035 / 8,430 | 1.2 | — | — |
|  | Quotes confirmed, asked for more | 1 | shared GPU | 147,317 / 26,261 | 8.2 | — | — |
|  | Asked for more, key findings too | 1 | shared GPU | 168,585 / 28,804 | 9.4 | — | — |
|  | Quotes confirmed, claims re-checked | 1 | shared GPU | 34,780 / 15,893 | 24.8 | — | — |
| Qwen3.8 27B, thinking off | Model alone | 3 | shared GPU | 20,720 / 2,225 | 1 | — | — |
|  | Quotes confirmed | 1 | shared GPU | 26,457 / 2,503 | 4 | — | — |
|  | Quotes confirmed, asked for more | 1 | shared GPU | 154,942 / 4,954 | 12 | — | — |
|  | Asked for more, key findings too | 1 | shared GPU | 176,780 / 5,379 | 13.4 | — | — |
|  | Quotes confirmed, claims re-checked | 1 | shared GPU | 38,179 / 2,568 | 26.2 | — | — |

## The whole run

Three plain runs and the four harness settings, five papers each.

| Model | Run folders | GPU time | Energy |
|---|---|---|---|
| Gemma 4 26B-A4B | 7 | 8 min | ≤ 0.06 kWh |
| Qwen3.6 35B-A3B | 7 | 11 min | ≤ 0.08 kWh |
| Muse Glimmer 30B | 7 | 37 min | ≤ 0.26 kWh |
| Gemma 4 31B | 7 | 136 min | ≤ 0.95 kWh |
| Qwen3.8 27B, thinking on | 7 | shared GPU | — |
| Qwen3.8 27B, thinking off | 7 | shared GPU | — |

The 4 models with a GPU to themselves: 3.2 GPU hours, at most 1.35 kWh (≤ $0.27 at the example rate).

Qwen3.8 shared GPU capacity with other work. Its token counts are reported, and its timings are excluded from speed and energy comparisons.

## Where each row comes from

Folders under `runs/` in the packet. A harness row adds up its folders, as `scripts/costs.py` `per_paper` does; a row for the model alone is the mean of its three runs.

| Model | Setting | Run folders |
|---|---|---|
| Gemma 4 26B-A4B | Model alone | `local-gemma4-26b-a4b-judge-text-prompt3`, `local-gemma4-26b-a4b-judge-text-prompt3-run2`, `local-gemma4-26b-a4b-judge-text-prompt3-run3` |
|  | Quotes confirmed | `local-gemma4-26b-a4b-judge-text-prompt3`, `local-gemma4-26b-a4b-judge-harness-confirm` |
|  | Quotes confirmed, asked for more | `local-gemma4-26b-a4b-judge-text-prompt3`, `local-gemma4-26b-a4b-judge-harness-expand` |
|  | Asked for more, key findings too | `local-gemma4-26b-a4b-judge-text-prompt3`, `local-gemma4-26b-a4b-judge-harness-expand`, `local-gemma4-26b-a4b-judge-harness-expand-findings` |
|  | Quotes confirmed, claims re-checked | `local-gemma4-26b-a4b-judge-text-prompt3`, `local-gemma4-26b-a4b-judge-harness-confirm`, `local-gemma4-26b-a4b-judge-harness-confirm-recheck2` |
| Qwen3.6 35B-A3B | Model alone | `local-qwen3.6-35b-a3b-q4km-text-prompt3`, `local-qwen3.6-35b-a3b-q4km-text-prompt3-run2`, `local-qwen3.6-35b-a3b-q4km-text-prompt3-run3` |
|  | Quotes confirmed | `local-qwen3.6-35b-a3b-q4km-text-prompt3`, `local-qwen3.6-35b-a3b-q4km-harness-confirm` |
|  | Quotes confirmed, asked for more | `local-qwen3.6-35b-a3b-q4km-text-prompt3`, `local-qwen3.6-35b-a3b-q4km-harness-expand` |
|  | Asked for more, key findings too | `local-qwen3.6-35b-a3b-q4km-text-prompt3`, `local-qwen3.6-35b-a3b-q4km-harness-expand`, `local-qwen3.6-35b-a3b-q4km-harness-expand-findings` |
|  | Quotes confirmed, claims re-checked | `local-qwen3.6-35b-a3b-q4km-text-prompt3`, `local-qwen3.6-35b-a3b-q4km-harness-confirm`, `local-qwen3.6-35b-a3b-q4km-harness-confirm-recheck2` |
| Muse Glimmer 30B | Model alone | `local-muse-glimmer-30b-q4km-text-prompt3`, `local-muse-glimmer-30b-q4km-text-prompt3-run2`, `local-muse-glimmer-30b-q4km-text-prompt3-run3` |
|  | Quotes confirmed | `local-muse-glimmer-30b-q4km-text-prompt3`, `local-muse-glimmer-30b-q4km-harness-confirm` |
|  | Quotes confirmed, asked for more | `local-muse-glimmer-30b-q4km-text-prompt3`, `local-muse-glimmer-30b-q4km-harness-expand` |
|  | Asked for more, key findings too | `local-muse-glimmer-30b-q4km-text-prompt3`, `local-muse-glimmer-30b-q4km-harness-expand`, `local-muse-glimmer-30b-q4km-harness-expand-findings` |
|  | Quotes confirmed, claims re-checked | `local-muse-glimmer-30b-q4km-text-prompt3`, `local-muse-glimmer-30b-q4km-harness-confirm`, `local-muse-glimmer-30b-q4km-harness-confirm-recheck2` |
| Gemma 4 31B | Model alone | `local-gemma4-31b-qat-q4_0-text-prompt3`, `local-gemma4-31b-qat-q4_0-text-prompt3-run2`, `local-gemma4-31b-qat-q4_0-text-prompt3-run3` |
|  | Quotes confirmed | `local-gemma4-31b-qat-q4_0-text-prompt3`, `local-gemma4-31b-qat-q4_0-harness-confirm` |
|  | Quotes confirmed, asked for more | `local-gemma4-31b-qat-q4_0-text-prompt3`, `local-gemma4-31b-qat-q4_0-harness-expand` |
|  | Asked for more, key findings too | `local-gemma4-31b-qat-q4_0-text-prompt3`, `local-gemma4-31b-qat-q4_0-harness-expand`, `local-gemma4-31b-qat-q4_0-harness-expand-findings` |
|  | Quotes confirmed, claims re-checked | `local-gemma4-31b-qat-q4_0-text-prompt3`, `local-gemma4-31b-qat-q4_0-harness-confirm`, `local-gemma4-31b-qat-q4_0-harness-confirm-recheck2` |
| Qwen3.8 27B, thinking on | Model alone | `local-qwen3.8-27b-default-text-prompt3`, `local-qwen3.8-27b-default-text-prompt3-run2`, `local-qwen3.8-27b-default-text-prompt3-run3` |
|  | Quotes confirmed | `local-qwen3.8-27b-default-text-prompt3`, `local-qwen3.8-27b-default-harness-confirm` |
|  | Quotes confirmed, asked for more | `local-qwen3.8-27b-default-text-prompt3`, `local-qwen3.8-27b-default-harness-expand` |
|  | Asked for more, key findings too | `local-qwen3.8-27b-default-text-prompt3`, `local-qwen3.8-27b-default-harness-expand`, `local-qwen3.8-27b-default-harness-expand-findings` |
|  | Quotes confirmed, claims re-checked | `local-qwen3.8-27b-default-text-prompt3`, `local-qwen3.8-27b-default-harness-confirm`, `local-qwen3.8-27b-default-harness-confirm-recheck2` |
| Qwen3.8 27B, thinking off | Model alone | `local-qwen3.8-27b-default-nothink-text-prompt3`, `local-qwen3.8-27b-default-nothink-text-prompt3-run2`, `local-qwen3.8-27b-default-nothink-text-prompt3-run3` |
|  | Quotes confirmed | `local-qwen3.8-27b-default-nothink-text-prompt3`, `local-qwen3.8-27b-default-nothink-harness-confirm` |
|  | Quotes confirmed, asked for more | `local-qwen3.8-27b-default-nothink-text-prompt3`, `local-qwen3.8-27b-default-nothink-harness-expand` |
|  | Asked for more, key findings too | `local-qwen3.8-27b-default-nothink-text-prompt3`, `local-qwen3.8-27b-default-nothink-harness-expand`, `local-qwen3.8-27b-default-nothink-harness-expand-findings` |
|  | Quotes confirmed, claims re-checked | `local-qwen3.8-27b-default-nothink-text-prompt3`, `local-qwen3.8-27b-default-nothink-harness-confirm`, `local-qwen3.8-27b-default-nothink-harness-confirm-recheck2` |
