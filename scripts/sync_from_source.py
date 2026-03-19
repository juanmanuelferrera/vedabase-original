#!/usr/bin/env python3
"""
Script para actualizar el repositorio srila_prabhupada_vedabase_original
con los textos gold standard de vedabase.bhaktiyoga.es

Estrategia: Borrar todos los .txt y descargar todos los .md frescos
"""

import os
import subprocess
import zipfile
import shutil
from pathlib import Path

# URL base para los ZIPs
BASE_URL = "https://pub-9ebe02965a9f4aeb9c5d3d9741790d2d.r2.dev/books"

# Todos los libros disponibles en vedabase.bhaktiyoga.es
BOOKS = [
    "bhagavad-gita-as-it-is",
    "srimad-bhagavatam",
    "sri-caitanya-caritamrta",
    "krsna-book",
    "nectar-of-devotion",
    "nectar-of-instruction",
    "isopanisad",
    "teachings-of-lord-caitanya",
    "teachings-of-lord-kapila",
    "teachings-of-queen-kunti",
    "teachings-of-prahlada-maharaja",
    "science-of-self-realization",
    "raja-vidya",
    "path-of-perfection",
    "perfect-questions-perfect-answers",
    "perfection-of-yoga",
    "beyond-birth-and-death",
    "easy-journey-to-other-planets",
    "elevation-to-krsna-consciousness",
    "life-comes-from-life",
    "light-of-the-bhagavata",
    "on-the-way-to-krsna",
    "reservoir-of-pleasure",
    "second-chance",
    "topmost-yoga-system",
    "lectures-part-1",
    "lectures-part-2",
    "conversations",
    "letters",
]

def download_and_extract_md(slug: str, dest_dir: Path) -> bool:
    """Descarga un ZIP y extrae solo el archivo .md"""
    url = f"{BASE_URL}/{slug}.zip"
    zip_path = dest_dir / f"{slug}.zip"

    print(f"  Descargando {slug}...", end=" ", flush=True)
    result = subprocess.run(
        ["curl", "-sL", "-o", str(zip_path), url],
        capture_output=True
    )

    if result.returncode != 0 or not zip_path.exists() or zip_path.stat().st_size < 1000:
        print("ERROR: descarga fallida")
        if zip_path.exists():
            zip_path.unlink()
        return False

    # Extraer solo el .md
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            md_files = [f for f in zf.namelist() if f.endswith('.md')]
            if md_files:
                zf.extract(md_files[0], dest_dir)
                print(f"OK ({md_files[0]})")
                zip_path.unlink()
                return True
    except zipfile.BadZipFile:
        print("ERROR: ZIP corrupto")

    if zip_path.exists():
        zip_path.unlink()
    return False


def main():
    # Directorio del repositorio
    repo_dir = Path.home() / "srila_prabhupada_vedabase_original"
    temp_dir = Path("/tmp/vedabase_update")

    temp_dir.mkdir(exist_ok=True)

    # Clonar si no existe
    if not repo_dir.exists():
        print(f"Clonando repositorio en {repo_dir}...")
        subprocess.run([
            "git", "clone",
            "https://github.com/juanmanuelferrera/srila_prabhupada_vedabase_original.git",
            str(repo_dir)
        ])
    else:
        print(f"Repositorio encontrado en {repo_dir}")

    print("\n" + "=" * 60)
    print("PASO 1: Descargando archivos .md de vedabase.bhaktiyoga.es")
    print("=" * 60 + "\n")

    success = []
    failed = []

    for slug in BOOKS:
        if download_and_extract_md(slug, temp_dir):
            success.append(slug)
        else:
            failed.append(slug)

    print("\n" + "=" * 60)
    print("PASO 2: Actualizando repositorio")
    print("=" * 60 + "\n")

    # Borrar TODO el contenido del repositorio (excepto .git y README.md)
    print("  Eliminando contenido antiguo...")
    deleted = 0
    for item in repo_dir.iterdir():
        if item.name in [".git", "README.md"]:
            continue
        if item.is_file():
            item.unlink()
            print(f"    - {item.name}")
            deleted += 1
        elif item.is_dir():
            shutil.rmtree(item)
            print(f"    - {item.name}/")
            deleted += 1
    print(f"  Total eliminado: {deleted} items")

    # Mover los .md nuevos al repositorio
    md_files = list(temp_dir.glob("*.md"))
    print(f"\n  Copiando {len(md_files)} archivos .md nuevos...")
    for md in md_files:
        dest = repo_dir / md.name
        shutil.move(str(md), str(dest))
        print(f"    + {md.name}")

    # Limpiar temp
    shutil.rmtree(temp_dir, ignore_errors=True)

    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"\n  Descargados: {len(success)}/{len(BOOKS)}")
    print(f"  Contenido antiguo eliminado: {deleted} items")
    print(f"  Archivos .md agregados: {len(md_files)}")

    if failed:
        print(f"\n  Fallidos ({len(failed)}):")
        for slug in failed:
            print(f"    - {slug}")

    print(f"\n" + "=" * 60)
    print("SIGUIENTE PASO: Revisar y hacer commit")
    print("=" * 60)
    print(f"""
  cd {repo_dir}
  git status
  git diff --stat
  git add -A
  git commit -m "Replace .txt with gold standard .md from vedabase.bhaktiyoga.es"
  git push
""")


if __name__ == "__main__":
    main()
