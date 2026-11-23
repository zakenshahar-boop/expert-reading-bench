"""Run a Claude model on the papers and save its raw replies.

    python scripts/run_anthropic.py --model claude-opus-5-5 --name opus-5-5-text
    python scripts/run_anthropic.py --model claude-opus-5-5 --name opus-5-5-pdf --track pdf

Credentials come from the environment (ANTHROPIC_API_KEY) or an `ant auth login` profile.
No refusal fallback is set on purpose: a benchmark reply must come from the named
model, so the served model and stop reason are recorded instead.
"""

import argparse
import base64
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
    ap.add_argument("--track", choices=["text", "pdf"], default="text")
    ap.add_argument("--effort", default="high")
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--papers", nargs="*")
    args = ap.parse_args()

    import anthropic

    client = anthropic.Anthropic()
    out_dir = ROOT / "runs" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    papers = args.papers or sorted(p.name for p in (ROOT / "data" / "plos").iterdir() if p.is_dir())
    for pid in papers:
        pdf = ROOT / "data" / "plos" / pid / "paper.pdf"
        if args.track == "text":
            content = build_prompt(pdf_pages(pdf))
        else:
            instructions = build_prompt([]).replace(
                "Pages are marked in the text as [page N].",
                "Use the page numbers of the attached PDF, counting its first page as 1.")
            content = [
                {"type": "document", "source": {
                    "type": "base64", "media_type": "application/pdf",
                    "data": base64.standard_b64encode(pdf.read_bytes()).decode()}},
                {"type": "text", "text": instructions.replace("The paper:", "The paper is the attached PDF.")},
            ]
        t0 = time.time()
        try:
            with client.messages.stream(
                model=args.model, max_tokens=args.max_tokens,
                output_config={"effort": args.effort},
                messages=[{"role": "user", "content": content}],
            ) as stream:
                msg = stream.get_final_message()
        except anthropic.RateLimitError as e:
            print(pid, "rate limited:", e.message, flush=True)
            continue
        except anthropic.APIStatusError as e:
            print(pid, "API error", e.status_code, e.message, flush=True)
            continue
        except anthropic.APIConnectionError as e:
            print(pid, "connection error:", e, flush=True)
            continue
        raw = "".join(b.text for b in msg.content if b.type == "text")
        record = {"paper_id": pid, "model": args.model, "served_model": msg.model,
                  "track": args.track, "prompt_version": PROMPT_VERSION, "effort": args.effort,
                  "max_tokens": args.max_tokens, "stop_reason": msg.stop_reason,
                  "input_tokens": msg.usage.input_tokens, "output_tokens": msg.usage.output_tokens,
                  "seconds": round(time.time() - t0, 1), "raw": raw}
        (out_dir / f"{pid}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
        print(pid, msg.model, msg.stop_reason, msg.usage.input_tokens, "in",
              msg.usage.output_tokens, "out", record["seconds"], "s", flush=True)


if __name__ == "__main__":
    main()
