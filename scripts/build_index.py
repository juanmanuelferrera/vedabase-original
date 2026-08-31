#!/usr/bin/env python3
"""Build a browsable directory of the archive: one link per file.

Why this exists
---------------
An Arweave path manifest resolves files, not folders. `<tx>/corpus/` returns
nothing, so without something like this the only way to reach a file is to know
its path already — which means reading a 12 MB manifest. That is fine for a
machine and useless for a person.

So this writes plain HTML index pages into the package, which the next manifest
then makes addressable. One page per group, one link per file, and a front page
listing the groups. Nothing but relative links: the pages work under any gateway
and any transaction id, because they never name one.

The grouping keeps every page under about a megabyte. The Caitanya-caritāmṛta in
four languages is eleven thousand files apiece; a single page for the whole
archive would be eight megabytes and open on nothing.

What is left out
----------------
`_early-tests/`, which is not archive content; the front page itself; and the
Russian translation, which is held back from publication. Indexing the Russian
would have produced 16,311 links to files that are not on the chain — every one
of them a 404, and every one of them looking like data loss rather than like the
deliberate omission it is. Keep this list in step with EXCLUIR_RUTAS in
upload_archive.py.

Usage
-----
    python3 scripts/build_index.py           # writes ~/vedabase-archive/_index/
"""
import html
import os
import sys
from collections import defaultdict

ARCHIVE = os.path.expanduser("~/vedabase-archive")
DESTINO = os.path.join(ARCHIVE, "_index")
FUERA = ("_early-tests/", "_index/", "corpus/translations/russian/")

CSS = """body{max-width:60rem;margin:0 auto;padding:2rem 1.25rem 4rem;
font:15px/1.6 Georgia,"Times New Roman",serif;background:#fbfaf7;color:#22201c}
@media(prefers-color-scheme:dark){body{background:#171614;color:#e6e2da}}
h1{font-size:1.5rem;margin:0 0 .2rem}.sub{opacity:.65;margin:0 0 1.6rem;font-size:.95rem}
a{color:#1a6f63;text-decoration:none}a:hover{text-decoration:underline}
@media(prefers-color-scheme:dark){a{color:#63c3b4}}
ul{list-style:none;padding:0;margin:0;columns:2;column-gap:2rem}
@media(max-width:640px){ul{columns:1}}
li{padding:.12rem 0;font-size:.9rem;break-inside:avoid}
.n{opacity:.5;font-size:.85rem}
.back{display:inline-block;margin-bottom:1.2rem;font-size:.9rem}"""


def grupo(p):
    """Which page a path belongs on. Keeps every page roughly readable."""
    part = p.split("/")
    if len(part) == 1:
        return "(root)"
    if part[0] != "corpus":
        return part[0]
    if part[1] == "translations" and len(part) > 3:
        return f"corpus/translations/{part[2]}/{part[3]}"
    return f"corpus/{part[1]}"


def slug(g):
    return g.replace("/", "-").replace("(", "").replace(")", "") or "root"


def pagina(titulo, cuerpo, atras=True):
    v = ["<!doctype html><meta charset=utf-8>",
         f"<title>{html.escape(titulo)} — Vedabase Original</title>",
         "<meta name=viewport content='width=device-width,initial-scale=1'>",
         f"<style>{CSS}</style>"]
    if atras:
        v.append("<a class=back href='./index.html'>← index</a>")
    v.append(f"<h1>{html.escape(titulo)}</h1>")
    v.append(cuerpo)
    return "\n".join(v)


def main():
    rutas = []
    for dp, dn, fn in os.walk(ARCHIVE):
        for f in fn:
            rel = os.path.relpath(os.path.join(dp, f), ARCHIVE).replace(os.sep, "/")
            if rel.startswith(FUERA) or f.startswith(".") or rel == "index.html":
                continue
            if f in ("UPLOAD-STATE.json", "upload.log", "verify.log") \
               or f.startswith(("UPLOAD-STATE", "VERIFY-CHAIN")):
                continue
            rutas.append(rel)
    rutas.sort()

    grupos = defaultdict(list)
    for r in rutas:
        grupos[grupo(r)].append(r)

    os.makedirs(DESTINO, exist_ok=True)

    for g, rs in grupos.items():
        li = "\n".join(
            f"<li><a href='../{html.escape(r)}'>{html.escape(r.split('/')[-1])}</a></li>"
            for r in rs)
        cuerpo = (f"<p class=sub>{len(rs):,} files · <code>{html.escape(g)}/</code></p>"
                  f"<ul>{li}</ul>")
        with open(os.path.join(DESTINO, slug(g) + ".html"), "w", encoding="utf-8") as f:
            f.write(pagina(g, cuerpo))

    filas = "\n".join(
        f"<li><a href='./{slug(g)}.html'>{html.escape(g)}</a> "
        f"<span class=n>{len(rs):,}</span></li>"
        for g, rs in sorted(grupos.items()))
    portada = pagina(
        "Directory",
        f"<p class=sub>Every file in the archive, {len(rutas):,} of them, grouped so "
        f"no page grows unreadable. Links are relative: they work under any gateway.</p>"
        f"<ul>{filas}</ul>",
        atras=False)
    with open(os.path.join(DESTINO, "index.html"), "w", encoding="utf-8") as f:
        f.write(portada)

    total = sum(os.path.getsize(os.path.join(DESTINO, x))
                for x in os.listdir(DESTINO))
    print(f"{len(grupos) + 1} paginas, {len(rutas):,} enlaces, {total/1e6:.1f} MB")
    print(f"  en {DESTINO}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
