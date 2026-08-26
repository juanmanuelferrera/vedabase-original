# Provenance and permanent archive

This repository holds the **text**. The work that backs it — the scans of the
printed pages, the two OCR readings, the record of every discrepancy and the
tools that did the collation — lives outside it, because those are binaries and
working files with no place in git.

This file says where each piece is and how to check it. A permanent copy of
everything together is published on Arweave, where it cannot be modified or
withdrawn; the transaction ids go in the table below as they are published.

## The pieces

| Piece | What it is | Where it lives today | Size | Arweave |
|---|---|---|---|---|
| **corpus** | The text of the first editions, 102,835 files | this repository | 767 MB | `ar://<pending>` |
| **scans** | 70 PDFs of the printed books, including the complete Śrīmad-Bhāgavatam | `scan_vedabase/originals/` | 2,078 MB | `ar://<pending>` |
| **ocr-surya** | Every page as read by the Surya engine | `scan_vedabase/surya_ocr/` | 72 MB | `ar://<pending>` |
| **ocr-tesseract** | Every page as read by Tesseract — the other half of the collation | `.../scan_audit/ocr/` | 80 MB | `ar://<pending>` |
| **audit** | The ledger of discrepancies: open, arbitrated, applied | `astro_vedabase/scripts/scan_audit/*.json` | 68 MB | `ar://<pending>` |
| **reports** | Each difference beside the image of the scanned page | `.../scan_audit/*.html` | 126 MB | `ar://<pending>` |
| **tools** | The code that did the comparison and applied the fixes | both repos, `*.py` | 1.1 MB | `ar://<pending>` |
| **manifest** | SHA-256 of every file plus a root hash for the whole set | `MANIFEST.sha256` | 15 MB | `ar://<pending>` |

To assemble the complete package:

```
python3 scripts/build_archive.py --dry-run       # see what goes in
python3 scripts/build_archive.py --with-tesseract
```

## How to check that the text has not changed

```
python3 scripts/hash_manifest.py --check
```

This recomputes the hash of every file and compares it against
`MANIFEST.sha256`. If the `root` matches the one anchored on Arweave for that
date, the text is the same as it was when published. If it does not match,
something changed — and being able to detect that is the whole point.

The manifest proves the text **has not been altered**. What proves it **matches
the paper** is the collation, and its record is in `audit/` and `reports/`:
every discrepancy, which page settled it, and what was decided.

## Published anchors

An anchor on a single date says nothing about what came after. What counts is
the succession. Every time the corpus changes, the manifest is regenerated and
the new `root` is anchored.

| Date | Corpus root | Transaction |
|---|---|---|
| *(pending)* | `1d26996b1d851271290c6640496d1ea7547b4172450093f7d69635c2b4816f29` | `ar://<pending>` |

*Test upload, 26 Aug 2026: an earlier draft of this file, used to verify the
pipeline end to end — `U9uIEx_mc2e1zVFPXduR6whbtdqIexzk73HMV6JVV8k`. Retrieved
from a public gateway and confirmed byte-identical to the local original. Not an
anchor; kept here as the record of the first successful upload.*

## Provenance of the scans

*(To be completed. A PDF of a 1972 book does not establish on its own where it
came from; this is what turns a file into evidence.)*

For each scan the record should state:

- edition and **printing** — the copyright year is not enough: two volumes of
  the Caitanya-caritāmṛta that looked like first editions turned out to be the
  1983 reprint, and it showed only on the copyright page
- which physical copy it came from, and whose it was
- when and how it was scanned, and at what resolution
- if it came from a public copy, which one and on what date

What is known so far:

- **Caitanya-caritāmṛta, 17 volumes** — byte-identical to the archive.org item
  uploaded on 2021-10-24. Ādi-līlā volumes 1 and 2 are the **second printing of
  1983**, not the first run (1974 and 1973 respectively); volume 3 is a 1974
  first printing. Documented in the README.

## A note on character encoding

Every text file here is UTF-8, and the corpus is full of Sanskrit diacritics
(ā, ī, ū, ṛ, ṣ, ṭ, ñ, ś) as well as Spanish, Portuguese and Russian text in the
translations. When uploading, the content type must carry the charset —
`text/markdown; charset=utf-8`, not bare `text/markdown` — or browsers fall back
to Latin-1 and the diacritics come out as mojibake. This cannot be corrected
after the fact: a file already on Arweave can only be replaced by uploading it
again and paying again.
