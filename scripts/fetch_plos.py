"""Download PLOS ONE articles (PDF + JATS XML) and write their published peer review
history to a readable Markdown file.

  python3 scripts/fetch_plos.py 10.1371/journal.pone.0360061 [more DOIs...]

Output: data/plos/<pone id>/paper.pdf, paper.xml, reviews.md
"""
import html, pathlib, re, sys, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://journals.plos.org/plosone/article/file?id={doi}&type={kind}"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "research-script"})
    for attempt in range(4):
        try:
            return urllib.request.urlopen(req, timeout=120).read()
        except Exception:
            time.sleep(2 ** (attempt + 1))
    raise SystemExit(f"failed: {url}")


def to_text(xml):
    xml = re.sub(r"</p>|</title>|<break\s*/>", "\n\n", xml)
    text = html.unescape(re.sub(r"<[^>]+>", "", xml))
    return re.sub(r"\n\s*\n+", "\n\n", re.sub(r"[ \t]+", " ", text)).strip()


for doi in sys.argv[1:]:
    out = ROOT / "data" / "plos" / doi.split("journal.")[-1]
    out.mkdir(parents=True, exist_ok=True)
    xml = get(BASE.format(doi=doi, kind="manuscript")).decode("utf-8", "replace")
    (out / "paper.xml").write_text(xml)
    (out / "paper.pdf").write_bytes(get(BASE.format(doi=doi, kind="printable")))
    title = to_text(re.search(r"<article-title>(.*?)</article-title>", xml, re.S).group(1))
    parts = [f"# Peer review history: {title}\n\nDOI: {doi} (CC BY)\n"]
    for attrs, body in re.findall(r"<sub-article([^>]*)>(.*?)</sub-article>", xml, re.S):
        kind = re.search(r'article-type="([^"]+)"', attrs)
        sub_title = re.search(r"<article-title>(.*?)</article-title>", body, re.S)
        date = re.search(r"<named-content content-type=\"[^\"]*date\">(.*?)</named-content>", body, re.S)
        main = re.search(r"<body>(.*?)</body>", body, re.S)
        parts.append(f"\n---\n\n## {to_text(sub_title.group(1)) if sub_title else '?'} "
                     f"[{kind.group(1) if kind else '?'}]"
                     f"{' ' + to_text(date.group(1)) if date else ''}\n\n"
                     f"{to_text(main.group(1)) if main else ''}\n")
    (out / "reviews.md").write_text("\n".join(parts))
    print(out.relative_to(ROOT), "|", title[:70], "|", len(parts) - 1, "review documents |",
          (out / "paper.pdf").stat().st_size // 1024, "KB pdf")
    time.sleep(1)
