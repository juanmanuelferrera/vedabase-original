#!/usr/bin/env python3
"""
Hybrid text comparison (Option C): vedabase-original repo  vs  prabhupadabooks.com

Step 1 (0 tokens): programmatic diff. Parse the repo's verse text, scrape the
matching prabhupadabooks.com pages, ASCII-fold both, and diff translation +
purport per verse. Emits a report of every verse that differs and a JSON of the
differing passages (verbatim, non-normalized) for the optional LLM step.

Step 2 (paid, separate): feed ONLY diffs/*.json passages to a model to classify
each difference (typo / OCR / real edit). Not done here — this script is free.

Usage:
    python3 diff_prabhupadabooks.py sb 1 1        # SB Canto 1, Chapter 1
    python3 diff_prabhupadabooks.py bg 2          # BG Chapter 2  (book parsing TBD)
"""
import sys, re, html, json, time, unicodedata, subprocess, difflib, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "pb_diffs"
OUT.mkdir(exist_ok=True)

UA = "Mozilla/5.0 (vedabase-original diff tool; contact: owner)"

# ---------- normalization (ASCII-fold both sides; compare words only) ----------
def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))   # drop diacritics
    s = s.lower().replace("—", "-").replace("–", "-")
    s = re.sub(r"[‘’`´]", "'", s)
    s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

# ---------- repo parser ----------
def parse_repo_sb(canto: int):
    """Return {ref: {'translation':..., 'purport':...}} for one SB canto file."""
    path = REPO / "srimad-bhagavatam" / f"canto-{canto:02d}.md"
    text = path.read_text(encoding="utf-8")
    # split into verse sections on '### SB x.y.z'
    parts = re.split(r"\n###\s+(SB\s[\d.]+)\s*\n", text)
    out = {}
    # parts = [pre, ref1, body1, ref2, body2, ...]
    for i in range(1, len(parts), 2):
        ref = parts[i].replace("SB ", "SB ").strip()
        body = parts[i + 1]
        tm = re.search(r"\*\*(.+?)\*\*", body, re.S)          # **translation**
        translation = tm.group(1).strip() if tm else ""
        # purport = everything after the translation bold block
        purport = body[tm.end():].strip() if tm else ""
        # drop residual markdown emphasis / blockquotes
        purport = re.sub(r"[*>#]", "", purport)
        out[ref] = {"translation": translation, "purport": purport}
    return out

# ---------- prabhupadabooks scraper ----------
def fetch_pb_sb(canto: int, chapter: int, verse: int):
    url = f"https://prabhupadabooks.com/sb/{canto}/{chapter}/{verse}"
    # NOTE: prabhupadabooks.com serves a JS shell to "bot-like" User-Agents and
    # full content to curl's default UA — so do NOT override -A here.
    raw = subprocess.run(
        ["curl", "-4", "-sL", url],
        capture_output=True, timeout=40,
    ).stdout
    t = raw.decode("cp1252", errors="replace")
    def block(cls):
        m = re.search(rf'class="{cls}"[^>]*>(.*?)</(?:div|p)>', t, re.S)
        if not m:
            return ""
        x = re.sub(r"<[^>]+>", " ", m.group(1))
        return re.sub(r"\s+", " ", html.unescape(x)).strip()
    # purport may span many <p class="Purport"> blocks
    purs = re.findall(r'class="Purport"[^>]*>(.*?)</p>', t, re.S)
    purport = " ".join(
        re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", p))).strip()
        for p in purs
    )
    return {"translation": block("Translation"), "purport": purport}

# ---------- per-verse diff ----------
def word_diff(a: str, b: str):
    """Return a compact unified word-diff if normalized forms differ, else None."""
    na, nb = norm(a), norm(b)
    if na == nb:
        return None
    sm = difflib.SequenceMatcher(None, na.split(), nb.split())
    chunks = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        chunks.append({
            "op": tag,
            "repo": " ".join(na.split()[i1:i2]),
            "pb": " ".join(nb.split()[j1:j2]),
        })
    ratio = sm.ratio()
    return {"similarity": round(ratio, 4), "changes": chunks}

def main():
    if len(sys.argv) < 4 or sys.argv[1] != "sb":
        print("usage: diff_prabhupadabooks.py sb <canto> <chapter>")
        sys.exit(1)
    canto, chapter = int(sys.argv[2]), int(sys.argv[3])
    repo = parse_repo_sb(canto)
    refs = sorted(
        [r for r in repo if re.match(rf"SB {canto}\.{chapter}\.\d", r)],
        key=lambda r: int(r.split(".")[-1]),
    )
    print(f"Repo: {len(refs)} verses in SB {canto}.{chapter}")
    report, diffs = [], []
    for r in refs:
        verse = int(r.split(".")[-1])
        try:
            pb = fetch_pb_sb(canto, chapter, verse)
        except Exception as e:
            print(f"  {r}: FETCH ERROR {e}")
            continue
        rr = repo[r]
        # Distinguish a real text difference from a section simply absent on PB
        # (combined verses / verses without a purport) — don't count those as diffs.
        def cmp(field):
            repo_t, pb_t = rr[field], pb[field]
            if repo_t and not pb_t:
                return ("pb_missing", None)
            if pb_t and not repo_t:
                return ("repo_missing", None)
            return ("diff", word_diff(repo_t, pb_t))
        tk, td = cmp("translation")
        pk, pd = cmp("purport")
        status = []
        if td: status.append(f"translation(sim={td['similarity']})")
        elif tk != "diff": status.append(f"translation[{tk}]")
        if pd: status.append(f"purport(sim={pd['similarity']})")
        elif pk != "diff": status.append(f"purport[{pk}]")
        real = bool(td or pd)
        print(f"  {r}: {', '.join(status) if status else 'identical'}")
        if td or pd:
            report.append({"ref": r, "translation_diff": td, "purport_diff": pd,
                           "translation_status": tk, "purport_status": pk})
            # verbatim passages for the optional LLM classification step
            diffs.append({
                "ref": r,
                "translation": {"repo": rr["translation"], "pb": pb["translation"]} if td else None,
                "purport": {"repo": rr["purport"], "pb": pb["purport"]} if pd else None,
            })
        time.sleep(0.7)  # be polite to prabhupadabooks.com
    tag = f"sb-{canto}-{chapter}"
    (OUT / f"{tag}.report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    (OUT / f"{tag}.diffs.json").write_text(json.dumps(diffs, indent=1, ensure_ascii=False))
    print(f"\n{len(report)}/{len(refs)} verses differ. "
          f"Report: scripts/pb_diffs/{tag}.report.json | "
          f"LLM input: scripts/pb_diffs/{tag}.diffs.json")

if __name__ == "__main__":
    main()
