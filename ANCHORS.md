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

The SHA-256 over the lines of `MANIFEST.sha256`, which lists every `.md` and
`.jsonl` in this repository — the text of the first editions and the ledger of
corrections applied to it.

| Date | Corpus root | Transaction |
|---|---|---|
| 26 Aug 2026 | `2ec622af2c5933cb8ea12856ce0ca6476931107456bab338d974d2e94cd497f7` | `ar://<pending>` |

Check any copy against it:

    python3 scripts/hash_manifest.py --check

An anchor on a single date says nothing about what came after. What counts is
the succession: every time the corpus changes, the manifest is regenerated and
the new root is anchored, and the old rows stay so the sequence stays legible.

## Package root

The SHA-256 over the manifest of the whole permanent archive — corpus, scans,
OCR containers, audit ledger, reports and tools together.

| Date | Package root | Manifest transaction |
|---|---|---|
| *(pending)* | *(regenerate: `python3 scripts/build_archive.py --manifest-only`)* | `ar://<pending>` |

## Superseded uploads

Arweave keeps everything, so a mistake is not removed, it is superseded. What
is listed here is what no longer stands, and why. Silence about a wrong copy
still on chain would be the one thing this archive exists to prevent.

| Date | Transaction | What it was | Why superseded |
|---|---|---|---|
| 26 Aug 2026 | `U9uIEx_mc2e1zVFPXduR6whbtdqIexzk73HMV6JVV8k` | An early draft of `PROVENANCE.md` | A test that proved the pipeline worked end to end. Retrieved from a public gateway and confirmed byte-identical to the local original. Never an anchor. |
| 26 Aug 2026 | `TxIXCmb4h3kyAVuIyaNwbBpMmabAEb6ts24bsnhhGLs` | `MANIFEST.sha256`, package root `9aeb1cb5…d718` | Uploaded before the package was final: its copy of `PROVENANCE.md` predates the OCR containers, and it still lists the 11,474 duplicated Bhāgavatam pages. Replaced by the manifest named above. |