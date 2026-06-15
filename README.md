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

Generated directly from the vedabase.cc database, at the repository root. Small books are one
file each; large works are split so every file stays browsable on GitHub:

| Path | Contents |
|------|----------|
| `bhagavad-gita-as-it-is.md`, `isopanisad.md`, `nectar-of-devotion.md`, … | one file per small book |
| `srimad-bhagavatam/canto-01.md` … `canto-10.md` | Śrīmad-Bhāgavatam, by canto |
| `sri-caitanya-caritamrta/{adi,madhya,antya}-lila.md` | Caitanya-caritāmṛta, by līlā |
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
