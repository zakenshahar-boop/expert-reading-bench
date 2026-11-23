"""Run an OpenAI model on the papers and save its raw replies.

    python scripts/run_openai.py --model gpt-4o --name gpt-4o-text-prompt3

Credentials come from the environment (OPENAI_API_KEY). Reasoning models are asked for
high effort; a model that does not take that setting is run at temperature 0. What was
actually sent is recorded with each reply.
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
    ap.add_argument("--effort", default="high")
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--papers", nargs="*")
    args = ap.parse_args()

    from openai import BadRequestError, OpenAI

    client = OpenAI()
    out_dir = ROOT / "runs" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    papers = args.papers or sorted(p.name for p in (ROOT / "data" / "plos").iterdir() if p.is_dir())
    settings = [{"reasoning_effort": args.effort}, {"temperature": 0}, {}]
    for pid in papers:
        content = build_prompt(pdf_pages(ROOT / "data" / "plos" / pid / "paper.pdf"))
        t0 = time.time()
        reply, used, error = None, None, None
        for extra in list(settings):
            try:
                reply = client.chat.completions.create(
                    model=args.model, max_completion_tokens=args.max_tokens,
                    messages=[{"role": "user", "content": content}], **extra)
                used = extra
                break
            except BadRequestError as e:
                error = str(e)[:300]
                settings.remove(extra)  # this model does not take the setting; do not try it again
        if reply is None:
            print(pid, "FAILED", error, flush=True)
            continue
        choice = reply.choices[0]
        record = {"paper_id": pid, "model": args.model, "served_model": reply.model, "track": "text",
                  "prompt_version": PROMPT_VERSION, "settings": used, "max_tokens": args.max_tokens,
                  "stop_reason": choice.finish_reason, "prompt_tokens": reply.usage.prompt_tokens,
                  "output_tokens": reply.usage.completion_tokens, "seconds": round(time.time() - t0, 1),
                  "raw": choice.message.content or ""}
        (out_dir / f"{pid}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
        print(pid, reply.model, choice.finish_reason, used, record["prompt_tokens"], "in", record["output_tokens"], "out", record["seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
