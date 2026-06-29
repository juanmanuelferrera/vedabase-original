#!/usr/bin/env python3
"""Normalize verse synonyms/translation to the English Vedabase convention:
  - synonyms : each term italicized, term—gloss separated by em-dash, pairs by '; '
  - translation : whole field wrapped in **bold**
Idempotent: applied to already-conformant English text it must be a no-op.
Applied only to real verses (verse_text present / synonyms present)."""
import re

def normalize_synonyms(syn):
    s = (syn or '').strip()
    if not s:
        return syn
    out = []
    for pair in s.split(';'):
        p = pair.strip()
        if not p:
            continue
        # term/gloss boundary = first en/em-dash (NOT the hyphen inside terms)
        m = re.match(r'^(.*?)\s*[–—]\s*(.*)$', p, re.S)
        if not m:
            out.append(p)                 # no separator — leave as-is
            continue
        term = m.group(1).replace('*', '').strip()   # strip ALL stray italics, re-wrap once
        gloss = m.group(2).strip()
        if not term:
            out.append(p); continue
        out.append(f'*{term}*—{gloss}')
    return '; '.join(out)

def normalize_translation(tr):
    t = (tr or '').strip()
    if not t:
        return tr
    if '**' in t:        # already has bold markup — don't touch
        return t
    return f'**{t}**'

def normalize_row(r):
    """Mutate a verse row in place. Only verses (have verse_text or synonyms)."""
    is_verse = bool((r.get('verse_text') or '').strip()) or bool((r.get('synonyms') or '').strip())
    if not is_verse:
        return r
    if (r.get('synonyms') or '').strip():
        r['synonyms'] = normalize_synonyms(r['synonyms'])
    if (r.get('translation') or '').strip():      # is_verse already true here
        r['translation'] = normalize_translation(r['translation'])
    return r
