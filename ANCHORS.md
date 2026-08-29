# Anchors

Every figure here depends on a manifest, so this file is deliberately outside
every manifest: it is excluded from `MANIFEST.sha256`, excluded from the
permanent archive package, and uploaded on its own after the transaction ids
are known.

A file cannot state the hash of a set it belongs to. Writing the number would
change the number. On 26 Aug 2026 the package root was noted inside
`PROVENANCE.md`, which the manifest covers, and the manifest was stale the
instant the file was saved. This file exists so that cannot happen again.

`PROVENANCE.md` explains the method and carries no figure that changes, which
is what allows it to be certified along with the text it describes.

## Corpus root

The SHA-256 over the lines of `MANIFEST.sha256` in this repository, which lists
every `.md` and `.jsonl` here — the text of the first editions and the ledger of
corrections applied to it, 102,836 files.

| Date | Corpus root | Anchored in |
|---|---|---|
| 29 Aug 2026 | `8bcaa67ed8498e09c6e956f45807d5f7cb67ae394ee37e51532a080af77a221d` | this file |

Check any copy against it:

    python3 scripts/hash_manifest.py --check

An anchor on a single date says nothing about what came after. What counts is
the succession: every time the corpus changes, the manifest is regenerated and
the new root is anchored, and the old rows stay so the sequence stays legible.

## Package root

The SHA-256 over the manifest of the permanent archive — corpus, scans, OCR
containers, correction ledgers, audit ledger, reports and tools together. It
covers the 86,995 files that were published, and only those.

| Date | Package root | Manifest transaction |
|---|---|---|
| 29 Aug 2026 | `51c0318a5eb1857bc4dac99c9e3a1118ab57e9241ffd18bab826409056fae988` | `ar://81Fo6FX9AR4RcleArZt0VwFBujN_JyfAALcvsMQ7uoA` |

Reproduce it with `python3 scripts/build_archive.py --manifest-only`.

## What is in the archive

| Piece | Files |
|---|---:|
| corpus — English, Spanish, Portuguese, Hindi | 86,418 |
| scans, 71 PDFs of the printed books | 71 |
| OCR containers, one `.tar` per book per engine | 43 |
| correction ledgers | 107 |
| audit ledger | 208 |
| reports | 8 |
| tools | 137 |
| reference standards | 3 |
| manifest | 1 |
| **published in total** | **86,995** |

The Russian translation, 16,311 files, is not published. See *What is
deliberately absent* in `PROVENANCE.md`.

`PROVENANCE.md` as published: `ar://NO7ILnkpN3nUgZ1dsCxIBvWWKs3EI9EV1YuCjJSWxTA`

This file as published: `ar://cdzR8SqY5IGYPvh-inBYE6h2PZNaWKdrri5USKEx9a8`
Recording its own address here is not circular: nothing hashes this file, so
adding a line changes nothing but the line.

## Superseded uploads

Arweave keeps everything, so a mistake is not removed, it is superseded. What
is listed here is what no longer stands, and why. Silence about a wrong copy
still on chain would be the one thing this archive exists to prevent.

| Date | Transaction | What it was | Why superseded |
|---|---|---|---|
| 26 Aug 2026 | `U9uIEx_mc2e1zVFPXduR6whbtdqIexzk73HMV6JVV8k` | An early draft of `PROVENANCE.md` | A test that proved the pipeline worked end to end. Retrieved from a public gateway and confirmed byte-identical to the local original. Never an anchor. |
| 26 Aug 2026 | `TxIXCmb4h3kyAVuIyaNwbBpMmabAEb6ts24bsnhhGLs` | `MANIFEST.sha256`, package root `9aeb1cb5…d718` | Uploaded before the package was final: its copy of `PROVENANCE.md` predated the OCR containers, and it still listed the 11,474 duplicated Bhāgavatam pages. |
| 26 Aug 2026 | `y7AgXnAdRsvd7tuFeKTRVEB1SuB9u2eOmSpgOMk9mCg` | `PROVENANCE.md` | Did not yet say that the Russian translation is held back, so it described an archive with 16,311 files silently missing. |
| 26 Aug 2026 | corpus root `2ec622af…d497f7` | The corpus root anchored that day | Superseded: `PROVENANCE.md` gained the section on what is absent, and every `.md` is inside the corpus manifest. |
| 28 Aug 2026 | `ar://Wf8LWB6xrovGKM4xZHYRcz6F4G1L74MKdsUjUFsb9rg` | `MANIFEST.sha256`, package root `274c2af2…a09b17` | Written before six files were found to be missing from the chain and uploaded, and before the verifier's own working files were kept out of it. |
| 28 Aug 2026 | `ar://UL6GCZ4-o51WCJHfQb9ZLrv0NAJAVSiQNB9NiupFql8` | `PROVENANCE.md` | Did not yet record the six missing files, nor the warning about single-gateway checks. |
