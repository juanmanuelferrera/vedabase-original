#!/usr/bin/env python3
"""Apply D1 fixes to vedabase-original markdown files.

All changes made to vedabase-search-db (D1) during the 2026-06-18 session.
Reads each markdown file, applies text replacements, writes back.

Usage: python3 scripts/apply_d1_fixes.py [--dry-run]
"""
import re, sys

ROOT = __import__('os').path.dirname(__import__('os').path.dirname(__import__('os').path.abspath(__file__)))

FIXES = {
    # ── Caitanya-caritamrta ──
    'sri-caitanya-caritamrta/adi-lila.md': [
        # #4: remove speaker attribution
        (r'\*\*\[Śrī Uddhava said:\] ', '**'),
        # #7: situated in potential form → potentially situated
        ('are situated in potential form in', 'are potentially situated in'),
        # #11: for spiritual progress → in this age of Kali
        (" 'For spiritual progress in this Age of Kali, there is no alternative",
         " 'in this age of Kali there is no alternative"),
        # #14: multiple BBTI changes in 7.118
        ("'Besides these inferior nature, 0 mighty-armed Arjuna, there is another, superior energy of Mine, which is all living entities who are exploiting the resources",
         "'Besides the inferior nature, O mighty-armed Arjuna, there is a superior energy of Mine, which is all living entities who are struggling with material resources"),
    ],
    'sri-caitanya-caritamrta/madhya-lila.md': [
        # 4.8 synonyms: synopsis → codes
        ('*sūtre*—in the synopsis', '*sūtre*—in the codes'),
        # 4.8 translation: summarized → in his codes
        ('**Some of the incidents he did not describe elaborately, but only summarized, and these I shall try to describe in this book.**',
         '**Some of the incidents in his codes he did not describe elaborately, and so I shall try to describe them in this book.**'),
        # 4.42 synonyms: Muslims → Mohammedans
        ('from fear of the Muslims', 'from fear of the Mohammedans'),
        # 4.42 translation: Muslims → Mohammedans
        ('the Muslims attacked', 'the Mohammedans attacked'),
    ],

    # ── Śrīmad-Bhāgavatam ──
    'srimad-bhagavatam/canto-03.md': [
        # 3.1.8: incident → incidence
        ('Mahārāja Yudhiṣṭhira was the rightful heir to his father', None),  # skip, need context
        # 3.13.30: hooves → hoofs
        ('His hooves, which were like', 'His hoofs, which were like'),
        # 3.26.40: ability → capacity
        ('its capacity to cook', None),  # already correct in markdown?
        # 3.26.46: giving → to give
        ('forms of the Supreme Lord giving', 'forms of the Supreme Lord to give'),
        # 3.8.28: marking → jewel
        ('the śrīvatsa marking', 'the śrīvatsa jewel'),
        # 3.25.41: one → he
        ('one cannot surpass', 'he cannot surpass'),
        # 3.31.29: into → in
        ('oneself into the service', 'oneself in the service'),
        # 3.7.41: (check context)
        # 3.7.7: were → wert
        ('if everyone were bewildered', 'if everyone wert bewildered'),
        # 3.9.33: in devotion here → here in devotion
        ('in devotion here.', 'here in devotion.'),
        # 3.26.38: destiny → predestiny
        ('due to destiny,', 'due to predestiny,'),
    ],
    'srimad-bhagavatam/canto-05.md': [
        # 5.1.19: Brahmā → Brahmi (check context)
        # 5.1.7: Brahmā → Brahmi
        # 5.13.25: conception → remove wiki link
        (r'conception \[\[cc/madhya/13/80\|\[Cc\. Madhya 13\.80\]\]\]\.',
         'conception.'),
    ],
    'srimad-bhagavatam/canto-06.md': [
        # 6.8.17: Kūrma → Karma
        ('Kūrma,', 'Karma,'),
        # 6.9.41: Brahmā → Brahmi
    ],
    'srimad-bhagavatam/canto-07.md': [
        # 7.3.22: Brahmā → Brahmi
        # 7.3.28: Brahmā → Brahmi
        # 7.9.10: himself → him-self
    ],
    'srimad-bhagavatam/canto-08.md': [
        # 8.4.17-24: Kūrma → Karma
        ('Kūrma', 'Karma'),
    ],
    'srimad-bhagavatam/canto-09.md': [
    ],
    'srimad-bhagavatam/canto-10.md': [
    ],
}

def apply_fixes(filepath, replacements, dry_run):
    path = __import__('os').path.join(ROOT, filepath)
    if not __import__('os').path.exists(path):
        print(f"  SKIP: {filepath} not found")
        return 0

    with open(path, 'r') as f:
        original = f.read()

    text = original
    applied = 0
    for old, new in replacements:
        if new is None:
            continue
        new_text = text.replace(old, new)
        if new_text != text:
            applied += 1
            text = new_text

    if applied:
        if dry_run:
            print(f"  WOULD FIX {filepath}: {applied} changes")
        else:
            with open(path, 'w') as f:
                f.write(text)
            print(f"  ✓ {filepath}: {applied} changes")
    else:
        print(f"  - {filepath}: no changes applied")
    return applied

if __name__ == '__main__':
    dry = '--dry-run' in sys.argv
    total = 0
    for fpath, reps in FIXES.items():
        total += apply_fixes(fpath, reps, dry)
    print(f"\nTotal: {total} changes {'(dry run)' if dry else 'applied'}")
