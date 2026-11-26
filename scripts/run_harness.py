"""Run a local model inside the harness and save the notes it ends with.

    # quote confirmation only, on replies an earlier run already produced
    python scripts/run_harness.py --model <mlx model> --name qwen-harness-confirm --from-run runs/qwen3-4b-4bit-prompt3
    # one slot at a time, then quote confirmation
    python scripts/run_harness.py --model <mlx model> --name qwen-harness-slots
    # the same notes, with each claim re-checked against its page
    python scripts/run_harness.py --model <mlx model> --name qwen-harness-recheck --from-run runs/qwen-harness-slots --recheck

Each saved file has the final note under "raw" (so the usual scoring scripts read it) and
every model call and harness decision under "trace".
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grb import harness  # noqa: E402
from grb.extract import pdf_pages  # noqa: E402
from grb.task import PROMPT_VERSION, parse_output  # noqa: E402


class Local:
    """An mlx model that keeps what it has read: prompts sharing a beginning (the paper)
    reuse the work done on it, so asking seven questions costs one reading."""

    def __init__(self, name: str, args):
        import mlx.core as mx
        from mlx_lm import load
        if args.seed is not None:
            mx.random.seed(args.seed)
        self.model, self.tok = load(name)
        self.args = args
        self.cache, self.seen, self.calls, self.tokens_in, self.tokens_out = None, [], 0, 0, 0

    def _ids(self, content: str) -> list[int]:
        prompt = self.tok.apply_chat_template([{"role": "user", "content": content}], add_generation_prompt=True, tokenize=False)
        bos = self.tok.bos_token
        return self.tok.encode(prompt, add_special_tokens=bos is None or not prompt.startswith(bos))

    def ask(self, content: str, keep: bool, max_tokens: int) -> str:
        from mlx_lm import generate
        from mlx_lm.models.cache import can_trim_prompt_cache, make_prompt_cache, trim_prompt_cache
        from mlx_lm.sample_utils import make_logits_processors, make_sampler
        a = self.args
        how = dict(max_tokens=max_tokens, sampler=make_sampler(temp=a.temp, top_p=a.top_p, top_k=a.top_k),
                   logits_processors=make_logits_processors(repetition_penalty=a.repetition_penalty))
        ids = self._ids(content)
        self.calls += 1
        self.tokens_in += len(ids)
        if not keep:
            raw = generate(self.model, self.tok, prompt=ids, **how)
        else:
            same = 0
            limit = min(len(ids) - 1, len(self.seen))
            while same < limit and ids[same] == self.seen[same]:
                same += 1
            offsets = [c.offset for c in self.cache or [] if hasattr(c, "offset")]
            if self.cache is None or same == 0 or not offsets or not can_trim_prompt_cache(self.cache):
                self.cache, same = make_prompt_cache(self.model), 0  # some models' memory cannot be cut back; they re-read
            else:
                trim_prompt_cache(self.cache, offsets[0] - same)
            raw = generate(self.model, self.tok, prompt=ids[same:], prompt_cache=self.cache, **how)
            self.seen = ids
        self.tokens_out += len(self.tok.encode(raw))
        return raw


class Claude:
    """A Claude model through the API, with the settings of the plain runs (effort high)."""

    def __init__(self, name: str, args):
        import anthropic
        self.client, self.name, self.calls, self.tokens_in, self.tokens_out = anthropic.Anthropic(), name, 0, 0, 0

    def ask(self, content: str, keep: bool, max_tokens: int) -> str:
        self.calls += 1
        with self.client.messages.stream(model=self.name, max_tokens=max(max_tokens, 4000), output_config={"effort": "high"},
                                         messages=[{"role": "user", "content": content}]) as stream:
            msg = stream.get_final_message()
        self.tokens_in += msg.usage.input_tokens
        self.tokens_out += msg.usage.output_tokens
        return "".join(b.text for b in msg.content if b.type == "text")


class OpenAIModel:
    """An OpenAI model through the API at temperature 0, as in the plain GPT-4o run."""

    def __init__(self, name: str, args):
        from openai import OpenAI
        self.client, self.name, self.calls, self.tokens_in, self.tokens_out = OpenAI(), name, 0, 0, 0

    def ask(self, content: str, keep: bool, max_tokens: int) -> str:
        self.calls += 1
        reply = self.client.chat.completions.create(model=self.name, max_completion_tokens=max(max_tokens, 600), temperature=0,
                                                    messages=[{"role": "user", "content": content}])
        self.tokens_in += reply.usage.prompt_tokens
        self.tokens_out += reply.usage.completion_tokens
        return reply.choices[0].message.content or ""


class Endpoint:
    """Any OpenAI-compatible chat endpoint, such as a local llama.cpp or NInfer server. --body (JSON) is sent with
    every call (the model's own sampling, chat_template_kwargs, a seed), and --headers with every request. One retry
    after a failed call, then the error stops the paper."""

    def __init__(self, name: str, args):
        self.url, self.name, self.timeout = args.url, name, args.timeout
        self.settings = json.loads(args.body or "{}")
        self.headers = json.loads(args.headers or "{}")
        self.calls, self.tokens_in, self.tokens_out = 0, 0, 0

    def ask(self, content: str, keep: bool, max_tokens: int) -> str:
        import urllib.request
        self.calls += 1
        body = {"model": self.name, "messages": [{"role": "user", "content": content}], "max_tokens": max_tokens,
                "stream": False, **self.settings}
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                             headers={"Content-Type": "application/json", **self.headers})
                with urllib.request.urlopen(req, timeout=self.timeout) as r:
                    out = json.loads(r.read())
                break
            except OSError:
                if attempt == 2:
                    raise
                time.sleep(10)
        usage = out.get("usage") or {}
        self.tokens_in += usage.get("prompt_tokens") or 0
        self.tokens_out += usage.get("completion_tokens") or 0
        return out["choices"][0]["message"].get("content") or ""  # a server that splits thinking off keeps it apart


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--provider", choices=["mlx", "anthropic", "openai", "http"], default="mlx")
    ap.add_argument("--url", help="http: the chat completions URL")
    ap.add_argument("--body", help="http: JSON merged into every request (sampling, chat_template_kwargs, seed)")
    ap.add_argument("--headers", help="http: JSON of extra request headers")
    ap.add_argument("--timeout", type=float, default=1800, help="http: seconds per call")
    ap.add_argument("--name", required=True, help="folder name under runs/")
    ap.add_argument("--from-run", help="start from the notes of an earlier run instead of asking slot by slot")
    ap.add_argument("--reuse-extract", help="re-read the slot-by-slot replies saved in an earlier harness run")
    ap.add_argument("--recheck", type=int, choices=[1, 2], help="re-check each claim: 1 = four questions in one call beside the whole page; 2 = one narrow question per call beside the quote's passage")
    ap.add_argument("--expand", action="store_true", help="ask for answers the note lacks, slot by slot and for unquoted pages")
    ap.add_argument("--more-findings", action="store_true", help="ask for further key findings, beyond the task's limit of five")
    ap.add_argument("--complete", action="store_true", help="ask the model to complete thin entries (direction, comparison, size, conditions)")
    ap.add_argument("--slot-prompt", type=int, choices=[1, 2], default=1, help="wording used when asking one slot at a time")
    ap.add_argument("--papers", nargs="*")
    ap.add_argument("--temp", type=float, default=0.0, help="local models only")
    ap.add_argument("--top-p", type=float, default=1.0, help="local models only")
    ap.add_argument("--top-k", type=int, default=0, help="local models only")
    ap.add_argument("--repetition-penalty", type=float, help="local models only")
    ap.add_argument("--seed", type=int, help="local models only")
    ap.add_argument("--short-tokens", type=int, default=300, help="output allowance for calls without the paper; raise for a reasoning model")
    ap.add_argument("--long-tokens", type=int, default=2500, help="output allowance for calls with the paper")
    args = ap.parse_args()

    model = {"mlx": Local, "anthropic": Claude, "openai": OpenAIModel, "http": Endpoint}[args.provider](args.model, args)
    out_dir = ROOT / "runs" / args.name
    out_dir.mkdir(parents=True, exist_ok=True)
    papers = args.papers or sorted(p.name for p in (ROOT / "data" / "plos").iterdir() if p.is_dir())
    for pid in papers:
        pages = pdf_pages(ROOT / "data" / "plos" / pid / "paper.pdf")
        block = harness.paper_block(pages)
        ask = lambda prompt, with_paper: model.ask(block + prompt, True, args.long_tokens) if with_paper else model.ask(prompt, False, args.short_tokens)  # noqa: E731
        trace, steps, t0, calls0, in0, out0 = [], [], time.time(), model.calls, model.tokens_in, model.tokens_out
        if args.from_run:
            note, how = parse_output(json.loads((Path(args.from_run) / f"{pid}.json").read_text())["raw"])
            note = note or {"slots": {}}
            steps.append(f"notes from {Path(args.from_run).name} ({how})")
        elif args.reuse_extract:
            old = json.loads((Path(args.reuse_extract) / f"{pid}.json").read_text())["trace"]
            note = harness.extract_by_slot(ask, pages, trace, {t["slot"]: t["raw"] for t in old if t["step"] == "extract"})
            steps.append("one slot at a time")
        else:
            note = harness.extract_by_slot(ask, pages, trace, version=args.slot_prompt)
            steps.append(f"one slot at a time (prompt {args.slot_prompt})")
        note = harness.confirm_quotes(ask, pages, note, trace)
        steps.append("quotes confirmed")
        if args.expand:
            note = harness.expand_note(ask, pages, note, trace)
            steps.append("asked for more")
        if args.more_findings:
            note = harness.expand_note(ask, pages, note, trace, more_slots=("key_findings",), unread_pages=False)
            steps.append("asked for more key findings (no limit of five)")
        if args.complete:
            note = harness.complete_entries(ask, pages, note, trace)
            steps.append("thin entries completed")
        if args.recheck:
            note = (harness.recheck_claims if args.recheck == 1 else harness.recheck_claims_2)(ask, pages, note, trace)
            steps.append(f"claims re-checked (version {args.recheck})")
        count = lambda step, **kv: sum(1 for t in trace if t["step"] == step and all(t.get(k) == v for k, v in kv.items()))  # noqa: E731
        summary = {"quotes found": count("confirm", result="found"), "pages corrected": count("confirm", result="page corrected"),
                   "repairs that worked": count("repair", result="repaired"), "repair attempts": count("repair"),
                   "claims dropped, no quote": count("drop"), "claims dropped at re-check": count("recheck", verdict="dropped") + count("recheck2", verdict="dropped"),
                   "claims rewritten at re-check": count("recheck", verdict="rewritten") + count("recheck2", verdict="rewritten"),
                   "entries completed": count("complete", result="rewritten"),
                   "completions rejected": sum(1 for t in trace if t["step"] == "complete" and t["result"].startswith("rejected")),
                   "claims added": sum(t.get("added", 0) for t in trace if t["step"].startswith("more: ") and "added" in t)}
        record = {"paper_id": pid, "model": args.model, "track": "text", "prompt_version": PROMPT_VERSION, "provider": args.provider,
                  "harness": steps, "settings": getattr(model, "settings", None), "short_tokens": args.short_tokens,
                  "long_tokens": args.long_tokens, "model_calls": model.calls - calls0,
                  "input_tokens": model.tokens_in - in0, "output_tokens": model.tokens_out - out0, "seconds": round(time.time() - t0, 1),
                  "summary": summary, "raw": json.dumps(note, ensure_ascii=False), "trace": trace}
        (out_dir / f"{pid}.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
        print(pid, record["seconds"], "s", record["model_calls"], "calls", summary, flush=True)


if __name__ == "__main__":
    main()
