# Contributed local model runs

Ellian-Eorwyn evaluated six configurations on the five benchmark papers using prompt version 3. Each setup used one RTX 3090 with 24 GB of memory. The two Qwen3.8 configurations shared GPU capacity with other work, so their timings are excluded from speed and energy comparisons.

Model files, checksums, quantizations, inference engines, context sizes where recorded, and sampling settings are in `models.json` and `models.csv`. The saved replies and quote checks are in `runs/local-*/`. The tables below summarize the contributed runs before coverage judging. The judged results are in [RESULTS.md](../RESULTS.md).

| Model | Run | File and quant | Engine | Papers | Cut off | Min/paper | Out tok/s | Quotes in paper | Page right |
|---|---|---|---|---|---|---|---|---|---|
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | 1 | gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf, Unsloth Dynamic UD-Q4_K_XL | llamacpp | 5/5 | 0 | 0.3 | 76.6 | 54/67 | 49/67 |
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | 2 | gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf, Unsloth Dynamic UD-Q4_K_XL | llamacpp | 5/5 | 0 | 0.2 | 73.3 | 42/48 | 42/48 |
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | 3 | gemma-4-26B-A4B-it-qat-UD-Q4_K_XL.gguf, Unsloth Dynamic UD-Q4_K_XL | llamacpp | 5/5 | 0 | 0.2 | 71.0 | 40/47 | 36/47 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | 1 | Qwen3.6-35B-A3B-UD-Q4_K_M.gguf, Unsloth Dynamic UD-Q4_K_M | llamacpp | 5/5 | 0 | 0.4 | 82.9 | 53/95 | 48/95 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | 2 | Qwen3.6-35B-A3B-UD-Q4_K_M.gguf, Unsloth Dynamic UD-Q4_K_M | llamacpp | 5/5 | 0 | 0.4 | 88.6 | 77/104 | 74/104 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | 3 | Qwen3.6-35B-A3B-UD-Q4_K_M.gguf, Unsloth Dynamic UD-Q4_K_M | llamacpp | 5/5 | 0 | 0.4 | 89.2 | 56/102 | 55/102 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | 1 | Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf, official KQuant Q4_K_M | llamacpp | 5/5 | 0 | 0.9 | 29.7 | 57/61 | 51/61 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | 2 | Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf, official KQuant Q4_K_M | llamacpp | 5/5 | 0 | 1.0 | 30.0 | 80/89 | 74/89 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | 3 | Muse-Glimmer-30B-KQuant-17GB-Q4_K_M.gguf, official KQuant Q4_K_M | llamacpp | 5/5 | 0 | 0.7 | 38.0 | 67/70 | 64/70 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | 1 | gemma-4-31B_q4_0-it.gguf, official QAT q4_0 | llamacpp | 5/5 | 0 | 2.8 | 19.5 | 73/73 | 70/73 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | 2 | gemma-4-31B_q4_0-it.gguf, official QAT q4_0 | llamacpp | 5/5 | 0 | 3.7 | 20.0 | 67/69 | 64/69 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | 3 | gemma-4-31B_q4_0-it.gguf, official QAT q4_0 | llamacpp | 5/5 | 0 | 3.5 | 19.8 | 80/80 | 77/80 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | 1 | qwen3_8_27b-v013.ninfer, the qwen3_8_27b recipe (mixed 4/5/8-bit, ~5.6 bits per weight), as for the two fine-tunes above | ninfer | 5/5 | 0 | — | — | 123/124 | 123/124 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | 2 | qwen3_8_27b-v013.ninfer, the qwen3_8_27b recipe (mixed 4/5/8-bit, ~5.6 bits per weight), as for the two fine-tunes above | ninfer | 5/5 | 0 | — | — | 110/113 | 109/113 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | 3 | qwen3_8_27b-v013.ninfer, the qwen3_8_27b recipe (mixed 4/5/8-bit, ~5.6 bits per weight), as for the two fine-tunes above | ninfer | 5/5 | 0 | — | — | 115/117 | 113/117 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | 1 | qwen3_8_27b-v013.ninfer, the qwen3_8_27b recipe (mixed 4/5/8-bit, ~5.6 bits per weight), as for the two fine-tunes above | ninfer | 5/5 | 0 | — | — | 104/127 | 104/127 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | 2 | qwen3_8_27b-v013.ninfer, the qwen3_8_27b recipe (mixed 4/5/8-bit, ~5.6 bits per weight), as for the two fine-tunes above | ninfer | 5/5 | 0 | — | — | 108/122 | 108/122 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | 3 | qwen3_8_27b-v013.ninfer, the qwen3_8_27b recipe (mixed 4/5/8-bit, ~5.6 bits per weight), as for the two fine-tunes above | ninfer | 5/5 | 0 | — | — | 108/118 | 106/118 |

"Cut off": replies that hit the token limit or the window (`stop_reason` "length"); your parser salvages what is
complete. "Out tok/s" is output tokens over the whole request time, prefill included. "—": the GPU was shared, so the
speed is left out (and `seconds` is empty in those replies).

## With your harness

Your chain, each step from a saved run as in your `docs/REPRODUCE.md`: quotes confirmed and asked for more from the
plain run; key findings too from asked for more; claims re-checked (version 2) from quotes confirmed. Your
`scripts/run_harness.py` ran it, with one addition: a provider `http` for any OpenAI-compatible server (`--url`,
`--body` sent with every call: the model's own sampling and switches, as in its plain run; `--headers`). The diff is in
`run_harness.patch`. Output room per call: 600 short and 4,000 long for a model that answers at once, 4,000 and 8,000
for one that thinks first (8,000 and 16,000 for Turbo Fusion); each file records them (`short_tokens`,
`long_tokens`) with `settings`, `harness` (its steps), `model_calls`, tokens, `seconds`, `summary` and the full
`trace` of every call. Folders: `runs/local-<model>-harness-confirm`, `-harness-expand`, `-harness-expand-findings`,
`-harness-confirm-recheck2`.

| Model | Setting | Papers | Calls/paper | Min/paper | Claims | Quotes in paper |
|---|---|---|---|---|---|---|
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | Quotes confirmed | 5/5 | 2 | 0.1 | 58 | 62/62 |
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | Quotes confirmed, asked for more | 5/5 | 14 | 0.6 | 150 | 162/162 |
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | Asked for more, key findings too | 5/5 | 2 | 0.2 | 162 | 174/174 |
| Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off) | Quotes confirmed, claims re-checked | 5/5 | 16 | 0.1 | 52 | 56/56 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | Quotes confirmed | 5/5 | 6 | 0.1 | 53 | 72/72 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | Quotes confirmed, asked for more | 5/5 | 18 | 0.8 | 154 | 208/208 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | Asked for more, key findings too | 5/5 | 1 | 0.1 | 168 | 223/223 |
| Qwen3.6-35B-A3B UD-Q4_K_M (thinking off) | Quotes confirmed, claims re-checked | 5/5 | 14 | 0.1 | 38 | 54/54 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | Quotes confirmed | 5/5 | 1 | 0.1 | 51 | 60/60 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | Quotes confirmed, asked for more | 5/5 | 8 | 3.2 | 158 | 196/196 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | Asked for more, key findings too | 5/5 | 1 | 0.6 | 178 | 216/216 |
| Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low) | Quotes confirmed, claims re-checked | 5/5 | 13 | 0.8 | 35 | 40/40 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | Quotes confirmed | 5/5 | 0 | — | 68 | 73/73 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | Quotes confirmed, asked for more | 5/5 | 7 | 12.2 | 137 | 161/161 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | Asked for more, key findings too | 5/5 | 2 | 2.5 | 154 | 178/178 |
| Gemma 4 31B it, QAT q4_0 (thinking off) | Quotes confirmed, claims re-checked | 5/5 | 19 | 2.6 | 65 | 70/70 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | Quotes confirmed | 5/5 | 0 | — | 92 | 124/124 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | Quotes confirmed, asked for more | 5/5 | 7 | — | 208 | 297/297 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | Asked for more, key findings too | 5/5 | 1 | — | 221 | 315/315 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low | Quotes confirmed, claims re-checked | 5/5 | 24 | — | 69 | 95/95 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | Quotes confirmed | 5/5 | 3 | — | 83 | 117/117 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | Quotes confirmed, asked for more | 5/5 | 11 | — | 182 | 241/241 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | Asked for more, key findings too | 5/5 | 1 | — | 200 | 263/263 |
| Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking off | Quotes confirmed, claims re-checked | 5/5 | 22 | — | 65 | 92/92 |

## Gaps

- Gemma 4 26B-A4B it, QAT UD-Q4_K_XL (thinking off): pone.0362373 read as repaired.
- Meta Muse Glimmer 30B dense, Q4_K_M (always thinks; strength low): pone.0347327 read as repaired, pone.0360061 read as repaired.
- Qwen3.8 27B stock (NInfer, qwen3_8_27b-v013.ninfer, DFlash2), thinking low: pone.0342063 read as partial.
