#!/usr/bin/env python3
"""
Show ONLY genuine textual differences between the repo SB and the 2003 Original
VedaBase. Filters out (a) diacritic/OCR near-variants (words differing by a char
or two), and (b) boundary over-capture artifacts. A verse survives only if it has
a real word substitution or a multi-word add/drop.

  python3 gen_genuine_html.py  ->  scripts/rtf_diffs/SB_GENUINE.html
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
def near(a, b):
    a, b = fold(a), fold(b)
    if not a or not b: return True            # pure-diacritic/punct token
    if a == b: return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.72   # same word, OCR/diacritic

# parse RTF + repo (translations)
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
repo = {}
for c in range(1, 11):
    t = (REPO / "srimad-bhagavatam" / f"canto-{c:02d}.md").read_text()
    p = re.split(r"\n###\s+(SB [\d.]+)\s*\n", t)
    for i in range(1, len(p), 2):
        m = re.search(r"\*\*(.+?)\*\*", p[i+1], re.S)
        if m: repo[p[i].strip()] = m.group(1).strip()

def analyze(a, b):
    aw, bw = a.split(), b.split()
    sm = difflib.SequenceMatcher(None, [fold(w) for w in aw], [fold(w) for w in bw])
    ops = sm.get_opcodes()
    # drop trailing over-capture
    if ops:
        tg, i1, i2, j1, j2 = ops[-1]
        if tg in ("insert", "replace") and (j2 - j1) > 12 and i2 == len(aw) and j2 == len(bw):
            bw = bw[:j1]; sm = difflib.SequenceMatcher(None, [fold(w) for w in aw], [fold(w) for w in bw]); ops = sm.get_opcodes()
    score = 0; out = []
    for tag, i1, i2, j1, j2 in ops:
        A, B = aw[i1:i2], bw[j1:j2]
        if tag == "equal":
            out.append(html.escape(" ".join(A)))
        elif tag == "replace":
            # pair words; genuine if any pair not near OR counts differ a lot
            genuine = (abs(len(A) - len(B)) > 1) or any(
                not near(A[i] if i < len(A) else "", B[i] if i < len(B) else "")
                for i in range(max(len(A), len(B))))
            if genuine:
                score += 1
                out.append(f'<del>{html.escape(" ".join(A))}</del> <ins>{html.escape(" ".join(B))}</ins>')
            else:
                out.append(html.escape(" ".join(A)))   # diacritic/OCR: show repo form, no highlight
        elif tag == "delete":
            if len(A) >= 2: score += 1; out.append(f'<del>{html.escape(" ".join(A))}</del>')
            else: out.append(f'<del class="m">{html.escape(" ".join(A))}</del>')
        elif tag == "insert":
            if len(B) >= 2: score += 1; out.append(f'<ins>{html.escape(" ".join(B))}</ins>')
            else: out.append(f'<ins class="m">{html.escape(" ".join(B))}</ins>')
    return score, " ".join(out)

# strip VedaBase-added bracketed scripture references like [Bhäg. 1964:1.13.52],
# [SB 1.1.1], [4.1] — any bracket containing a digit. Name-glosses ([Dhṛtarāṣṭra])
# have no digit and are kept.
REFBR = re.compile(r"\[[^\]]*\d[^\]]*\]")
def strip_refs(s):
    return re.sub(r"\s+", " ", REFBR.sub(" ", s)).strip()

cards = []
for ref in repo:
    o = rtf.get(ref)
    if not o: continue
    score, h = analyze(strip_refs(repo[ref]), strip_refs(o))
    if score >= 1:
        cards.append((ref, score, h))
cards.sort(key=lambda c: (-c[1], c[0]))

css = """body{font:15px/1.65 -apple-system,Segoe UI,Roboto,sans-serif;margin:0;background:#faf8f4;color:#222}
header{background:#2b2b2b;color:#f4f1ea;padding:22px 32px}header h1{margin:0 0 4px;font-size:21px}.sub{color:#bdb6a8;font-size:13px}
.wrap{max-width:900px;margin:0 auto;padding:24px 32px}.card{background:#fff;border:1px solid #e6e0d4;border-radius:8px;padding:14px 18px;margin:13px 0}
.ref{font-weight:700;color:#9a3b12}.meta{float:right;font-size:12px;color:#999}.body{margin-top:8px}
del{background:#ffd9d6;color:#9a0000;text-decoration:none;border-radius:3px;padding:0 2px}
ins{background:#cdeccd;color:#0a5b0a;text-decoration:none;border-radius:3px;padding:0 2px}
del.m,ins.m{opacity:.5;font-size:13px}
.note{background:#fff8e6;border:1px solid #ecd9a0;border-radius:8px;padding:12px 16px;font-size:14px;margin-bottom:8px}"""
rows = "\n".join(f'<div class="card"><span class="ref">{html.escape(r)}</span><span class="meta">{s} genuine change(s)</span><div class="body">{h}</div></div>' for r, s, h in cards)
doc = f"""<!doctype html><html><head><meta charset=utf-8><title>SB genuine diffs</title><style>{css}</style></head><body>
<header><h1>Śrīmad-Bhāgavatam — GENUINE differences (repo vs 1972 original)</h1>
<div class=sub>{len(repo)} verses compared · diacritic/OCR near-variants &amp; over-capture excluded · <del>repo</del> / <ins>original</ins></div></header>
<div class=wrap><div class=note><b>{len(cards)}</b> verses have a genuine word/phrase difference (out of {len(repo)}).
Faded marks = single-word add/drop. Solid = real substitution or multi-word change.</div>
{rows}</div></body></html>"""
(OUT / "SB_GENUINE.html").write_text(doc)
print(f"genuine-difference verses: {len(cards)} of {len(repo)}")
