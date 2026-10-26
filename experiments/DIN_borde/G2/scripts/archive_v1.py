"""Empaquetado reversible de escalares; no altera ni borra originales."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from support_v1 import ROOT, STAGE, RUN


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pack():
    records = []
    payload = []
    for p in sorted((RUN/'states').glob('*.json')):
        original = p.read_bytes()
        obj = json.loads(original)
        restored = json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode()
        if restored != original:
            raise RuntimeError('Roundtrip no exacto: '+str(p))
        payload.append(json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')
        records.append(dict(path=str(p.relative_to(STAGE)), sha256=digest(original), bytes=len(original)))
    if len(records) != 4200:
        raise RuntimeError('Cohorte no completa para archivar')
    with (RUN/'state_records.jsonl').open('x') as f:
        f.writelines(payload)
    with (STAGE/'state_records_manifest.csv').open('x') as f:
        w = csv.DictWriter(f, fieldnames=['path', 'sha256', 'bytes']); w.writeheader(); w.writerows(records)
    print('PASS:4200 registros reversibles bit a bit; originales conservados')


def unpack():
    expected = {row['path']: row for row in csv.DictReader((STAGE/'state_records_manifest.csv').open())}
    with (RUN/'state_records.jsonl').open() as f:
        for line in f:
            obj = json.loads(line)
            rel = 'results/run_v1/states/'+obj['id']+'.json'
            data = json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode()
            if rel not in expected or digest(data) != expected[rel]['sha256']:
                raise RuntimeError('SHA inválido: '+rel)
            p = STAGE/rel
            if p.exists():
                if p.read_bytes() != data:
                    raise RuntimeError('Original existente distinto: '+rel)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open('xb') as out:
                    out.write(data)
    print('PASS: registros originales comprobados/restaurados sin sobrescribir')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--part', choices=['pack', 'unpack'], required=True)
    args = parser.parse_args()
    pack() if args.part == 'pack' else unpack()
