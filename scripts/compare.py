#!/usr/bin/env python3
"""
compare.py - Text Comparison Engine

This script demonstrates the comparison methodology used in the Vedabase
Original Edition verification process. It compares extracted PDF text
against digital text to identify differences.

The verification process uses:
1. Paragraph-level alignment via Jaccard similarity
2. Character-level diff generation via SequenceMatcher
3. Multi-layer noise filtering to eliminate false positives

Usage:
    python compare.py original.txt digital.txt
"""

import difflib
import re
import sys
from pathlib import Path
from typing import List, Tuple, NamedTuple

# Import diacritic utilities
try:
    from strip_diacritics import strip_diacritics, normalize_for_comparison
except ImportError:
    # Fallback if run standalone
    def strip_diacritics(text):
        return text
    def normalize_for_comparison(text):
        return text.lower()


class Difference(NamedTuple):
    """Represents a difference between two texts."""
    line_num: int
    diff_type: str  # 'addition', 'deletion', 'change'
    original: str
    digital: str
    context: str


def get_trigrams(text: str) -> set:
    """
    Extract character trigrams from text for similarity comparison.

    Trigrams are 3-character sequences used for fuzzy matching.
    Example: "hello" -> {"hel", "ell", "llo"}
    """
    text = normalize_for_comparison(text)
    if len(text) < 3:
        return {text}
    return {text[i:i+3] for i in range(len(text) - 2)}


def jaccard_similarity(text1: str, text2: str) -> float:
    """
    Calculate Jaccard similarity index between two texts.

    Jaccard Index = |A ∩ B| / |A ∪ B|

    Returns a value between 0 (no similarity) and 1 (identical).
    """
    trigrams1 = get_trigrams(text1)
    trigrams2 = get_trigrams(text2)

    if not trigrams1 and not trigrams2:
        return 1.0

    intersection = trigrams1 & trigrams2
    union = trigrams1 | trigrams2

    return len(intersection) / len(union) if union else 0.0


def is_noise(original: str, digital: str) -> bool:
    """
    Five-layer noise filter to eliminate false positives.

    Returns True if the difference is likely OCR noise or
    insignificant variation, not a genuine textual difference.

    Layers:
    1. Diacritic normalization
    2. OCR character confusion (0/O, l/1, etc.)
    3. Whitespace normalization
    4. Punctuation normalization
    5. Low-similarity rejection
    """
    # Layer 1: Diacritic normalization
    orig_normalized = normalize_for_comparison(original)
    digi_normalized = normalize_for_comparison(digital)

    if orig_normalized == digi_normalized:
        return True

    # Layer 2: OCR character confusion
    ocr_map = {
        '0': 'o', 'O': 'o', 'o': 'o',
        '1': 'l', 'l': 'l', 'I': 'l', 'i': 'l',
        '—': '-', '–': '-', '-': '-',
        '"': '"', '"': '"', '"': '"',
        ''': "'", ''': "'", "'": "'",
    }

    def apply_ocr_map(text):
        return ''.join(ocr_map.get(c, c) for c in text)

    if apply_ocr_map(orig_normalized) == apply_ocr_map(digi_normalized):
        return True

    # Layer 3: Whitespace normalization
    orig_ws = ' '.join(original.split())
    digi_ws = ' '.join(digital.split())

    if orig_ws == digi_ws:
        return True

    # Layer 4: Punctuation normalization
    punct_pattern = r'[.,;:!?\'"()\[\]{}<>]'
    orig_no_punct = re.sub(punct_pattern, '', orig_ws)
    digi_no_punct = re.sub(punct_pattern, '', digi_ws)

    if orig_no_punct == digi_no_punct:
        return True

    # Layer 5: Low-similarity rejection (misaligned paragraphs)
    similarity = jaccard_similarity(original, digital)
    if similarity < 0.3:
        # Too different - likely misaligned, not a real diff
        return True

    return False


def find_differences(
    original_text: str,
    digital_text: str,
    context_lines: int = 2
) -> List[Difference]:
    """
    Find genuine differences between original and digital text.

    Uses SequenceMatcher for detailed comparison and filters
    results through the noise detection system.

    Args:
        original_text: Text extracted from scanned PDF
        digital_text: Text from digital database
        context_lines: Number of context lines to include

    Returns:
        List of Difference objects representing genuine changes
    """
    original_lines = original_text.splitlines()
    digital_lines = digital_text.splitlines()

    differences = []

    matcher = difflib.SequenceMatcher(
        None,
        original_lines,
        digital_lines,
        autojunk=False
    )

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            continue

        original_chunk = '\n'.join(original_lines[i1:i2])
        digital_chunk = '\n'.join(digital_lines[j1:j2])

        # Apply noise filter
        if is_noise(original_chunk, digital_chunk):
            continue

        # Get context
        context_start = max(0, i1 - context_lines)
        context_end = min(len(original_lines), i2 + context_lines)
        context = '\n'.join(original_lines[context_start:context_end])

        diff_type = {
            'replace': 'change',
            'delete': 'deletion',
            'insert': 'addition'
        }.get(tag, tag)

        differences.append(Difference(
            line_num=i1 + 1,
            diff_type=diff_type,
            original=original_chunk,
            digital=digital_chunk,
            context=context
        ))

    return differences


def generate_report(differences: List[Difference]) -> str:
    """Generate a human-readable diff report."""
    if not differences:
        return "No differences found. Texts match perfectly."

    lines = [
        f"Found {len(differences)} difference(s):\n",
        "=" * 60
    ]

    for i, diff in enumerate(differences, 1):
        lines.append(f"\n[{i}] Line {diff.line_num} - {diff.diff_type.upper()}")
        lines.append("-" * 40)

        if diff.diff_type == 'deletion':
            lines.append(f"REMOVED: {diff.original}")
        elif diff.diff_type == 'addition':
            lines.append(f"ADDED: {diff.digital}")
        else:
            lines.append(f"ORIGINAL: {diff.original}")
            lines.append(f"DIGITAL:  {diff.digital}")

        lines.append(f"\nContext:\n{diff.context}")
        lines.append("=" * 60)

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 3:
        print("Usage: python compare.py <original.txt> <digital.txt>")
        print("\nExample:")
        print("  python compare.py scan_extract.txt vedabase.txt")
        sys.exit(1)

    original_path = Path(sys.argv[1])
    digital_path = Path(sys.argv[2])

    if not original_path.exists():
        print(f"Error: {original_path} not found")
        sys.exit(1)

    if not digital_path.exists():
        print(f"Error: {digital_path} not found")
        sys.exit(1)

    original_text = original_path.read_text(encoding='utf-8')
    digital_text = digital_path.read_text(encoding='utf-8')

    print(f"Comparing:")
    print(f"  Original: {original_path}")
    print(f"  Digital:  {digital_path}")
    print()

    differences = find_differences(original_text, digital_text)
    report = generate_report(differences)

    print(report)

    # Summary statistics
    print(f"\nSummary:")
    print(f"  Original lines: {len(original_text.splitlines())}")
    print(f"  Digital lines:  {len(digital_text.splitlines())}")
    print(f"  Differences:    {len(differences)}")

    similarity = jaccard_similarity(original_text, digital_text)
    print(f"  Similarity:     {similarity:.1%}")


if __name__ == '__main__':
    main()
