#!/usr/bin/env python3
"""
Full local diff of the repo's Śrīmad-Bhāgavatam vs the 2003 Original Book
VedaBase RTF (1972 originals). Parses the RTF once; diffs every SB verse.
0 tokens, no network.

Output:
  scripts/rtf_diffs/SB_DEVIATIONS.md   — verses where the repo deviates from the original
  scripts/rtf_diffs/sb_all.json        — every verse + similarity (machine-readable)
"""
import re, json, unicodedata, difflib, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "rtf_diffs"; OUT.mkdir(exist_ok=True)
TXT = pathlib.Path("/tmp/vb2003.txt")

BBT = str.maketrans({
    "ä":"a","à":"m","å":"r","ç":"s","é":"i","ë":"n","ï":"n","ñ":"s","ü":"u",
    "í":"i","ö":"t","ò":"d","ó":"o","ù":"u","û":"u","è":"e","ê":"e","î":"i","ô":"o","õ":"n",
    "Ä":"a","Å":"r","Ç":"s","É":"i","Ë":"n","Ï":"n","Ñ":"s","Ü":"u","Ö":"t","Ò":"d",
})
def norm(s):
    s = s.translate(BBT)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("—", "-").replace("–", "-")
    s = re.sub(r"[‘’`´]", "'", s); s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def sim(a, b):
    return round(difflib.SequenceMatcher(None, norm(a).split(), norm(b).split()).ratio(), 4)

# ---- parse the whole RTF once for all SB book verses ----
print("parsing RTF (once)...")
lines = TXT.read_text(encoding="utf-8", errors="replace").split("\n")
ref_re = re.compile(r"^(SB \d+\.\d+\.\d+(?:-\d+)?)\s*$")
idx = [(i, m.group(1)) for i, l in enumerate(lines) if (m := ref_re.match(l))]
rtf = {}
for k, (i, ref) in enumerate(idx):
    end = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
    block = lines[i:end]
    try:
        ti = next(j for j, l in enumerate(block) if l.strip() == "TRANSLATION")
    except StopIteration:
        continue
    # translation runs from after TRANSLATION until the FIRST structural marker:
    # PURPORT, Collier, a new TEXT block, or another verse ref line (incl. the
    # comma-separated combined-verse lines like "SB 8.10.30, SB 8.10.31, ...").
    STOP = re.compile(r"^(PURPORT|Collier|TEXTS? \d|SB \d|Bg \d|CC |Thus end|END OF|—Completed|The Author|Glossary)")
    te = next((j for j in range(ti+1, len(block)) if STOP.match(block[j].strip())), len(block))
    pi = next((j for j, l in enumerate(block) if l.strip() == "PURPORT"), None)
    pe = len(block)
    if pi is not None:
        pe = next((j for j in range(pi+1, len(block))
                   if re.match(r"^(Collier|TEXTS? \d|SB \d\d?\.\d|Bg \d|CC )", block[j].strip())), len(block))
    transl = " ".join(x.strip() for x in block[ti+1:te] if x.strip())
    pur = " ".join(x.strip() for x in block[pi+1:pe] if x.strip() and x.strip() != "Collier") if pi is not None else ""
    rtf.setdefault(ref, {"translation": transl, "purport": pur})
print(f"RTF SB verses: {len(rtf)}")

# ---- parse repo SB (all cantos) ----
repo = {}
for c in range(1, 11):
    text = (REPO / "srimad-bhagavatam" / f"canto-{c:02d}.md").read_text(encoding="utf-8")
    parts = re.split(r"\n###\s+(SB [\d.]+)\s*\n", text)
    for i in range(1, len(parts), 2):
        ref, body = parts[i].strip(), parts[i+1]
        tm = re.search(r"\*\*(.+?)\*\*", body, re.S)
        if not tm: continue
        repo[ref] = {
            "translation": tm.group(1).strip(),
            "purport": re.sub(r"[*>#]", "", body[tm.end():]).strip(),
        }
print(f"repo SB verses: {len(repo)}")

# ---- diff ----
rows = []
matched = missing = 0
for ref in repo:
    o = rtf.get(ref)
    if not o:
        missing += 1
        rows.append({"ref": ref, "in_rtf": False}); continue
    matched += 1
    ts = sim(repo[ref]["translation"], o["translation"]) if o["translation"] else None
    ps = sim(repo[ref]["purport"], o["purport"]) if o["purport"] else None
    rows.append({"ref": ref, "in_rtf": True, "transl_sim": ts, "purport_sim": ps})

(OUT / "sb_all.json").write_text(json.dumps(rows, ensure_ascii=False))

# similarity buckets (translation)
def canto(ref): return int(ref.split()[1].split(".")[0])
from collections import defaultdict
buckets = {"identical(≥0.99)":0, "trivial(0.95-0.99)":0, "minor(0.90-0.95)":0,
           "notable(0.80-0.90)":0, "MAJOR(<0.80)":0, "no_translation":0}
deviations = []  # verses worth a look (transl sim < 0.90)
for r in rows:
    if not r.get("in_rtf"): continue
    ts = r.get("transl_sim")
    if ts is None: buckets["no_translation"]+=1; continue
    if ts >= 0.99: buckets["identical(≥0.99)"]+=1
    elif ts >= 0.95: buckets["trivial(0.95-0.99)"]+=1
    elif ts >= 0.90: buckets["minor(0.90-0.95)"]+=1
    elif ts >= 0.80: buckets["notable(0.80-0.90)"]+=1; deviations.append(r)
    else: buckets["MAJOR(<0.80)"]+=1; deviations.append(r)

print(f"\nmatched {matched}, missing-from-RTF {missing}")
print("translation similarity distribution:")
for k,v in buckets.items(): print(f"  {k:24s} {v}")

deviations.sort(key=lambda r: r["transl_sim"])
md = ["# SB repo vs 2003 Original VedaBase — deviation report", "",
      f"Matched {matched} verses; {missing} not found in RTF (combined-verse/numbering).",
      "", "## Translation-similarity distribution", ""]
md += [f"- {k}: {v}" for k,v in buckets.items()]
md += ["", "## Verses where the repo DEVIATES from the original (transl sim < 0.90)", "",
       "| ref | transl sim | purport sim |", "|---|---|---|"]
for r in deviations:
    md.append(f"| {r['ref']} | {r['transl_sim']} | {r.get('purport_sim')} |")
(OUT / "SB_DEVIATIONS.md").write_text("\n".join(md))
print(f"\n{len(deviations)} verses deviate (transl sim < 0.90). → scripts/rtf_diffs/SB_DEVIATIONS.md")
