# Vedabase Original Edition

The complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda, in the form
they were originally published during his lifetime — verified word-by-word against scanned
photographs of the first-edition books, free from posthumous revisions.

**How that verification was done** — two independent OCR engines read every page, and every
place they disagreed with the text was adjudicated against the scan: see
[How the originals were verified](#how-the-originals-were-verified).

## Purpose

To preserve Śrīla Prabhupāda's teachings exactly as he published them, before later editors
changed the wording. Every verse, synonym, translation, and purport here can be traced back
to a printed page that was set in type while he was alive.

## Source

This repository is the **source of truth** for the original-edition text — the master copy that
the live site (vedabase.cc) is kept in sync with. Each entry keeps the original markup:
Devanāgarī and Bengali ślokas and IAST transliteration as `>` blockquotes, `*italic*` synonyms,
`**bold**` translations, and italics inside the purports.

**Provenance.** The corpus was first generated from the vedabase.cc database
(`vedabase-search-db`), a scan-verified original-edition corpus — one export, no manual
retyping. That database was not copied from another digital edition and trusted; it was
corrected, cell by cell, against the **original printed scans** using the pipeline described
below. To regenerate the Markdown from the current database at any time:

> `bash scripts/export_d1.sh && python3 scripts/build_from_d1.py` (read-only — it never writes
> to the database). See **Contents** below for the layout.

The earlier text set (sourced from vedabase.site, before this database existed) is kept for
reference in [`legacy-vedabase-site/`](legacy-vedabase-site/).

## Making corrections (repo → live site)

Wording fixes are now made **here first** — edit the relevant Markdown file, commit, and push —
then mirrored into the live database so vedabase.cc reflects the change. For transcripts and
letters this is a single command: the companion `astro_vedabase` repo's
[`scripts/sync_transcript_to_d1.py`](https://github.com/juanmanuelferrera/astro_vedabase)
takes the corrected phrase, updates the one matching row in the live D1 (`verses`), verifies it,
and purges the edge cache. It refuses to write unless this repository already contains the new
wording and the old wording occurs exactly once in that row, and it scopes the update to that
single row — so it never rewrites anything it shouldn't. See `astro_vedabase`'s
`SUCCESSION.md` §6 for the full procedure.

---

---

## How the originals were verified

> **Collation against the scans finished on 19 August 2026.** Every book in this
> repository has been read against a photograph of the printed page, and no page
> image is left awaiting a human decision.

The hard problem is that the only trustworthy authority — the first-edition books —
exists as **photographs of paper**, not as text. A scan has to be turned into reliable
text before it can be compared to anything, and raw OCR of a fifty-year-old book is
full of errors, especially on Sanskrit transliteration with its diacritics. So the
work happens in two halves: first make the scans readable by machine, then let the
machine find every place the text disagrees with the scan — while teaching it to
ignore its own mistakes.

It took two rounds. The first round (2025) used Tesseract and got the corpus most of
the way. The second round (June–August 2026) re-read every page with a different OCR
engine, and that is what closed the remainder: the small things that did not change
much but had to be right.

### Round 1 — Tesseract, and its limits

#### 1.1 Making the scans machine-readable (re-OCR)

Many of the source PDFs carried a poor, garbled text layer over the page image. Rather
than trust that layer, every page is re-read from the picture:

- **Page classification.** Each page is inspected. If a single raster image covers more
  than ~45% of the page, it is a real scan and gets re-OCR'd. Pages that are already
  clean digital text (some books were born-digital) are passed through untouched.
- **Fresh OCR.** Scanned pages are rendered to **grayscale at 200–300 DPI** and run
  through **Tesseract 5** (`--psm 6`, English), which writes a new searchable PDF — the
  original image with a fresh, invisible text layer behind it.
- **Double reading.** Later, each page was read **twice** with different page-segmentation
  settings — `psm 6` (uniform block) and `psm 4` (variable-size column), both `--oem 1`
  (LSTM). Where the two readings agree there is reliable consensus; where they disagree
  the page is flagged.
- **Batch + skip.** All books are classified; only the image-based ones are processed,
  several in parallel, and anything already done is skipped — so the job is resumable.

#### 1.2 Comparing scan against text — and rejecting OCR noise

With clean-enough scans, the **scan is treated as gold** and the digital text as the
candidate. For every book (and every Śrīmad-Bhāgavatam canto and Caitanya-caritāmṛta
līlā separately):

- **Extract & clean the scan.** Text is pulled with **PyMuPDF**, hyphenated line breaks
  are re-joined (`exam-\nple` → `example`), running headers/footers are removed by
  frequency (a line appearing near the top or bottom of ≥10% of pages is chrome, not
  content), and bare page numbers are dropped.
- **Fold before matching.** Both sides are normalized — Unicode NFKD, combining
  diacritics stripped, smart quotes and dashes flattened, lowercased — so an IAST variant
  never registers as a "difference." Diacritics are preserved in the output; folding is
  only used for the match.
- **Align.** The two word streams are aligned with Python's `difflib.SequenceMatcher`,
  and every mismatching span becomes a candidate positioned to an exact cell and column.
- **Classify.** Spans are sorted into `trivial`, `translit` (Sanskrit on both sides — not
  an edit), `scan_only`, `d1_only`, `big_replace`/`big_insert` (likely misalignment),
  `noise`, and `real`.

This is where the scripts **correct themselves**: an OCR error in the scan would
otherwise look like a "correction" to be applied. A garbage detector vetoes it. A scan
span is rejected as OCR noise when it shows the fingerprints of bad OCR — half its
tokens are single characters, fewer than ~34% are real dictionary words, or it contains
tell-tale junk like `l1`, `rn`/`m` confusion, stray `{}|^~` symbols, or a lowercase
letter glued to a capital. Only differences that survive every filter are reported.

#### 1.3 Confidence tiering, memory, safe application

- **Tiers.** Each surviving difference is graded **alta / media / baja** from its
  dictionary-word ratio, length, and garbage signature.
- **Memory.** Every change already applied or already vetted is remembered, so a re-run
  reports only **what is new** instead of re-surfacing settled ones.
- **Gates.** Nothing is written blindly. A change is applied only if the scan side is
  clean, the span is small (guard at 8 words), it reproduces a **human-approved**
  correction pair verbatim after folding, and a **hard offset check** passes: the exact
  character span in the target cell must fold back to precisely the text being replaced.

#### 1.4 Why this was not enough

Tesseract gets a lot right, but it **gets things wrong the same way every time**: `h`
read as `il`, `e` read as `c`. A systematic error does not cancel out by reading twice
with the same engine, so consensus alone cannot settle a disputed word. Worse, Tesseract
threw away the punctuation that the word-for-word synonyms depend on: the em dashes and
semicolons that separate `key—gloss` pairs arrived as an undifferentiated stream of
words.

### Round 2 — Surya, and the last two months

#### 2.1 A second, independent OCR engine

**Surya** is a neural OCR model, architecturally unrelated to Tesseract. It does not
share Tesseract's failure modes, which is exactly what makes it useful: where the two
engines disagree about a word, that disagreement is informative, and where they agree
against the digital text, the digital text is wrong.

- First it was run **only on the pages carrying open candidates** — render to PNG, one
  `surya_ocr` invocation per folder (loading the model is the expensive part), output to
  `surya/<book>/<pdf>/pNNNN.surya.txt`.
- Then it was run on **everything**: **35,509 pages across 21 books**, resumable, skipping
  pages already done.

Surya brought an unplanned benefit that turned out to be decisive: **it preserves em
dashes, semicolons and diacritics**. The synonyms now come off the page exactly as they
were printed —

```
śrī sūtaḥ uvāca—Śrī Sūta Gosvāmī said; viduraḥ—Vidura; tīrtha-yātrāyām—…
```

— which made it possible to read the `key—gloss` pairs natively, instead of guessing
where each gloss ends.

#### 2.2 The ledger

A practical problem had been costing time: **the candidate count does not go down when
you fix things.** The diff is recomputed from scratch each run and proposes the same
spans again, so every session risked re-adjudicating settled cases — sometimes in the
opposite direction.

The ledger cross-references every candidate against everything already decided and
records one state each:

| State | Meaning | Count |
|---|---|---|
| `RUIDO` | falls in a documented noise class | 3,496 |
| `DESCARTADO` | rejected, with a reason on file | 2,501 |
| `APLICADO` | the reported text no longer exists in the repo | 1,343 |
| `VERIFICADO` | checked against the page image — **never propose again** | 203 |
| `AUDITADO` | reviewed in a later pass | 23 |
| `ABIERTO` | still to look at | 145 |

8,724 candidates in total.

#### 2.3 The word-for-word synonyms, handled separately

The synonyms needed their own pass, for a specific reason: `difflib` compares two streams
of words, so **a long gloss gets split in half and shows up as three unrelated
candidates** that mean nothing individually. In SB 1.18.42 the diff produced
`by the prowess`/`deserve` and `of whom`/`by whose` as if they were separate problems.
Paired up, the fault is obvious at a glance:

```
print   arhasi—deserve          yat—by whose
repo    arhasi—by the prowess   yat—of whom
```

The repo had given `arhasi` the gloss belonging to `tejasā`, two pairs further along. It
is a copy slip, and it is only visible when the pairs are aligned.

Three things had to be got right, each of which caused a reverted change before it was:

- **The anchor is the transliteration, and it must match exactly once.** Anchoring on the
  first key does not work: `tasmāt—` heads the glosses of dozens of verses, so the block
  came from the wrong place. Windows of decreasing length are tried and the first
  unambiguous one wins.
- **The block after the anchor must actually be glosses.** In SB 7.13.7 the anchor landed
  inside a purport that quotes the verse translation, and the "block" was prose from
  elsewhere. A wrong correction came out of that and had to be reverted.
- **A key can repeat inside one verse with different glosses.** In SB 1.1.19 `svādu`
  appears twice, "relishing" and "palatable", and the print has it that way too. Keeping
  only the first invented differences that did not exist — and inverted, at that. First
  must pair with first.

A fallback locates a gloss when OCR has mangled the transliteration and there is no
anchor: it uses **two keys of the same verse at once**. `te—` heads glosses in two hundred
places, but `te—` within 400 characters of a rare key from the same verse can only be
this one.

Of 234 gloss differences, 149 were OCR noise and 85 were genuinely different text.

#### 2.4 Scan arbitrating between repo and database

When the repository and the live database disagree, the scan breaks the tie without
anyone opening an image:

```
scan says what the repo says  ->  the database is wrong
scan says what the database says  ->  the repo is wrong (rare; inspect the case)
scan says neither  ->  the page image is needed
```

A single word is not enough to search on — "one" appears on every page — so the repo's
context around the divergence is taken and that context is looked up in the book's OCR.

#### 2.5 Propagating to the translations

The four translations — Spanish, Portuguese, Hindi, Russian — have to follow the English
when a gloss changes. Two things make this harder than it sounds:

- **The pairs come from git history, not from a corrections log.** A corrections file
  stores fragments; reconstructing before/after pairs from it produced 119 incoherent
  results out of 149. `git diff --unified=0` over the synonyms line is the only source
  that knows what the gloss said before and what it says now. A pair is accepted only
  when the gloss count matches on both sides; if the verse was restructured, it is set
  aside.
- **Languages are matched by position, not by key text.** Russian writes its keys in
  Cyrillic, so searching by the Latin key finds about one in eighty. The lists run
  parallel in 98% of verses; where they do not, the key is looked up by name, which only
  works for Spanish and Portuguese.

Every batch is then written back to the live database **and read back to compare**. This
matters: an `UPDATE` that matches no row does not raise an error, it simply changes
nothing. Without the read-back, a half-applied batch looks successful.

---

## What "matching the scans" actually means

The repository reproduces the first editions **including their mistakes**.

A first edition has typos, misspelled names, and glosses that say the opposite of what
the word means. Where the digital text and the paper differ, the paper wins — even when
the paper is wrong. What a reader gets here is the book **as it was printed**, not the
book as it should have been printed. Silently improving Prabhupāda's published text is
precisely the thing this repository exists to undo; a corrector who fixes an obvious typo
today is doing a small version of what a later editor did on a large scale.

So the errors are kept, and they are **labelled** — in three places:

| Where | What |
|---|---|
| [`PRINT_ERRATA.md`](PRINT_ERRATA.md) | 76 entries, each with the reference, what the digital text used to say, what the page actually reads, and the page number. Generated from the `print_errata` table — do not edit by hand. |
| <https://vedabase.cc/print-errata/> | The same list as a public page, linked from the site navigation. |
| The verse page itself | Each affected verse carries an **About the printed text** note naming the reading and explaining it, with a link to the full list. |

For example, CC Madhya 3.28 prints "daughter of the son-god" where the word-for-word on
that same verse glosses the word as the sun-god. The page serves "son-god", and says so.

Two limits are worth stating plainly:

- **The 76 are a floor, not a total.** The method can only surface an errata where the
  digital text and the scan *differ*. An error the digital text had carried from the
  start produces no divergence and never comes up. These are the print's errors that
  someone had silently corrected and that have been put back — not every error in
  the print.
- **One thing is not reproduced:** the print contradicting itself inside a single
  sentence. A line printed twice because a plate slipped is damage to that copy, not a
  reading.

---

## Tools

| Tool | Role |
|------|------|
| **Tesseract 5** | Round 1 OCR (grayscale, 200–300 DPI, `psm 6` and `psm 4`, `--oem 1`) |
| **Surya** | Round 2 OCR — a different engine, so a different set of errors; preserves em dashes, semicolons and diacritics |
| **PyMuPDF (fitz)** | Page classification, image rendering, diacritic-safe text extraction |
| **difflib `SequenceMatcher`** | Scan-vs-text alignment and opcode diffing |
| **Custom Python** | Folding/normalization, OCR-garbage rejection, confidence tiering, offset-gated applier, the ledger, the gloss pair reader |
| Unix `words` list | Dictionary-ratio test separating real English from OCR noise and transliteration |

The audit scripts live in the companion working repository, `astro_vedabase`, under
`scripts/scan_audit/` — which has its own README describing each step and the mistakes
that shaped it. The [`scripts/`](scripts/) folder here holds the database export and
Markdown build (`export_d1.sh`, `build_from_d1.py`, `letters_format.py`) plus the
comparison utilities (`compare.py`, `strip_diacritics.py`).

---

## Contents

Generated directly from the vedabase.cc database. **Every book is a folder, and every verse is
its own Markdown file** — so each unit is individually addressable for search, diffing, and
parallel processing. Each file's content is verbatim from the database; only structural divider
headings (chapter/canto labels) are omitted, since that information is carried in the file names.

Translations in Spanish, Hindi, Portuguese, and Russian live under
[`translations/`](translations/) — see the [Translations](#translations) section below.

### Book folders

| Folder | One file per | Example file |
|--------|--------------|--------------|
| `bhagavad-gita-as-it-is/chapter-NN/` | Bhagavad-gītā verse | `chapter-01/bg-1.1.md` |
| `srimad-bhagavatam/canto-NN/chapter-NN/` | Śrīmad-Bhāgavatam verse | `canto-01/chapter-01/sb-1.1.1.md` |
| `sri-caitanya-caritamrta/LILA-lila/chapter-NN/` | Caitanya-caritāmṛta verse | `madhya-lila/chapter-20/cc-madhya-20.1.md` |
| `isopanisad/` | Śrī Īśopaniṣad mantra | `iso-1.md` |
| `nectar-of-instruction/` | Upadeśāmṛta verse | `verse-1.md` |
| `light-of-the-bhagavata/` | Light of the Bhāgavata text | `text-1.md` |
| `krsna-the-supreme-personality-of-godhead/` | Kṛṣṇa book chapter | `chapter-1.md` |
| `nectar-of-devotion/`, `teachings-of-lord-caitanya/`, `science-of-self-realization/`, … | chapter (prose books) | `chapter-1.md` |

The three largest works are **nested by chapter** — Bhagavad-gītā by `chapter-NN/`, and
Śrīmad-Bhāgavatam and Caitanya-caritāmṛta additionally by `canto-NN/` and `LILA-lila/` — so no
single directory exceeds a few hundred files and stays browsable on GitHub (which truncates a
folder listing at 1,000 entries). The smaller books are flat. Front matter (`preface.md`,
`introduction.md`, …) sits at each book's root; chapter/canto folder numbers are zero-padded so
they sort in order.

### File-name conventions

- **Verse files** keep the book's own verse id: `bg-1.1.md`, `sb-<canto>.<chapter>.<verse>.md`,
  `cc-<līlā>-<chapter>.<verse>.md`, `iso-<n>.md`. Combined verses use a range, e.g.
  `bg-1.16-18.md`.
- **Chapter files** (prose books with no numbered verses) are `chapter-<n>.md`. Short
  verse-texts without an id prefix are `verse-<n>.md` (Nectar of Instruction) or `text-<n>.md`
  (Light of the Bhāgavata).
- **Front matter** — dedication, foreword, preface, introduction, etc. — each gets its own file
  named after the section: `preface.md`, `introduction.md`, `dedication.md`,
  `disciplic-succession.md`.
- **Chapter colophons** (the "Thus end the Bhaktivedanta Purports…" closings, Bhagavad-gītā only)
  are `bg-<chapter>-colophon.md`.
- Inside a prose chapter, the book's own `## ` subsection headings are kept within the chapter
  file.

Names use simple, lowercase, dot/hyphen ids, so a recursive glob selects a whole book
(`bhagavad-gita-as-it-is/**/bg-*.md`, `srimad-bhagavatam/**/sb-*.md`). Because the order is
encoded in the verse numbers rather than in zero padding, lexical sort and numeric sort of the
*files* can differ (`bg-1.10.md` sorts before `bg-1.2.md`); the chapter/canto *folders* are
zero-padded and sort correctly.

### Each verse file

Holds exactly that verse's block as published: the `### Bg 1.1` heading, the Devanāgarī/Bengali
and IAST śloka as `>` blockquotes, `*italic*` word-for-word synonyms, the `**bold**` translation,
and the purport — byte-for-byte from the source.

### Other material (unchanged)

| Path | Contents |
|------|----------|
| `letters/<year>.md` | 6,582 letters, by year |
| `lectures-and-conversations/<year>/<id>.md` | one file per lecture / conversation |
| `legacy-vedabase-site/` | the earlier vedabase.site text set, kept for reference |

**Scope note.** Śrīmad-Bhāgavatam runs through **Canto 10** — the portion Prabhupāda himself
completed. Cantos and chapters finished by disciples after his disappearance are not in the
database, and so are not here.

---

## Translations

[**`translations/`**](translations/) holds the books in four languages —
[Spanish](translations/espanol/), [Hindi](translations/hindi/),
[Portuguese](translations/portugues/), [Russian](translations/russian/) — plus
[English](translations/english/), in the same book folders as the originals above.

Each language carries two things per book:

- **Canonical data** — one `<book>_<lang>.jsonl` per book (e.g. `espanol/bhagavad-gita-as-it-is/bg_es.jsonl`).
  Each line is one verse with the full schema: `ref`, `book`, `lang`, `url`, `verse_text`,
  `devanagari`, `synonyms`, `translation`, `purport`.
- **Generated Markdown** — one file per verse/chapter, mirroring the English layout exactly
  (same paths, same `### Bg 1.1` headings). Each verse carries the **Devanāgarī/Bengali śloka**
  and the **IAST transliteration** as separate `>` blockquotes, the same as the English verse
  files in the main folder.

### Source of truth runs the other way from English

For English, the Markdown is canonical and is mirrored *into* the database. For the translations
it is the reverse: **the jsonl is canonical**, and the database (and the live site) is regenerated
*from* it — never the other way. The Markdown is a generated view rendered from the jsonl.

```
jsonl (canonical)  ──render──►  Markdown (read-only view)
        │
        └──sync──►  D1 / vedabase.cc
```

This means:

- **Fixing a translation:** edit the `.jsonl` (or fix it in D1 and re-export), then regenerate.
  Never hand-edit a generated `.md` — `scripts/build_translations.py` will overwrite it.
- The English Devanāgarī in `english/*.jsonl` is the one field sourced from D1 (the repo Markdown
  has none); it is verified to contain Indic script only.
- Synonyms and translations are normalized to the English convention — each synonym term is
  italicized (`*term*—gloss`) and each verse translation is bold (`**…**`).

### Scripts

- `scripts/build_translations.py` — regenerate the jsonl and Markdown for all languages.
- `scripts/check_translations_drift.py` — verify every generated `.md` still equals
  `render(its jsonl)`; fails on any hand-edit, stale, or orphan file.

---

## Independent verification

The original scanned PDFs are available so anyone can check the text against the paper:

- [Krishna.org scans](https://krishna.org)
- Devotee Google Drive archives (linked from the source sites)

---

## License

**Scripts:** [MIT License](LICENSE) — free to copy, modify, and use.

**Texts:** Shared for educational and devotional purposes. The original works are the literary
property of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda.
