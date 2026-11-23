"""Run a local MLX model on the text track and save its raw replies.

Needs mlx-lm. Run with an interpreter that has it, for example:

    ../fine_tune_train_model/.venv/bin/python scripts/run_mlx.py \
        --model mlx-community/Qwen3-4B-Instruct-2507-4bit --name qwen3-4b-4bit
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb.extract import pdf_pages  # noqa: E402
from grb.task import PROMPT_VERSION, build_prompt  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--name", required=True, help="folder name under runs/")
    ap.add_argument("--max-tokens", type=int, default=3000)
    ap.add_argument("--papers", nargs="*", help="paper ids; default is all of data/plos")
    ap.add_argument("--temp", type=float, default=0.0, help="0 is deterministic; above 0 samples")
    ap.add_argument("--top-p", type=float, default=1.0)
    ap.add_argument("--top-k", type=int, default=0)
    ap.add_argument("--seed", type=int, help="random seed for a sampled run")
    ap.add_argument("--repetition-penalty", type=float, help="as recommended by some model cards; none by default")
    args = ap.parse_args()

    from mlx_lm import generate, load
    from mlx_lm.sample_utils import make_logits_processors, make_sampler

    import mlx.core as mx
    if args.seed is not None:
        mx.random.seed(args.seed)
    model, tokenizer = load(args.model)
    out_dir = ROOT / "runs" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    papers = args.papers or sorted(p.name for p in (ROOT / "data" / "plos").iterdir() if p.is_dir())
    for pid in papers:
        pages = pdf_pages(ROOT / "data" / "plos" / pid / "paper.pdf")
        prompt = tokenizer.apply_chat_template(
            [{"role": "user", "content": build_prompt(pages)}],
            add_generation_prompt=True, tokenize=False)
        n_prompt = len(tokenizer.encode(prompt))
        t0 = time.time()
        raw = generate(model, tokenizer, prompt=prompt, max_tokens=args.max_tokens,
                       sampler=make_sampler(temp=args.temp, top_p=args.top_p, top_k=args.top_k),
                       logits_processors=make_logits_processors(repetition_penalty=args.repetition_penalty))
        record = {"paper_id": pid, "model": args.model, "track": "text", "prompt_version": PROMPT_VERSION, "temperature": args.temp,
                  "top_p": args.top_p, "top_k": args.top_k, "seed": args.seed,
                  "repetition_penalty": args.repetition_penalty,
                  "max_tokens": args.max_tokens, "prompt_tokens": n_prompt,
                  "seconds": round(time.time() - t0, 1), "raw": raw}
        (out_dir / f"{pid}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
        print(pid, n_prompt, "prompt tokens,", record["seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
