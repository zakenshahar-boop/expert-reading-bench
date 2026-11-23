"""Draw the figures of the README into docs/figures/ from the saved results.

    python3 scripts/make_figures.py

The reading score is coverage discounted by the share of a note's entries that carry a
serious flag or rest on a quote that is not in the paper:
    reading score = coverage x (1 - (serious flags + quotes not in the paper) / entries)
"""

import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_dashboard_data import HARNESS, MODELS, PAPERS, SLOTS, frac, matches  # noqa: E402
from costs import per_paper as cost_per_paper  # noqa: E402
from score_coverage import score  # noqa: E402

OUT = ROOT / "docs" / "figures"
BLUE, LIGHT, INK, GRID, DARK, RED, AMBER = "#3b6fb6", "#9db8dc", "#5b6470", "#d5d9df", "#16202e", "#b4442f", "#c98a1b"
FONT = 'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif" font-size="13"'
ORDER = ["Claude Opus 5.5", "GPT-6.2 Astra", "GPT-6.2 Sol", "Claude Haiku 5.5", "GPT-4o", "Qwen3 4B (local)"]


def cells(run: str) -> list[dict]:
    """One record per paper of a run."""
    fid = json.loads((ROOT / "runs" / run / "scores.json").read_text())
    out = []
    for pid, pname in PAPERS:
        s = score(json.loads((ROOT / "gold" / f"pone.{pid}.json").read_text()), matches(run, pid))
        q = fid["pone." + pid]
        pts, n = frac(s["acceptable answers, points"])
        bad = q["quotes"] - q["faithful"]
        entries = max(q["entries"], 1)
        trust = max(0.0, 1 - (int(s["serious flags"]) + bad) / entries)
        out.append(dict(paper=pname, points=pts, answers=n, coverage=100 * pts / n, serious=int(s["serious flags"]), mild=int(s["mild flags"]),
                        quotes=q["quotes"], faithful=q["faithful"], entries=q["entries"], trust=trust, reading=100 * pts / n * trust,
                        slots={sid: frac(s["  " + sid]) for sid, _ in SLOTS}))
    return out


def total(cs: list[dict]) -> dict:
    pts, n = sum(c["points"] for c in cs), sum(c["answers"] for c in cs)
    entries = max(sum(c["entries"] for c in cs), 1)
    bad = sum(c["quotes"] - c["faithful"] for c in cs)
    serious = sum(c["serious"] for c in cs)
    trust = max(0.0, 1 - (serious + bad) / entries)
    return dict(coverage=100 * pts / n, serious=serious, mild=sum(c["mild"] for c in cs), bad=bad, quotes=sum(c["quotes"] for c in cs),
                faithful=sum(c["faithful"] for c in cs), entries=entries, trust=trust, reading=100 * pts / n * trust)


def svg(name: str, width: int, height: int, body: list[str], label: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" {FONT} role="img" aria-label="{label}">'
    (OUT / name).write_text("\n".join([head, f'<rect width="{width}" height="{height}" fill="#ffffff"/>'] + body + ["</svg>"]) + "\n")


def text(x, y, s, anchor="start", fill=INK, size=None, weight=None) -> str:
    extra = (f' font-size="{size}"' if size else "") + (f' font-weight="{weight}"' if weight else "")
    return f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{fill}"{extra}>{s}</text>'


def axis(x, top, bottom, ticks=(0, 25, 50, 75, 100), suffix="") -> list[str]:
    out = []
    for v in ticks:
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="{top}" y2="{bottom}" stroke="{GRID}"/>')
        out.append(text(x(v), top - 8, f"{v}{suffix}", "middle"))
    return out


def main() -> None:
    data = {name: [cells(r) for r in runs] for _, name, runs in MODELS}
    tot = {name: [total(cs) for cs in runs] for name, runs in data.items()}
    mean = lambda name, k: statistics.mean(t[k] for t in tot[name])  # noqa: E731
    harness = {}
    for name, setting, run in HARNESS:
        harness.setdefault(name, []).append((setting, total(cells(run)), run))

    # 1. Headline: the reading score, each model a point among its paper-by-paper scores
    W, left, right, top, row = 820, 170, 40, 56, 46
    x = lambda v: left + (W - left - right) * v / 100  # noqa: E731
    H = top + len(ORDER) * row + 64
    b = [text(left, 22, "Reading score: coverage, discounted for wrong or unquotable entries", fill=DARK, size=15, weight=600)]
    b += axis(x, top, top + len(ORDER) * row)
    for i, name in enumerate(ORDER):
        y = top + i * row + row / 2
        b.append(text(left - 12, y + 4.5, name, "end", DARK))
        pts = [c["reading"] for cs in data[name] for c in cs]
        for k, v in enumerate(sorted(pts)):
            b.append(f'<circle cx="{x(v):.1f}" cy="{y + ((k % 5) - 2) * 3.2:.1f}" r="3.4" fill="{BLUE}" fill-opacity="0.28"/>')
        best = max((h for h in harness.get(name, []) if h[0] != "Model alone"), key=lambda h: h[1]["reading"], default=None)
        m = mean(name, "reading")
        if best and best[1]["reading"] > m + 1:
            hx = x(best[1]["reading"])
            b.append(f'<line x1="{x(m):.1f}" x2="{hx - 9:.1f}" y1="{y:.1f}" y2="{y:.1f}" stroke="{INK}" stroke-dasharray="3 3"/>')
            b.append(f'<path d="M{hx:.1f} {y - 8:.1f}L{hx + 8:.1f} {y:.1f}L{hx:.1f} {y + 8:.1f}L{hx - 8:.1f} {y:.1f}Z" fill="#ffffff" stroke="{DARK}" stroke-width="1.8"/>')
            b.append(text(hx + 13, y + 4.5, f"{best[1]['reading']:.0f} with harness", fill=DARK))
        b.append(f'<circle cx="{x(m):.1f}" cy="{y:.1f}" r="8" fill="{BLUE}" stroke="#ffffff" stroke-width="2"/>')
        b.append(text(x(m), y - 13, f"{m:.0f}", "middle", DARK, weight=600))
    ky = H - 28
    b.append(f'<circle cx="{left + 6}" cy="{ky}" r="8" fill="{BLUE}"/>' + text(left + 20, ky + 4.5, "model alone, mean"))
    b.append(f'<circle cx="{left + 168}" cy="{ky}" r="3.4" fill="{BLUE}" fill-opacity="0.28"/>' + text(left + 178, ky + 4.5, "one paper in one run"))
    b.append(f'<path d="M{left + 340} {ky - 8}l8 8l-8 8l-8 -8Z" fill="#ffffff" stroke="{DARK}" stroke-width="1.8"/>' + text(left + 354, ky + 4.5, "best harness setting"))
    svg("reading_score.svg", W, H, b, "Reading score by model, with each paper and run as a point")

    # 2. Coverage by paper and by part of the note
    cw, ch, lab = 48, 30, 140
    groups = [("By paper", [p for _, p in PAPERS], lambda name, g: 100 * sum(c["points"] for cs in data[name] for c in cs if c["paper"] == g) /
               sum(c["answers"] for cs in data[name] for c in cs if c["paper"] == g)),
              ("By part of the note", [s for _, s in SLOTS], lambda name, g: 100 * sum(c["slots"][sid][0] for cs in data[name] for c in cs for sid, sn in SLOTS if sn == g) /
               sum(c["slots"][sid][1] for cs in data[name] for c in cs for sid, sn in SLOTS if sn == g))]
    short = [n.replace("Claude ", "").replace(" (local)", "") for n in ORDER]
    cw, lab = 78, 170
    W = lab + cw * len(ORDER) + 20
    heights = [62 + ch * len(rows) + 26 for _, rows, _ in groups]
    H = sum(heights)
    b, oy = [], 0
    for gi, (title, rows, value) in enumerate(groups):
        b.append(text(lab, oy + 20, f"Coverage: {title[0].lower()}{title[1:]}", fill=DARK, size=15, weight=600))
        for j, s in enumerate(short):
            b.append(text(lab + j * cw + cw / 2, oy + 48, s, "middle", size=12))
        for i, g in enumerate(rows):
            y = oy + 58 + i * ch
            b.append(text(lab - 10, y + ch / 2 + 4.5, g, "end", DARK))
            for j, name in enumerate(ORDER):
                v = value(name, g)
                b.append(f'<rect x="{lab + j * cw + 1}" y="{y + 1}" width="{cw - 2}" height="{ch - 2}" rx="3" fill="{BLUE}" fill-opacity="{0.06 + 0.86 * v / 100:.2f}"/>')
                b.append(text(lab + j * cw + cw / 2, y + ch / 2 + 4.5, f"{v:.0f}%", "middle", "#ffffff" if v > 55 else DARK))
        oy += heights[gi]
    svg("coverage_grids.svg", W, H, b, "Coverage by paper and by part of the note, percent")

    # 3. Quotes and flags
    W, left, top, row = 820, 170, 56, 34
    half = (W - left - 60) / 2
    H = top + len(ORDER) * row + 50
    b = [text(left, 22, "Quotes found in the paper", fill=DARK, size=15, weight=600),
         text(left + half + 40, 22, "Flags per run", fill=DARK, size=15, weight=600)]
    xq = lambda v: left + (half - 30) * v / 100  # noqa: E731
    fmax = max(max(statistics.mean(t["serious"] + t["mild"] for t in tot[n]) for n in ORDER), 1)
    xf = lambda v: left + half + 40 + (half - 210) * v / fmax  # noqa: E731
    b += axis(xq, top, top + len(ORDER) * row, (0, 50, 100), "%")
    for i, name in enumerate(ORDER):
        y = top + i * row + 6
        b.append(text(left - 12, y + 15, name, "end", DARK))
        q, f = sum(t["quotes"] for t in tot[name]), sum(t["faithful"] for t in tot[name])
        b.append(f'<rect x="{xq(0):.1f}" y="{y}" width="{xq(100 * f / q) - xq(0):.1f}" height="20" rx="2" fill="{BLUE}"/>')
        b.append(text(xq(100 * f / q) - 6, y + 15, f"{f:,} of {q:,}", "end", "#ffffff", size=12))
        s, m = mean(name, "serious"), mean(name, "mild")
        b.append(f'<rect x="{xf(0):.1f}" y="{y}" width="{xf(s) - xf(0):.1f}" height="20" rx="2" fill="{RED}"/>')
        b.append(f'<rect x="{xf(s):.1f}" y="{y}" width="{xf(s + m) - xf(s):.1f}" height="20" rx="2" fill="{AMBER}"/>')
        b.append(text(xf(s + m) + 8, y + 15, f"{s:.1f} serious, {m:.1f} mild"))
    ky = H - 16
    b.append(f'<rect x="{left + half + 40}" y="{ky - 10}" width="12" height="12" rx="2" fill="{RED}"/>' + text(left + half + 58, ky, "serious"))
    b.append(f'<rect x="{left + half + 130}" y="{ky - 10}" width="12" height="12" rx="2" fill="{AMBER}"/>' + text(left + half + 148, ky, "mild"))
    svg("quotes_and_flags.svg", W, H, b, "Share of quotes found in the paper, and flags per run, by model")

    # 4. The harness: coverage and serious flags under each setting
    W, left, top, row = 820, 330, 56, 26
    rows = [(n, s, t) for n in ("Qwen3 4B (local)", "GPT-4o", "Claude Haiku 5.5") for s, t, _ in harness[n]]
    H = top + len(rows) * row + 3 * 10 + 20
    x = lambda v: left + (W - left - 190) * v / 100  # noqa: E731
    b = [text(20, 22, "What each harness setting does to coverage and serious flags", fill=DARK, size=15, weight=600)]
    b += axis(x, top, H - 14, suffix="%")
    b.append(text(W - 170, top - 8, "serious flags"))
    y, last = top, None
    for name, setting, t in rows:
        if name != last:
            y += 10 if last else 0
            b.append(text(20, y + 17, name, fill=DARK, weight=600))
            last = name
        alone = setting == "Model alone"
        b.append(text(left - 10, y + 17, "alone" if alone else setting.lower(), "end"))
        b.append(f'<rect x="{x(0):.1f}" y="{y + 4}" width="{x(t["coverage"]) - x(0):.1f}" height="18" rx="2" fill="{BLUE if alone else LIGHT}"/>')
        b.append(text(x(t["coverage"]) + 6, y + 17, f"{t['coverage']:.0f}%", fill=DARK))
        for k in range(t["serious"]):
            b.append(f'<circle cx="{W - 166 + k * 8}" cy="{y + 13}" r="3.2" fill="{RED}"/>')
        if not t["serious"]:
            b.append(text(W - 170, y + 17, "none"))
        y += row
    svg("harness.svg", W, H, b, "Coverage and serious flags for each model under each harness setting")

    # 5. Cost against coverage
    W, H, left, right, top, bottom = 820, 420, 70, 150, 50, 56
    pts = []
    for mid, name, runs in MODELS:
        c = statistics.mean(cost_per_paper([r])["dollars"] or 0 for r in runs)
        if c:
            pts.append((name, c, mean(name, "coverage"), False))
    for tag, name, steps in (("haiku-5-5", "Claude Haiku 5.5", ["haiku-5-5-text-prompt3", "cost-haiku-5-5-expand", "cost-haiku-5-5-findings"]),):
        t = [h for h in harness[name] if h[0] == "Asked for more, key findings too"][0][1]
        pts.append((name + " + harness", cost_per_paper(steps)["dollars"], t["coverage"], True))
    lo, hi = math.log10(0.003), math.log10(1)
    x = lambda c: left + (W - left - right) * (math.log10(c) - lo) / (hi - lo)  # noqa: E731
    yv = lambda v: H - bottom - (H - top - bottom) * v / 100  # noqa: E731
    b = [text(left, 22, "Cost per paper against coverage", fill=DARK, size=15, weight=600)]
    for c in (0.003, 0.01, 0.03, 0.1, 0.3, 1):
        b.append(f'<line x1="{x(c):.1f}" x2="{x(c):.1f}" y1="{top}" y2="{H - bottom}" stroke="{GRID}"/>')
        b.append(text(x(c), H - bottom + 18, f"${c:g}", "middle"))
    for v in (0, 25, 50, 75, 100):
        b.append(f'<line x1="{left}" x2="{W - right}" y1="{yv(v):.1f}" y2="{yv(v):.1f}" stroke="{GRID}"/>')
        b.append(text(left - 8, yv(v) + 4.5, f"{v}%", "end"))
    b.append(text((left + W - right) / 2, H - 12, "cost per paper, standard rates, log scale", "middle"))
    base = {n: (c, v) for n, c, v, h in pts if not h}
    for name, c, v, h in pts:
        if h:
            bc, bv = base[name.replace(" + harness", "")]
            b.append(f'<line x1="{x(bc):.1f}" y1="{yv(bv):.1f}" x2="{x(c):.1f}" y2="{yv(v):.1f}" stroke="{INK}" stroke-dasharray="3 3"/>')
            b.append(f'<path d="M{x(c):.1f} {yv(v) - 8:.1f}l8 8l-8 8l-8 -8Z" fill="#ffffff" stroke="{DARK}" stroke-width="1.8"/>')
        else:
            b.append(f'<circle cx="{x(c):.1f}" cy="{yv(v):.1f}" r="7" fill="{BLUE}" stroke="#ffffff" stroke-width="2"/>')
        dx, dy, anchor = {"GPT-6.2 Sol": (-12, 4.5, "end"), "Claude Opus 5.5": (0, -14, "middle"), "GPT-6.2 Astra": (12, 16, "start")}.get(name, (12, 4.5, "start"))
        b.append(text(x(c) + dx, yv(v) + dy, name, anchor, DARK))
    svg("cost.svg", W, H, b, "Cost per paper against coverage, by model")

    for name in ORDER:
        best = max((h for h in harness.get(name, []) if h[0] != "Model alone"), key=lambda h: h[1]["reading"], default=None)
        print(f"{name:18s} reading {mean(name, 'reading'):5.1f}  coverage {mean(name, 'coverage'):5.1f}  trust {statistics.mean(t['trust'] for t in tot[name]):.3f}"
              + (f"   best harness: {best[0]} -> {best[1]['reading']:.1f}" if best else ""))


if __name__ == "__main__":
    main()
