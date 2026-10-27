"""Inyección operacional en memoria; la fuente del analista permanece intacta."""
import argparse
from pathlib import Path
import sys
from support import target,CFG


def main():
    p=argparse.ArgumentParser();p.add_argument('--injection',required=True);a,rest=p.parse_known_args();m=target()
    original=m.analizar
    def bounded(*args,**kw):return original(*args,**dict(kw,B=CFG['case_B'],NB=CFG['case_NB']))
    m.analizar=bounded
    def fail(*args,**kw):
        if a.injection=='race':
            out=Path(rest[rest.index('--out')+1]);out.mkdir(parents=True,exist_ok=True)
            with (out/'RESULTADO_Q13M2.json').open('x') as f:f.write('RACE_MARKER_PRESERVE')
        raise FloatingPointError('SYNTHETIC_LS_POINT_FAILURE')
    m.referencia_ls=fail
    sys.argv=[str(m.__file__)]+rest;m.main()


if __name__=='__main__':main()
