#!/usr/bin/env python3
"""Parse a single run-on letter blob (D1 `purport` field) into clean Markdown.

The letters were scraped from HTML into one flattened string with no line breaks:

    Letter to: NameLetter to: NameDated: <date>Location: <loc>Letter to: Name<datecode><address>My Dear <recipient>,<body...>Your ever well-wisher,A.C. Bhaktivedanta Swami<sigcode>Letter to: <next>Letter to: <next>

This module reconstructs the structural breaks (metadata, address, salutation,
body, closing, signature) and strips the trailing navigation bleed. It does NOT
invent paragraph breaks inside the body — that information was lost in the scrape —
but it does restore spaces dropped at sentence boundaries ("contents.We" -> "contents. We").
"""
import re

SIGNATURE = 'A.C. Bhaktivedanta Swami'


def _despace(text):
    """Restore a space dropped after sentence punctuation: 'contents.We' -> 'contents. We'.
    Guarded so initials like 'A.C.' (single capital before the dot) are left intact."""
    text = re.sub(r'([a-z]{2})([.!?,;:])([A-Z])', r'\1\2 \3', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()


def format_letter(translation, purport):
    header = (translation or '').strip()            # "Letter to: A. K. Shivdasani"
    name = re.sub(r'^Letter to:\s*', '', header).strip()
    blob = purport or ''

    # 1) Drop the repeated "Letter to: <Name>" headers. Two scrape formats exist
    #    (fields glued, or newline-separated), so match the name flexibly: keep the
    #    word characters literal and let any run of separators (spaces, dots, commas,
    #    hyphens, newlines) vary. Built manually to avoid re.escape() version quirks.
    if name:
        name_pat = re.sub(r'[^\w]+', r'\\W*', name)
        blob = re.sub(r'Letter to:\s*' + name_pat, '', blob)

    # 2) Extract and remove the date ("Dated: <Month Day Year>") — match the date shape
    #    explicitly, since the scrape left no delimiter after it.
    date = ''
    dm = re.search(r'Dated:\s*([A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th)?,? \d{4})', blob)
    if dm:
        date = dm.group(1).strip()
        blob = blob.replace(dm.group(0), '')
    blob = re.sub(r'Dated:\s*', '', blob)            # drop any malformed "Dated:" marker

    # 3) Extract and remove the location (1–3 capitalised words after "Location:").
    location = ''
    lm = re.search(r'Location:\s*([A-Z][a-zA-Z.]*(?: [A-Z][a-zA-Z.]*){0,2})', blob)
    if lm:
        location = lm.group(1).strip()
        blob = blob.replace(lm.group(0), '')
    blob = re.sub(r'Location:\s*', '', blob)

    # 4) Cut the signature and everything after it (sig-code + nav bleed + footnote).
    sigcode, footnote = '', ''
    found_sig = SIGNATURE in blob
    if found_sig:
        blob, post = blob.split(SIGNATURE, 1)
        post = re.split(r'Letter to:', post)[0]      # drop nav-link bleed
        ac = re.search(r'ACBS[:/][\w:/.]+', post)     # sig-code may sit after a c.c./P.S. note
        if ac:
            sigcode = ac.group(0)
            post = post.replace(ac.group(0), '')
        footnote = post.strip(' .:\n\t')
    # Remove any trailing nav-link bleed on the final line (no re.S — must not eat the body).
    blob = re.sub(r'(?:\s*Letter to:[^\n]*)+\s*$', '', blob).strip()

    # 5) Split salutation ("My dear X," / "Dear X,") from the address block before it.
    address, salutation, body = '', '', blob
    sm = re.search(r'((?:My |Our )?[Dd]ear\b[^,:\n]{1,60}[,:])', blob)
    if sm:
        address = blob[:sm.start()].strip()
        salutation = sm.group(1).strip()
        body = blob[sm.end():].strip()
    else:
        body = blob.strip()
    # Strip the date-code (YY-MM-DD) wherever it sits in the address, and tidy edges.
    address = re.sub(r'\d\d-\d\d-\d\d', ' ', address)
    address = address.strip(' ,.\n\t')
    # Salutation-less memos begin the body with the date-code — drop it there too.
    body = re.sub(r'^\s*\d\d-\d\d-\d\d\s*', '', body)

    # 5) Lift the closing ("Your ever well-wisher," and similar) onto its own line.
    closing = ''
    cm = re.search(
        r'\s*((?:Hoping|I hope|Trusting|Awaiting)[^.,]*[.,])?\s*'
        r'(Your ever ?well-?wisher|Your eternal well-?wisher|Your servant|Yours? in the service[^,]*|Your spiritual master)\s*[,.]?\s*$',
        body)
    if cm:
        closing = ' '.join(p.strip() for p in cm.groups() if p).strip()
        body = body[:cm.start()].strip()

    body = _despace(body)

    # 6) Assemble Markdown.
    out = [f'### Letter to {name}' if name else '### Letter']
    meta = []
    if date:
        meta.append(f'**Date:** {date}')
    if location:
        meta.append(f'**Location:** {location}')
    if meta:
        out.append(' — '.join(meta))
    if address:
        # Address blocks (not Prabhupāda's words) lost spaces at word boundaries;
        # restore the space at lowercase->Uppercase joins, e.g. "EastBombay" -> "East Bombay".
        addr = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', address)
        addr = re.sub(r'[ \t]{2,}', ' ', addr).strip()
        out.append('> ' + addr.replace('\n', '\n> '))
    if salutation:
        out.append(salutation)
    if body:
        out.append(body)
    if closing:
        out.append(closing + ',')
    if found_sig:
        out.append(SIGNATURE + (f'  \n{sigcode}' if sigcode else ''))
    if footnote:
        out.append('---\n\n' + _despace(footnote))
    return '\n\n'.join(out)


if __name__ == '__main__':
    import json, sys
    d = json.load(open('/tmp/d1md/letters.json'))
    rows = d[0]['results'] if isinstance(d, list) else d['results']
    for r in rows[:int(sys.argv[1]) if len(sys.argv) > 1 else 4]:
        print(format_letter(r.get('translation'), r.get('purport')))
        print('\n' + '=' * 70 + '\n')
