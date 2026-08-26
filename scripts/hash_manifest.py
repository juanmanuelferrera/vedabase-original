#!/usr/bin/env python3
"""Manifiesto de hashes del corpus, para anclarlo fuera de nuestro control.

Para que sirve
--------------
Todo el proyecto se sostiene en una afirmacion: este texto es el de las
primeras ediciones y no lo hemos tocado. Hoy esa afirmacion descansa en la
palabra de quien lo publica y en un repositorio que esa misma persona controla
y podria reescribir.

Este manifiesto convierte la afirmacion en algo comprobable. Calcula el SHA-256
de cada fichero del corpus, los ordena de forma determinista y produce un
`root` que resume el conjunto entero. Publicado ese `root` en un sitio que
nadie puede reescribir —Arweave— cualquiera puede repetir el calculo sobre su
propia copia y ver si coincide, sin preguntarnos y sin fiarse de nosotros.

Es el mismo principio que PRINT_ERRATA.md: no pedimos que nos crean, enseñamos
como comprobarlo. Aqui aplicado a nosotros mismos y a lo largo del tiempo.

Lo que NO prueba
----------------
Que el texto sea fiel al impreso. Eso lo demuestra el cotejo contra los
escaneos, no un hash. El manifiesto solo congela el resultado con fecha, para
que despues no se pueda discutir que el corpus haya cambiado sin decirlo.

Determinismo
------------
Mismo corpus = mismo `root`, en cualquier maquina. Por eso: rutas relativas con
`/` siempre, orden por bytes de la ruta, y el `root` se calcula sobre las lineas
del manifiesto, no sobre metadatos que cambian (fechas, nombres de maquina).

Uso
---
    python3 scripts/hash_manifest.py                 # escribe MANIFEST.sha256
    python3 scripts/hash_manifest.py --check         # verifica el existente
    python3 scripts/hash_manifest.py --incluir-escaneos  # añade los PDF de scan_vedabase
"""
import argparse
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
SALIDA = os.path.join(RAIZ, "MANIFEST.sha256")
ESCANEOS = os.path.expanduser("~/git_projects/scan_vedabase")

# Lo que entra en el manifiesto. El .git queda fuera a proposito: es historia
# mutable (un rebase la cambia) y no es el objeto que se certifica.
EXTENSIONES = (".md", ".jsonl")
EXCLUIR_DIRS = {".git", "__pycache__", "node_modules", ".deploy-state"}


def sha256(ruta, bloque=1 << 20):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(bloque), b""):
            h.update(trozo)
    return h.hexdigest()


def recorrer(base, extensiones=None):
    """Rutas relativas, ordenadas por bytes, con '/' como separador."""
    encontradas = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in EXCLUIR_DIRS]
        for n in filenames:
            if n.startswith("."):
                continue
            if extensiones and not n.endswith(extensiones):
                continue
            completa = os.path.join(dirpath, n)
            rel = os.path.relpath(completa, base).replace(os.sep, "/")
            encontradas.append((rel, completa))
    encontradas.sort(key=lambda p: p[0].encode("utf-8"))
    return encontradas


def commit_actual():
    try:
        return subprocess.check_output(
            ["git", "-C", RAIZ, "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return "(sin git)"


def construir(incluir_escaneos=False):
    lineas = []
    total_bytes = 0

    for rel, completa in recorrer(RAIZ, EXTENSIONES):
        lineas.append(f"{sha256(completa)}  corpus/{rel}")
        total_bytes += os.path.getsize(completa)

    if incluir_escaneos and os.path.isdir(ESCANEOS):
        for sub in ("originals", "improved"):
            base = os.path.join(ESCANEOS, sub)
            if not os.path.isdir(base):
                continue
            for rel, completa in recorrer(base, (".pdf",)):
                lineas.append(f"{sha256(completa)}  scans/{sub}/{rel}")
                total_bytes += os.path.getsize(completa)

    cuerpo = "\n".join(lineas) + "\n"
    root = hashlib.sha256(cuerpo.encode("utf-8")).hexdigest()
    return lineas, cuerpo, root, total_bytes


def escribir(lineas, cuerpo, root, total_bytes):
    cab = [
        "# Manifiesto de integridad — vedabase-original",
        "#",
        "# El `root` de abajo es el SHA-256 de las lineas de este manifiesto,",
        "# excluida esta cabecera. Se publica en Arweave; su identificador de",
        "# transaccion queda en ANCLAS.md.",
        "#",
        "# Comprobarlo por tu cuenta:",
        "#     python3 scripts/hash_manifest.py --check",
        "#",
        f"# fecha:    {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"# commit:   {commit_actual()}",
        f"# ficheros: {len(lineas)}",
        f"# bytes:    {total_bytes}",
        f"# root:     {root}",
        "#",
    ]
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("\n".join(cab) + "\n" + cuerpo)


def leer_root_guardado():
    if not os.path.isfile(SALIDA):
        return None, None
    guardado, lineas = None, []
    with open(SALIDA, encoding="utf-8") as f:
        for l in f:
            if l.startswith("# root:"):
                guardado = l.split(":", 1)[1].strip()
            elif not l.startswith("#"):
                lineas.append(l.rstrip("\n"))
    cuerpo = "\n".join(lineas) + "\n" if lineas else ""
    return guardado, cuerpo


def main():
    ap = argparse.ArgumentParser(description="Manifiesto de hashes del corpus.")
    ap.add_argument("--check", action="store_true",
                    help="recalcular y comparar con el manifiesto guardado")
    ap.add_argument("--incluir-escaneos", action="store_true",
                    help="añadir los PDF de scan_vedabase (originals + improved)")
    args = ap.parse_args()

    lineas, cuerpo, root, total = construir(args.incluir_escaneos)

    if args.check:
        guardado, cuerpo_guardado = leer_root_guardado()
        if guardado is None:
            print("No hay MANIFEST.sha256 que comprobar.")
            return 1
        recomputado = hashlib.sha256(cuerpo_guardado.encode("utf-8")).hexdigest()
        print(f"root guardado en la cabecera : {guardado}")
        print(f"root recalculado del cuerpo  : {recomputado}")
        print(f"root del corpus en disco     : {root}")
        if guardado != recomputado:
            print("\nFALLO: la cabecera no cuadra con el cuerpo del manifiesto.")
            return 1
        if root != guardado:
            print(f"\nEl corpus ha cambiado desde el ultimo manifiesto "
                  f"({len(lineas)} ficheros ahora).")
            print("Si el cambio es intencionado, regenera el manifiesto y ancla el root nuevo.")
            return 1
        print(f"\nOK: {len(lineas)} ficheros, sin cambios respecto al manifiesto.")
        return 0

    escribir(lineas, cuerpo, root, total)
    print(f"MANIFEST.sha256 escrito: {len(lineas)} ficheros, {total/1e6:.1f} MB")
    print(f"root: {root}")
    print("\nAncla ese root en Arweave y apunta el txid en ANCLAS.md.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
