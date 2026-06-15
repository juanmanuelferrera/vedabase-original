#!/usr/bin/env python3
"""Build one Markdown file per book from the vedabase.cc D1 export (/tmp/d1md/*.json).

Each verse is rendered in standard Vedabase order, preserving the markdown that is
already stored in D1 (Devanāgarī/Bengali blockquotes, IAST blockquotes, *italic*
synonyms, **bold** translation, italics inside purports):

    ### SB 1.1.1
    > <devanāgarī / bengali śloka>
    > <iast transliteration>
    *word*—gloss; ...
    **translation**
    purport ...

Output goes to vedabase-cc/<slug>.md (alongside the existing vedabase.site files,
so the two can be diffed). lang='en' only — the original Prabhupāda edition.
"""
import json, re, glob, os
from letters_format import format_letter

SRC = '/tmp/d1md'
OUT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))   # repo root

# book code -> (output slug, display title). Slugs match the existing repo files.
BOOKS = {
 'bg':   ('bhagavad-gita-as-it-is',                 'Bhagavad-gītā As It Is'),
 'sb':   ('srimad-bhagavatam',                      'Śrīmad-Bhāgavatam'),
 'cc':   ('sri-caitanya-caritamrta',                'Śrī Caitanya-caritāmṛta'),
 'kb':   ('krsna-the-supreme-personality-of-godhead','Kṛṣṇa, the Supreme Personality of Godhead'),
 'nod':  ('nectar-of-devotion',                     'The Nectar of Devotion'),
 'noi':  ('nectar-of-instruction',                  'The Nectar of Instruction'),
 'iso':  ('isopanisad',                             'Śrī Īśopaniṣad'),
 'tlc':  ('teachings-of-lord-caitanya',             'Teachings of Lord Caitanya'),
 'tqk':  ('teachings-of-queen-kunti',               'Teachings of Queen Kuntī'),
 'ssr':  ('science-of-self-realization',            'The Science of Self-Realization'),
 'rv':   ('raja-vidya',                             'Rāja-Vidyā: The King of Knowledge'),
 'pop':  ('path-of-perfection',                     'The Path of Perfection'),
 'pqpa': ('perfect-questions-perfect-answers',      'Perfect Questions, Perfect Answers'),
 'poy':  ('perfection-of-yoga',                     'The Perfection of Yoga'),
 'bbd':  ('beyond-birth-and-death',                 'Beyond Birth and Death'),
 'ej':   ('easy-journey-to-other-planets',          'Easy Journey to Other Planets'),
 'ekc':  ('elevation-to-krsna-consciousness',       'Elevation to Kṛṣṇa Consciousness'),
 'lcfl': ('life-comes-from-life',                   'Life Comes from Life'),
 'lob':  ('light-of-the-bhagavata',                 'Light of the Bhāgavata'),
 'owk':  ('on-the-way-to-krsna',                    'On the Way to Kṛṣṇa'),
 'krp':  ('reservoir-of-pleasure',                  'Kṛṣṇa, the Reservoir of Pleasure'),
 'ttp':  ('topmost-yoga-system',                    'Kṛṣṇa Consciousness: The Topmost Yoga System'),
 'letters':     ('letters',     'Letters'),
 'transcripts': ('transcripts', 'Lectures & Conversations'),
}

LILA = {'adi': ('Ādi-līlā', 1), 'madhya': ('Madhya-līlā', 2), 'antya': ('Antya-līlā', 3)}


def sort_key(ref):
    """Natural sort key over ref segments (numbers numeric, lila in canonical order,
    ranges like '24-26' by first number, slugs alphabetically last)."""
    key = []
    for p in ref.split('/')[1:]:
        if p in LILA:
            key.append((0, LILA[p][1], ''))
        else:
            m = re.match(r'(\d+)', p)
            if m:
                key.append((0, int(m.group(1)), p))
            else:
                key.append((1, 0, p))  # textual slug -> after numerics
    return key


def chapter_label(book, ref):
    p = ref.split('/')
    if book == 'sb' and len(p) >= 4 and p[1].isdigit() and p[2].isdigit():
        return f'Canto {p[1]}, Chapter {p[2]}'
    if book == 'cc' and len(p) >= 4 and p[1] in LILA:
        return f'{LILA[p[1]][0]}, Chapter {p[2]}'
    if book == 'bg' and len(p) >= 3 and p[1].isdigit():
        return f'Chapter {p[1]}'
    return None


def verse_label(book, ref):
    """Human reference for the per-verse heading, e.g. 'SB 1.1.1', 'CC Adi 1.1'."""
    p = ref.split('/')
    if book == 'sb':
        return 'SB ' + '.'.join(p[1:])
    if book == 'cc' and len(p) >= 4 and p[1] in LILA:
        return f'CC {p[1].capitalize()} {p[2]}.{p[3]}'
    if book == 'bg' and len(p) >= 3:
        return f'Bg {p[1]}.{p[2]}'
    if book == 'iso':
        return f'Īśo {p[-1]}'
    # prose / single-segment books: just the trailing segment
    return p[-1].replace('-', ' ').strip()


def field(v):
    return (v or '').strip()


def render_verse(book, r):
    out = []
    dev = field(r.get('devanagari'))
    tr  = field(r.get('verse_text'))
    syn = field(r.get('synonyms'))
    tx  = field(r.get('translation'))
    pu  = field(r.get('purport'))
    if dev:
        out.append(dev)
    if tr:
        out.append(tr)
    if syn:
        out.append(syn)
    if tx:
        out.append(tx)
    if pu:
        out.append(pu)
    return '\n\n'.join(out)


def render_verses(code, rows, title):
    """Render a group of verse rows (with chapter headings) into a Markdown parts list."""
    parts = [f'# {title}\n']
    cur_ch = None
    for r in rows:
        ref = r['ref']
        ch = chapter_label(code, ref)
        if ch and ch != cur_ch:
            cur_ch = ch
            parts.append(f'## {ch}\n')
        body = render_verse(code, r)
        if not body:
            continue
        parts.append(f'### {verse_label(code, ref)}\n')
        parts.append(body + '\n')
    return parts


def render_transcript(r):
    """Render one lecture/conversation: lift the metadata header, strip the scrape's
    [#bbNNN] paragraph anchors and [[[ref|Text]]] wiki-links (keeping editorial
    markers like [?], [break]). Preserves the **Speaker:** labels, *italics*, and
    > verse blockquotes already in the data."""
    title = (r.get('translation') or r['ref'].split('/', 1)[1]).strip().splitlines()[0]
    pu = r.get('purport') or ''
    meta = ''
    hm = re.match(r'(.*?Audio file:[^\n]*)', pu)
    if hm:
        meta = re.sub(r'^' + re.escape(title) + r'\s*', '', hm.group(1)).strip()
        pu = pu[hm.end():]
    pu = re.sub(r'\[#\w+\]\n?', '', pu)                                   # paragraph anchors
    pu = re.sub(r'\[\[+\s*[^\]|]*\|\s*([^\]]*?)\s*\]\]+', r'\1', pu)      # [[[ref|Text]]] -> Text
    pu = re.sub(r'\[\[+\s*([^\]|]*?)\s*\]\]+', r'\1', pu)                 # [[ref]] -> ref
    pu = re.sub(r'\n{3,}', '\n\n', pu).strip()
    parts = [f'# {title}\n']
    if meta:
        parts.append(f'*{meta}*\n')
    parts.append(pu + '\n')
    return parts


def render_letters(rows, title):
    parts = [f'# {title}\n']
    for r in rows:
        parts.append(format_letter(r.get('translation'), r.get('purport')) + '\n')
    return parts


def letter_year(r):
    m = re.search(r'Dated:\s*[A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?,? (\d{4})', r.get('purport') or '')
    return m.group(1) if m else 'undated'


def transcript_year(ref):
    m = re.match(r'transcripts/(\d\d)', ref)
    return str(1900 + int(m.group(1))) if m else 'undated'


def group_by(rows, keyfn):
    out = {}
    for r in rows:
        out.setdefault(keyfn(r), []).append(r)
    return out


def build(code, rows):
    """Return a list of (relative_path, parts). Oversized works are split into a
    subfolder so every file stays small enough to browse on GitHub; small books
    stay as a single file at the top level."""
    slug, title = BOOKS[code]
    rows = sorted(rows, key=lambda r: sort_key(r['ref']))
    outputs = []

    if code == 'sb':                       # split by canto -> srimad-bhagavatam/canto-NN.md
        groups = group_by(rows, lambda r: r['ref'].split('/')[1])
        front = [r for seg in groups if not seg.isdigit() for r in groups[seg]]
        if front:                          # sb/0a, sb/0b -> front matter
            outputs.append((f'{slug}/front-matter.md',
                            render_verses(code, front, f'{title} — Front Matter')))
        for seg in sorted((s for s in groups if s.isdigit()), key=int):
            canto = int(seg)
            outputs.append((f'{slug}/canto-{canto:02d}.md',
                            render_verses(code, groups[seg], f'{title} — Canto {canto}')))

    elif code == 'cc':                     # split by līlā -> sri-caitanya-caritamrta/<lila>-lila.md
        for lila in ('adi', 'madhya', 'antya'):
            grp = [r for r in rows if r['ref'].split('/')[1] == lila]
            if grp:
                outputs.append((f'{slug}/{lila}-lila.md',
                                render_verses(code, grp, f'{title} — {LILA[lila][0]}')))

    elif code == 'letters':                # split by year -> letters/<year>.md
        for year, grp in sorted(group_by(rows, letter_year).items()):
            outputs.append((f'{slug}/{year}.md', render_letters(grp, f'Letters — {year}')))

    elif code == 'transcripts':            # one file per lecture/conversation, foldered by year
        for r in rows:
            year = transcript_year(r['ref'])
            ref_slug = r['ref'].split('/', 1)[1]
            outputs.append((f'lectures-and-conversations/{year}/{ref_slug}.md', render_transcript(r)))

    else:                                  # small books -> single file at the top level
        outputs.append((f'{slug}.md', render_verses(code, rows, title)))

    for rel, parts in outputs:
        _write(rel, parts)
    return len(outputs), len(rows)


def _write(rel, parts):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write('\n'.join(parts).rstrip() + '\n')


def main():
    files = sorted(glob.glob(f'{SRC}/*.json'))
    if not files:
        raise SystemExit(f'No JSON in {SRC}. Run export_d1.sh first.')
    total_rows = total_files = 0
    for fp in files:
        code = os.path.splitext(os.path.basename(fp))[0]
        if code not in BOOKS:
            print(f'  SKIP {code} (no slug mapping)')
            continue
        d = json.load(open(fp))
        rows = d[0]['results'] if isinstance(d, list) else d['results']
        if not rows:
            continue
        nfiles, n = build(code, rows)
        total_rows += n
        total_files += nfiles
        print(f'  {code:12} {n:6} rows -> {nfiles} file(s)')
    print(f'Done. {total_rows} entries -> {total_files} files in {os.path.normpath(OUT)}')


if __name__ == '__main__':
    main()
