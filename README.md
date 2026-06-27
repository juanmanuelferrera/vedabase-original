# Vedabase Original Edition

The complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda, in the form
they were originally published during his lifetime — verified word-by-word against scanned
photographs of the first-edition books, free from posthumous revisions.

## Purpose

To preserve Śrīla Prabhupāda's teachings exactly as he published them, before later editors
changed the wording. Every verse, synonym, translation, and purport here can be traced back
to a printed page that was set in type while he was alive.

## Source

The text comes **directly from the vedabase.cc database** (`vedabase-search-db`), the
scan-verified original-edition corpus. The Markdown files in this repository are generated
straight from that database — one export, no manual retyping — so they always match the
database row-for-row. Each entry keeps the database's own markup: Devanāgarī and Bengali
ślokas and IAST transliteration as `>` blockquotes, `*italic*` synonyms, `**bold**`
translations, and italics inside the purports.

The database itself was not copied from another digital edition and trusted. It was corrected,
cell by cell, against the **original printed scans** using the pipeline described below.

> Generate the Markdown yourself: `bash scripts/export_d1.sh && python3 scripts/build_from_d1.py`
> (read-only — it never writes to the database). See **Contents** below for the layout.

The earlier text set (sourced from vedabase.site, before this database existed) is kept for
reference in [`legacy-vedabase-site/`](legacy-vedabase-site/).

---

## How the originals were verified

The hard problem is that the only trustworthy authority — the first-edition books — exists as
**photographs of paper**, not as text. A scan has to be turned into reliable text before it can
be compared to anything, and raw OCR of a fifty-year-old book is full of errors, especially on
Sanskrit transliteration with its diacritics. So the work happens in two halves: first make the
scans readable by machine, then let the machine find every place the database disagrees with the
scan — while teaching it to ignore its own mistakes.

### 1. Making the scans machine-readable (re-OCR)

Many of the source PDFs carried a poor, garbled text layer over the page image. Rather than
trust that layer, every page is re-read from the picture:

- **Page classification.** Each page is inspected. If a single raster image covers more than
  ~45% of the page, it is a real scan and gets re-OCR'd. Pages that are already clean digital
  text (some books were born-digital) are passed through untouched.
- **Fresh OCR.** Scanned pages are rendered to **grayscale at 200–300 DPI** and run through
  **Tesseract 5** (`--psm 6`, English), which writes a new searchable PDF — the original image
  with a fresh, invisible text layer behind it.
- **Same look, better text.** The output PDF looks identical to the scan, but the text you can
  now extract is the new OCR, which fixes the garbled transliteration in the old layer.
- **Batch + skip.** All books in `originals/` are classified; only the image-based ones are
  processed, several in parallel, and anything already done in `improved/` is skipped — so the
  job is resumable and re-runnable.

`reocr_book.py` does one book; `reocr_all.py` runs the whole shelf.

### 2. Comparing scan against database — and rejecting OCR noise

With clean-enough scans, the **scan is treated as the gold truth** and the database text as the
candidate. For every book (and every Śrīmad-Bhāgavatam canto and Caitanya-caritāmṛta līlā
separately):

- **Extract & clean the scan.** Text is pulled with **PyMuPDF**, hyphenated line breaks are
  re-joined (`exam-\nple` → `example`), running headers/footers are removed by frequency (a line
  that appears near the top or bottom of ≥10% of pages is chrome, not content), and bare page
  numbers are dropped.
- **Fold before matching.** Both sides are normalized — Unicode NFKD, combining diacritics
  stripped, smart quotes and dashes flattened, lowercased — so an IAST variant never registers
  as a "difference." Diacritics are preserved in the output; folding is only used for the match.
- **Align.** The two word streams are aligned with Python's `difflib.SequenceMatcher`, and every
  mismatching span becomes a candidate change positioned to an exact cell and column.
- **Classify each difference.** Spans are sorted into `trivial`, `translit` (Sanskrit on both
  sides — not an edit), `scan_only`, `d1_only`, `big_replace`/`big_insert` (likely
  misalignment), `noise`, and `real`.

This is where the scripts **correct themselves**: an OCR error in the scan would otherwise look
like a "correction" to be applied. A garbage detector vetoes it. A scan span is rejected as OCR
noise when it shows the fingerprints of bad OCR — half its tokens are single characters, fewer
than ~34% are real dictionary words, or it contains tell-tale junk like `l1`, `rn`/`m`
confusion, stray `{}|^~` symbols, or a lowercase letter glued to a capital. Only differences
that survive every filter are reported as genuine.

### 3. Confidence tiering and idempotent passes

The surviving `real` differences are triaged automatically:

- **Tiers.** Each is graded **alta / media / baja** (high / medium / low confidence) from its
  dictionary-word ratio, length, and garbage signature. High-confidence, short, clean-word
  changes rise to the top.
- **Memory.** Every change already applied or already vetted is remembered, so a re-run reports
  only **what is new** (`alta NUEVA`) instead of re-surfacing settled ones. Each pass therefore
  converges instead of repeating itself.
- **Density.** Books are ranked by differences per 1,000 words, so attention goes where the
  divergence is densest.

### 4. Applying corrections safely

Nothing is written blindly. The applier is **preview-by-default** and emits SQL only when asked.
A change is applied only if it clears every gate:

1. the scan (gold) side is clean, not OCR garbage;
2. the span is small and non-trivial — large inserts/deletes are refused as probable
   misalignment (guard at 8 words);
3. it reproduces a **human-approved** correction pair verbatim (after folding);
4. a **hard offset check**: the exact character span in the target database cell must fold back
   to precisely the text being replaced — otherwise the edit is dropped.

The result is a surgical, positioned patch (exact character offsets in one cell), never a
fuzzy whole-field overwrite. Books that already matched their scans were left untouched.

---

## Tools

| Tool | Role |
|------|------|
| **Tesseract 5** | Fresh OCR of scanned pages (grayscale, 200–300 DPI, `psm 6`) |
| **PyMuPDF (fitz)** | Page classification, image rendering, diacritic-safe text extraction |
| **difflib `SequenceMatcher`** | Scan-vs-database alignment and opcode diffing |
| **Custom Python** | Folding/normalization, OCR-garbage rejection, confidence tiering, offset-gated applier |
| Unix `words` list | Dictionary-ratio test that separates real English from OCR noise and transliteration |

The verification scripts live in the companion working repository; the
[`scripts/`](scripts/) folder here contains the database export and Markdown build
(`export_d1.sh`, `build_from_d1.py`, `letters_format.py`) plus the comparison utilities
(`compare.py`, `strip_diacritics.py`).

---

## Contents

Generated directly from the vedabase.cc database. **Every book is a folder, and every verse is
its own Markdown file** — so each unit is individually addressable for search, diffing, and
parallel processing. Each file's content is verbatim from the database; only structural divider
headings (chapter/canto labels) are omitted, since that information is carried in the file names.

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

## Independent verification

The original scanned PDFs are available so anyone can check the text against the paper:

- [Krishna.org scans](https://krishna.org)
- Devotee Google Drive archives (linked from the source sites)

---

## License

**Scripts:** [MIT License](LICENSE) — free to copy, modify, and use.

**Texts:** Shared for educational and devotional purposes. The original works are the literary
property of His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda.
