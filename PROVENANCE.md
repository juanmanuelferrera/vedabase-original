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
| **corpus** | The text of the first editions, 102,729 files | this repository | 495 MB | `ar://<pending>` |
| **corrections** | The ledger of corrections applied to the text | this repository, `*.jsonl` | 272 MB | `ar://<pending>` |
| **scans** | 70 PDFs of the printed books, including the complete Śrīmad-Bhāgavatam | `scan_vedabase/originals/` | 2,078 MB | `ar://<pending>` |
| **ocr-packed** | Every page as read by both engines, one `.tar` per book | `surya_ocr/`, `.../scan_audit/ocr/` | 193 MB | `ar://<pending>` |
| **audit** | The ledger of discrepancies: open, arbitrated, applied | `astro_vedabase/scripts/scan_audit/*.json` | 68 MB | `ar://<pending>` |
| **reports** | Each difference beside the image of the scanned page | `.../scan_audit/*.html` | 126 MB | `ar://<pending>` |
| **tools** | The code that did the comparison and applied the fixes | both repos, `*.py` | 1.1 MB | `ar://<pending>` |
| **manifest** | SHA-256 of all 103,305 files plus a root over the whole set | `MANIFEST.sha256` | 15 MB | `ar://<pending>` |

Package root, 26 Aug 2026: `9aeb1cb5d6d3afbc5802601d3fced469a9c7eef6b299f077ff741b1fad76d718`
Reproduce it with `python3 scripts/build_archive.py --manifest-only`.

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

Because the content type applies to a whole upload, each section is uploaded
separately with its own:

| Section | `--content-type` |
|---|---|
| corpus, audit/notes | `text/markdown; charset=utf-8` |
| corrections, audit/candidates | `application/x-ndjson; charset=utf-8` |
| audit/ledger, audit/text-layer | `application/json; charset=utf-8` |
| ocr-packed, `*.tar` | `application/x-tar` |
| ocr-packed, `OCR-CONTENTS.sha256` | `text/plain; charset=utf-8` |
| reports | `text/html; charset=utf-8` |
| tools | `text/x-python; charset=utf-8` |
| scans | `application/pdf` |

This is why `corpus` and `corrections` are separate sections even though both
come from this repository: they are different kinds of thing and they cannot
share a content type.

Note the syntax: `text/markdown;charset=utf-8`, with **no space** after the
semicolon. With a space the shell splits the argument and the CLI keeps only the
first half, so the charset never reaches the transaction and the file is served
without it. Verified on 26 Aug 2026 — the first attempt, written with a space,
recorded a bare `text/markdown` and rendered the Sanskrit as mojibake.

## A note on the OCR containers

Everything in this archive is uploaded one file at a time, addressable on its
own from any gateway — except the OCR, which travels as 42 `.tar` containers,
one per book per engine.

The reason is arithmetic. The OCR output is 69,799 text files, one per page per
engine, with a median size of 1,874 bytes. Measured against the Turbo price API
on 26 Aug 2026, an upload costs **9,174,313 winc per file plus 11,184.90 winc
per byte** — a formula that reproduces the API's own quotes to 0.000% across
sizes from 500 bytes to 1 MB. The per-file part is small in money, but the CLI
spends 0.58 s on each file, so those pages alone were thirteen hours of upload.

Packing them costs slightly *more* in credits, not less: tar pads every member
to a 512-byte boundary, so 129 MB of pages become 193 MB of containers, and the
0.64 credits saved on per-file overhead are given back in padding and then some.
What it buys is time — thirteen hours become seconds. Nothing else in the
archive is packed, because being readable one file at a time is most of what the
corpus, the scans and the reports are for.

`tar` was chosen over `zip` or `gzip` deliberately. It is uncompressed and its
format is specified in POSIX, so a flipped bit damages one member and the rest
still extract; compression would couple every byte to every other and bet on a
decompressor still existing in fifty years. The variant is `ustar`, the most
conservative one that fits these paths — the longest is 112 characters, split
across the 155-byte prefix and the 100-byte name field.

The containers are deterministic: members sorted by path, uid and gid zeroed,
owner names emptied. The same input produces the same bytes on any machine.

**A container is only worth using if you need not trust it.** So
`OCR-CONTENTS.sha256` travels beside the tars and lists the SHA-256 of each
container followed by the SHA-256 of all 69,799 members, as `container!path`.
To check one page without extracting the rest:

    P=isopanisad/Sri-Isopanisad-scans-of-original-1969-edition/p0001.surya.txt
    tar -xOf ocr-surya-isopanisad.tar "$P" | shasum -a 256
    grep "ocr-surya-isopanisad.tar!$P" OCR-CONTENTS.sha256

Inside a container the path keeps the edition directory the scan came from, so
the page carries the printing it was read from, not just a page number.

### One duplicate, removed

The Surya run left the Bhāgavatam laid out twice: as loose volume directories
`SB1.1 … SB10.3` at the top of `surya_ocr/`, and again inside
`srimad-bhagavatam/`, which holds those same thirty. Verified on 26 Aug 2026:
the 11,474 relative paths match exactly and all 11,474 SHA-256 match. Only the
merged copy is archived — it is how every other book in the section is named.
The loose copies were dropped before packing, which is why `ocr-surya` holds
24,035 files here and 35,509 in the working directory it came from.

## A note on the markup

Ślokas in Devanāgarī and their IAST transliteration are `>` blockquotes, and
each line of the verse ends with a **backslash**. That backslash is Markdown's
hard line break: without it the pādas would be joined into one running line.

It is markup, not text. Anyone extracting plain text from these files should
strip a trailing `\` from each line — it is not part of the verse.

The backslash was chosen over Markdown's other hard-break form, two trailing
spaces, because trailing whitespace is invisible and almost every editor strips
it on save. A verse break is information, not formatting, so it is written in a
way that is visible and hard to destroy by accident.
