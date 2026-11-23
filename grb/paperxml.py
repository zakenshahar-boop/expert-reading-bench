"""What the JATS XML of a paper adds to its PDF: sections and the reference list."""

from __future__ import annotations

import html
import re

from .quotes import normalize_text

BUCKETS = (  # first match wins
    ("methods", r"method|material|data|measure|sample|design"),
    ("results", r"result|finding|analys"),
    ("discussion", r"discussion|conclusion|limitation|implication"),
    ("introduction", r"introduction"),
)


_INLINE = r"</?(?:xref|italic|bold|sup|sub|sc|underline|ext-link|named-content|styled-content|monospace|inline-formula)\b[^>]*>"


def _text(fragment: str) -> str:
    """Tags removed. Inline tags vanish, so "[<xref>1</xref>]" reads "[1]" as in the PDF;
    block tags become spaces."""
    return html.unescape(re.sub(r"<[^>]+>", " ", re.sub(_INLINE, "", fragment)))


def _main_article(xml: str) -> str:
    cut = xml.find("<sub-article")
    return xml if cut == -1 else xml[:cut]


def bucket(title: str, seen_methods: bool) -> str:
    t = title.lower()
    for name, pattern in BUCKETS:
        if re.search(pattern, t):
            return name
    return "other" if seen_methods else "background"


def sections(xml: str) -> list[tuple[str, str, str]]:
    """(bucket, title, normalized text) for the abstract and each top-level section.
    Sections before the methods that are not the introduction are "background"."""
    xml = _main_article(xml)
    out = []
    m = re.search(r"<abstract\b[^>]*>(.*?)</abstract>", xml, re.S)
    if m:
        out.append(("abstract", "Abstract", normalize_text(_text(m.group(1)))))
    b0, b1 = xml.find("<body"), xml.find("</body>")
    body = xml[b0:b1] if b0 != -1 else ""
    depth, start, seen_methods = 0, None, False
    for tag in re.finditer(r"<sec\b[^>]*>|</sec>", body):
        if tag.group().startswith("</"):
            depth -= 1
            if depth == 0 and start is not None:
                chunk = body[start:tag.start()]
                t = re.search(r"<title>(.*?)</title>", chunk, re.S)
                title = _text(t.group(1)).strip() if t else ""
                name = bucket(title, seen_methods)
                seen_methods = seen_methods or name == "methods"
                out.append((name, title, normalize_text(_text(chunk))))
        else:
            if depth == 0:
                start = tag.end()
            depth += 1
    return out


def references(xml: str) -> dict[int, set[str]]:
    """Reference number -> the surnames (or group names) of its authors."""
    xml = _main_article(xml)
    refs = {}
    for m in re.finditer(r"<ref id=[^>]*>(.*?)</ref>", xml, re.S):
        label = re.search(r"<label>\s*(\d+)", m.group(1))
        if not label:
            continue
        names = re.findall(r"<surname>(.*?)</surname>", m.group(1), re.S)
        names += re.findall(r"<collab>(.*?)</collab>", m.group(1), re.S)
        refs[int(label.group(1))] = {html.unescape(_text(n)).strip() for n in names if n.strip()}
    return refs
