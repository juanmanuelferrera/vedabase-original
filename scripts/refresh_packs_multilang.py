#!/usr/bin/env python3
"""Refresh vedabase-pwa frontend/data/<book>.json from D1, for MULTIPLE languages.

Closes the gap where offline packs only carried English (and es from a separate,
non-D1 source). Reads /tmp/d1md/<book>.<lang>.json (exported by sync_from_d1) and
rewrites each language's content in frontend/data, reusing build-content.py's exact
formatting (clean_blockquote + md_to_html + parse_prose_chapter).

Verse books: text/synonyms/translation/purport refreshed; devanagari/title preserved.
Prose books: chapters[key][lang] = {title, blocks}.
Only keys already present in frontend/data are touched (structure preserved).

Usage: refresh_packs_multilang.py --books sb bg --langs en es
"""
import argparse, json, re, tempfile, os, importlib.util
from pathlib import Path

PWA = Path('/Users/jaganat/git_projects/vedabase-pwa')
DUMP = Path('/tmp/d1md')
spec = importlib.util.spec_from_file_location('bc', PWA / 'build-content.py')
bc = importlib.util.module_from_spec(spec); spec.loader.exec_module(bc)

def strip_wiki(t):
    t = re.sub(r'\[\[+\s*[^\]|]*\|\s*([^\]]*?)\s*\]\]+', r'\1', t or '')
    return re.sub(r'\[\[+\s*([^\]|]*?)\s*\]\]+', r'\1', t)

def verse_fields(row):
    out = {}
    if (row.get('verse_text') or '').strip(): out['text'] = bc.clean_blockquote(row['verse_text'].strip())
    if (row.get('synonyms') or '').strip(): out['synonyms'] = bc.md_to_html(row['synonyms'].strip())
    if (row.get('translation') or '').strip():
        out['translation'] = bc.md_to_html(bc.clean_blockquote(row['translation'].strip()).replace('**',''))
    if (row.get('purport') or '').strip(): out['purport'] = bc.md_to_html(row['purport'].strip())
    return out

def prose_blocks(purport):
    tf = tempfile.NamedTemporaryFile('w', suffix='.md', delete=False, encoding='utf-8')
    tf.write(strip_wiki(purport or '')); tf.close()
    try: _t, blocks = bc.parse_prose_chapter(tf.name)
    finally: os.unlink(tf.name)
    out = []
    for b in blocks:
        h = bc.md_to_html(b['text'])
        if b['type'] == 'verse': h = h.replace('\n', '<br/>')
        out.append({'type': b['type'], 'html': h})
    return out

def refresh(book, langs):
    fp = PWA / 'frontend' / 'data' / f'{book}.json'
    if not fp.exists(): print(f'  {book}: no frontend/data file, skip'); return
    data = json.loads(fp.read_text())
    is_prose = 'chapters' in data and not data.get('verses')
    bucket = data.get('chapters') if is_prose else data.get('verses')
    if not bucket: print(f'  {book}: empty, skip'); return
    total = {}
    for lang in langs:
        dl = DUMP / f'{book}.{lang}.json'
        if not dl.exists(): print(f'  {book}/{lang}: no dump, skip'); continue
        rows = json.loads(dl.read_text())[0]['results']
        by_key = {r['ref'].split('/', 1)[1] if '/' in r['ref'] else r['ref']: r for r in rows}
        upd = 0
        for key, langs_d in bucket.items():
            if key not in by_key: continue
            row = by_key[key]
            if is_prose:
                new = {'title': (row.get('translation') or (langs_d.get(lang, {}) or {}).get('title') or '').strip(),
                       'blocks': prose_blocks(row.get('purport'))}
            else:
                cur = dict(langs_d.get(lang, {}))   # preserve title/devanagari
                cur.update(verse_fields(row)); new = cur
            if langs_d.get(lang) != new:
                langs_d[lang] = new; upd += 1
        total[lang] = upd
    fp.write_text(json.dumps(data, ensure_ascii=False))
    print(f'  {book}: updated { {l: total.get(l, 0) for l in langs} }')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', nargs='+', required=True)
    ap.add_argument('--langs', nargs='+', default=['en', 'es'])
    a = ap.parse_args()
    for b in a.books:
        refresh(b, a.langs)
