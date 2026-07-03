#!/usr/bin/env python3
"""
Fully-local 0-token diff: vedabase-original repo (REVISED) vs the 2003 "Original
Book VedaBase" RTF export (ORIGINAL 1972 editions). No scraping.

The RTF (converted to txt via `textutil -convert txt`) lays each book verse as:
    Bg 2.13            <- exact ref line (lecture refs have trailing tabs/timestamps)
    TEXT 13
    TEXT ...transliteration / word-for-word...
    TRANSLATION
    <translation>
    PURPORT
    <purport>
We parse {ref: {translation, purport}} from it and diff against the repo.

Usage:
    python3 rtf_diff.py bg 2          # BG chapter 2
    python3 rtf_diff.py sb 1 1        # SB canto 1 chapter 1
"""
import sys, re, json, unicodedata, difflib, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "rtf_diffs"; OUT.mkdir(exist_ok=True)
TXT = pathlib.Path("/tmp/vb2003.txt")

# BBT Balaram ANSI diacritics -> IAST-fold ASCII (so both sides fold identically).
# Derived empirically from known-identical pairs (repo IAST vs RTF BBT):
#   Sañjaya↔Saïjaya (ï=ñ→n)  Kṛṣṇa↔Kåñëa (å=ṛ→r, ñ=ṣ→s, ë=ṇ→n)  kṣatriya↔kñatriya
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

# ---------- parse the RTF txt ----------
def parse_rtf(ref_prefix):
    """{ref: {translation, purport}} from the RTF txt for refs matching prefix."""
    lines = TXT.read_text(encoding="utf-8", errors="replace").split("\n")
    # find exact book-verse ref lines (no trailing timestamp/tab content)
    ref_re = re.compile(rf"^({ref_prefix})\s*$")
    idx = [(i, m.group(1)) for i, l in enumerate(lines) if (m := ref_re.match(l))]
    out = {}
    for k, (i, ref) in enumerate(idx):
        end = idx[k + 1][0] if k + 1 < len(idx) else len(lines)
        block = lines[i:end]
        # locate TRANSLATION and PURPORT markers
        try:
            ti = next(j for j, l in enumerate(block) if l.strip() == "TRANSLATION")
        except StopIteration:
            continue
        pi = next((j for j, l in enumerate(block) if l.strip() == "PURPORT"), len(block))
        translation = " ".join(x.strip() for x in block[ti + 1:pi] if x.strip())
        purport = " ".join(x.strip() for x in block[pi + 1:] if x.strip())
        # purport may run to next ref; trailing "Collier"/devanagari noise is tolerable
        out.setdefault(ref, {"translation": translation, "purport": purport})
    return out

# ---------- repo parser ----------
def parse_repo(book):
    if book == "bg":
        path = REPO / "bhagavad-gita-as-it-is.md"; rr = r"Bg [\d.]+"
    elif book == "sb":
        path = REPO / "srimad-bhagavatam" / f"canto-{int(sys.argv[2]):02d}.md"; rr = r"SB [\d.]+"
    text = path.read_text(encoding="utf-8")
    parts = re.split(rf"\n###\s+({rr})\s*\n", text)
    out = {}
    for i in range(1, len(parts), 2):
        ref, body = parts[i].strip(), parts[i + 1]
        tm = re.search(r"\*\*(.+?)\*\*", body, re.S)
        translation = tm.group(1).strip() if tm else ""
        purport = re.sub(r"[*>#]", "", body[tm.end():]).strip() if tm else ""
        out[ref] = {"translation": translation, "purport": purport}
    return out

def wdiff(a, b):
    na, nb = norm(a), norm(b)
    if na == nb:
        return None
    sm = difflib.SequenceMatcher(None, na.split(), nb.split())
    return round(sm.ratio(), 4)

def main():
    book = sys.argv[1]
    if book == "bg":
        ch = int(sys.argv[2]); pref = rf"Bg {ch}\.\d+"; tag = f"bg-{ch}"
        repo = {r: v for r, v in parse_repo("bg").items() if re.match(rf"Bg {ch}\.\d+$", r)}
    elif book == "sb":
        canto, ch = int(sys.argv[2]), int(sys.argv[3]); pref = rf"SB {canto}\.{ch}\.\S+"; tag = f"sb-{canto}-{ch}"
        repo = {r: v for r, v in parse_repo("sb").items() if re.match(rf"SB {canto}\.{ch}\.", r)}
    rtf = parse_rtf(pref)
    print(f"repo verses: {len(repo)} | RTF(original) verses parsed: {len(rtf)}")
    rows = []
    for ref in sorted(repo, key=lambda r: [int(x) if x.isdigit() else x for x in re.split(r"[ .]", r)]):
        o = rtf.get(ref)
        if not o:
            print(f"  {ref}: (not found in RTF)"); continue
        ts = wdiff(repo[ref]["translation"], o["translation"])
        ps = wdiff(repo[ref]["purport"], o["purport"])
        st = []
        if ts is not None: st.append(f"transl sim={ts}")
        if ps is not None: st.append(f"purport sim={ps}")
        print(f"  {ref}: {', '.join(st) if st else 'IDENTICAL'}")
        if ts is not None or ps is not None:
            rows.append({"ref": ref, "transl_sim": ts, "purport_sim": ps,
                         "translation": {"repo": repo[ref]["translation"], "orig": o["translation"]} if ts is not None else None,
                         "purport": {"repo": repo[ref]["purport"], "orig": o["purport"]} if ps is not None else None})
    (OUT / f"{tag}.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    diff_t = sum(1 for r in rows if r["transl_sim"] is not None)
    print(f"\n{diff_t}/{len(repo)} verses have translation differences. → scripts/rtf_diffs/{tag}.json")

if __name__ == "__main__":
    main()
