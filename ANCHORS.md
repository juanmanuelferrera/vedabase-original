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

| Date | Corpus root | Commit | Anchored in |
|---|---|---|---|
| 29 Aug 2026 | `0c8523c221b02001d918ca9bb17d81f4d138e10580ec2820992281d89a38235d` | `0b1142633040cc5c2effeac0b25e1e38e8ea13dd` | this file |
| 17 Sep 2026 | `42e78565f7e05bc5d0da6ded9a399669b421b9bd7a44b6bf44141601d7f26b37` | `cab11a0318dff52acb070b99e9d00d530636ab6b` | this file |
| 20 Sep 2026 | `f13169c3e9b2d5825568c5455601dccee95338a86cabbf52525a64af981f09b2` | `79f61689741a01fd422e58d81e33bc308b9133aa` | superseded same day — see below |
| 20 Sep 2026 | `cfc82f90ac2441ffaedb008e1c164dabe50057d478aeacdd49b6301e08026be7` | `74bf463eaace855f8995cd4b951ed9c1c8b771d0` | superseded same day |
| 20 Sep 2026 | `71e4874b0ca2cd12ed04d773385518a2a07838fdbfe9009736655c80ff0986be` | `2648cd44f7a67f93376597d0ca8228d346f5a397` | this file |

The 17 Sep root covers 102,866 files, thirty more than the August one and
forty-one changed. The additions and thirty-eight of the changes are the Russian
translation, completed on 16 Sep: all 22 books of the archive now have Russian.
The other three changes are older than that work — `corpus/corrections.jsonl` and
two Bhagavad-gītā files touched by `d3159060f2`, a commit that came after the
August anchor and for which the manifest was never regenerated. The manifest had
been stale by those three files since 31 Aug; saying so is the point of this
table.

The 20 Sep root covers 107,201 files, 4,335 more than the September one. All
4,335 are the Śrīmad-Bhāgavatam in Russian, cantos 5 to 10. They were not new
translations: the canonical `sb_ru.jsonl` already held all ten cantos and
vedabase.cc had been serving them since they were finished. What had never been
re-run was the Markdown export, so the corpus stopped at canto 4 while English,
Spanish, Portuguese and Hindi each had ten. The gap surfaced while validating
the path manifest, when a canto 5 path resolved to nothing.

Three roots were written on 20 Sep and only the last is anchored. `f13169c3`
covered the Russian Bhāgavatam; `cfc82f90` added *Light of the Bhāgavata* in
Hindi, 49 texts translated since June that had no canonical file; `71e4874b`
adds 342 corrections to Portuguese, Hindi and Spanish — the chapter-end colophon
restored in 328 Portuguese files, and a stray `*Sinônimos` line removed from
inside the synonyms field, where it left the italics open and bleeding into the
rest of the block. Only `71e4874b` is on chain. The intermediate two are named
because a reader checking out those commits will compute them, and an
unexplained root is the thing this file exists to prevent.

`f13169c3` stood for a few hours. It was superseded by `cfc82f90` when *Light of
the Bhāgavata* was assembled in Hindi and added to the corpus — 49 texts that had
been translated since June but had no canonical file. Neither root has been
anchored on chain, so the succession costs nothing to correct; both rows stay so
the sequence stays legible.

One root that appears in no row: `ea5e2562231b8ec90ca4fbe1521ba42649bacc486395d5c856130526dc1eb576`,
written into `MANIFEST.sha256` at commit `19fee208bb` on 17 Sep and superseded
before it was ever published. It is named here rather than omitted, because a
reader who checks out that commit will compute it and find it in no table, and
an unexplained root is the thing this file exists to prevent.

**On the commit column.** The manifest's own header names the commit that was
checked out when it was generated, which is always the one *before* the commit
that carries it — the file cannot contain a hash of a tree it has not joined yet.
`--check` therefore fails at the header's commit and passes at the next one. The
August row already worked around this by naming `0b114263` rather than the
`6cc37978` in its header, and this row names `cab11a03` for the same reason.

An anchor names a date, and a date is not something anyone can return to. It also
names the **commit**, which is: `git checkout <commit>` puts the repository in
exactly the state the root was computed over, and `--check` will agree. Without
that, editing so much as this README after anchoring leaves a published root that
matches nothing anyone can reproduce — which reads like tampering. It happened on
the first attempt at this table.

Check any copy against it:

    python3 scripts/hash_manifest.py --check

An anchor on a single date says nothing about what came after. What counts is
the succession: every time the corpus changes, the manifest is regenerated and
the new root is anchored, and the old rows stay so the sequence stays legible.

## Package root

The SHA-256 over the manifest of the permanent archive — corpus, scans, OCR
containers, correction ledgers, audit ledger, reports and tools together. Each
root covers the files that were published as of its date, and only those.

| Date | Package root | Manifest transaction |
|---|---|---|
| 29 Aug 2026 | `51c0318a5eb1857bc4dac99c9e3a1118ab57e9241ffd18bab826409056fae988` | `ar://81Fo6FX9AR4RcleArZt0VwFBujN_JyfAALcvsMQ7uoA` |
| 17 Sep 2026 | `37faf5b420ec6717d081f95852b6b12a192f7ad46ecfd823dff962298f49c464` | `ar://llpmiWxk1pGKskJ5HcOlP5kVevSy44qUCo6sGTIGIsM` |

The 17 Sep package root covers 103,481 files: the 86,995 of August, the 16,361
Russian files uploaded that day, the 124 index pages regenerated to include them,
and the root-level `index.html`.

**Three lists had to be emptied for this, not one**, and the archive only works
because each of them names the others. `EXCLUIR_RUTAS` in `upload_archive.py`
kept the text off the chain; `NO_PUBLICADO` in `build_archive.py` kept it out of
the manifest; `FUERA` in `build_index.py` kept it out of the browsable index.
Lifting the first alone would have published 16,361 files under a root that did
not describe them — a manifest that fails the verification it exists to make
possible reads as tampering, not as an oversight. The second was caught because
the package root did not move when the Russian files on disk were replaced: they
were never being hashed. The third, because the index still counted 102 pages
when it should have counted 124.

**The 17 Sep package root no longer describes the archive.** On 20 Sep the
4,335 Russian Bhāgavatam files above were uploaded, along with 222 files that
had never reached the chain at all and 8 that were re-uploaded with corrected
internal links. The archive now holds 107,816 published files, and no package
root has been computed over them yet.

It cannot be computed on the machine this was done from. That machine holds
`corpus`, `_index` and the manifest, and nothing else: the 577 files of the
other sections — 71 scans, 43 OCR containers, 107 correction ledgers, 208 audit
ledgers, 8 reports, 137 tools, 3 reference standards — are on chain and in the
path manifest, but are not on its disk. Running `--manifest-only` there would
produce a root over 107,239 files and present it as a root over 107,816, which
is precisely the kind of figure this file exists to stop. It has to be recomputed
where the whole package lives.

Reproduce it with `python3 scripts/build_archive.py --manifest-only`.

## What is in the archive

| Piece | Files |
|---|---:|
| corpus — English, Spanish, Portuguese, Hindi | 86,467 |
| corpus — Russian, all 22 books | 20,696 |
| scans, 71 PDFs of the printed books | 71 |
| OCR containers, one `.tar` per book per engine | 43 |
| correction ledgers | 108 |
| audit ledger | 208 |
| reports | 8 |
| tools | 137 |
| reference standards | 3 |
| index pages | 124 |
| manifest | 1 |
| **published in total** | **107,866** |

Counted from the path manifest of 20 Sep 2026, which is the only list that
covers every published file. The 50 added since the previous count are *Light of
the Bhāgavata* in Hindi: 49 texts and one correction ledger. An earlier version of this table said the Russian
translation was not published, and went on saying it after the 17 Sep row above
recorded that it had been — the two statements sat three paragraphs apart. What
`PROVENANCE.md` has to say about the Russian is not that it is absent but that
it carries a weaker warrant than the text beside it: see *The Russian
translation, and what it is worth*.

`PROVENANCE.md` as published: `ar://NO7ILnkpN3nUgZ1dsCxIBvWWKs3EI9EV1YuCjJSWxTA`

This file as published: `ar://620vnKvmZGfrE4ft2vAu4ovjAe2FmAcQVh5CFKChj9o`
Recording its own address here is not circular: nothing hashes this file, so
adding a line changes nothing but the line.

## Browsing the archive

The transaction ids above address single files. To walk the archive as folders:

The drive is public in the ArFS sense — nothing is encrypted, and every file can
be fetched by its transaction id by anyone. But **`app.ardrive.io` is not a way in
for a stranger**: it asks for a password even in a private window, because it is
an application for managing your own drives, not a viewer for someone else's.
Tested 29 Aug 2026. An earlier version of this file said otherwise; it was wrong.

| | |
|---|---|
| drive id | `f1be3a02-a7cd-4251-aa65-5e3652b690a1` |
| root folder id | `a01bc670-61a5-46a4-87b8-5b4439b45750` |
| privacy | public (unencrypted) |

Those two identifiers are written here because they exist nowhere else, and from
them any ArFS-aware tool can rebuild the tree without ArDrive's involvement.

### The way in

**https://arweave.net/_XwhslATEbSsiHRcbV8t3aFN5rrHr8UGoQUEFVZXeAA**

An Arweave path manifest over the whole archive: 107,866 paths, served by any
gateway, needing no account and no application. The address above returns a front
page; append a path and you get the file:

    .../_XwhslATEbSsiHRcbV8t3aFN5rrHr8UGoQUEFVZXeAA/corpus/isopanisad/iso-1.md
    .../_XwhslATEbSsiHRcbV8t3aFN5rrHr8UGoQUEFVZXeAA/scans/adi1.pdf
    .../_XwhslATEbSsiHRcbV8t3aFN5rrHr8UGoQUEFVZXeAA/MANIFEST.sha256

    .../_XwhslATEbSsiHRcbV8t3aFN5rrHr8UGoQUEFVZXeAA/corpus/translations/russian/srimad-bhagavatam/canto-10/chapter-01/sb-10.1.1.md

**This manifest was built by hand, and the reason is worth recording.**
`ardrive create-manifest` enumerates folders through `/tx/<id>`, and that
endpoint returns 404 for every transaction that travels inside a Turbo bundle —
which is all of this archive. The CLI walks into cascading 404s and the web
interface cannot list the folders either. The manifest was therefore assembled
from the uploader's own state file, which records the path and transaction of
every file as it goes up, and checked against the archive on disk: 0 files on
disk absent from it, 0 paths in it absent from disk.

**A path must name a file.** Arweave manifests resolve files, not folders, so
`/corpus/` returns nothing. `MANIFEST.sha256` lists every path there is.

Verified 29 Aug 2026 across four gateways: the front page, `PROVENANCE.md` at both
its paths, the manifest, a verse, a 37 MB scan and an OCR container all returned
byte-identical to the local originals.

The root holds one folder per section, the manifest, this file, and
`PROVENANCE.md`. It also holds **`_early-tests/`**, which is what it says: the
trial uploads made on 26 August while working out how the pipeline behaved — a
thousand throwaway files, two books uploaded loose before the structure was
settled, a stray scan, and `PROCEDENCIA.md`, the Spanish draft that `PROVENANCE.md`
replaced. Nothing on Arweave can be deleted, so they were moved out of the way
rather than removed, and are named for what they are. Do not read them as part of
the archive; `PROCEDENCIA.md` in particular is superseded and should not be
mistaken for the provenance record.

## Superseded uploads

Arweave keeps everything, so a mistake is not removed, it is superseded. What
is listed here is what no longer stands, and why. Silence about a wrong copy
still on chain would be the one thing this archive exists to prevent.

| Date | Transaction | What it was | Why superseded |
|---|---|---|---|
| 26 Aug 2026 | `U9uIEx_mc2e1zVFPXduR6whbtdqIexzk73HMV6JVV8k` | An early draft of `PROVENANCE.md` | A test that proved the pipeline worked end to end. Retrieved from a public gateway and confirmed byte-identical to the local original. Never an anchor. |
| 26 Aug 2026 | `TxIXCmb4h3kyAVuIyaNwbBpMmabAEb6ts24bsnhhGLs` | `MANIFEST.sha256`, package root `9aeb1cb5…d718` | Uploaded before the package was final: its copy of `PROVENANCE.md` predated the OCR containers, and it still listed the 11,474 duplicated Bhāgavatam pages. |
| 26 Aug 2026 | `y7AgXnAdRsvd7tuFeKTRVEB1SuB9u2eOmSpgOMk9mCg` | `PROVENANCE.md` | Did not yet say that the Russian translation is held back, so it described an archive with 16,311 files silently missing. |
| 29 Aug 2026 | `ar://m4Botm_JlN-DIsZT43PsxJenKwmo6EJi3KtRJ7oZbk4` | The first path manifest | Its root served a stray test file, and `/PROVENANCE.md` resolved to a superseded 6 KB draft rather than the document. |
| 29 Aug 2026 | `ar://vL2sv5dNLsIoNl1pXCO7awOzaByCZnmdhFA-enHr_UM` | The second path manifest | Its front page linked to folders, and Arweave manifests do not resolve folders, so every one of those links returned 404. `/PROVENANCE.md` still resolved to the old draft. |
| 26 Aug 2026 | corpus root `2ec622af…d497f7` | The corpus root anchored that day | Superseded: `PROVENANCE.md` gained the section on what is absent, and every `.md` is inside the corpus manifest. |
| 28 Aug 2026 | `ar://Wf8LWB6xrovGKM4xZHYRcz6F4G1L74MKdsUjUFsb9rg` | `MANIFEST.sha256`, package root `274c2af2…a09b17` | Written before six files were found to be missing from the chain and uploaded, and before the verifier's own working files were kept out of it. |
| 28 Aug 2026 | `ar://UL6GCZ4-o51WCJHfQb9ZLrv0NAJAVSiQNB9NiupFql8` | `PROVENANCE.md` | Did not yet record the six missing files, nor the warning about single-gateway checks. |
| 29 Aug 2026 | `ar://S_KxoVfwKsJqKbHTVbcFdRdYhrb_G2TX_hSD1UBvwFo` | The third path manifest, 88,709 paths | It predates the Russian translation entirely, and it predates the 222 files that were later found never to have reached the chain. Correct for what existed when it was written; it describes an archive a fifth smaller than the one that stands. |
| 20 Sep 2026 | `ar://nz3TsdzdXGxXDImC6qDis4IcLff1GLsq-RNdw3brJYE` | The fourth path manifest, 107,816 paths | Right for 107,808 paths and wrong for 8. Those 8 had been re-uploaded with corrected internal links, but the builder read their transaction ids from the upload state file, which still held the superseded ones. Found by fetching them back through the manifest and comparing against disk, which is the only check that would have caught it. |
| 20 Sep 2026 | `ar://qwHR1n4s9EHGeNlij8Iu6aiAPXG18GS4Fls0F_Ggx0s` | The fifth path manifest, 107,816 paths | Correct when published. Superseded hours later by 50 Hindi files and 343 re-uploads carrying corrected text; a manifest names transactions, so new content means a new manifest. |
| 29 Aug 2026 | corpus root `8bcaa67e…f77a221d` | The corpus root anchored earlier that day | Superseded within hours: the README gained the section on how to use the manifest, and the README is inside the manifest. That is exactly the drift the commit column now prevents. |

## Pending

Written 20 Sep 2026, revised the same evening. Each line is a thing that is true
and not yet done; the point of listing them is that an archive with a silent gap
is worse than one with a stated gap.

1. **Recompute the package root.** The 17 Sep root covered 103,481 files; the
   archive now holds 107,866. This must be done on the machine that holds the
   whole package — see *Package root* above for why it cannot be done anywhere
   else. It is the last figure in this file that does not describe what stands.

### The Russian `.jsonl` files are published twice, and neither copy is clean

`build_archive.py` splits the same source tree by extension: `corpus` takes the
`.md`, `corrections` takes the `.jsonl`, and they get different content types
because, as `PROVENANCE.md` says, a content type on Arweave cannot be corrected
afterwards — only replaced.

For English, Spanish, Portuguese and Hindi that is what happened. For Russian,
two things went wrong on 17 Sep and both were found on 20 Sep:

1. **22 Russian `.jsonl` were uploaded under `corpus/`**, where by that rule no
   `.jsonl` belongs, and declared `text/markdown;charset=utf-8`.
2. **The 20 under `corrections/` carry an older text.** They render the Sanskrit
   in Latin IAST — `dehī nityam avadhyo` — where the published Russian, the
   working repository and the `corpus/` copy all render it in Cyrillic
   transliteration, `дехӣ нитйам авадхйо`. Checked against vedabase.cc: the
   Cyrillic is what is served. They are also declared `text/markdown`.

So the current Russian text is on chain, in the wrong section with the wrong
content type, and an older Russian text is on chain in the right section, also
with the wrong content type. Two books, `krp_ru.jsonl` and `tqk_ru.jsonl`, exist
only in the `corpus/` copy.

None of this touches the 20,674 per-verse `.md` files, which are correct in
section, content type and text — that is what the path manifest serves and what
a reader actually reads. What is wrong is the aggregate file, twice.

Putting it right means re-uploading 22 files, 61.8 MB, 0.8055 credits — about
6.03 USD. The wallet held 0.790 when this was written, 0.0155 short. It is
written down rather than fixed, which is the rule this file follows: an archive
with a stated defect is worth more than one with a silent one.

### A known defect, stated rather than quietly fixed

`corpus/translations/russian/srimad-bhagavatam/sb_ru.jsonl` as published carries
one doubled asterisk — `**апсу*` where `*апсу*` was meant — in the synonyms of
`sb/7/9/34`. One byte, in a 30 MB file, in one entry of 8,265. The per-verse
Markdown for that same verse is correct on chain; only the aggregate file
carries it.

It was left because Arweave charges for the whole file, so correcting one byte
costs 2.60 USD, and the next upload that touches this file will carry the fix at
no extra cost. That is a judgement about money, not about the text, and it is
recorded here so that nobody later finds the asterisk and wonders what else was
passed over in silence.
