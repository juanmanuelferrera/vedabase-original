# Scripts

This folder contains scripts used in the Vedabase Original Edition verification and synchronization process.

## Overview

| Script | Purpose |
|--------|---------|
| `sync_from_source.py` | Downloads and updates texts from vedabase.bhaktiyoga.es |
| `compare.py` | Text comparison engine with noise filtering |
| `strip_diacritics.py` | IAST diacritic processing utilities |

---

## sync_from_source.py

**Purpose:** Synchronize this repository with the gold standard texts from vedabase.bhaktiyoga.es.

**Usage:**
```bash
python scripts/sync_from_source.py
```

**What it does:**
1. Downloads ZIP files for each book from the source
2. Extracts the `.md` files
3. Replaces all content in the repository
4. Reports success/failure for each download

---

## compare.py

**Purpose:** Compare extracted PDF text against digital text to identify genuine differences.

**Usage:**
```bash
python scripts/compare.py original.txt digital.txt
```

**Features:**
- Paragraph-level alignment via Jaccard trigram similarity
- Character-level diff generation via `difflib.SequenceMatcher`
- **Five-layer noise filtering:**
  1. Diacritic normalization
  2. OCR character confusion handling (0/O, l/1)
  3. Whitespace normalization
  4. Punctuation normalization
  5. Low-similarity rejection

**Output:** Human-readable diff report with context and statistics.

---

## strip_diacritics.py

**Purpose:** Process IAST (International Alphabet of Sanskrit Transliteration) diacritics for text comparison.

**Usage:**
```bash
python scripts/strip_diacritics.py "Śrīla Prabhupāda"
# Output: Srila Prabhupada
```

**Features:**
- Complete IAST to ASCII mapping table
- Unicode NFD normalization for combining characters
- Whitespace and quote normalization

**Example output:**
```
IAST Diacritic Stripping Examples:

  Śrīla Prabhupāda
  → Srila Prabhupada

  Bhagavad-gītā As It Is
  → Bhagavad-gita As It Is

  Śrīmad-Bhāgavatam
  → Srimad-Bhagavatam
```

---

## Requirements

- Python 3.8+
- No external dependencies (uses only standard library)

For PDF text extraction (not included), the verification process uses:
- **PyMuPDF (fitz):** `pip install pymupdf`

---

## Verification Methodology

These scripts implement the hybrid verification process:

```
┌─────────────────┐     ┌─────────────────┐
│  Scanned PDF    │     │  Digital Text   │
│  (68 sources)   │     │  (Vedabase)     │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│  PyMuPDF        │     │  UTF-8 Text     │
│  Extraction     │     │  Normalization  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌─────────────────────┐
         │  Jaccard Alignment  │
         │  + SequenceMatcher  │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  5-Layer Noise      │
         │  Filtering          │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  Manual Review      │
         │  + Correction       │
         └──────────┬──────────┘
                    ▼
         ┌─────────────────────┐
         │  Gold Standard      │
         │  Output             │
         └─────────────────────┘
```

---

## Source

Scripts based on methodology from [vedabase.bhaktiyoga.es](https://vedabase.bhaktiyoga.es).
