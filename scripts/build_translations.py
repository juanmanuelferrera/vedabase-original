#!/usr/bin/env python3
"""Build vedabase-original/translations/ : canonical per-book jsonl + generated
Markdown mirroring the English repo layout, for en/es/hi/pt/ru.

- Translation text  : from traducciones_vedabase per-book jsonl (complete, verified).
- English text      : from the vedabase-original repo Markdown (repo_source).
- English devanagari: from D1 (ref+devanagari ONLY), Indic-script-guarded.
- Markdown view     : mirrors each English file's path & heading; devanagari omitted;
                      italics/bold preserved verbatim.
"""
import json, re, sys, os, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # this scripts/ dir
sys.path.insert(0, '/Users/jaganat/git_projects/astro_vedabase/scripts/regen_books')
import repo_source as rs
import dump_d1_translations_to_repo as dd   # TV, LANG_ROOT, FOLDER(book->traducciones folder)
import translation_normalize as N           # synonyms italic + translation bold (English convention)

VO   = Path(__file__).resolve().parent.parent              # vedabase-original repo root
OUT  = Path(os.environ['VB_OUT']) if os.environ.get('VB_OUT') else VO / 'translations'
ASTRO = Path('/Users/jaganat/git_projects/astro_vedabase')
LANG_DIR = {'en':'english','es':'espanol','hi':'hindi','pt':'portugues','ru':'russian'}

# ---- English ref -> (relpath, heading_line, mode) map, built by walking the repo ----
# permissive verse-ref recognition (allows letter-suffix verses 1a/1b and ranges,
# and .summary) which repo_source.numbered_ref rejects.
# verse segment = digits (+ optional letter, + optional range), OR a chapter-level
# keyword (summary/notes) that repo_source.numbered_ref doesn't recognize.
_SEG = r'(\d+[a-z]?(?:-\d+[a-z]?)?|summary|notes)'
_PV_BG = re.compile(rf'^bg-(\d+)\.{_SEG}$')
_PV_SB = re.compile(rf'^sb-(\d+)\.(\d+)\.{_SEG}$')
_PV_CC = re.compile(rf'^cc-(adi|madhya|antya)-(\d+)\.{_SEG}$')

def permissive_ref(slug, stem):
    if slug == 'bg':
        x = _PV_BG.match(stem);  return f'bg/{int(x[1])}/{x[2]}' if x else None
    if slug.startswith('sb-canto-'):
        x = _PV_SB.match(stem);  return f'sb/{int(x[1])}/{int(x[2])}/{x[3]}' if x else None
    if slug.startswith('cc-'):
        x = _PV_CC.match(stem);  return f'cc/{x[1]}/{int(x[2])}/{x[3]}' if x else None
    return rs.numbered_ref(slug, stem)   # flat books unchanged

def english_ref_map():
    """For every English content file: ref -> (relative path, '### heading' line, mode)."""
    m = {}
    for slug, folder in rs.FOLDER.items():
        base = VO / folder
        if not base.exists():
            continue
        mode = rs.book_mode(slug)
        book = slug.split('-')[0]   # bg, sb, cc, iso, ...
        files = rs._content_files(slug)
        numbered = []
        for f in files:
            ref = permissive_ref(slug, f.stem)
            if ref is None:
                continue
            numbered.append(f)
            m[ref] = (f.relative_to(VO), _heading(f), mode)
        # genuine front matter = files NOT recognized as numbered/summary verses
        fm = sorted((f for f in files if f not in set(numbered)), key=rs._fm_sort_key)
        for i, f in enumerate(fm):
            suffix = chr(ord('a')+i) if i < 26 else f'a{i-25}'
            m[f'{book}/0{suffix}'] = (f.relative_to(VO), _heading(f), mode)
    # book-level front matter for nested books (lives at the book ROOT, not under
    # canto/lila folders, so the per-slug walk above never sees it).
    for book, root in [('sb', 'srimad-bhagavatam'), ('cc', 'sri-caitanya-caritamrta')]:
        rootp = VO / root
        roots = sorted((f for f in rootp.glob('*.md') if f.name not in rs._SKIP_FILES),
                       key=rs._fm_sort_key)
        for i, f in enumerate(roots):
            suffix = chr(ord('a')+i) if i < 26 else f'a{i-25}'
            m.setdefault(f'{book}/0{suffix}', (f.relative_to(VO), _heading(f), 'prose'))
    return m

def _heading(f):
    for ln in f.read_text(encoding='utf-8').splitlines():
        if ln.lstrip().startswith('###'):
            return ln.rstrip()
        if ln.strip():
            break
    return None

def _en_slugs(book):
    if book == 'sb': return [s for s in rs.FOLDER if s.startswith('sb-canto-')]
    if book == 'cc': return ['cc-adi','cc-madhya','cc-antya']
    return [book] if book in rs.FOLDER else []

def _en_book_folder(book):
    if book == 'sb': return 'srimad-bhagavatam'
    if book == 'cc': return 'sri-caitanya-caritamrta'
    return rs.FOLDER.get(book, book)

def _merge_colophons(book, rows):
    """Append each colophon file's text to the last verse in its directory
    (bg's 'Thus end the Bhaktivedanta Purports…' closings), matching repo_source."""
    for slug in _en_slugs(book):
        for cf in rs._colophon_files(slug):
            cdir = str(cf.parent.relative_to(VO))
            same = [r for r in rows if str(Path(r['_rel']).parent) == cdir]
            if not same:
                continue
            last = max(same, key=lambda r: dd.verse_sort_key(r['ref']))
            colo = re.sub(r'^\s*#{1,6}[^\n]*\n+', '', cf.read_text(encoding='utf-8').strip()).strip()
            if colo:
                last['purport'] = (last['purport'] + '\n\n' + colo).strip() if last.get('purport') else colo

def derive_target(ref):
    """Fallback path/heading for a translation ref with no matching English file
    (verse-grouping differences, summaries, lila front matter). Mirrors English
    naming conventions; reuses the real English heading if such a file exists."""
    p = ref.split('/')
    relpath = heading = None
    if p[0] == 'bg' and len(p) >= 3:
        C, rest = p[1], '.'.join(p[2:])
        relpath = Path(f'bhagavad-gita-as-it-is/chapter-{int(C):02d}/bg-{C}.{rest}.md')
        heading = f'### Bg {C}.{rest}'
    elif p[0] == 'sb' and len(p) >= 4:
        C, H, rest = p[1], p[2], '.'.join(p[3:])
        relpath = Path(f'srimad-bhagavatam/canto-{int(C):02d}/chapter-{int(H):02d}/sb-{C}.{H}.{rest}.md')
        heading = f'### SB {C}.{H}.{rest}'
    elif p[0] == 'cc' and len(p) >= 4:
        lila, H, rest = p[1], p[2], '.'.join(p[3:])
        relpath = Path(f'sri-caitanya-caritamrta/{lila}-lila/chapter-{int(H):02d}/cc-{lila}-{H}.{rest}.md')
        heading = f'### CC {lila.capitalize()} {H}.{rest}'
    elif p[0] == 'cc' and len(p) == 3:        # lila front matter: cc/adi/0a
        lila, seg = p[1], p[2]
        relpath = Path(f'sri-caitanya-caritamrta/{lila}-lila/front-{seg}.md')
        heading = None
    if relpath is None:
        return None
    f = VO / relpath
    if f.exists():
        h = _heading(f)
        if h: heading = h
    return relpath, heading, 'verse'

def field(v): return (v or '').strip()

def render_row(row, heading, mode):
    """Render one row to Markdown. devanagari intentionally omitted (English convention)."""
    parts = [heading] if heading else []
    if mode == 'verse':
        order = ('verse_text','synonyms','translation','purport')
    else:                       # prose / lob: translation holds the title/bold line
        order = ('verse_text','synonyms','translation','purport')
    body = [field(row.get(k)) for k in order]
    body = [b for b in body if b]
    return ('\n\n'.join(parts + body)).rstrip() + '\n'

# ---- D1 devanagari for English (ref+devanagari only), guarded ----
LATIN = re.compile(r'[A-Za-zĀ-ſ]')
def d1_devanagari(book):
    env = dict(os.environ); env.pop('CF_API_TOKEN',None); env.pop('CLOUDFLARE_API_TOKEN',None)
    out, last = {}, 0
    while True:
        sql = (f"SELECT id, ref, devanagari FROM verses WHERE lang='en' AND book='{book}' "
               f"AND id>{last} ORDER BY id LIMIT 400;")
        r = subprocess.run(['npx','wrangler','d1','execute','vedabase-search-db','--remote',
                            '--json','--command',sql], cwd=ASTRO, env=env,
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            raise RuntimeError(r.stderr[-300:])
        rows = json.loads(r.stdout)[0]['results']
        if not rows: break
        for x in rows:
            d = x.get('devanagari') or ''
            if d and LATIN.search(d):
                raise SystemExit(f'GUARD FAIL: Latin text in devanagari for {x["ref"]}')
            if d: out[x['ref']] = d
            last = x['id']
        if len(rows) < 400: break
    return out

def write_jsonl(path, rows, cols):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as fh:
        for r in rows:
            fh.write(json.dumps({c:(r.get(c) or '') for c in cols}, ensure_ascii=False)+'\n')

COLS = ['ref','book','lang','url','verse_text','devanagari','synonyms','translation','purport']

if __name__ == '__main__':
    only = sys.argv[1:] or None     # optional book slugs to limit (sample run)
    EMAP = english_ref_map()
    print(f'English ref map: {len(EMAP)} refs')
    stats = {}
    unmapped = {}

    # ---------- translations ----------
    for lang in ('es','hi','pt','ru'):
        root = dd.TV / dd.LANG_ROOT[lang]
        nmd = njsonl = nun = 0
        for book, tfolder in dd.FOLDER.items():
            if only and book not in only: continue
            src = root / tfolder / f'{book}_{lang}.jsonl'
            if not src.exists(): continue
            rows = [json.loads(l) for l in src.read_text(encoding='utf-8').splitlines() if l.strip()]
            for r in rows: N.normalize_row(r)   # synonyms italic + translation bold (English convention)
            # canonical jsonl (normalized, normalized columns)
            en_folder = _en_book_folder(book)
            write_jsonl(OUT/LANG_DIR[lang]/en_folder/f'{book}_{lang}.jsonl', rows, COLS); njsonl += 1
            # markdown mirroring English paths
            for r in rows:
                ref = r['ref']
                if ref in EMAP:
                    relpath, heading, mode = EMAP[ref]
                else:
                    d = derive_target(ref)
                    if d is None:
                        unmapped.setdefault(lang, []).append(ref); nun += 1; continue
                    relpath, heading, mode = d
                target = OUT/LANG_DIR[lang]/relpath
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(render_row(r, heading, mode), encoding='utf-8')
                nmd += 1
        stats[lang] = (njsonl, nmd, nun)
        print(f'  {lang}: {njsonl} jsonl, {nmd} md, {nun} unmapped')

    # ---------- english jsonl (repo text via EMAP refs + D1 devanagari) ----------
    if not os.environ.get('SKIP_EN'):
        from collections import defaultdict
        by_book = defaultdict(list)
        for ref, (rel, heading, mode) in EMAP.items():
            by_book[ref.split('/')[0]].append((ref, rel, mode))
        for book in dd.FOLDER:
            if only and book not in only: continue
            refs = by_book.get(book, [])
            if not refs: continue
            rows = []
            for ref, rel, mode in refs:
                fields = rs.parse_content((VO/rel).read_text(encoding='utf-8'), mode)
                fields.update(ref=ref, book=book, lang='en', _rel=str(rel))
                rows.append(fields)
            _merge_colophons(book, rows)              # bg "Thus end…" colophons
            dev = {}
            try: dev = d1_devanagari(book)
            except Exception as e: print(f'    en/{book} devanagari pull failed: {e}')
            ndev = 0
            for r in rows:
                if r['ref'] in dev: r['devanagari'] = dev[r['ref']]; ndev += 1
                r.pop('_rel', None)
            rows.sort(key=lambda r: dd.verse_sort_key(r['ref']))
            write_jsonl(OUT/'english'/_en_book_folder(book)/f'{book}_en.jsonl', rows, COLS)
            print(f'  en/{book}: {len(rows)} rows, {ndev} devanagari')

    if unmapped:
        print('\nUNMAPPED refs (sample):')
        for lang, refs in unmapped.items():
            print(f'  {lang}: {len(refs)}  e.g. {refs[:8]}')
