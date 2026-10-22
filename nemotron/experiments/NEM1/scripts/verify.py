"""NEM1 — Verificación de integridad y reproducción del protocolo.

Comprueba:
- Existencia de archivos esperados en el directorio de resultados.
- Reproduce una corrida en un directorio temporal y compara dos salidas
  científicas byte a byte (summary.json, stability.csv).
- No modifica directorios existentes ni sobrescribe evidencia.

Uso:
    python scripts/verify.py --output results/run_v1
    python scripts/verify.py --output results/run_v2_wine
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]  # leviathan/
NEM1_DIR = REPO_ROOT / "nemotron" / "experiments" / "NEM1"

EXPECTED_FILES = ["summary.json", "stability.csv"]
SCIENTIFIC_OUTPUTS = ["summary.json", "stability.csv"]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_expected_files(run_dir: Path) -> list[str]:
    missing = []
    for name in EXPECTED_FILES:
        if not (run_dir / name).exists():
            missing.append(name)
    return missing


def reproduce_in_tmp(output_rel: str) -> Path:
    """Ejecuta run.py en un directorio temporal y devuelve la ruta de resultados."""
    tmp = Path(tempfile.mkdtemp(prefix="nem1-verify-"))
    out = tmp / output_rel
    out.mkdir(parents=True, exist_ok=True)

    script = NEM1_DIR / "scripts" / "run.py"
    # Extraer el dataset del path de output si es posible
    dataset = "synthetic"
    if "wine" in output_rel:
        dataset = "wine"

    env = os.environ.copy()
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["OMP_NUM_THREADS"] = "1"

    subprocess.run(
        [sys.executable, str(script), "--output", str(out), "--dataset", dataset],
        check=True,
        env=env,
        cwd=str(REPO_ROOT),
    )
    return out


def compare_outputs(original: Path, replica: Path) -> list[str]:
    diffs = []
    for name in SCIENTIFIC_OUTPUTS:
        o = original / name
        r = replica / name
        if not o.exists() or not r.exists():
            diffs.append(f"Falta {name} en {'original' if not o.exists() else 'replica'}")
            continue
        if not filecmp.cmp(o, r, shallow=False):
            diffs.append(f"{name}: diffiere byte a byte")
    return diffs


def main() -> int:
    parser = argparse.ArgumentParser(description="NEM1 — verificación de reproducción")
    parser.add_argument("--output", required=True,
                        help="Directorio de resultados a verificar (relativo a NEM1/)")
    args = parser.parse_args()

    # Resolver ruta: relativo a repo root o a NEM1/
    run_dir = REPO_ROOT / args.output
    if not run_dir.exists():
        run_dir = NEM1_DIR / args.output
    print(f"Repo root: {REPO_ROOT}")
    print(f"NEM1 dir: {NEM1_DIR}")
    print(f"Run dir: {run_dir}")

    missing = check_expected_files(run_dir)
    if missing:
        print(f"FALTAN archivos: {missing}")
        print("Ejecuta primero: python scripts/run.py --output ...")
        return 1

    print("Archivos esperados presentes.")

    print("Reproduciendo en directorio temporal...")
    try:
        replica_dir = reproduce_in_tmp(args.output)
    except subprocess.CalledProcessError as exc:
        print(f"Fallo en reproducción: {exc}")
        return 1

    diffs = compare_outputs(run_dir, replica_dir)
    if diffs:
        print("Diferencias encontradas:")
        for d in diffs:
            print(f"  - {d}")
        return 1

    print("Reproducción byte a byte: OK")
    print("Verificación de NEM1 completada sin errores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
