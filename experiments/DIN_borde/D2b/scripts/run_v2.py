"""Guarda de secuencia v2; algoritmo científico v1 intacto."""
import hashlib
from pathlib import Path
import subprocess
import sys
import run_v1 as instrument

if __name__ == '__main__':
    root = instrument.ROOT
    for path in [Path(__file__).resolve(), Path(instrument.__file__).resolve()]:
        rel = str(path.relative_to(root))
        committed = subprocess.check_output(['git', 'show', 'HEAD:'+rel], cwd=root)
        if path.read_bytes() != committed:
            raise RuntimeError('Código no comprometido: '+rel)
    subprocess.run(['git', 'diff', '--exit-code', 'HEAD', '--', 'experiments/DIN_borde/D2b'],
                   cwd=root, check=True, stdout=subprocess.DEVNULL)
    instrument.CONFIG = dict(instrument.CONFIG, version='v2',
                             arrays_dir='/workspace/work/din-d2b-v2-arrays')
    sys.argv = [sys.argv[0], '--run-id', 'run_v2']
    instrument.main()
