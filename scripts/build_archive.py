#!/usr/bin/env python3
"""Reune el archivo permanente: texto, escaneos, pruebas y herramientas.

Por que existe
--------------
El trabajo vive repartido en tres sitios: el texto en este repo, los escaneos y
el OCR en `scan_vedabase`, y el registro de la auditoria en
`astro_vedabase/scripts/scan_audit`. Separados estan bien para trabajar, porque
cada uno cambia a su ritmo y los binarios no tienen sitio en git.

Pero el archivo permanente si tiene que ir junto. De poco sirve conservar el
texto si se pierde la prueba de contra que se coteja, o conservar los escaneos
sin el registro de que se decidio en cada discrepancia. Este script monta ese
arbol unico, calcula un manifiesto sobre el conjunto entero y deja el paquete
listo para subir.

Que NO entra, y por que
-----------------------
- entornos virtuales, `__pycache__`, `node_modules`: se reinstalan
- `improved/`: se regenera de `originals/` con reocr_all.py
- `reports/` y los lotes `out_surya*` intermedios: superados por el resultado final
- cualquier cosa que se pueda reconstruir de lo que si entra

Se usan enlaces duros, asi que montar el paquete no duplica los 3 GB en disco.
Si el destino esta en otro volumen, se copia.

Uso
---
    python3 scripts/build_archive.py --dry-run        # que entraria, sin tocar nada
    python3 scripts/build_archive.py                  # montarlo
    python3 scripts/build_archive.py --con-tesseract  # añadir ocr/ (179 MB)
"""
import argparse
import hashlib
import os
import shutil
import sys

CORPUS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCAN = os.path.expanduser("~/git_projects/scan_vedabase")
AUDIT = os.path.expanduser("~/git_projects/astro_vedabase/scripts/scan_audit")
DESTINO = os.path.expanduser("~/vedabase-archivo")

EXCLUIR_DIRS = {".git", "__pycache__", "node_modules", "surya-venv", ".venv", "venv"}

# (destino_en_el_paquete, origen, filtro)
#   filtro: None = todo; tupla = solo esas extensiones; callable = predicado
SECCIONES = [
    ("corpus",            CORPUS,                          (".md", ".jsonl")),
    ("escaneos",          os.path.join(SCAN, "originals"),  (".pdf",)),
    ("ocr-surya",         os.path.join(SCAN, "surya_ocr"),  (".txt",)),
    ("auditoria/registro", AUDIT,                           (".json",)),
    ("auditoria/notas",   AUDIT,                            (".md",)),
    ("auditoria/candidatos", os.path.join(AUDIT, "out_fine"), (".jsonl",)),
    ("auditoria/capa-texto", os.path.join(AUDIT, "capa_texto"), (".json",)),
    ("informes",          AUDIT,                            (".html",)),
    ("herramientas/comparacion", SCAN,                      (".py",)),
    ("herramientas/auditoria",   AUDIT,                     (".py", ".sh")),
    ("patrones",          os.path.join(SCAN, "gold_standards"), None),
]

OPCIONAL_TESSERACT = ("ocr-tesseract", os.path.join(AUDIT, "ocr"), (".txt",))


def recorrer(base, extensiones, recursivo=True):
    if not os.path.isdir(base):
        return []
    salida = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUIR_DIRS]
        if not recursivo and dirpath != base:
            dirnames[:] = []
            continue
        for n in filenames:
            if n.startswith("."):
                continue
            if extensiones and not n.endswith(extensiones):
                continue
            completa = os.path.join(dirpath, n)
            rel = os.path.relpath(completa, base).replace(os.sep, "/")
            salida.append((rel, completa))
    salida.sort(key=lambda p: p[0].encode("utf-8"))
    return salida


def enlazar(origen, destino):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    if os.path.exists(destino):
        os.remove(destino)
    try:
        os.link(origen, destino)          # sin duplicar en disco
    except OSError:
        shutil.copy2(origen, destino)     # otro volumen: copiar


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for t in iter(lambda: f.read(bloque), b""):
            h.update(t)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(description="Monta el paquete de archivo permanente.")
    ap.add_argument("--destino", default=DESTINO)
    ap.add_argument("--dry-run", action="store_true", help="solo listar, no montar")
    ap.add_argument("--con-tesseract", action="store_true",
                    help="incluir ocr/ de tesseract (179 MB): la otra mitad del cotejo")
    args = ap.parse_args()

    secciones = list(SECCIONES)
    if args.con_tesseract:
        secciones.insert(3, OPCIONAL_TESSERACT)

    # Las secciones que apuntan a la raiz de AUDIT no deben recursar: ahi dentro
    # hay 45.000 .txt y lotes intermedios que no queremos arrastrar por accidente.
    no_recursivas = {AUDIT, SCAN, CORPUS}

    total_bytes, total_ficheros = 0, 0
    resumen = []

    for nombre, base, filtro in secciones:
        recursivo = base not in no_recursivas or base == CORPUS
        ficheros = recorrer(base, filtro, recursivo=recursivo)
        if not ficheros:
            resumen.append((nombre, 0, 0, "(vacio o no existe)"))
            continue
        bytes_seccion = sum(os.path.getsize(o) for _, o in ficheros)
        total_bytes += bytes_seccion
        total_ficheros += len(ficheros)
        resumen.append((nombre, len(ficheros), bytes_seccion, ""))
        if args.dry_run:
            continue
        for rel, origen in ficheros:
            enlazar(origen, os.path.join(args.destino, nombre, rel))

    print(f"{'seccion':<26} {'ficheros':>9} {'tamaño':>11}")
    print("-" * 49)
    for nombre, n, b, nota in resumen:
        print(f"{nombre:<26} {n:>9} {b/1e6:>9.1f} MB  {nota}")
    print("-" * 49)
    print(f"{'TOTAL':<26} {total_ficheros:>9} {total_bytes/1e6:>9.1f} MB")

    gib = total_bytes / (1 << 30)
    print(f"\nArweave: ~{gib*21.06:.0f} $ por protocolo · ~{gib*32.56:.0f} $ con tarjeta (pago unico)")

    if args.dry_run:
        print("\n(--dry-run: no se ha montado nada)")
        return 0

    # manifiesto sobre el paquete completo
    print("\ncalculando el manifiesto del paquete...")
    lineas = []
    for dirpath, dirnames, filenames in os.walk(args.destino):
        dirnames[:] = [d for d in dirnames if d not in EXCLUIR_DIRS]
        for n in sorted(filenames):
            if n in ("MANIFEST.sha256",):
                continue
            completa = os.path.join(dirpath, n)
            rel = os.path.relpath(completa, args.destino).replace(os.sep, "/")
            lineas.append((rel, completa))
    lineas.sort(key=lambda p: p[0].encode("utf-8"))
    cuerpo = "".join(f"{sha256(c)}  {r}\n" for r, c in lineas)
    root = hashlib.sha256(cuerpo.encode()).hexdigest()

    with open(os.path.join(args.destino, "MANIFEST.sha256"), "w", encoding="utf-8") as f:
        f.write(f"# Manifiesto del archivo permanente — {len(lineas)} ficheros\n")
        f.write(f"# root: {root}\n#\n")
        f.write(cuerpo)

    print(f"paquete en {args.destino}")
    print(f"root del paquete: {root}")
    print("\nSiguiente paso: subirlo, y apuntar los identificadores en PROCEDENCIA.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
