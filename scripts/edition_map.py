#!/usr/bin/env python3
"""
Free (0-token) edition map: vedabase-original repo vs prabhupadabooks.com.

Scans EVERY chapter of every verse-book (SB, BG, CC) by sampling its first
verse's translation and comparing (ASCII-folded) against prabhupadabooks.com.
Because the divergence is at the edition level (whole chapters are original or
revised), one verse per chapter classifies the whole chapter. Pure diff — no API.

Output:
  scripts/pb_diffs/EDITION_MAP.md    — human-readable list of diffs
  scripts/pb_diffs/edition_map.json  — machine-readable
"""
import re, html, json, time, unicodedata, subprocess, pathlib, difflib

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "scripts" / "pb_diffs"; OUT.mkdir(exist_ok=True)

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().replace("—", "-").replace("–", "-")
    s = re.sub(r"[‘’`´]", "'", s); s = re.sub(r"[“”]", '"', s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def repo_translations(path, ref_re):
    """{ref: translation} for headers matching ref_re (capturing the ref)."""
    text = pathlib.Path(path).read_text(encoding="utf-8")
    parts = re.split(rf"\n###\s+({ref_re})\s*\n", text)
    out = {}
    for i in range(1, len(parts), 2):
        ref, body = parts[i].strip(), parts[i + 1]
        tm = re.search(r"\*\*(.+?)\*\*", body, re.S)
        if tm:
            out[ref] = tm.group(1).strip()
    return out

def pb_translation(url):
    raw = subprocess.run(["curl", "-4", "-sL", url], capture_output=True, timeout=40).stdout
    t = raw.decode("cp1252", errors="replace")
    m = re.search(r'class="Translation"[^>]*>(.*?)</(?:div|p)>', t, re.S)
    if not m:
        return ""
    x = re.sub(r"<[^>]+>", " ", m.group(1))
    return re.sub(r"\s+", " ", html.unescape(x)).strip()

def verdict(sim):
    if sim is None: return "NO_DATA"
    if sim >= 0.85: return "ORIGINAL (match)"
    if sim < 0.50:  return "REVISED (differs)"
    return "MIXED"

# Build the full chapter work-list: (book_label, repo_ref, pb_url)
JOBS = []

# --- SB: cantos 1..10, first verse of each chapter ---
for c in range(1, 11):
    tr = repo_translations(REPO / "srimad-bhagavatam" / f"canto-{c:02d}.md", r"SB [\d.]+")
    chapters = {}
    for ref in tr:
        m = re.match(rf"SB {c}\.(\d+)\.(\d+)", ref)
        if m:
            ch, v = int(m.group(1)), int(m.group(2))
            chapters.setdefault(ch, (v, ref))
            if v < chapters[ch][0]:
                chapters[ch] = (v, ref)
    for ch in sorted(chapters):
        v, ref = chapters[ch]
        JOBS.append((f"SB {c}.{ch}", ref, tr[ref], f"https://prabhupadabooks.com/sb/{c}/{ch}/{v}"))

# --- BG: chapters 1..18 ---
trbg = repo_translations(REPO / "bhagavad-gita-as-it-is.md", r"Bg [\d.]+")
bgch = {}
for ref in trbg:
    m = re.match(r"Bg (\d+)\.(\d+)", ref)
    if m:
        ch, v = int(m.group(1)), int(m.group(2))
        bgch.setdefault(ch, (v, ref))
        if v < bgch[ch][0]:
            bgch[ch] = (v, ref)
for ch in sorted(bgch):
    v, ref = bgch[ch]
    JOBS.append((f"BG {ch}", ref, trbg[ref], f"https://prabhupadabooks.com/bg/{ch}/{v}"))

# --- CC: adi / madhya / antya ---
for lila, fn in [("adi", "adi-lila.md"), ("madhya", "madhya-lila.md"), ("antya", "antya-lila.md")]:
    label = lila.capitalize()
    tr = repo_translations(REPO / "sri-caitanya-caritamrta" / fn, rf"CC {label} [\d.\-]+")
    chs = {}
    for ref in tr:
        m = re.match(rf"CC {label} (\d+)\.([\d\-]+)", ref)
        if m:
            ch = int(m.group(1)); v = int(m.group(2).split("-")[0])
            chs.setdefault(ch, (v, ref))
            if v < chs[ch][0]:
                chs[ch] = (v, ref)
    for ch in sorted(chs):
        v, ref = chs[ch]
        JOBS.append((f"CC {label} {ch}", ref, tr[ref], f"https://prabhupadabooks.com/cc/{lila}/{ch}/{v}"))

print(f"Total chapters to scan: {len(JOBS)}")
rows = []
for label, ref, repo_tr, url in JOBS:
    try:
        pb = pb_translation(url)
    except Exception as e:
        pb = ""
    sim = round(difflib.SequenceMatcher(None, norm(repo_tr).split(), norm(pb).split()).ratio(), 3) if pb else None
    vd = verdict(sim)
    rows.append({"chapter": label, "sample_ref": ref, "similarity": sim, "verdict": vd, "url": url})
    print(f"  {label:16s} {ref:18s} sim={sim}  {vd}")
    time.sleep(0.6)

# write outputs
(OUT / "edition_map.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
from collections import Counter
cnt = Counter(r["verdict"] for r in rows)
md = ["# Edition map — vedabase-original repo vs prabhupadabooks.com",
      "",
      "Free diff, sampled at the first verse of every chapter. "
      "REVISED = repo translation differs from prabhupadabooks (likely revised edition); "
      "ORIGINAL = matches; MIXED = partial; NO_DATA = page not found.",
      "",
      "## Summary",
      ""]
for k, v in cnt.most_common():
    md.append(f"- **{k}**: {v} chapters")
md += ["", "## Chapters that DIFFER (REVISED or MIXED)", "",
       "| Chapter | sample | similarity | verdict |", "|---|---|---|---|"]
for r in rows:
    if r["verdict"].startswith("REVISED") or r["verdict"] == "MIXED" or r["verdict"] == "NO_DATA":
        md.append(f"| {r['chapter']} | {r['sample_ref']} | {r['similarity']} | {r['verdict']} |")
md += ["", "## Chapters that MATCH (ORIGINAL)", "",
       "| Chapter | sample | similarity |", "|---|---|---|"]
for r in rows:
    if r["verdict"].startswith("ORIGINAL"):
        md.append(f"| {r['chapter']} | {r['sample_ref']} | {r['similarity']} |")
(OUT / "EDITION_MAP.md").write_text("\n".join(md))
print("\nSummary:", dict(cnt))
print("Wrote scripts/pb_diffs/EDITION_MAP.md and edition_map.json")
