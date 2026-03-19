#!/usr/bin/env python3
"""
strip_diacritics.py - IAST Diacritic Processing Utility

This script demonstrates the diacritic normalization technique used in the
Vedabase Original Edition verification process. It maps IAST (International
Alphabet of Sanskrit Transliteration) characters to their ASCII equivalents
for comparison purposes.

Usage:
    python strip_diacritics.py "Śrīla Prabhupāda"
    # Output: Srila Prabhupada
"""

import unicodedata
import sys

# IAST to ASCII mapping table
IAST_MAP = {
    # Vowels
    'ā': 'a', 'Ā': 'A',
    'ī': 'i', 'Ī': 'I',
    'ū': 'u', 'Ū': 'U',
    'ṛ': 'r', 'Ṛ': 'R',
    'ṝ': 'r', 'Ṝ': 'R',
    'ḷ': 'l', 'Ḷ': 'L',
    'ḹ': 'l', 'Ḹ': 'L',

    # Anusvara and Visarga
    'ṁ': 'm', 'Ṁ': 'M',
    'ṃ': 'm', 'Ṃ': 'M',
    'ḥ': 'h', 'Ḥ': 'H',

    # Consonants
    'ṅ': 'n', 'Ṅ': 'N',
    'ñ': 'n', 'Ñ': 'N',
    'ṭ': 't', 'Ṭ': 'T',
    'ḍ': 'd', 'Ḍ': 'D',
    'ṇ': 'n', 'Ṇ': 'N',
    'ś': 's', 'Ś': 'S',
    'ṣ': 's', 'Ṣ': 'S',

    # Additional characters sometimes used
    'ç': 's', 'Ç': 'S',  # Alternative for ś
}


def strip_diacritics(text: str) -> str:
    """
    Remove IAST diacritics from text for comparison purposes.

    This function:
    1. Applies Unicode NFD normalization (decomposes combined characters)
    2. Maps known IAST characters to ASCII equivalents
    3. Removes any remaining combining marks

    Args:
        text: Input text with IAST diacritics

    Returns:
        Text with diacritics removed
    """
    # First pass: direct character mapping
    result = []
    for char in text:
        if char in IAST_MAP:
            result.append(IAST_MAP[char])
        else:
            result.append(char)

    text = ''.join(result)

    # Second pass: NFD normalization to handle combining characters
    # This decomposes characters like "ā" into "a" + combining macron
    normalized = unicodedata.normalize('NFD', text)

    # Remove combining marks (category 'M')
    stripped = ''.join(
        char for char in normalized
        if unicodedata.category(char) != 'Mn'  # Mn = Mark, Nonspacing
    )

    return stripped


def normalize_for_comparison(text: str) -> str:
    """
    Full normalization for text comparison.

    Applies:
    - Diacritic stripping
    - Lowercase conversion
    - Whitespace normalization
    - Quote normalization
    """
    text = strip_diacritics(text)
    text = text.lower()

    # Normalize whitespace
    text = ' '.join(text.split())

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text


if __name__ == '__main__':
    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
        print(f"Original:   {input_text}")
        print(f"Stripped:   {strip_diacritics(input_text)}")
        print(f"Normalized: {normalize_for_comparison(input_text)}")
    else:
        # Demo
        examples = [
            "Śrīla Prabhupāda",
            "Bhagavad-gītā As It Is",
            "Śrīmad-Bhāgavatam",
            "Śrī Caitanya-caritāmṛta",
            "Kṛṣṇa, the Supreme Personality of Godhead",
        ]
        print("IAST Diacritic Stripping Examples:\n")
        for text in examples:
            print(f"  {text}")
            print(f"  → {strip_diacritics(text)}\n")
