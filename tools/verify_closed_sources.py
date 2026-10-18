"""Verifica únicamente las fuentes documentales seleccionadas; no ejecuta experimentos."""
from pathlib import Path
import csv
import hashlib

root = Path(__file__).resolve().parents[1]
errors = []
with (root / "experiments/closed_sources.csv").open(newline="") as stream:
    rows = list(csv.DictReader(stream))
for row in rows:
    path = root / row["path"]
    if not path.is_file():
        errors.append(f"MISSING {row['path']}")
        continue
    data = path.read_bytes()
    if len(data) != int(row["bytes"]) or hashlib.sha256(data).hexdigest() != row["sha256"]:
        errors.append(f"MISMATCH {row['path']}")
for error in errors:
    print(error)
print(f"{len(rows)-len(errors)}/{len(rows)} fuentes verificadas")
raise SystemExit(bool(errors))
