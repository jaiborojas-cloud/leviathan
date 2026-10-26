"""Shards JSONL reversibles, originales intactos y SHA por registro."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
from support_v1 import STAGE, RUN, CFG


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pack():
    files = sorted((RUN/'states').glob('*.json'))
    if len(files) != CFG['planned_states']:
        raise RuntimeError('Universo no completo')
    directory = RUN/'state_records'; directory.mkdir(exist_ok=False)
    records = []
    for start in range(0, len(files), 1000):
        destination = directory/f'part_{start//1000:03d}.jsonl'
        payload = []
        for line_no, path in enumerate(files[start:start+1000], 1):
            original = path.read_bytes(); obj = json.loads(original)
            restored = json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode()
            if original != restored:
                raise RuntimeError('Roundtrip no exacto: '+str(path))
            payload.append(json.dumps(obj, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n')
            records.append(dict(path=str(path.relative_to(STAGE)), sha256=sha(original), bytes=len(original),
                        shard=str(destination.relative_to(STAGE)), line=line_no))
        with destination.open('x') as f:
            f.writelines(payload)
    with (STAGE/'state_records_manifest.csv').open('x') as f:
        w = csv.DictWriter(f, fieldnames=['path', 'sha256', 'bytes', 'shard', 'line']); w.writeheader(); w.writerows(records)
    print(f'PASS:{len(records)} registros reversibles bit a bit; originales conservados')


def unpack():
    expected = list(csv.DictReader((STAGE/'state_records_manifest.csv').open()))
    mapping = {(r['shard'], int(r['line'])): r for r in expected}
    restored_count = 0
    for path in sorted((RUN/'state_records').glob('*.jsonl')):
        shard = str(path.relative_to(STAGE))
        with path.open() as file:
            for line_no, line in enumerate(file, 1):
                obj = json.loads(line); row = mapping[shard, line_no]
                target = STAGE/row['path']
                data = json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False).encode()
                if sha(data) != row['sha256'] or obj['id'] != target.stem:
                    raise RuntimeError('SHA/ID inválido')
                if target.exists():
                    if target.read_bytes() != data:
                        raise RuntimeError('Original existente distinto')
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with target.open('xb') as f:
                        f.write(data)
                restored_count += 1
    if restored_count != len(mapping) or restored_count != CFG['planned_states']:
        raise RuntimeError('Registros incompletos')
    print(f'PASS:{restored_count} originales comprobados/restaurados sin sobrescribir')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--part', choices=['pack', 'unpack'], required=True)
    args = parser.parse_args()
    pack() if args.part == 'pack' else unpack()
