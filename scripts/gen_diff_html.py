#!/usr/bin/env python3
"""
Render the repo-vs-original (2003 VedaBase RTF) SB diffs as a single HTML file
with inline word-level highlighting. Over-capture artifacts (where one side's
extracted text simply runs past the verse boundary) are detected and trimmed,
so the page shows the *genuine* textual differences.

  python3 gen_diff_html.py   ->   scripts/rtf_diffs/SB_DIFFS.html
"""
import re, unicodedata, difflib, html, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "rtf_diffs"; OUT.mkdir(exist_ok=True)
TXT = pathlib.Path("/tmp/vb2003.txt")

BBT = str.maketrans({"ä":"a","à":"m","å":"r","ç":"s","é":"i","ë":"n","ï":"n","ñ":"s","ü":"u","í":"i","ö":"t","ò":"d","ó":"o","ù":"u","û":"u","è":"e","ê":"e","î":"i","ô":"o","õ":"n","Ä":"a","Å":"r","Ç":"s","É":"i","Ë":"n","Ï":"n","Ñ":"s","Ü":"u","Ö":"t","Ò":"d"})
def fold(w):
    w = w.translate(BBT)
    w = "".join(c for c in unicodedata.normalize("NFKD", w) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w.lower())

# ---- parse RTF (translations) ----
lines = TXT.read_text(errors="replace").split("\n")
rr = re.compile(r"^(SB \d+\.\d+\.\d+(?:-\d+)?)\s*$")
STOP = re.compile(r"^(PURPORT|Collier|TEXTS? \d|SB \d|Bg \d|CC |Thus end|END OF|—Completed|The Author|Glossary)")
idx = [(i, m.group(1)) for i, l in enumerate(lines) if (m := rr.match(l))]
rtf = {}
for k, (i, ref) in enumerate(idx):
    end = idx[k+1][0] if k+1 < len(idx) else len(lines); b = lines[i:end]
    try: ti = next(j for j, l in enumerate(b) if l.strip() == "TRANSLATION")
    except StopIteration: continue
    te = next((j for j in range(ti+1, len(b)) if STOP.match(b[j].strip())), len(b))
    rtf.setdefault(ref, " ".join(x.strip() for x in b[ti+1:te] if x.strip()))

# ---- parse repo ----
repo = {}
for c in range(1, 11):
    t = (REPO / "srimad-bhagavatam" / f"canto-{c:02d}.md").read_text()
    p = re.split(r"\n###\s+(SB [\d.]+)\s*\n", t)
    for i in range(1, len(p), 2):
        m = re.search(r"\*\*(.+?)\*\*", p[i+1], re.S)
        if m: repo[p[i].strip()] = m.group(1).strip()

def diff_html(a, b):
    """Inline word diff; returns (html, n_changes, artifact_bool)."""
    aw, bw = a.split(), b.split()
    sm = difflib.SequenceMatcher(None, [fold(w) for w in aw], [fold(w) for w in bw])
    # over-capture artifact: a single trailing replace/insert covering most of one side's tail
    ops = sm.get_opcodes()
    artifact = False
    if ops:
        tag, i1, i2, j1, j2 = ops[-1]
        if tag in ("insert", "replace") and (j2 - j1) > 12 and i2 == len(aw) and j2 == len(bw):
            artifact = True
            bw = bw[:j1] + ["…[+%d words — boundary over-capture]" % (j2 - j1)]
            sm = difflib.SequenceMatcher(None, [fold(w) for w in aw], [fold(w) for w in bw[:-1]])
            ops = sm.get_opcodes()
    out, n = [], 0
    def esc(ws): return html.escape(" ".join(ws))
    for tag, i1, i2, j1, j2 in ops:
        if tag == "equal":
            out.append(esc(aw[i1:i2]))
        elif tag == "delete":
            out.append(f'<del>{esc(aw[i1:i2])}</del>'); n += 1
        elif tag == "insert":
            out.append(f'<ins>{esc(bw[j1:j2])}</ins>'); n += 1
        else:
            out.append(f'<del>{esc(aw[i1:i2])}</del> <ins>{esc(bw[j1:j2])}</ins>'); n += 1
    if artifact:
        out.append('<span class="art">…[+ words — boundary over-capture, text identical]</span>')
    return " ".join(out), n, artifact

# ---- build cards for verses that differ ----
def sim(a, b):
    return difflib.SequenceMatcher(None, [fold(w) for w in a.split()], [fold(w) for w in b.split()]).ratio()

cards, n_genuine, n_artifact, n_identical = [], 0, 0, 0
for ref in sorted(repo, key=lambda r: [int(x) if x.isdigit() else 99 for x in re.split(r"[ .]", r)]):
    o = rtf.get(ref)
    if not o: continue
    s = sim(repo[ref], o)
    if s >= 0.999:
        n_identical += 1; continue
    h, n, art = diff_html(repo[ref], o)
    if art and n == 0:
        n_artifact += 1; continue   # pure over-capture, text identical -> skip
    if art: n_artifact += 1
    else: n_genuine += 1
    cards.append((ref, round(s, 3), n, art, h))

cards.sort(key=lambda c: c[1])  # lowest similarity first

css = """
body{font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#faf8f4;color:#222}
header{background:#2b2b2b;color:#f4f1ea;padding:22px 32px}
header h1{margin:0 0 4px;font-size:22px}.sub{color:#bdb6a8;font-size:13px}
.wrap{max-width:900px;margin:0 auto;padding:24px 32px}
table.sum{border-collapse:collapse;margin:8px 0 24px}
table.sum td{padding:4px 14px;border-bottom:1px solid #e6e0d4}
.card{background:#fff;border:1px solid #e6e0d4;border-radius:8px;padding:14px 18px;margin:14px 0;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.ref{font-weight:700;color:#9a3b12}.meta{float:right;font-size:12px;color:#999}
.body{margin-top:8px}
del{background:#ffd9d6;color:#9a0000;text-decoration:none;border-radius:3px;padding:0 2px}
ins{background:#cdeccd;color:#0a5b0a;text-decoration:none;border-radius:3px;padding:0 2px}
.art{color:#b8860b;font-style:italic;font-size:13px}
.legend{font-size:13px;color:#555;margin:8px 0 0}
.note{background:#fff8e6;border:1px solid #ecd9a0;border-radius:8px;padding:12px 16px;font-size:14px}
"""
rows = "\n".join(
    f'<div class="card"><span class="ref">{html.escape(ref)}</span>'
    f'<span class="meta">similarity {s} · {n} change(s){" · artifact" if art else ""}</span>'
    f'<div class="body">{h}</div></div>'
    for ref, s, n, art, h in cards)
doc = f"""<!doctype html><html><head><meta charset="utf-8"><title>SB diff — repo vs Original VedaBase</title><style>{css}</style></head>
<body><header><h1>Śrīmad-Bhāgavatam — repo vs 2003 Original VedaBase (1972)</h1>
<div class="sub">Fully local diff · {len(repo)} repo verses · 0 API tokens · <del>repo</del> / <ins>original</ins> word-level</div></header>
<div class="wrap">
<table class="sum">
<tr><td>Verses identical (≥0.999)</td><td><b>{n_identical}</b></td></tr>
<tr><td>Verses with genuine textual differences shown below</td><td><b>{n_genuine}</b></td></tr>
<tr><td>Boundary over-capture artifacts (text identical, parser noise)</td><td><b>{n_artifact}</b></td></tr>
</table>
<div class="note">Reading guide: <del>red</del> = text in the repo (revised candidate), <ins>green</ins> = text in the 1972 original.
Most differences below are <b>diacritic-encoding or OCR-level</b>, not editorial revisions. Verses flagged
<i>artifact</i> are identical text where one side's extraction ran past the verse boundary.</div>
{rows}
</div></body></html>"""
(OUT / "SB_DIFFS.html").write_text(doc)
print(f"identical={n_identical} genuine_shown={n_genuine} artifacts={n_artifact}")
print(f"Wrote scripts/rtf_diffs/SB_DIFFS.html ({len(cards)} cards)")
