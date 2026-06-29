#!/usr/bin/env python3
"""Drift guard for translations/.

Invariant: every generated Markdown file equals render(its canonical jsonl row).
This re-renders Markdown from the COMMITTED per-book jsonl and compares it to the
COMMITTED .md files — so a hand-edit of a generated .md, a stale file, or an
orphan is caught. Fully offline (no D1, no traducciones_vedabase needed).

    python3 scripts/check_translations_drift.py        # exits 1 on any drift

English is skipped (its .md is the hand-verified canonical source, not generated;
its jsonl is the derived artifact — the opposite direction)."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_translations as B

TRANS = B.VO / 'translations'
LANGS = {'espanol', 'hindi', 'portugues', 'russian'}


def main():
    emap = B.english_ref_map()
    mism = missing = orphan = checked = 0
    for lang in sorted(LANGS):
        root = TRANS / lang
        if not root.exists():
            continue
        expected = {}                       # relpath(str) -> rendered text
        for jf in root.rglob('*.jsonl'):
            for line in jf.read_text(encoding='utf-8').splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                ref = r['ref']
                if ref in emap:
                    rel, heading, mode = emap[ref]
                else:
                    d = B.derive_target(ref)
                    if d is None:
                        continue
                    rel, heading, mode = d
                expected[str(Path(lang) / rel)] = B.render_row(r, heading, mode)
        # compare expected vs on-disk
        for rel, text in expected.items():
            p = TRANS / rel
            checked += 1
            if not p.exists():
                missing += 1
                if missing <= 5: print(f'  MISSING  {rel}')
            elif p.read_text(encoding='utf-8') != text:
                mism += 1
                if mism <= 5: print(f'  EDITED   {rel}')
        # orphans: committed .md not produced by any jsonl row
        on_disk = {str(p.relative_to(TRANS)) for p in root.rglob('*.md')}
        for rel in sorted(on_disk - set(expected)):
            orphan += 1
            if orphan <= 5: print(f'  ORPHAN   {rel}')

    print(f'\nchecked {checked} generated files: '
          f'{mism} edited, {missing} missing, {orphan} orphan')
    if mism or missing or orphan:
        print('DRIFT DETECTED — regenerate with scripts/build_translations.py')
        return 1
    print('OK — every generated Markdown file matches render(its jsonl)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
