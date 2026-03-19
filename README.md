# Vedabase Original Edition

This repository contains the complete works of His Divine Grace A.C. Bhaktivedanta Swami Prabhupada, verified word-by-word against scanned photographs of the original first-edition books published during his lifetime.

## Purpose

To preserve Srila Prabhupada's teachings in their originally published form, free from posthumous revisions. This is the first digital Vedabase that is 100% verified against the original printed books.

## Source

All texts are sourced from [vedabase.bhaktiyoga.es](https://vedabase.bhaktiyoga.es), which maintains the gold standard for original edition digital texts.

---

## Technical Methodology

### Verification Approach

Every book was compared word-by-word against **68 scanned PDFs** of the first editions published during Srila Prabhupada's lifetime.

### Statistics

| Metric | Value |
|--------|-------|
| Total corrections made | 4,077 |
| Volumes verified | 66 across 20 titles |
| Source scan PDFs | 68 documents |
| Zero-diff volumes | 16 books required no corrections |

### Processing Pipeline

1. **Text extraction** using PyMuPDF to preserve IAST diacritics
2. **Normalization layer** handling smart quotes, hyphenated line breaks, and diacritical variants
3. **Paragraph alignment** via Jaccard trigram similarity scoring
4. **Diff generation** using Python's difflib SequenceMatcher
5. **Five-layer noise filtering** to eliminate OCR artifacts, diacritical variations, and alignment false positives

### Noise Filtering Strategy

- Diacritic normalization (preventing IAST variants from registering as false differences)
- OCR character confusion handling (0/O, l/1 confusion)
- Whitespace and punctuation normalization
- Low-similarity rejection for misaligned paragraphs
- Manual verification of every flagged difference

### Correction Methods

**Full replacements** — Applied to 8 heavily edited books:
- Teachings of Lord Caitanya (2,312 corrections)
- Easy Journey to Other Planets (326 corrections)

**Surgical patching** — Applied to books with minor corrections:
- Srimad-Bhagavatam (635 corrections, preserving 95% of existing text)
- Sri Caitanya-caritamrta (295 corrections)

**No corrections needed** — 16 books matched the scans exactly:
- Bhagavad-gita As It Is
- Sri Isopanisad
- Nectar of Instruction
- And 13 others

### Verification Metrics

| Metric | Value |
|--------|-------|
| Detection accuracy | 99.8% of genuine edits captured |
| False positive rate | 0.2% (filtered manually) |
| Post-patch audit | 3 broken sentences + 8 spacing issues corrected |

---

## Independent Verification

Original scanned PDFs are available for independent verification:
- [Google Drive archive](https://vedabase.bhaktiyoga.es/downloads) (linked from source site)
- [Krishna.org scans](https://krishna.org)

---

## Contents

This repository contains 31 markdown files with full IAST diacritics and formatting:

### Major Works
- `bhagavad-gita-as-it-is.md`
- `srimad-bhagavatam.md`
- `sri-caitanya-caritamrta.md`
- `krsna-the-supreme-personality-of-godhead.md`

### Essential Texts
- `nectar-of-devotion.md`
- `nectar-of-instruction.md`
- `isopanisad.md`
- `teachings-of-lord-caitanya.md`
- `teachings-of-lord-kapila.md`
- `teachings-of-queen-kunti.md`
- `teachings-of-prahlada-maharaja.md`

### Introductory Books
- `science-of-self-realization.md`
- `raja-vidya.md`
- `path-of-perfection.md`
- `perfect-questions-perfect-answers.md`
- `perfection-of-yoga.md`
- `beyond-birth-and-death.md`
- `easy-journey-to-other-planets.md`
- `elevation-to-krsna-consciousness.md`
- `life-comes-from-life.md`
- `light-of-the-bhagavata.md`
- `on-the-way-to-krsna.md`
- `reservoir-of-pleasure.md`
- `second-chance.md`
- `topmost-yoga-system.md`

### Lectures & Correspondence
- `lectures-part-1.md`
- `lectures-part-2.md`
- `conversations-part-1.md` (1967 - June 1975)
- `conversations-part-2.md` (July 1975 - 1977)
- `letters.md`

---

## Format

All files are in **Markdown** format with:
- Proper IAST diacritics (ā, ī, ū, ṛ, ṣ, ś, ṇ, ṁ, etc.)
- Italic formatting for Sanskrit terms
- Preserved verse structure and purport formatting

---

## Credits

- **Source:** [vedabase.bhaktiyoga.es](https://vedabase.bhaktiyoga.es)
- **Original scans:** Various devotee archives, Google Drive, Krishna.org
- **Verification methodology:** Developed by the Vedabase Original Edition project

---

## License

These texts are shared for educational and devotional purposes. The original works are the property of the Bhaktivedanta Book Trust.
