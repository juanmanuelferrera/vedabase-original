#!/usr/bin/env python3
"""Upload the permanent archive to Arweave, resumably.

Why this exists
---------------
The archive is 184,535 files in 1,874 directories. Measured on 2026-08-26, the
CLI moves about 0.35 s per file, so a full run is roughly eighteen hours. A run
that long will be interrupted — wifi drops, the laptop sleeps, a token expires.
Without a record of what already went up, resuming means starting over or
guessing.

So every completed folder and every uploaded file is written to a state file as
it happens. On restart the script reads that file and skips what is done. An
interruption costs the current batch, nothing more.

What it does
------------
1. Mirrors the directory tree into the drive, recording each folder id.
2. Uploads the files of each directory in batches, with the content type that
   section requires — see the table in PROVENANCE.md.
3. Records every transaction id, so PROVENANCE.md can be filled in afterwards
   and anyone can verify what was published.

Content types matter and cannot be fixed later: on Arweave a file can only be
replaced by uploading it again. Note the syntax — `charset=utf-8` with NO space
after the semicolon, or the shell splits the argument and the charset is lost.

Usage
-----
    python3 scripts/upload_archive.py --dry-run          # plan, touching nothing
    python3 scripts/upload_archive.py --only scans       # one section
    python3 scripts/upload_archive.py                    # everything pending
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

ARCHIVE = os.path.expanduser("~/vedabase-archive")
STATE = os.path.join(ARCHIVE, "UPLOAD-STATE.json")
WALLET = os.path.expanduser("~/.arweave/wallet.json")
ROOT_FOLDER = "a01bc670-61a5-46a4-87b8-5b4439b45750"

# From the table in PROVENANCE.md. A section not listed here falls back to the
# CLI's own guess from the file extension. A dict value maps extension to type,
# for a section that holds more than one kind of thing.
CONTENT_TYPES = {
    "corpus":            "text/markdown;charset=utf-8",
    "corrections":       "application/x-ndjson;charset=utf-8",
    "scans":             "application/pdf",
    "ocr-packed":        {".tar":    "application/x-tar",
                          ".sha256": "text/plain;charset=utf-8"},
    "audit":             "application/json;charset=utf-8",
    "reports":           "text/html;charset=utf-8",
    "tools":             "text/x-python;charset=utf-8",
    "reference-standards": None,
}

# The OCR sections are uploaded as ocr-packed: one tar per book, built and
# verified by pack_ocr.py. 69,799 page files became 42 containers, which is
# thirteen hours of CLI time saved. It costs 0.08 credits more, not less — tar
# pads every member to a 512 byte boundary and the median page is 1,874 bytes —
# so this buys time, not money. OCR-CONTENTS.sha256 travels with them so a
# single page can be checked without trusting the container.
# Order matters when a run gets interrupted. Everything cheap in time goes
# first, so an overnight failure leaves as much finished as possible: the 43
# containers of ocr-packed carry 193 MB and take seconds, while corpus is
# 102,729 files and sixteen hours. Corpus goes last for that reason alone.
SECTION_ORDER = ["scans", "reports", "corrections", "audit", "tools",
                 "reference-standards", "ocr-packed", "corpus"]

# Paths not to publish, as prefixes relative to the package root. The files stay
# on disk and in the package: this excludes them from the upload only.
#
# Russian was held back from 26 Aug 2026 until 16 Sep 2026 because the
# translation was unfinished, and Arweave does not allow taking anything back.
# The condition the exclusion named has been met: the translation is complete —
# all 22 books of the archive have Russian, 20,673 rows, checked ref by ref
# against the English. So the exclusion is lifted, exactly as it said it should
# be, and the uploader picks the files up on the next run.
#
# Nothing else changes: the state file records the 86,996 files already
# published, so a run now proposes the 16,361 Russian ones and nothing more.
EXCLUIR_RUTAS = ()

# Files at the root of the package, uploaded to the root of the drive. Easy to
# forget, because the walk below only ever descends into sections — MANIFEST
# was left out of the first run for exactly that reason, and it is the one file
# that makes every other file checkable.
ROOT_FILES = {"MANIFEST.sha256": "text/plain;charset=utf-8"}


# The floor guard
# ---------------
# The state file is the ONLY record of what is already on chain, and it is local
# to whichever machine did the uploading. It is not in git — it is 30 MB of
# churn — so a second machine with an older copy will see thousands of files as
# pending and upload them all again. They cannot be unpublished, and they cost
# money. This happened in spirit on 20 Sep 2026: the Mac mini held 107,744
# entries while the MacBook was still at the September figure.
#
# So the repository carries the floor, the count is checked against it, and a
# state file that knows about fewer files than the floor is treated as stale.
# Raise the floor from the machine that did the upload:
#     python3 scripts/upload_archive.py --sellar-suelo
SUELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UPLOAD-STATE.suelo")


def lee_suelo():
    if not os.path.isfile(SUELO):
        return 0, "(sin sellar)"
    with open(SUELO, encoding="utf-8") as f:
        d = json.load(f)
    return d.get("subidos", 0), d.get("sellado", "?")


def load_state(comprobar=True):
    if os.path.isfile(STATE):
        with open(STATE, encoding="utf-8") as f:
            st = json.load(f)
    else:
        st = {"folders": {}, "uploaded": {}, "failed": {}, "started": now()}

    suelo, sellado = lee_suelo()
    n = len(st["uploaded"])
    if comprobar and n < suelo:
        sys.exit(
            f"\nABORTADO: este fichero de estado esta ATRASADO.\n\n"
            f"  {STATE}\n"
            f"  conoce {n:,} ficheros subidos\n"
            f"  y el repositorio dice que hay al menos {suelo:,} (sellado el {sellado})\n\n"
            f"Faltan {suelo - n:,}. Si se sigue, se volverian a subir ficheros que YA\n"
            f"estan en la cadena: no se pueden borrar y se pagan otra vez.\n\n"
            f"Trae el fichero de estado de la maquina que hizo la ultima subida y\n"
            f"vuelve a intentarlo. Si de verdad quieres seguir con este, --sin-suelo.\n")
    return st


def sella_suelo():
    """Record the current count in the repository, so another machine with an
    older state file refuses to run. Commit the result."""
    st = load_state(comprobar=False)
    n = len(st["uploaded"])
    suelo, _ = lee_suelo()
    if n < suelo:
        sys.exit(f"ABORTADO: no se baja el suelo. Local {n:,} < sellado {suelo:,}.")
    with open(SUELO, "w", encoding="utf-8") as f:
        json.dump({"subidos": n, "sellado": now(),
                   "nota": "Minimo de ficheros que el estado debe conocer. Ver SUELO en upload_archive.py."},
                  f, indent=2)
        f.write("\n")
    print(f"suelo sellado en {n:,} ficheros -> {os.path.relpath(SUELO)}")
    print("Ahora hazle commit, para que la otra maquina lo reciba con git pull.")
    return 0


def save_state(st):
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATE)          # atomic: a crash mid-write cannot corrupt it


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")


def ardrive(args, timeout=600):
    """Run the CLI and return parsed JSON, or None with the error text."""
    try:
        r = subprocess.run(["ardrive"] + args, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return None, "timeout"
    out = r.stdout.strip()
    if not out:
        return None, (r.stderr.strip() or "no output")[:300]
    try:
        return json.loads(out), None
    except json.JSONDecodeError:
        return None, out[:300]


def ensure_folder(st, rel, name, parent_id, dry):
    """Create a folder in the drive if the state does not already have it."""
    if rel in st["folders"]:
        return st["folders"][rel]
    if dry:
        return f"<nuevo:{rel}>"
    # Same retry as an upload, and for the same reason. Creating a folder is a
    # network call like any other, and on 27 Aug 2026 one of them came back
    # "TypeError: fetch failed" and ended a run with 20,000 files still to go —
    # a run that had already survived two days precisely because uploads retry.
    # Guarding the upload and leaving the folder call bare was an oversight.
    espera = 30
    for intento in range(1, 5):
        data, err = ardrive(["create-folder", "--parent-folder-id", parent_id,
                             "--folder-name", name, "-w", WALLET, "--turbo"])
        if not err:
            break
        limite = 2 if err == "timeout" else 4
        if intento >= limite:
            raise RuntimeError(f"create-folder {rel}: {err} (tras {intento} intentos)")
        print(f"    reintento {intento}/{limite - 1} creando {rel} tras '{err}', "
              f"esperando {espera}s", flush=True)
        time.sleep(espera)
        espera *= 2
    fid = next((c.get("entityId") for c in data.get("created", [])
                if c.get("type") == "folder"), None)
    if not fid:
        raise RuntimeError(f"create-folder {rel}: sin entityId")
    st["folders"][rel] = fid
    save_state(st)
    return fid


def ocupacion(st, rel):
    """How many files the state says are already in this drive folder.

    The CLI enumerates the destination folder on every upload to resolve name
    conflicts — every one of --replace, --skip, --upsert and --ask does it, so
    there is no flag that avoids the cost. It grows with what the folder already
    holds, and it is the reason a folder must go up in a single invocation.
    """
    p = rel + "/"
    return sum(1 for k in st["uploaded"]
               if k.startswith(p) and "/" not in k[len(p):])


def upload_batch(st, paths, folder_id, ctype, dry, timeout=600):
    if dry:
        for p in paths:
            st["uploaded"][relkey(p)] = {"tx": "<dry>", "at": now()}
        return
    args = ["upload-file", "--local-paths"] + paths + \
           ["--parent-folder-id", folder_id, "-w", WALLET, "--turbo", "--replace"]
    if ctype:
        args += ["--content-type", ctype]

    # Retry before giving up. A single hung invocation used to kill the whole
    # run: on 26 Aug 2026 a batch of 100 files totalling 2.3 MB — the largest
    # 40 KB — sat for over thirty minutes without returning and ended a job with
    # twenty-six hours still to go. The network was fine minutes later, so it
    # was transient. Over a run this long, transient failures are certainties,
    # not risks, and the uploader has to survive them unattended.
    #
    # A timed-out upload may in fact have landed, so a retry can pay for the
    # same batch twice. At roughly 0.001 credits per hundred small files that is
    # a good trade for not losing a day of work.
    # A dropped connection is worth retrying; an exhausted deadline is not. The
    # deadline already scales with the destination, so if it ran out, repeating
    # the same call runs it out again — four attempts at a 43-minute deadline
    # would be nearly three hours of an overnight run spent achieving nothing.
    espera = 30
    for intento in range(1, 5):
        data, err = ardrive(args, timeout=timeout)
        if not err:
            break
        limite = 2 if err == "timeout" else 4
        if intento >= limite:
            raise RuntimeError(f"upload: {err} (tras {intento} intentos)")
        print(f"    reintento {intento}/{limite - 1} tras '{err}', "
              f"esperando {espera}s", flush=True)
        time.sleep(espera)
        espera *= 2
    # Match each transaction to its file by the sourceUri the CLI reports, never
    # by position. The order of `created` does not follow the order of the paths
    # given, and pairing them by index silently files each transaction under the
    # wrong name. Measured 28 Aug 2026: about three in a thousand were crossed —
    # sb-4.22.48 was recorded against the transaction holding sb-4.22.49 — and a
    # short `created` list left six files with no transaction at all.
    #
    # Nothing was lost by it: every file reached the chain and the manifest, which
    # maps hash to path, was never touched by this. What was wrong was only this
    # bookkeeping, and only until now.
    por_uri = {}
    for c in data.get("created", []):
        if not c.get("dataTxId"):
            continue
        uri = c.get("sourceUri", "")
        if uri.startswith("file://"):
            por_uri[os.path.realpath(uri[7:])] = c["dataTxId"]

    sin_pareja = []
    for p in paths:
        tx = por_uri.get(os.path.realpath(p))
        if tx is None:
            sin_pareja.append(p)
        st["uploaded"][relkey(p)] = {"tx": tx, "at": now()}
    if sin_pareja:
        print(f"    AVISO: {len(sin_pareja)} sin transaccion emparejable "
              f"(p.ej. {relkey(sin_pareja[0])})", flush=True)
    save_state(st)


def relkey(path):
    return os.path.relpath(path, ARCHIVE).replace(os.sep, "/")


def excluida(rel):
    """Held back from publication. On disk, but not uploaded."""
    return rel.startswith(EXCLUIR_RUTAS)


def tipo(seccion, ruta):
    """Content type for one file: per section, or per extension within it."""
    c = CONTENT_TYPES.get(seccion)
    if isinstance(c, dict):
        return c.get(os.path.splitext(ruta)[1])
    return c


def por_tipo(seccion, paths):
    """Group a folder's files by content type, preserving order.

    A batch goes to the CLI with a single --content-type, so files that need
    different ones cannot travel together. On Arweave a wrong content type
    cannot be corrected afterwards, only re-uploaded and paid for again.
    """
    grupos = {}
    for p in paths:
        grupos.setdefault(tipo(seccion, p), []).append(p)
    return grupos


def lotes(paths, max_files, max_bytes):
    """Batches capped by BOTH file count and total bytes.

    Counting files alone is not enough. The scans are 70 PDFs averaging 30 MB,
    so a batch of 100 files is over a gigabyte in a single CLI invocation:
    nothing is recorded until the whole gigabyte finishes, a failure at the last
    file throws away the whole batch, and the subprocess timeout can fire
    mid-upload. Observed on the first run, 2026-08-26.

    A file larger than the cap goes on its own — never skipped.
    """
    lote, acc = [], 0
    for p in paths:
        n = os.path.getsize(p)
        if lote and (len(lote) >= max_files or acc + n > max_bytes):
            yield lote
            lote, acc = [], 0
        lote.append(p)
        acc += n
    if lote:
        yield lote


def sube_carpeta(st, sec, pendientes, parent, rel, args, hechos, t0):
    """Upload one folder's pending files. Returns an error string, or None."""
    # A fixed deadline does not fit a cost that depends on the destination.
    # Measured 26 Aug 2026: one file into an empty folder takes 4.4 s; one file
    # into a folder already holding 200 takes over five minutes, because the CLI
    # enumerates the destination to resolve name conflicts. A flat 600 s killed
    # the run twice on the five most populated folders of the corpus — the
    # lectures, at 409 to 703 files each — while leaving small folders with a
    # deadline far longer than they need.
    dentro = ocupacion(st, rel)
    for ctype, grupo in por_tipo(sec, pendientes).items():
        for lote in lotes(grupo, args.batch, args.max_bytes):
            tmo = min(3600, 300 + 4 * (dentro + len(lote)))
            try:
                upload_batch(st, lote, parent, ctype, args.dry_run, timeout=tmo)
            except RuntimeError as e:
                return str(e)
            dentro += len(lote)
            n = len(st["uploaded"])
            trans = time.time() - t0
            vel = (n - hechos) / trans if trans else 0
            print(f"  {rel[:44]:44} {n:>7} hechos  {vel:5.1f} fich/s", flush=True)
    return None


def sube_raiz(st, args):
    """Upload the package's root-level files. Returns (files, bytes) pending."""
    n = b = 0
    for nombre, ctype in sorted(ROOT_FILES.items()):
        ruta = os.path.join(ARCHIVE, nombre)
        if not os.path.isfile(ruta) or nombre in st["uploaded"]:
            continue
        print(f"\n=== raiz: {nombre}  ({ctype})")
        n += 1
        b += os.path.getsize(ruta)
        if args.dry_run:
            continue
        upload_batch(st, [ruta], ROOT_FOLDER, ctype, args.dry_run)
        print(f"  subido  tx {st['uploaded'][nombre]['tx']}")
    return n, b


def main():
    ap = argparse.ArgumentParser(description="Resumable upload of the archive.")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--sellar-suelo", action="store_true",
                    help="anota el recuento actual en el repositorio y sal. Se ejecuta "
                         "en la maquina que acaba de subir, y se le hace commit")
    ap.add_argument("--sin-suelo", action="store_true",
                    help="salta la comprobacion de estado atrasado. Solo si sabes por que")
    ap.add_argument("--only", help="upload just this section")
    ap.add_argument("--batch", type=int, default=1000,
                    help="max files per CLI invocation (default 1000, above the "
                         "largest folder in the package so each goes up in one call)")
    ap.add_argument("--max-bytes", type=int, default=200_000_000,
                    help="max bytes per CLI invocation (default 200 MB). Caps the "
                         "work lost to a failure and keeps batches inside the timeout")
    args = ap.parse_args()

    if args.sellar_suelo:
        return sella_suelo()

    st = load_state(comprobar=not args.sin_suelo)
    hechos = len(st["uploaded"])
    pend_files = pend_bytes = 0
    t0 = time.time()

    secciones = [args.only] if args.only else SECTION_ORDER
    if not args.only:
        pend_files, pend_bytes = sube_raiz(st, args)

    for sec in secciones:
        base = os.path.join(ARCHIVE, sec)
        if not os.path.isdir(base):
            continue
        c = CONTENT_TYPES.get(sec)
        etiqueta = ("por extension: " + ", ".join(sorted(c))) if isinstance(c, dict) \
            else (c or "tipo deducido por extension")
        print(f"\n=== {sec}  ({etiqueta})")

        for dirpath, dirnames, filenames in os.walk(base):
            dirnames.sort()
            files = sorted(f for f in filenames if not f.startswith("."))
            pendientes = [os.path.join(dirpath, f) for f in files
                          if relkey(os.path.join(dirpath, f)) not in st["uploaded"]
                          and not excluida(relkey(os.path.join(dirpath, f)))]
            if not pendientes:
                continue

            rel = os.path.relpath(dirpath, ARCHIVE).replace(os.sep, "/")
            if args.dry_run:
                pend_files += len(pendientes)
                pend_bytes += sum(os.path.getsize(p) for p in pendientes)
                continue

            # asegurar la carpeta y todas sus ascendientes
            # A failure here used to escape as a traceback, losing the tidy exit
            # that tells you where it stopped and that a relaunch resumes.
            parent = ROOT_FOLDER
            acumulado = ""
            try:
                for parte in rel.split("/"):
                    acumulado = f"{acumulado}/{parte}" if acumulado else parte
                    parent = ensure_folder(st, acumulado, parte, parent, args.dry_run)
            except RuntimeError as e:
                st["failed"][rel] = {"error": str(e), "at": now()}
                save_state(st)
                print(f"\nPARADO creando carpeta para {rel}: {e}")
                print(f"Subidos {len(st['uploaded']) - hechos} ficheros en esta sesion.")
                print("Vuelve a lanzar el script y continuara donde lo dejo.")
                return 1

            err = sube_carpeta(st, sec, pendientes, parent, rel, args, hechos, t0)
            if err:
                st["failed"][rel] = {"error": err, "at": now()}
                save_state(st)
                print(f"\nPARADO en {rel}: {err}")
                print(f"Subidos {len(st['uploaded']) - hechos} ficheros en esta sesion.")
                print("Vuelve a lanzar el script y continuara donde lo dejo.")
                return 1

    if args.dry_run:
        # 0.58 s/file, not the 0.35 first estimated: that figure came from one
        # folder-level invocation and ignored the CLI start-up paid per batch.
        # Cost from the Turbo price API, measured 2026-08-26, exact to 0.000%.
        horas = pend_files * 0.58 / 3600
        creditos = (pend_files * 9_174_313 + pend_bytes * 11_184.90) / 1e12
        print(f"\nPENDIENTE: {pend_files} ficheros, {pend_bytes/1e9:.3f} GB")
        print(f"  a 0,58 s/fichero medidos: ~{horas:.1f} horas")
        print(f"  coste: ~{creditos:.3f} creditos  (~{creditos*3.4:.2f} USD)")
        print(f"  ya registrados como subidos: {hechos}")
        return 0

    print(f"\nCompletado. {len(st['uploaded'])} ficheros registrados en {STATE}")

    # Sin esto el suelo se queda viejo por olvido, y la proteccion que da deja de
    # cubrir lo que se acaba de subir.
    suelo, _ = lee_suelo()
    if len(st["uploaded"]) > suelo:
        print(f"\nEl suelo del repositorio esta en {suelo:,} y esta maquina va por "
              f"{len(st['uploaded']):,}.\n"
              f"  python3 scripts/upload_archive.py --sellar-suelo\n"
              f"y hazle commit, o la otra maquina no sabra de estos ficheros.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
