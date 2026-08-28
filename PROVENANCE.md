# Provenance and permanent archive

This repository holds the **text**. The work that backs it — the scans of the
printed pages, the two OCR readings, the record of every discrepancy and the
tools that did the collation — lives outside it, because those are binaries and
working files with no place in git.

This file says where each piece is and how to check it. A permanent copy of
everything together is published on Arweave, where it cannot be modified or
withdrawn; the transaction ids go in the table below as they are published.

## The pieces

| Piece | What it is | Where it lives today | Size | Arweave |
|---|---|---|---|---|
| **corpus** | The text of the first editions, 102,729 files, of which 86,418 are published — see *What is deliberately absent* | this repository | 495 MB | see [ANCHORS.md](ANCHORS.md) |
| **corrections** | The ledger of corrections applied to the text | this repository, `*.jsonl` | 272 MB | see [ANCHORS.md](ANCHORS.md) |
| **scans** | 71 PDFs of the printed books, including the complete Śrīmad-Bhāgavatam | `scan_vedabase/originals/` | 2,078 MB | see [ANCHORS.md](ANCHORS.md) |
| **ocr-packed** | Every page as read by both engines, one `.tar` per book | `surya_ocr/`, `.../scan_audit/ocr/` | 193 MB | see [ANCHORS.md](ANCHORS.md) |
| **audit** | The ledger of discrepancies: open, arbitrated, applied | `astro_vedabase/scripts/scan_audit/*.json` | 68 MB | see [ANCHORS.md](ANCHORS.md) |
| **reports** | Each difference beside the image of the scanned page | `.../scan_audit/*.html` | 126 MB | see [ANCHORS.md](ANCHORS.md) |
| **tools** | The code that did the comparison and applied the fixes | both repos, `*.py` | 1.1 MB | see [ANCHORS.md](ANCHORS.md) |
| **manifest** | SHA-256 of every file in the package plus a root over the whole set | `MANIFEST.sha256` | 15 MB | see [ANCHORS.md](ANCHORS.md) |

Reproduce the package root with `python3 scripts/build_archive.py --manifest-only`
and compare it against ANCHORS.md.

To assemble the complete package:

```
python3 scripts/build_archive.py --dry-run       # see what goes in
python3 scripts/build_archive.py --with-tesseract
```

## How to check that the text has not changed

```
python3 scripts/hash_manifest.py --check
```

This recomputes the hash of every file and compares it against
`MANIFEST.sha256`. If the `root` matches the one anchored on Arweave for that
date, the text is the same as it was when published. If it does not match,
something changed — and being able to detect that is the whole point.

The manifest proves the text **has not been altered**. What proves it **matches
the paper** is the collation, and its record is in `audit/` and `reports/`:
every discrepancy, which page settled it, and what was decided.

## Published anchors

An anchor on a single date says nothing about what came after. What counts is
the succession. Every time the corpus changes, the manifest is regenerated and
the new `root` is anchored.

**The roots and transaction ids live in [ANCHORS.md](ANCHORS.md), not here.**

That separation is not tidiness, it is arithmetic. This file is part of the
corpus the manifest covers, so if it stated the manifest's own `root`, writing
the root down would change the root — the document would be false the instant
it was saved. It happened: on 26 Aug 2026 the package root was noted here, and
the manifest was stale before the file was closed.

So the rule is: every number that depends on the manifest lives in ANCHORS.md,
and ANCHORS.md is excluded from both manifests and from the package. It is
uploaded on its own, last, once the transaction ids are known. This file carries
no figure that changes, which is precisely what lets it be certified along with
the text it describes.

## Provenance of the scans

A PDF of a 1972 book does not establish on its own where it came from. This is
what turns a file into evidence, and it is why the table below records what each
scan *says about itself* rather than what its filename claims.

**How this was obtained.** Two independent sources, neither of them anyone's
memory. The technical columns come from the PDF metadata (`pdfinfo`,
`pdfimages`). The copyright column is the text of the book's own copyright page,
as read by the Surya OCR engine and quoted verbatim, misprints and all. Anyone
can repeat both readings against the published scans.

**Checked against the second engine.** The same method used on the text itself
was used here: every copyright page was read again by Tesseract and the two
readings compared on printing number and year. Of the sixty-nine scans, sixty-four
have both readings and **all sixty-four agree**; the remaining five have no
Tesseract pass. Three volumes appeared to differ and did not — Tesseract also
caught the phrase *"the first edition widely available to the English-reading
public"* from a jacket blurb in Bhāgavatam 10.1-10.3, which is publicity, not a
printing statement.

Two of the five without a second reading matter, and were confirmed differently.
The Bhagavad-gītā copyright page was read in full rather than in fragments, and
says plainly that the Collier paperback and the Macmillan hardcover are separate
editions. The Śrī Īśopaniṣad page carries all three lines together:

    Copyright © 1969 by ISKCON Books
    First edition published by ISKCON Books in 1969
    Fifth Printing 1972

**Read the names with suspicion.** Several files are named for an edition their
copyright page does not support, and the discrepancy is always in the same
direction — the name claims an earlier, more authoritative printing than the
book actually is:

- `Bhagavad-gita_As_It_Is-Original_1972_Macmillan_edition-SCAN` is not the 1972
  Macmillan first printing. Its copyright page reads *First Collier Books
  Edition 1972 · Third Printing 1973*, and adds that the book *"is also published
  in a hardcover edition by the Macmillan Company"* — naming the Macmillan as a
  separate edition, not as this one. What was scanned is the Collier paperback,
  third printing. That matters more here than anywhere else: the 1972 Macmillan
  is the edition this project treats as its source.
- `Beyond_Birth_and_Death-Original_1974_edition_scan` is the **third** printing.
  The page lists 1972, 1973 and 1974; 1974 is the last of the three.
- `Sri-Isopanisad-scans-of-original-1969-edition` carries the 1969 first edition
  notice, but the copy scanned is the **fifth printing, 1972**. Both engines read
  the three lines identically on page 7.
- `The_Nectar_of_Instruction-Original_1976_SCAN` has a 1975 copyright and a
  first printing of 1975.
- `sri-caitanya-caritamrta` Ādi-līlā volumes 1 and 2 read *Second printing,
  1983*, which the README already records.

None of this makes the scans less useful. It makes them *honest*, which is the
point: a collation is only as good as the knowledge of which printing it was
made against.

**The two doubtful readings, resolved.** Neither was an OCR failure.

`KRSNA-the-Reservoir-of-Pleasure-1970` carries a full printing history, and the
earlier extract had simply truncated it after the first line:

    Copyright ©1970 by ISKCON PRESS
    Printing History
    First Printing 1966 - 1,000      Second Printing 1967 - 5,000
    Third Printing 1968 - 5,000      Fourth Printing 1969 - 20,000
    Fifth Printing 1970 - 30,000

The 1966 is real — the text circulated as an essay from then. What was scanned
is the **fifth printing, 1970**, which is what the copyright year records.

`1972_Perfection_of_Yoga_2008_Original` lists two printings and no years because
**the printed page itself omits them**. Both OCR engines read the page
identically. Copyright 1972; which of the two printings this copy is cannot be
told from that page.

**Three more scans, read directly.**

- `Easy-Journey-to-Other-Planets-1972-krishnaorg-SCAN` is the *First Collier
  Paperbacks Edition 1972* — the same Collier/Macmillan arrangement as the
  Bhagavad-gītā.
- `Easy_Journey_to_Other_Planets-Original_India_Edition_SCAN` is what its name
  says, and is the one case where the name is exactly right: published by
  Prabhupāda himself through The League of Devotees, 1/859 Keshi Ghat,
  Vrindaban, printed by Surendra Printer's of Delhi, priced at one rupee, with
  *Copy Right: Author* and no year. It is a different book from the Collier
  edition, not another printing of it.
- `Life_Comes_from_Life-1979_first_edition-SCAN` **is not a scan**. Its PDF was
  produced by Microsoft Word — 68 pages, 535 KB, not one image in it. It is a
  retyping, and cannot serve as evidence of any printed page. That is also why
  its OCR shows no copyright page: there is none to read.

**A gap found while checking, and closed.** Two books had their OCR published in
the containers while their PDFs were absent from the archive; both sat outside
the `originals/` directory the package is built from, so the build never saw
them. `Teachings_of_Lord_Chaitanya-1968_first_edition-SCAN` is a genuine scan —
351 pages at 200 ppi — and has since been added, which is why the archive holds
seventy-one scans rather than seventy. `Life_Comes_from_Life` was left out on
purpose: as noted above it is a Word document, not a scan, and putting it among
the page images would misrepresent what it is.

**A second version exists for eight books.** `improved/` holds reprocessed
copies of eight of the published scans, differing in bytes and file size but not
in pagination — same book, same pages, different image processing. The archive
publishes the `originals/` version in each case.

**Where these files come from.** Not from scanning done for this project. The
evidence is in the files themselves and it is consistent.

The PDFs carry their own creation dates, and they fall into a campaign rather
than a trickle: twenty-seven were made between 13 and 16 September 2012 — the
Bhāgavatam and Caitanya-caritāmṛta volumes, several a day — twenty-two more
between 27 September and 9 October, then individual books through 2013 and 2014
at roughly weekly intervals, and two stragglers in 2016 and 2020. Seven carry no
date. Seventeen name `krishnapath.org` in their metadata. Eight name the machine
that produced them: a CanoScan LiDE 210, and one Canon SC1801.

That matches what the source says of itself. KrishnaPath.org describes a
volunteer effort to scan and **digitally remaster** the authorised editions —
removing background marks and sharpening the text so it can be searched and
copied. Forty-three of the seventy-one bear the fingerprint of that work: Adobe
Acrobat's Paper Capture *ClearScan*, which replaces the scanned glyphs with
synthesised fonts. **These are therefore remastered images, not raw captures.**
The page images survive at the resolutions listed, and the collation against
them stands, but anyone treating a letterform in these files as photographic
evidence of the printed page should know what was done to it first.

For the Bhāgavatam the trail is recorded elsewhere by the same hands that
assembled this archive: *"The Śrīmad-Bhāgavatam scans (original 1972 edition,
© BBT) come from prabhupadabooks.com / krishna.org; the rest from devotee
archives."*

**What remains unknown.** Which physical copy each volunteer worked from, and
whose it was. That is not recorded in any file and cannot be recovered from
them; it would have to come from the people who did the scanning. Given that
KrishnaPath itself warns that altered copies of these free scans circulate, the
practical check is not provenance by testimony but byte-identity against a known
public copy — which is what was done for the seventeen Caitanya-caritāmṛta
volumes, and what the hashes in this archive make possible for the rest.

Note too that forty-three of the seventy were processed with Adobe Acrobat's
Paper Capture *ClearScan*, which substitutes synthesised fonts for the scanned
glyphs. The page images survive at the resolutions listed, but anyone treating
these as photographic evidence of letterforms should know that.

| Scan | Book | What its copyright page says | ppi | Source |
|---|---|---|---:|---|
| `Beyond_Birth_and_Death-Original_1974_edition_scan` | beyond-birth-and-death | © 1972 by the Bhaktivedanta Book Trust (B.B.T.) · First Printing, 1972: 25,000 copies Second Printing, 1973: 100,000 copies Third Printing, 1974: 200,000 copies | 600 | krishnapath.org |
| `Bhagavad-gita_As_It_Is-Original_1972_Macmillan_edition-SCAN` | bhagavad-gita-as-it-is | Copyright © 1972 by His Divine Grace A.C. Bhaktivedanta Swami Prabhupāda · First Collier Books Edition 1972 Third Printing 1973 | 600 | krishnapath.org |
| `Easy-Journey-to-Other-Planets-1972-krishnaorg-SCAN` | easy-journey-to-other-planets | Copyright © 1970, 1972 by ISKCON Press | 300 | CanoScan LiDE 210 |
| `Easy_Journey_to_Other_Planets-Original_India_Edition_SCAN` | easy-journey-to-other-planets | *(not found in the first 30 pages)* | 600 | krishnapath.org |
| `1973_Elevation_to_Krsna_Consciousness` | elevation-to-krsna-consciousness | © 1973 the Bhaktivedanta Book Trust. · First Printing, 1973: | 300 | krishnapath.org |
| `Sri-Isopanisad-scans-of-original-1969-edition` | isopanisad | Copyright © 1969 by ISKCON Books · First edition published by ISKCON Books in 1969 | 600 | krishnapath.org |
| `KRSNA_Book_Vol.1_1970_ISKCON_Press_edition_SCAN` | krsna-the-supreme-personality-of-godhead | Copyright © 1970 A. C. Bhaktivedanta Swami | 598 | krishnapath.org |
| `KRSNA_Book_Vol.2_1970_ISKCON_Press_edition_SCAN` | krsna-the-supreme-personality-of-godhead | *(not found in the first 30 pages)* | 300 | krishnapath.org |
| `Life_Comes_from_Life-1979_first_edition-SCAN` | life-comes-from-life | *(not found in the first 30 pages)* |  | — |
| `Light_of_the_Bhagavata-1984_first_edition_SCAN` | light-of-the-bhagavata | First Printing, 1984: 40,000 copies. | 300 | CanoScan LiDE 210 |
| `The_Nectar_of_Devotion-1970_ISKCON_Press_edition-Hardcover-SCAN` | nectar-of-devotion | Copyright © 1970 by ISKCON PRESS | 300 | krishnapath.org |
| `The_Nectar_of_Instruction-Original_1976_SCAN` | nectar-of-instruction | ©1975 Bhaktivedanta Book Trust. · First printing, 1975: 10,000 copies | 600 | krishnapath.org |
| `On_the_Way_to_Krsna-1973_book_SCAN` | on-the-way-to-krsna | © 1973 by the Bhaktivedanta Book Trust. All rights reserved · First Printing, 1973: 100,000 Printed in the United States of America by ISKCON Press | 600 | krishnapath.org |
| `The-Path-of-Perfection-SCAN` | path-of-perfection | First Printing, 1979: 175,000 copies · © 1979 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 300 | CanoScan LiDE 210 |
| `Perfect_Questions_Perfect_Answers-Original_1977_Edition-SCAN` | perfect-questions-perfect-answers | © 1977 Bhaktivedanta Book Trust · First printing, 1977: 220,000 copies | 300 | krishnapath.org |
| `1972_Perfection_of_Yoga_2008_Original` | perfection-of-yoga | © 1972 by ISKCON PRESS. All rights reserved · First Printing: 30,000 copies Second Printing: 100,000 copies Printed in the United States of America | 600 | krishnapath.org |
| `1973_Raja-Vidya_The_King_of_Knowledge` | raja-vidya | © 1973 by the Bhaktivedanta Book Trust (B.B.T.). · First Printing, 1973: 100,000 copies | 600 | krishnapath.org |
| `KRSNA-the-Reservoir-of-Pleasure-1970` | reservoir-of-pleasure | Copyright ©1970 by ISKCON PRESS · First Printing 1966 - 1,000 | 150 | krishnapath.org |
| `Science-of-Self-Realization-1977` | science-of-self-realization | First Printing, 1977: 50,000 copies | 300 | CanoScan LiDE 210 |
| `adi1` | sri-caitanya-caritamrta | © 1974 the Bhaktivedanta Book Trust · First printing, 1974 Second printing, 1983 | 300 | Adobe Acrobat 10.1.4 |
| `adi2` | sri-caitanya-caritamrta | © 1973 the Bhaktivedanta Book Trust · First printing, 1973 Second printing, 1983 | 300 | Adobe Acrobat 10.1.4 |
| `adi3` | sri-caitanya-caritamrta | © 1974 the Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.0 |
| `ant1` | sri-caitanya-caritamrta | ©1975 Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.1.4 |
| `ant2` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `ant3` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `ant4` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `ant5` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `mad1` | sri-caitanya-caritamrta | ©1975 Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.1.4 |
| `mad2` | sri-caitanya-caritamrta | ©1975 Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.1.4 |
| `mad3` | sri-caitanya-caritamrta | ©1975 Bhaktivedanta Book Trust. | 300 | Adobe Acrobat 10.1.4 |
| `mad4` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat Pro 10.1.4 |
| `mad5` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `mad6` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust. · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `mad7` | sri-caitanya-caritamrta | © 1975 Bhaktivedanta Book Trust. · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `mad8` | sri-caitanya-caritamrta | ©1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `mad9` | sri-caitanya-caritamrta | ©1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 300 | Adobe Acrobat 10.1.4 |
| `SB1.1` | srimad-bhagavatam | Copyright © 1972 by the Bhaktivedanta Book Trust |  | Adobe Acrobat 10.0 |
| `SB1.2` | srimad-bhagavatam | © 1972 the Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.0 |
| `SB1.3` | srimad-bhagavatam | Copyright © 1972 by the Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.0 |
| `SB10.1` | srimad-bhagavatam | First Printing, 1977: 20,000 copies · © 1977 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 600 | CanoScan LiDE 210 |
| `SB10.2` | srimad-bhagavatam | First Printing, 1977: 50,000 copies · © 1977 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 600 | CanoScan LiDE 210 |
| `SB10.3` | srimad-bhagavatam | First Printing, 1980: 20,000 copies · © 1980 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 600 | CanoScan LiDE 210 |
| `SB2.1` | srimad-bhagavatam | *(not found in the first 30 pages)* | 300 | Adobe Acrobat 10.0 |
| `SB2.2` | srimad-bhagavatam | © 1972 the Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.1.4 |
| `SB3.1` | srimad-bhagavatam | © 1972 the Bhaktivedanta Book Trust | 150 | Adobe Acrobat 10.0 |
| `SB3.2` | srimad-bhagavatam | © 1974 the Bhaktivedanta Book Trust | 150 | Adobe Acrobat 10.0 |
| `SB3.3` | srimad-bhagavatam | © 1974 the Bhaktivedanta Book Trust | 150 | Adobe Acrobat 10.0 |
| `SB3.4` | srimad-bhagavatam | © 1974 the Bhaktivedanta Book Trust | 150 | Adobe Acrobat 10.0 |
| `SB4.1` | srimad-bhagavatam | Copyright © 1972 by the Bhaktivedanta Book Trust |  | — |
| `SB4.2` | srimad-bhagavatam | © 1974 the Bhaktivedanta Book Trust | 150 | Adobe Acrobat 10.0 |
| `SB4.3` | srimad-bhagavatam | © 1974 the Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.0 |
| `SB4.4` | srimad-bhagavatam | © 1974 the Bhaktivedanta Book Trust | 300 | Adobe Acrobat 10.0 |
| `SB5.1` | srimad-bhagavatam | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 299 | Adobe Acrobat 10.0 |
| `SB5.2` | srimad-bhagavatam | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 299 | Adobe Acrobat 10.0 |
| `SB6.1` | srimad-bhagavatam | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 299 | Adobe Acrobat 10.0 |
| `SB6.2` | srimad-bhagavatam | © 1975 Bhaktivedanta Book Trust · First printing, 1975: 20,000 copies | 299 | Adobe Acrobat 10.0 |
| `SB6.3` | srimad-bhagavatam | © 1976 Bhaktivedanta Book Trust · First printing, 1976: 20,000 copies | 300 | Adobe Acrobat 10.0 |
| `SB7.1` | srimad-bhagavatam | ©1976 Bhaktivedanta Book Trust · First printing, 1976: 50,000 copies | 300 | Adobe Acrobat 10.0 |
| `SB7.2` | srimad-bhagavatam | ©1976 Bhaktivedanta Book Trust · First printing, 1976: 20,000 copies | 300 | Adobe Acrobat 10.0 |
| `SB7.3` | srimad-bhagavatam | ©1976 Bhaktivedanta Book Trust · First printing, 1976: 20,000 copies | 300 | Adobe Acrobat 10.0 |
| `SB8.1` | srimad-bhagavatam | © 1976 Bhaktivedanta Book Trust · First printing, 1976: 20,000 copies |  | — |
| `SB8.2` | srimad-bhagavatam | ©1976 Bhaktivedanta Book Trust · First printing, 1976: 20,000 copies | 300 | Adobe Acrobat 10.0 |
| `SB8.3` | srimad-bhagavatam | © 1976 Bhaktivedanta Book Trust · First printing, 1976: 20,000 copies | 299 | Adobe Acrobat 10.0 |
| `SB9.1` | srimad-bhagavatam | First Printing, 1977: 20,000 copies · © 1977 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 299 | Adobe Acrobat 10.0 |
| `SB9.2` | srimad-bhagavatam | First Printing, 1977: 20,000 copies · © 1977 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 300 | Adobe Acrobat 10.0 |
| `SB9.3` | srimad-bhagavatam | First Printing, 1977: 20,000 copies · © 1977 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 299 | Adobe Acrobat 10.0 |
| `Teachings_of_Lord_Chaitanya-1968_first_edition-SCAN` | teachings-of-lord-caitanya | Copyright © 1968 International Society for Krishna Consciousness Inc. (ISKCON) · Library of Congress Catalogue Card Number: 68-29320 ALL RIGHTS RESERVED FIRST EDITION |  | — |
| `Teachings_of_Queen_Kunti-SCAN` | teachings-of-queen-kunti | First Printing, 1978: 57,300 copies · © 1978 Bhaktivedanta Book Trust All Rights Reserved Printed in the United States of America | 600 | krishnapath.org |
| `KRSNA Consciousness - The Topmost Yoga System - Original 1970 edition Scan` | topmost-yoga-system | Copyright © 1970 ISKCON PRESS | 600 | PDFium |

## What is deliberately absent

Count the files in the archive against the table above and 16,311 are missing.
They are not lost, and their absence is not an accident.

**The Russian translation is not published.** It is unfinished, and Arweave has
no way back: a half-translated chapter put up today stays up, and standing
beside a corpus collated page by page against the printed editions it would
borrow a credibility it has not earned. The files are held in the repository
until the translation is complete, and will be published then as a later
addition. The English, Spanish, Portuguese and Hindi translations are all here.

One Russian thing is here: the twenty `.jsonl` correction ledgers under
`corrections/translations/russian/`. They went up before the text was held back,
and on Arweave that cannot be undone. They record what was corrected, not what
the translation says, so they are listed rather than hidden — but they are not
the text, and the text is not here.

This is worth stating plainly rather than leaving to inference, because an
archive of this kind is read by people who cannot ask us anything. A silent gap
looks like data loss, or like something hidden. It is neither.

## A note on character encoding

Every text file here is UTF-8, and the corpus is full of Sanskrit diacritics
(ā, ī, ū, ṛ, ṣ, ṭ, ñ, ś) as well as Spanish, Portuguese and Russian text in the
translations. When uploading, the content type must carry the charset —
`text/markdown; charset=utf-8`, not bare `text/markdown` — or browsers fall back
to Latin-1 and the diacritics come out as mojibake. This cannot be corrected
after the fact: a file already on Arweave can only be replaced by uploading it
again and paying again.

Because the content type applies to a whole upload, each section is uploaded
separately with its own:

| Section | `--content-type` |
|---|---|
| corpus, audit/notes | `text/markdown; charset=utf-8` |
| corrections, audit/candidates | `application/x-ndjson; charset=utf-8` |
| audit/ledger, audit/text-layer | `application/json; charset=utf-8` |
| ocr-packed, `*.tar` | `application/x-tar` |
| ocr-packed, `OCR-CONTENTS.sha256` | `text/plain; charset=utf-8` |
| reports | `text/html; charset=utf-8` |
| tools | `text/x-python; charset=utf-8` |
| scans | `application/pdf` |

This is why `corpus` and `corrections` are separate sections even though both
come from this repository: they are different kinds of thing and they cannot
share a content type.

Note the syntax: `text/markdown;charset=utf-8`, with **no space** after the
semicolon. With a space the shell splits the argument and the CLI keeps only the
first half, so the charset never reaches the transaction and the file is served
without it. Verified on 26 Aug 2026 — the first attempt, written with a space,
recorded a bare `text/markdown` and rendered the Sanskrit as mojibake.

## A note on the OCR containers

Everything in this archive is uploaded one file at a time, addressable on its
own from any gateway — except the OCR, which travels as 42 `.tar` containers,
one per book per engine.

The reason is arithmetic. The OCR output is 69,799 text files, one per page per
engine, with a median size of 1,874 bytes. Measured against the Turbo price API
on 26 Aug 2026, an upload costs **9,174,313 winc per file plus 11,184.90 winc
per byte** — a formula that reproduces the API's own quotes to 0.000% across
sizes from 500 bytes to 1 MB. The per-file part is small in money, but the CLI
spends 0.58 s on each file, so those pages alone were thirteen hours of upload.

Packing them costs slightly *more* in credits, not less: tar pads every member
to a 512-byte boundary, so 129 MB of pages become 193 MB of containers, and the
0.64 credits saved on per-file overhead are given back in padding and then some.
What it buys is time — thirteen hours become seconds. Nothing else in the
archive is packed, because being readable one file at a time is most of what the
corpus, the scans and the reports are for.

`tar` was chosen over `zip` or `gzip` deliberately. It is uncompressed and its
format is specified in POSIX, so a flipped bit damages one member and the rest
still extract; compression would couple every byte to every other and bet on a
decompressor still existing in fifty years. The variant is `ustar`, the most
conservative one that fits these paths — the longest is 112 characters, split
across the 155-byte prefix and the 100-byte name field.

The containers are deterministic: members sorted by path, uid and gid zeroed,
owner names emptied. The same input produces the same bytes on any machine.

**A container is only worth using if you need not trust it.** So
`OCR-CONTENTS.sha256` travels beside the tars and lists the SHA-256 of each
container followed by the SHA-256 of all 69,799 members, as `container!path`.
To check one page without extracting the rest:

    P=isopanisad/Sri-Isopanisad-scans-of-original-1969-edition/p0001.surya.txt
    tar -xOf ocr-surya-isopanisad.tar "$P" | shasum -a 256
    grep "ocr-surya-isopanisad.tar!$P" OCR-CONTENTS.sha256

Inside a container the path keeps the edition directory the scan came from, so
the page carries the printing it was read from, not just a page number.

### One duplicate, removed

The Surya run left the Bhāgavatam laid out twice: as loose volume directories
`SB1.1 … SB10.3` at the top of `surya_ocr/`, and again inside
`srimad-bhagavatam/`, which holds those same thirty. Verified on 26 Aug 2026:
the 11,474 relative paths match exactly and all 11,474 SHA-256 match. Only the
merged copy is archived — it is how every other book in the section is named.
The loose copies were dropped before packing, which is why `ocr-surya` holds
24,035 files here and 35,509 in the working directory it came from.

## A note on the markup

Ślokas in Devanāgarī and their IAST transliteration are `>` blockquotes, and
each line of the verse ends with a **backslash**. That backslash is Markdown's
hard line break: without it the pādas would be joined into one running line.

It is markup, not text. Anyone extracting plain text from these files should
strip a trailing `\` from each line — it is not part of the verse.

The backslash was chosen over Markdown's other hard-break form, two trailing
spaces, because trailing whitespace is invisible and almost every editor strips
it on save. A verse break is information, not formatting, so it is written in a
way that is visible and hard to destroy by accident.
