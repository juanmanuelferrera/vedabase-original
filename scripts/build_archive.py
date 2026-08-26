#!/usr/bin/env python3
"""Assemble the permanent archive: text, scans, evidence and tools.

Why this exists
---------------
The work lives in three places: the text in this repository, the scans and the
OCR in `scan_vedabase`, and the audit ledger in
`astro_vedabase/scripts/scan_audit`. Keeping them apart is right for working:
each changes at its own pace, and binaries have no place in git.

The permanent archive is the opposite case — it has to travel together. Keeping
the text without the evidence it was checked against is worth little, and so is
keeping the scans without the record of what was decided at each discrepancy.
This script builds that single tree, computes a manifest over the whole set and
leaves the package ready to upload.

What stays out, and why
-----------------------
- virtualenvs, `__pycache__`, `node_modules`: they get reinstalled
- `improved/`: regenerated from `originals/` by reocr_all.py
- `reports/` and the intermediate `out_surya*` batches: superseded by the final result
- anything reconstructible from what does go in

Hard links are used, so assembling the package does not duplicate the 3 GB on
disk. If the destination is on another volume, files are copied instead.

Usage
-----
    python3 scripts/build_archive.py --dry-run         # what would go in, touching nothing
    python3 scripts/build_archive.py                   # assemble it
    python3 scripts/build_archive.py --with-tesseract  # add ocr/ (80 MB)
"""
import argparse
import hashlib
import os
import shutil
import sys

CORPUS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.expanduser("~/git_projects/scan_vedabase")
AUDIT = os.path.expanduser("~/git_projects/astro_vedabase/scripts/scan_audit")
DEST = os.path.expanduser("~/vedabase-archive")

EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", "surya-venv", ".venv", "venv"}

# (path in the package, source, extension filter)
# Section names match the table in PROVENANCE.md — keep them in step.
SECTIONS = [
    # .md and .jsonl are split on purpose. They are different things — the verses
    # and the ledger of corrections — and they need different content types on
    # upload. On Arweave a wrong content type cannot be corrected afterwards.
    ("corpus",              CORPUS,                             (".md",)),
    ("corrections",         CORPUS,                             (".jsonl",)),
    ("scans",               os.path.join(SCAN, "originals"),    (".pdf",)),
    ("ocr-surya",           os.path.join(SCAN, "surya_ocr"),    (".txt",)),  # see SURYA below
    ("audit/ledger",        AUDIT,                              (".json",)),
    ("audit/notes",         AUDIT,                              (".md",)),
    ("audit/candidates",    os.path.join(AUDIT, "out_fine"),    (".jsonl",)),
    ("audit/text-layer",    os.path.join(AUDIT, "capa_texto"),  (".json",)),
    ("reports",             AUDIT,                              (".html",)),
    ("tools/comparison",    SCAN,                               (".py",)),
    ("tools/audit",         AUDIT,                              (".py", ".sh")),
    ("reference-standards", os.path.join(SCAN, "gold_standards"), None),
]

OPTIONAL_TESSERACT = ("ocr-tesseract", os.path.join(AUDIT, "ocr"), (".txt",))

# The Surya run left the Bhagavatam laid out twice: once as loose volume
# directories at the top of surya_ocr (SB1.1 … SB10.3) and again inside
# srimad-bhagavatam/, which holds those same thirty. Verified 2026-08-26: the
# 11,474 relative paths match and all 11,474 SHA-256 match. Without this the
# package carried every Bhagavatam page twice — 23 MB and 11,474 files of pure
# duplication, which is also 11,474 files paid for twice on upload.
#
# The merged copy is kept: it is how every other book in the section is named.
SURYA = os.path.join(SCAN, "surya_ocr")


def duplicated_top(base, name):
    """Top-level directory to prune, because it appears again further down."""
    return base == SURYA and name.startswith("SB") and "." in name


def walk(base, extensions, recursive=True):
    if not os.path.isdir(base):
        return []
    found = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        if dirpath == base:
            dirnames[:] = [d for d in dirnames if not duplicated_top(base, d)]
        if not recursive and dirpath != base:
            dirnames[:] = []
            continue
        for n in filenames:
            if n.startswith("."):
                continue
            if extensions and not n.endswith(extensions):
                continue
            full = os.path.join(dirpath, n)
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            found.append((rel, full))
    found.sort(key=lambda p: p[0].encode("utf-8"))
    return found


def link(source, target):
    os.makedirs(os.path.dirname(target), exist_ok=True)
    if os.path.exists(target):
        os.remove(target)
    try:
        os.link(source, target)           # no extra disk used
    except OSError:
        shutil.copy2(source, target)      # different volume: copy


def sha256(path, block=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(block), b""):
            h.update(chunk)
    return h.hexdigest()


def escribe_manifiesto(dest):
    """SHA-256 of every file in the package, plus a root over the whole set.

    UPLOAD-STATE.json is skipped along with the manifest itself: it is the
    uploader's bookkeeping, it changes on every batch, and it is not part of
    what is being certified.
    """
    print("\ncomputing the manifest for the whole package...")
    volatiles = {"MANIFEST.sha256", "UPLOAD-STATE.json", "upload.log"}
    entries = []
    for dirpath, dirnames, filenames in os.walk(dest):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for n in sorted(filenames):
            if n in volatiles or n.startswith("."):
                continue
            full = os.path.join(dirpath, n)
            rel = os.path.relpath(full, dest).replace(os.sep, "/")
            entries.append((rel, full))
    entries.sort(key=lambda p: p[0].encode("utf-8"))
    body = "".join(f"{sha256(f)}  {r}\n" for r, f in entries)
    root = hashlib.sha256(body.encode("utf-8")).hexdigest()

    with open(os.path.join(dest, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
        f.write(f"# Manifest of the permanent archive — {len(entries)} files\n")
        f.write(f"# root: {root}\n#\n")
        f.write(body)

    print(f"package root: {root}")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Assemble the permanent archive package.")
    ap.add_argument("--dest", default=DEST)
    ap.add_argument("--dry-run", action="store_true", help="list only, assemble nothing")
    ap.add_argument("--with-tesseract", action="store_true",
                    help="include ocr/ from Tesseract (80 MB): the other half of the collation")
    ap.add_argument("--manifest-only", action="store_true",
                    help="recompute the manifest over the package as it stands, assembling "
                         "nothing. Needed because pack_ocr.py runs after assembly and changes "
                         "what the package contains")
    args = ap.parse_args()

    if args.manifest_only:
        return escribe_manifiesto(args.dest)

    sections = list(SECTIONS)
    if args.with_tesseract:
        sections.insert(3, OPTIONAL_TESSERACT)

    # Sections pointing at the root of AUDIT or SCAN must not recurse: below them
    # sit 45,000 .txt files and superseded batches we do not want dragged in.
    non_recursive = {AUDIT, SCAN, CORPUS}

    total_bytes, total_files = 0, 0
    summary = []

    for name, base, filt in sections:
        recursive = base not in non_recursive or base == CORPUS
        files = walk(base, filt, recursive=recursive)
        if not files:
            summary.append((name, 0, 0, "(empty or missing)"))
            continue
        section_bytes = sum(os.path.getsize(s) for _, s in files)
        total_bytes += section_bytes
        total_files += len(files)
        summary.append((name, len(files), section_bytes, ""))
        if args.dry_run:
            continue
        for rel, source in files:
            link(source, os.path.join(args.dest, name, rel))

    print(f"{'section':<26} {'files':>9} {'size':>11}")
    print("-" * 49)
    for name, n, b, note in summary:
        print(f"{name:<26} {n:>9} {b/1e6:>9.1f} MB  {note}")
    print("-" * 49)
    print(f"{'TOTAL':<26} {total_files:>9} {total_bytes/1e6:>9.1f} MB")

    gib = total_bytes / (1 << 30)
    print(f"\nArweave: ~${gib*21.06:.0f} at protocol rate · ~${gib*32.56:.0f} by card (one-time)")

    if args.dry_run:
        print("\n(--dry-run: nothing was assembled)")
        return 0

    escribe_manifiesto(args.dest)
    print(f"package at {args.dest}")
    print("\nNext: upload it, and record the transaction ids in PROVENANCE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
