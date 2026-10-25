"""Diagnóstico posterior congelado6512ffb. No cambia rho ni decisiones H1–H5."""
import json
import math
import time
import traceback
import warnings
import numpy as np
from scipy.integrate import quad
from support_v1 import RUN, frozen, guard, write


def main():
    guard()
    out = RUN/'angular_diagnostic'
    out.mkdir(exist_ok=False)
    rho, geom = frozen('rho'), frozen('geometry')
    selected = ['R27_s00_k0_u010', 'P60_s00_k0_u010', 'W27_s00_k0_u010', 'P60_s02_k0_u010']
    start = time.perf_counter()
    summaries = []
    for name in selected:
        r = json.loads((RUN/'states'/(name+'.json')).read_text())
        record = dict(id=name, source_array=r.get('array'), selected_post_design=True,
                      status='INCONCLUSIVE', rays=[])
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            try:
                with np.load(r['array']['path'], allow_pickle=False) as z:
                    M, f = z['M'], z['f']
                ev = np.linalg.eigvalsh(M)
                lam = float(max(abs(ev[0]), abs(ev[-1])))
                psd = bool(ev[0] >= -1e-8*max(1, ev[-1]))
                g = geom.Geometry(M, f)
                original = float(r['rho']['rho_borde'])
                for ux, uy in [(1., 0.), (-1., 0.), (0., 1.), (0., -1.)]:
                    if time.perf_counter()-start > 300:
                        raise TimeoutError('Presupuesto adicional300s')
                    u = np.array([ux, uy])
                    dots = f@u
                    dots -= dots.max()
                    gaps = -dots[dots < 0]
                    m = int(np.sum(dots == 0))
                    if not len(gaps):
                        raise RuntimeError('Rayo constante: rango f inesperado')
                    cuts = np.unique(np.r_[0., 1/gaps, 8/gaps, 32/gaps])
                    def fun(s):
                        return float(rho.integrando(g, u[None, :], np.array([s]))[0, 0])
                    values = [quad(fun, a, b, epsrel=1e-10, epsabs=1e-11, limit=200)
                              for a, b in zip(cuts[:-1], cuts[1:])]
                    value, err = sum(v for v, _ in values), sum(e for _, e in values)
                    tail = float(2*math.sqrt(lam)*np.exp(-gaps*cuts[-1]).sum()/m)
                    mean_gap_upper = float((gaps*np.exp(-gaps*cuts[-1])).sum()/m)
                    monotone = bool(mean_gap_upper < gaps.min())
                    upper = value+err+tail
                    witness = bool(psd and monotone and upper < original*(1-1e-4))
                    record['rays'].append(dict(u=[ux, uy], value=value, quad_error=err, tail=tail,
                                               upper_estimate=upper, cutoff=float(cuts[-1]),
                                               maxima=m, min_positive_gap=float(gaps.min()),
                                               monotonic_tail=monotone, numerical_witness=witness))
                record['rho_native'] = original
                record['min_axial_upper_estimate'] = min(ray['upper_estimate'] for ray in record['rays'])
                record['ratio_native_to_axial'] = original/record['min_axial_upper_estimate']
                record['PSD_with_primary_tolerance'] = psd
                record['status'] = 'TESTIGO_NUMERICO' if any(ray['numerical_witness'] for ray in record['rays']) else (
                    'SIN_TESTIGO' if psd and all(ray['monotonic_tail'] for ray in record['rays']) else 'INCONCLUSIVE')
            except Exception:
                record['exception'] = traceback.format_exc()
            record['warnings'] = [dict(category=w.category.__name__, message=str(w.message)) for w in caught]
        write(out/(name+'.json'), record)
        summaries.append(dict(id=name, status=record['status'], ratio=record.get('ratio_native_to_axial')))
    write(out/'summary.json', dict(selected_post_design=True, source_protocol='SUPLEMENTO_ANGULAR_FROZEN.md',
                                   seconds=time.perf_counter()-start, cases=summaries,
                                   modifies_primary_decisions=False, rigorous_certificate=False))
    print(json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
