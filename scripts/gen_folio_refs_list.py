#!/usr/bin/env python3
"""
List the FOLIO/VedaBase editorial additions: bracketed scripture references like
[Bhäg. 1964:1.13.52], [SB 1.1.1], [Bg. 4.7], [4.1] that appear in the 2003
VedaBase text but NOT in the repo (i.e. references the VedaBase inserted into
Prabhupāda's text). Per the RTF's own note: "references enclosed by [ ] are
added by the vedabase."

  python3 gen_folio_refs_list.py  ->  scripts/rtf_diffs/FOLIO_ADDED_REFS.md
"""
import re, unicodedata, pathlib
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "rtf_diffs"; OUT.mkdir(exist_ok=True)
TXT = pathlib.Path("/tmp/vb2003.txt")
BBT = str.maketrans({"ä":"a","à":"m","å":"r","ç":"s","é":"i","ë":"n","ï":"n","ñ":"s","ü":"u","í":"i","ö":"t","ò":"d","ó":"o","ù":"u","û":"u","è":"e","ê":"e","î":"i","ô":"o","õ":"n"})
def key(ref):  # normalized comparison key for a bracketed ref
    r = "".join(c for c in unicodedata.normalize("NFKD", ref.translate(BBT)) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", r.lower())
REFBR = re.compile(r"\[[^\]]*\d[^\]]*\]")

# ---- parse RTF (translation + purport, generously) ----
lines = TXT.read_text(errors="replace").split("\n")
rr = re.compile(r"^(SB \d+\.\d+\.\d+(?:-\d+)?)\s*$")
STOPp = re.compile(r"^(Collier|TEXTS? \d|SB \d\d?\.\d|Bg \d|CC |END OF|The Author|Glossary)")
idx = [(i, m.group(1)) for i, l in enumerate(lines) if (m := rr.match(l))]
folio = {}
for k, (i, ref) in enumerate(idx):
    end = idx[k+1][0] if k+1 < len(idx) else len(lines); b = lines[i:end]
    try: ti = next(j for j, l in enumerate(b) if l.strip() == "TRANSLATION")
    except StopIteration: continue
    pe = next((j for j in range(ti+1, len(b)) if STOPp.match(b[j].strip())), len(b))
    folio.setdefault(ref, " ".join(x.strip() for x in b[ti+1:pe] if x.strip()))

# ---- parse repo (translation + purport, full) ----
repo = {}
for c in range(1, 11):
    t = (REPO / "srimad-bhagavatam" / f"canto-{c:02d}.md").read_text()
    p = re.split(r"\n###\s+(SB [\d.]+)\s*\n", t)
    for i in range(1, len(p), 2):
        repo[p[i].strip()] = re.sub(r"[*>#]", "", p[i+1])

rows, total = [], Counter()
for ref in sorted(repo, key=lambda r:[int(x) if x.isdigit() else 999 for x in re.split(r"[ .]", r)[1:]]):
    o = folio.get(ref)
    if not o: continue
    folio_refs = REFBR.findall(o)
    repo_keys = {key(x) for x in REFBR.findall(repo[ref])}
    added = [x for x in folio_refs if key(x) not in repo_keys]
    if added:
        rows.append((ref, added))
        total["verses"] += 1; total["refs"] += len(added)

md = ["# Folio / VedaBase added references (not in the repo)", "",
      f"{total['verses']} SB verses where the 2003 VedaBase inserted "
      f"{total['refs']} scripture references that the repo does not carry.",
      "These are editorial cross-references added by the VedaBase, not part of Prabhupāda's original text.",
      ""]
cur = None
for ref, added in rows:
    c = ref.split()[1].split(".")[0]
    if c != cur: md.append(f"\n## Canto {c}\n"); cur = c
    md.append(f"**{ref}**: " + "  ".join(f"`{a}`" for a in added))
(OUT / "FOLIO_ADDED_REFS.md").write_text("\n".join(md))
print(f"verses with Folio-added refs: {total['verses']} | total added refs: {total['refs']}")
print("→ scripts/rtf_diffs/FOLIO_ADDED_REFS.md")
