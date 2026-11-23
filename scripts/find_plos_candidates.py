"""Find recent PLOS ONE social-science articles whose published XML includes the peer
review history (decision letters with reviewer comments), and rank them by how much
reviewer text there is.

  python3 scripts/find_plos_candidates.py > data/candidates.tsv

PLOS content is CC BY, so both the papers and the reviews can be redistributed.
"""
import json, re, sys, time, urllib.parse, urllib.request

SUBJECTS = ["Political science", "Sociology", "Political parties", "Elections",
            "Social stratification", "Public opinion", "Social networks"]
SINCE = "2026-01-01T00:00:00Z"
ROWS = 40


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "research-script"})
    for attempt in range(3):
        try:
            return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
        except Exception as e:
            time.sleep(2 * (attempt + 1))
    return ""


def search(subject):
    q = (f'subject:"{subject}" AND journal_key:PLoSONE AND article_type:"Research Article" '
         f'AND doc_type:full AND publication_date:[{SINCE} TO NOW]')
    url = "https://api.plos.org/search?" + urllib.parse.urlencode(
        {"q": q, "fl": "id,title,publication_date", "rows": ROWS, "wt": "json",
         "sort": "publication_date desc"})
    return json.loads(get(url) or '{"response":{"docs":[]}}')["response"]["docs"]


def strip(xml):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", xml)).strip()


seen = {}
for s in SUBJECTS:
    for d in search(s):
        seen.setdefault(d["id"], (d, s))
    time.sleep(1)

print("doi\tdate\tsubject\treview_words\treviewers\tpaper_words\ttitle")
for doi, (d, s) in seen.items():
    xml = get(f"https://journals.plos.org/plosone/article/file?id={doi}&type=manuscript")
    subs = re.findall(r"<sub-article[^>]*>(.*?)</sub-article>", xml, re.S)
    review_text = " ".join(strip(x) for x in subs)
    reviewers = len(set(re.findall(r"Reviewer #(\d+)", review_text)))
    body = re.search(r"<body>(.*?)</body>", xml, re.S)
    print(doi, d["publication_date"][:10], s, len(review_text.split()), reviewers,
          len(strip(body.group(1)).split()) if body else 0, d["title"], sep="\t", flush=True)
    time.sleep(0.5)
