#!/usr/bin/env python3
"""sync-from-d1 — one batch sync from the D1 source of truth to every surface.

Reads corrections.jsonl (the change list), applies it to D1 in all languages,
then regenerates ONLY the affected books across: the GitHub repo (markdown),
the offline-app packs (both hosts), and the download books (epub/pdf/mobi).
The website needs nothing — vedabase.cc reads D1 live.

Pipeline (dependency order):
  1. apply   — corrections.jsonl -> D1 (REPLACE per ref+lang)            [touches D1]
  (translations must already be in each entry; the script does NOT invent them)
  2. repo    — build_from_d1 affected books -> commit/push vedabase-original
  3. packs   — refresh frontend/data (en/es..) from D1 -> build -> upload
               to BOTH pack hosts -> purge
  4. books   — build_all_books --only (epub+pdf, en/es/pt) -> mobi -> upload
               to downloads/ -> purge
  5. verify  — spot-check live

SAFE BY DEFAULT: prints what it would do. Pass --execute to act for real.

Usage:
  python3 scripts/sync_from_d1.py --phase apply --execute
  python3 scripts/sync_from_d1.py --phase packs            # dry-run
  python3 scripts/sync_from_d1.py --phase all --execute
  python3 scripts/sync_from_d1.py --only sb-canto-1 --phase books --execute
"""
import argparse, json, re, subprocess, sys, os
from pathlib import Path

# ---- paths / config (account & zone IDs are NOT secret) ----
VO    = Path('/Users/jaganat/git_projects/vedabase-original')
ASTRO = Path('/Users/jaganat/git_projects/astro_vedabase')
PWA   = Path('/Users/jaganat/git_projects/vedabase-pwa')
EPUB_PY = '/Users/jaganat/git_projects/vedabase-epubs/.venv/bin/python'
D1 = 'vedabase-search-db'
ACCOUNT = '40035612bce74407c306499494965595'
ZONE    = 'e1b1110e90a81df5a93b900f1fd8d4dc'
CHANGELOG = VO / 'corrections.jsonl'
DUMP = Path('/tmp/d1md')
# pack content languages to source from D1 (the gap: es/pt/hi were never in packs)
PACK_LANGS = ['en', 'es']          # add 'pt','hi' once the app UI shows them
BOOK_LANGS = ['en', 'es', 'pt']    # download-book generator supports en/es/pt (no hi)
PACK_HOSTS = ['vedabase-files/packs', 'vedabase-site-content/app/packs']  # vedabase.cc + app.vedabase.cc

DRY = True
def sh(cmd, cwd=None, capture=False):
    print('  $', ' '.join(cmd) if isinstance(cmd, list) else cmd)
    if DRY: return ''
    r = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str),
                       capture_output=capture, text=True)
    if capture: return r.stdout
    return ''

def wr(args, capture=True):
    """wrangler via OAuth (unset token envs, like the repo's scripts)."""
    env = dict(os.environ); env.pop('CF_API_TOKEN', None); env.pop('CLOUDFLARE_API_TOKEN', None)
    cmd = ['npx', 'wrangler'] + args
    print('  $ wrangler', ' '.join(args[:4]), '...')
    if DRY: return ''
    return subprocess.run(cmd, cwd=str(ASTRO), env=env, capture_output=capture, text=True).stdout

def load_changes():
    if not CHANGELOG.exists():
        CHANGELOG.write_text(''); print(f'created empty {CHANGELOG}'); return []
    return [json.loads(l) for l in CHANGELOG.read_text().splitlines() if l.strip()]

# ---- ref -> targets ----
def affected(changes):
    """Return dicts of affected: d1 books, pack ids, download slugs, repo books."""
    d1books, packs, dl = set(), set(), set()
    for c in changes:
        seg = c['ref'].split('/')
        book = seg[0]; d1books.add(book)
        if book == 'sb':
            if len(seg) > 1 and seg[1].isdigit():        # a canto verse
                packs.add(f'sb-{seg[1]}'); dl.add(f'sb-canto-{seg[1]}')
            # else: front matter (sb/0a, sb/0b) -> repo only, no canto pack/download
        elif book == 'cc':
            if len(seg) > 1 and seg[1] in ('adi', 'madhya', 'antya'):
                packs.add(f'cc-{seg[1]}'); dl.add('cc')   # cc download slug — review if cc is split
        else:
            packs.add(book); dl.add(book)
    return {'d1books': sorted(d1books), 'packs': sorted(packs), 'downloads': sorted(dl)}

# ---- phase 1: apply changelog to D1 ----
def phase_apply(changes):
    print('\n== PHASE apply -> D1 ==')
    for c in changes:
        for lang, (old, new) in c.get('replace', {}).items():
            sql = (f"UPDATE verses SET {c['field']}=REPLACE({c['field']},"
                   f" '{old.replace(chr(39), chr(39)*2)}', '{new.replace(chr(39), chr(39)*2)}')"
                   f" WHERE book='{c['ref'].split('/')[0]}' AND ref='{c['ref']}' AND lang='{lang}';")
            wr(['d1', 'execute', D1, '--remote', '--command', sql], capture=False)

# ---- phase 2: repo ----
def phase_repo(aff):
    print('\n== PHASE repo (build_from_d1 -> commit) ==')
    for b in aff['d1books']:
        export_d1_book(b, 'en')
    sh(['python3', str((VO/'scripts/build_from_d1.py'))])
    sh(['git', 'add', '-A'], cwd=str(VO))
    sh(['git', 'commit', '-m', 'sync: regenerate affected books from D1'], cwd=str(VO))
    sh(['git', 'push', 'origin', 'main'], cwd=str(VO))

# ---- phase 3: packs (multi-language refresh from D1) ----
def export_d1_book(book, lang):
    DUMP.mkdir(exist_ok=True)
    sql = (f"SELECT ref,book,devanagari,verse_text,synonyms,translation,purport "
           f"FROM verses WHERE lang='{lang}' AND book='{book}';")
    print(f'  export D1 {book}/{lang} -> {DUMP}/{book}.{lang}.json')
    if DRY: return
    out = wr(['d1', 'execute', D1, '--remote', '--json', '--command', sql])
    (DUMP / f'{book}.{lang}.json').write_text(out)

def phase_packs(aff):
    print('\n== PHASE packs (refresh frontend/data multi-lang -> build -> upload both hosts -> purge) ==')
    for b in aff['d1books']:
        for lang in PACK_LANGS:
            export_d1_book(b, lang)
    print(f'  refresh frontend/data for {aff["d1books"]} langs={PACK_LANGS}')
    sh([sys.executable, str(VO/'scripts/refresh_packs_multilang.py'),
        '--books', *aff['d1books'], '--langs', *PACK_LANGS])
    sh([sys.executable, 'packer/build_all.py', '--out', '/tmp/vbpacks_v3'], cwd=str(PWA))
    for pid in aff['packs']:
        f = f'/tmp/vbpacks_v3/{pid}.vbpack.gz'
        for host in PACK_HOSTS:
            wr(['r2', 'object', 'put', f'{host}/{pid}.vbpack.gz', '--file', f,
                '--content-type', 'application/gzip', '--remote'], capture=False)
        purge([f'https://vedabase.cc/packs/{pid}.vbpack.gz',
               f'https://app.vedabase.cc/packs/{pid}.vbpack.gz'])

# ---- phase 4: books ----
def phase_books(aff):
    print('\n== PHASE books (epub+pdf+mobi -> downloads/ -> purge) ==')
    rb = ASTRO/'scripts/regen_books'
    sh([EPUB_PY, 'build_all_books.py', '--only', *aff['downloads'],
        '--langs', *BOOK_LANGS], cwd=str(rb))
    for slug in aff['downloads']:
        for lang in BOOK_LANGS:
            suf = '' if lang == 'en' else f'-{lang}'
            epub = rb/f'output/{slug}-{lang}.epub'
            sh(['ebook-convert', str(epub), str(rb/f'output/{slug}-{lang}.mobi')])
            for ext in ('epub', 'pdf', 'mobi'):
                wr(['r2', 'object', 'put', f'vedabase-files/downloads/{slug}{suf}.{ext}',
                    '--file', str(rb/f'output/{slug}-{lang}.{ext}'), '--remote'], capture=False)
        purge([f'https://vedabase.cc/downloads/{slug}.{e}' for e in ('epub','pdf','mobi')])

def purge(urls):
    tok = os.environ.get('CF_API_TOKEN', '')
    if not tok:
        print('  (purge skipped: CF_API_TOKEN not in env — `source ~/.zshrc.local` first)'); return
    import json as j
    print('  purge', len(urls), 'urls')
    if DRY: return
    subprocess.run(['curl', '-s', '-X', 'POST',
        f'https://api.cloudflare.com/client/v4/zones/{ZONE}/purge_cache',
        '-H', f'Authorization: Bearer {tok}', '-H', 'Content-Type: application/json',
        '--data', j.dumps({'files': urls})], capture_output=True)

def phase_verify(aff):
    print('\n== PHASE verify (spot-check live) ==')
    for pid in aff['packs']:
        print(f'  curl -sI https://vedabase.cc/packs/{pid}.vbpack.gz')

def main():
    global DRY
    ap = argparse.ArgumentParser()
    ap.add_argument('--phase', default='all',
                    choices=['apply','repo','packs','books','verify','all'])
    ap.add_argument('--only', nargs='*', help='limit to these d1 books (e.g. sb)')
    ap.add_argument('--execute', action='store_true', help='actually run (default: dry-run)')
    a = ap.parse_args()
    DRY = not a.execute
    changes = load_changes()
    if a.only:
        changes = [c for c in changes if c['ref'].split('/')[0] in set(a.only)]
    aff = affected(changes)
    print(f"{'EXECUTE' if a.execute else 'DRY-RUN'} | {len(changes)} change(s) | affected: {aff}")
    ph = a.phase
    if ph in ('apply','all'): phase_apply(changes)
    if ph in ('repo','all'):  phase_repo(aff)
    if ph in ('packs','all'): phase_packs(aff)
    if ph in ('books','all'): phase_books(aff)
    if ph in ('verify','all'): phase_verify(aff)
    print('\nDone' + ('' if a.execute else ' (dry-run — nothing changed)'))

if __name__ == '__main__':
    main()
