"""Archivo reversible de los registros forward sin borrar originales."""
import argparse
import csv
import hashlib
import json
from support_v1 import ROOT,STAGE,RUN,CFG,code_guard,guard,csv_write


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--part',choices=['pack','unpack'],required=True);args=parser.parse_args()
    code_guard();guard()
    if args.part=='pack':
        paths=sorted((RUN/'records').glob('*.json'))
        if len(paths)!=1500:raise RuntimeError('Universo de registros distinto')
        dest=RUN/'record_shards';dest.mkdir(exist_ok=False);records=[]
        for start in range(0,len(paths),500):
            output=dest/f'part_{start//500:03}.jsonl'
            with output.open('x') as file:
                for line,path in enumerate(paths[start:start+500],1):
                    data=path.read_bytes();obj=json.loads(data)
                    restored=json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False).encode()
                    if restored!=data:raise RuntimeError('Roundtrip inexacto')
                    file.write(json.dumps(obj,ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n')
                    records.append(dict(path=str(path.relative_to(STAGE)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),shard=str(output.relative_to(STAGE)),line=line))
        csv_write(STAGE/'record_manifest.csv',records)
    else:
        rows=list(csv.DictReader((STAGE/'record_manifest.csv').open()));mapping={(r['shard'],int(r['line'])):r for r in rows};n=0
        for path in sorted((RUN/'record_shards').glob('*.jsonl')):
            for number,line in enumerate(path.open(),1):
                obj=json.loads(line);data=json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False).encode();r=mapping[str(path.relative_to(STAGE)),number]
                if hashlib.sha256(data).hexdigest()!=r['sha256']:raise RuntimeError('SHA shard')
                target=STAGE/r['path']
                if target.exists():
                    if target.read_bytes()!=data:raise RuntimeError('Original distinto')
                else:
                    target.parent.mkdir(parents=True,exist_ok=True)
                    with target.open('xb') as file:file.write(data)
                n+=1
        if n!=1500:raise RuntimeError('Universo al restaurar')
    print('PASS: 1500 registros reversibles; originales conservados')

if __name__=='__main__':main()
