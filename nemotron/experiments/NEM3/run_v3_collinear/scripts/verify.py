"""NEM3 run_v3_collinear — Verificación de reproducción byte a byte.

Uso:
    python scripts/verify.py --output results/run_v1
"""

from __future__ import annotations

import argparse
import filecmp
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[5]  # leviathan/
RUN3_DIR = REPO_ROOT / "nemotron" / "experiments" / "NEM3" / "run_v3_collinear"

EXPECTED_FILES = ["summary.json", "observables.csv", "checks.csv"]
SCIENTIFIC_OUTPUTS = ["summary.json", "observables.csv", "checks.csv"]


def check_expected_files(run_dir: Path) -> list[str]:
    missing = []
    for name in EXPECTED_FILES:
        if not (run_dir / name).exists():
            missing.append(name)
    return missing


def reproduce_in_tmp(output_rel: str) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="nem3c-verify-"))
    out = tmp / output_rel
    out.mkdir(parents=True, exist_ok=True)

    script = RUN3_DIR / "scripts" / "run.py"
    env = os.environ.copy()
    env["OPENBLAS_NUM_THREADS"] = "1"
    env["OMP_NUM_THREADS"] = "1"

    subprocess.run(
        [sys.executable, str(script), "--output", str(out)],
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
    parser = argparse.ArgumentParser(description="NEM3 run_v3_collinear — verificación de reproducción")
    parser.add_argument("--output", required=True,
                        help="Directorio de resultados a verificar (relativo a repo root o NEM3/run_v3_collinear/)")
    args = parser.parse_args()

    run_dir = REPO_ROOT / args.output
    if not run_dir.exists():
        run_dir = RUN3_DIR / args.output
    print(f"Repo root: {REPO_ROOT}")
    print(f"Run3 dir: {RUN3_DIR}")
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
    print("Verificación de NEM3 run_v3_collinear completada sin errores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
