"""Caja negra aislada: ejecuta bytes intactos del sujeto, nunca la referencia."""
import argparse
import traceback
import warnings
import numpy as np
from support_v1 import SOURCES, guard, sha, write


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--B', type=int, required=True)
    ap.add_argument('--control')
    a = ap.parse_args()
    guard()
    path = SOURCES/'analisis_C1_v1.py'
    result = dict(source_sha256=sha(path))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        try:
            scope = dict(__name__='d2c_subject', __file__=str(path))
            exec(compile(path.read_bytes(), str(path), 'exec'), scope)
            with np.load(a.input, allow_pickle=False) as z:
                sp, X, L, Y = z['sp'], z['X'], z['L'], z['Y']
            if a.control:
                X, L, Y = scope['aplicar_control'](a.control, sp, X, L, Y, np.random.default_rng(1), .3)
            result['primary'] = scope['primaria'](sp, X, L, Y, 3, 260001, a.B)
            result['status'] = 'OK'
        except Exception:
            result.update(status='ERROR', exception=traceback.format_exc())
        result['warnings'] = [dict(category=w.category.__name__, message=str(w.message)) for w in caught]
    write(a.out, result)


if __name__ == '__main__':
    main()
