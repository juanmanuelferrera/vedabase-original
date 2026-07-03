#!/usr/bin/env python3
"""
Step 2 (paid, cheap): classify verse-level diffs with Claude Haiku 4.5.

Reads a diffs.json produced by diff_prabhupadabooks.py (verbatim repo-vs-PB
passages for verses that differ) and asks claude-haiku-4-5 to categorize each
difference. Output: <name>.classified.json + <name>.classified.md.

Categories:
  EDITION_REVISION          whole passage rewritten (original vs revised edition)
  SUBSTANTIVE_MEANING_CHANGE meaning differs (not just style)
  MINOR_WORDING             small phrasing change, same meaning
  ADDED_REMOVED_TEXT        one side has extra/fewer sentences
  TYPO_OR_OCR               likely a transcription/OCR error in one source
  PUNCTUATION_FORMATTING    only punctuation/spacing/caps
  DIACRITICS_ONLY           only diacritic/spelling-of-Sanskrit differences

Usage:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 classify_diffs.py scripts/pb_diffs/sb-1-1.diffs.json
"""
import sys, os, json, re, pathlib
import anthropic

MODEL = "claude-haiku-4-5"
CATS = ["EDITION_REVISION", "SUBSTANTIVE_MEANING_CHANGE", "MINOR_WORDING",
        "ADDED_REMOVED_TEXT", "TYPO_OR_OCR", "PUNCTUATION_FORMATTING", "DIACRITICS_ONLY"]

PROMPT = """You compare two versions of a passage from Śrīla Prabhupāda's books.
A = vedabase-original repo. B = prabhupadabooks.com.
Classify how they differ. Reply ONLY with compact JSON:
{{"category":"<one of: %s>","severity":"<low|medium|high>","summary":"<≤20 words>"}}

[A — repo]
{a}

[B — prabhupadabooks]
{b}
""" % ", ".join(CATS)

def classify(client, a, b):
    msg = client.messages.create(
        model=MODEL, max_tokens=200,
        messages=[{"role": "user", "content": PROMPT.format(a=a[:6000], b=b[:6000])}],
    )
    txt = "".join(blk.text for blk in msg.content if blk.type == "text")
    m = re.search(r"\{.*\}", txt, re.S)
    try:
        return json.loads(m.group(0)) if m else {"category": "PARSE_ERROR", "summary": txt[:80]}
    except Exception:
        return {"category": "PARSE_ERROR", "summary": txt[:80]}

def main():
    if "ANTHROPIC_API_KEY" not in os.environ:
        sys.exit("Set ANTHROPIC_API_KEY first (export ANTHROPIC_API_KEY=sk-ant-...).")
    if len(sys.argv) < 2:
        sys.exit("usage: classify_diffs.py <diffs.json>")
    path = pathlib.Path(sys.argv[1])
    diffs = json.load(open(path))
    client = anthropic.Anthropic()
    out = []
    for d in diffs:
        for field in ("translation", "purport"):
            seg = d.get(field)
            if not seg:
                continue
            res = classify(client, seg["repo"], seg["pb"])
            res.update({"ref": d["ref"], "field": field})
            out.append(res)
            print(f"  {d['ref']:14s} {field:11s} {res.get('category'):26s} {res.get('summary','')}")
    base = path.with_suffix("").with_suffix("")  # strip .diffs.json
    tag = path.name.replace(".diffs.json", "")
    outdir = path.parent
    (outdir / f"{tag}.classified.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    from collections import Counter
    c = Counter(r["category"] for r in out)
    md = [f"# Diff classification (Haiku 4.5) — {tag}", "", "## Summary", ""]
    md += [f"- **{k}**: {v}" for k, v in c.most_common()]
    md += ["", "| ref | field | category | severity | summary |", "|---|---|---|---|---|"]
    md += [f"| {r['ref']} | {r['field']} | {r.get('category')} | {r.get('severity','')} | {r.get('summary','')} |" for r in out]
    (outdir / f"{tag}.classified.md").write_text("\n".join(md))
    print(f"\n{len(out)} passages classified. → {outdir}/{tag}.classified.md  (summary: {dict(c)})")

if __name__ == "__main__":
    main()
