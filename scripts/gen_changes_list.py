#!/usr/bin/env python3
"""
Verse-ordered list of GENUINE translation differences between the repo SB and the
2003 Original VedaBase (1972). Excludes diacritic/OCR near-variants, VedaBase-added
bracketed references, and boundary over-capture. Output: a markdown list.

  python3 gen_changes_list.py  ->  scripts/rtf_diffs/SB_REAL_CHANGES.md
"""
import re, unicodedata, difflib, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "rtf_diffs"; OUT.mkdir(exist_ok=True)
TXT = pathlib.Path("/tmp/vb2003.txt")
BBT = str.maketrans({"ä":"a","à":"m","å":"r","ç":"s","é":"i","ë":"n","ï":"n","ñ":"s","ü":"u","í":"i","ö":"t","ò":"d","ó":"o","ù":"u","û":"u","è":"e","ê":"e","î":"i","ô":"o","õ":"n","Ä":"a","Å":"r","Ç":"s","É":"i","Ë":"n","Ï":"n","Ñ":"s","Ü":"u","Ö":"t","Ò":"d"})
def fold(w):
    w = "".join(c for c in unicodedata.normalize("NFKD", w.translate(BBT)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", w.lower())
def near(a, b):
    a, b = fold(a), fold(b)
    if not a or not b or a == b: return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.72
REFBR = re.compile(r"\[[^\]]*\d[^\]]*\]")
def clean(s): return re.sub(r"\s+", " ", REFBR.sub(" ", s)).strip()

# parse
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

def changes(a, b):
    aw, bw = a.split(), b.split()
    sm = difflib.SequenceMatcher(None, [fold(w) for w in aw], [fold(w) for w in bw]); ops = sm.get_opcodes()
    if ops:
        tg, i1, i2, j1, j2 = ops[-1]
        if tg in ("insert", "replace") and (j2 - j1) > 12 and i2 == len(aw) and j2 == len(bw):
            bw = bw[:j1]; ops = difflib.SequenceMatcher(None, [fold(w) for w in aw], [fold(w) for w in bw]).get_opcodes()
    def keep(A, B):
        # drop chapter colophons and over-long structural blocks (repo-side
        # purport over-capture) — real wording edits are short phrases
        if "Thus end the Bhaktivedanta" in A or "Thus end the Bhaktivedanta" in B:
            return False
        if A.startswith("PURPORT") or B.startswith("PURPORT"):
            return False
        return len(A.split()) <= 20 and len(B.split()) <= 20
    res = []
    for tag, i1, i2, j1, j2 in ops:
        A, B = " ".join(aw[i1:i2]), " ".join(bw[j1:j2])
        if tag == "replace":
            if (abs((i2-i1)-(j2-j1)) > 1) or any(not near(aw[i1+i] if i1+i<i2 else "", bw[j1+i] if j1+i<j2 else "") for i in range(max(i2-i1, j2-j1))):
                if keep(A, B): res.append((A, B))
        elif tag == "delete" and (i2-i1) >= 2:
            if keep(A, "—"): res.append((A, "—"))
        elif tag == "insert" and (j2-j1) >= 2:
            if keep("—", B): res.append(("—", B))
    return res

def keyf(ref):
    n = re.split(r"[ .]", ref)
    return tuple(int(x) if x.isdigit() else 999 for x in n[1:])

rows = []
for ref in sorted(repo, key=keyf):
    o = rtf.get(ref)
    if not o: continue
    ch = changes(clean(repo[ref]), clean(o))
    if ch:
        rows.append((ref, ch))

md = ["# Śrīmad-Bhāgavatam — real translation changes (repo vs 1972 original)",
      "",
      f"{len(rows)} verses with genuine wording differences (of {len(repo)}). "
      "Diacritic/OCR variants, VedaBase-added [refs], and over-capture excluded.",
      "Format per change:  **repo**  →  *1972 original*  (— = absent on that side).",
      ""]
cur_canto = None
for ref, ch in rows:
    canto = ref.split()[1].split(".")[0]
    if canto != cur_canto:
        md.append(f"\n## Canto {canto}\n"); cur_canto = canto
    md.append(f"**{ref}** ({len(ch)})")
    for a, b in ch:
        md.append(f"- `{a}` → `{b}`")
    md.append("")
(OUT / "SB_REAL_CHANGES.md").write_text("\n".join(md))
# per-canto tally
from collections import Counter
tally = Counter(r[0].split()[1].split(".")[0] for r in rows)
print("verses with real changes:", len(rows))
print("by canto:", dict(sorted(tally.items(), key=lambda x: int(x[0]))))
print("→ scripts/rtf_diffs/SB_REAL_CHANGES.md")
