"""DIN-I2: ínfimo numérico por conos y normales completas, sin modificar v1.

f(float) se interpreta como racional binario exacto. No hay certificado de
óptimo global ni aritmética de intervalos. Ver DESIGN_FROZEN.md y THEORY.md.
"""
from __future__ import annotations
import hashlib
import math
from fractions import Fraction as Q
from pathlib import Path
import time
import types
import warnings
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.optimize import minimize_scalar, brentq

IMPLEMENTATION_VERSION = 'r3'

GEOMETRY_SHA256 = 'b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3'
_GEOMETRY = {}
_GL = {}


def geometry_class(path=None):
    if path is None:
        root = Path(__file__).resolve().parents[3]
        path = root/'docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/instrument/geometry.py'
    path = Path(path).resolve()
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != GEOMETRY_SHA256:
        raise ValueError('GEOMETRY_SHA_MISMATCH')
    if str(path) not in _GEOMETRY:
        module = types.ModuleType('i2_frozen_geometry')
        module.__file__ = str(path)
        exec(compile(data, str(path), 'exec'), module.__dict__)
        _GEOMETRY[str(path)] = module.Geometry
    return _GEOMETRY[str(path)]


class BudgetExceeded(RuntimeError):
    pass


def _cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


class _Instrument:
    def __init__(self, M, f, *, grid=9, starts=3, margin=1e-8, order=12,
                 log_step=4., maxiter=40, xatol=1e-9, max_evaluations=4096,
                 seconds=60., geometry_path=None):
        self.start = time.perf_counter()
        self.deadline = self.start+seconds
        self.evaluations = 0
        self.cap = max_evaluations
        self.grid, self.starts, self.margin = grid, starts, margin
        self.order, self.log_step = order, log_step
        self.maxiter, self.xatol = maxiter, xatol
        self.M, self.f = np.asarray(M, float), np.asarray(f, float)
        n = len(self.f)
        if self.f.shape != (n, 2) or self.M.shape != (n, n) or n < 3:
            raise ValueError('INPUT_SHAPE')
        if not np.isfinite(self.M).all() or not np.isfinite(self.f).all():
            raise ValueError('INPUT_NONFINITE')
        self.input_eigenvalues = np.linalg.eigvalsh((self.M+self.M.T)/2)
        self.lam_input = float(self.input_eigenvalues[-1])
        scale = max(1., self.lam_input)
        if np.linalg.norm(self.M-self.M.T) > 1e-12*max(1., np.linalg.norm(self.M)):
            raise ValueError('M_NOT_SYMMETRIC')
        if self.input_eigenvalues[0] < -1e-10*scale:
            raise ValueError('M_NOT_PSD')
        self.unique, self.index, self.inverse, self.counts = np.unique(
            self.f, axis=0, return_index=True, return_inverse=True, return_counts=True)
        self.points = [tuple(Q(float(x)) for x in row) for row in self.unique]
        self.groups = [np.flatnonzero(self.inverse == j).tolist() for j in range(len(self.unique))]
        lower, upper = [], []
        for j in range(len(self.points)):
            while len(lower) >= 2 and _cross(self.points[lower[-2]], self.points[lower[-1]], self.points[j]) <= 0:
                lower.pop()
            lower.append(j)
        for j in reversed(range(len(self.points))):
            while len(upper) >= 2 and _cross(self.points[upper[-2]], self.points[upper[-1]], self.points[j]) <= 0:
                upper.pop()
            upper.append(j)
        self.hull = lower[:-1]+upper[:-1]
        if len(self.hull) < 3:
            raise ValueError('AFFINE_RANK_LESS_THAN_TWO')
        self.edges = []
        for k, a in enumerate(self.hull):
            b = self.hull[(k+1) % len(self.hull)]
            pa, pb = self.points[a], self.points[b]
            normal = (pb[1]-pa[1], pa[0]-pb[0])
            gaps = [(pa[0]-p[0])*normal[0]+(pa[1]-p[1])*normal[1] for p in self.points]
            maximum = max(gaps)
            if min(gaps) < 0 or maximum <= 0:
                raise ValueError('INVALID_EXACT_HULL')
            normal = tuple(v/maximum for v in normal)
            gaps = [v/maximum for v in gaps]
            support = [j for j, v in enumerate(gaps) if v == 0]
            near = [j for j, v in enumerate(gaps) if 0 < v <= Q(1, 10**10)]
            self.edges.append(dict(id=k, ends=[a, b], direction=normal, gaps=gaps,
                                   support=support, near=near))
        self.metric_cache = {}
        self.Geometry = geometry_class(geometry_path)
        self.geometry = self.Geometry(self.M, self.f)
        self.partial = dict(faces=[], cones=[], boundary_limits=[], active_cone=None)

    def check_budget(self, count=False):
        if count:
            self.evaluations += 1
        if self.evaluations > self.cap or time.perf_counter() > self.deadline:
            raise BudgetExceeded('SEARCH_BUDGET_EXHAUSTED')

    def original_indices(self, groups):
        return sorted(i for j in groups for i in self.groups[j])

    def metric(self, active):
        key = tuple(active)
        if key not in self.metric_cache:
            groups = [self.groups[j] for j in active]
            ids = sorted(i for group in groups for i in group)
            local = {i: k for k, i in enumerate(ids)}
            m = self.M[np.ix_(ids, ids)]
            # Esta eliminación es algebraica: las velocidades suman0.
            centered = m-m[:, [-1]]-m[[-1], :]+m[-1, -1]
            E = np.zeros((len(ids), len(groups)))
            for j, group in enumerate(groups):
                E[[local[i] for i in group], j] = 1/len(group)
            if len(groups) == 1:
                C = np.zeros((0, 0))
                factor = np.zeros((0, 0))
                lam, clipped = 0., 0.
                dominant, residual_bound = None, 0.
            else:
                B = E[:, :-1]-E[:, [-1]]
                C = B.T@centered@B
                C = (C+C.T)/2
                ev, vec = np.linalg.eigh(C)
                clipped = float(max(0., -ev[0]))
                if ev[0] < -1e-10*max(1., self.lam_input)*len(groups):
                    raise ValueError('CONTRAST_NOT_PSD')
                pos = ev > 0
                factor = vec[:, pos]*np.sqrt(ev[pos])
                lam = float(max(0., ev[-1]))
                dominant = None
                if lam > 0 and lam >= (1-1e-10)*float(np.maximum(ev, 0).sum()):
                    dominant = vec[:, -1]*math.sqrt(lam)
                residual_bound = 2*len(groups)*math.sqrt(float(max(0., ev[-2]))) if len(ev) > 1 else 0.
            self.metric_cache[key] = dict(C=C, factor=factor, lam=lam, clipped=clipped,
                                         counts=self.counts[list(active)].astype(float),
                                         dominant=dominant, residual_bound=residual_bound)
        return self.metric_cache[key]

    def turning_points(self, gaps, counts, mode, lo, hi):
        """Raíces con cambios de signo; no certificado de exhaustividad."""
        step = min(.25, self.log_step/16)
        xs = np.linspace(lo, hi, int(math.ceil((hi-lo)/step))+1)
        def probability(x):
            z = np.exp(np.minimum(x+np.where(gaps > 0, np.log(np.maximum(gaps, 1e-300)), -np.inf), np.log(1e4)))
            a = np.exp(-z)*counts
            return a/a.sum(), z
        def derivative(x):
            a, z = probability(x)
            return float((a*(a@z-z))[:-1]@mode)
        # Evaluación vectorizada de la malla para no multiplicar coste Python.
        zz = np.exp(np.minimum(xs[:, None]+np.where(gaps > 0, np.log(np.maximum(gaps, 1e-300)), -np.inf), np.log(1e4)))
        aa = np.exp(-zz)*counts; aa /= aa.sum(axis=1, keepdims=True)
        yy = (aa*((aa*zz).sum(axis=1, keepdims=True)-zz))[:, :-1]@mode
        roots, rejected = [], []
        for i in range(len(xs)-1):
            if yy[i]*yy[i+1] < 0:
                ya, yb = derivative(xs[i]), derivative(xs[i+1])
                if ya*yb < 0:
                    roots.append(float(brentq(derivative, xs[i], xs[i+1], xtol=1e-12)))
                elif ya == 0 or yb == 0:
                    roots.append(float(xs[i] if ya == 0 else xs[i+1]))
                else:
                    rejected.append(dict(bracket=[float(xs[i]), float(xs[i+1])],
                                         scalar=[ya, yb], vectorized=[float(yy[i]), float(yy[i+1])]))
        roots = sorted(set(roots))
        # La variación incluye los extremos exactos en s=0 e infinito.
        initial = counts/counts.sum()
        final = np.where(gaps == 0, counts, 0.); final /= final.sum()
        values = [float(initial[:-1]@mode)]
        values.extend(float(probability(x)[0][:-1]@mode) for x in roots)
        values.append(float(final[:-1]@mode))
        return roots, float(np.abs(np.diff(values)).sum()), rejected

    @staticmethod
    def integrand(logs, gaps, counts, factor):
        xs = np.atleast_1d(logs)
        ld = np.full(len(gaps), -np.inf)
        positive = gaps > 0
        ld[positive] = np.log(gaps[positive])
        # z>1e4 tiene peso menor que cualquier precisión float usada aquí.
        zz = np.exp(np.minimum(xs[:, None]+ld, np.log(1e4)))
        aa = np.exp(-zz)*counts
        aa /= aa.sum(axis=1, keepdims=True)
        beta = aa*((aa*zz).sum(axis=1, keepdims=True)-zz)
        transformed = beta[:, :-1]@factor
        return np.sqrt(np.sum(transformed**2, axis=1))

    def ray(self, rates, active=None, *, validate=False, exact_levels=None):
        active = list(range(len(self.points))) if active is None else list(active)
        raw = [rates[j] for j in active]
        if any(v < 0 for v in raw):
            raise ValueError('NEGATIVE_DIRECTION_GAP')
        maximum = max(raw)
        if maximum == 0:
            return dict(length=0., quad_error=0., prefix_bound=0., tail_bound=0.,
                        method='constant_curve', active_groups=active,
                        endpoint_groups=active, metric_clip=0.)
        normed = [v/maximum for v in raw]
        gaps = np.array([float(v) for v in normed])
        if any(v > 0 and gaps[j] == 0 for j, v in enumerate(normed)):
            raise ValueError('GAP_UNDERFLOW')
        metric = self.metric(active)
        counts = metric['counts']
        scale = math.sqrt(metric['lam'])
        end = np.flatnonzero(gaps == 0)
        support = [active[j] for j in end]
        base = dict(active_groups=active, endpoint_groups=support,
                    metric_clip=metric['clipped'], method='log_quad' if validate else 'log_GL')
        if scale == 0:
            return dict(base, length=0., quad_error=0., prefix_bound=0., tail_bound=0., method='zero_metric')
        # La fórmula exacta sólo se usa en validación con niveles racionales.
        levels = len(set(normed)) if validate else len(np.unique(gaps))
        if levels <= 2:
            a0 = counts/counts.sum()
            a1 = np.zeros(len(active))
            a1[end] = counts[end]/counts[end].sum()
            beta = (a1-a0)[:-1]
            length = float(np.linalg.norm(beta@metric['factor']))
            return dict(base, length=length, quad_error=0., prefix_bound=0., tail_bound=0., method='analytic_segment')
        lo, hi = -32., math.log(48.)-math.log(float(gaps[gaps > 0].min()))
        cuts = np.linspace(lo, hi, int(math.ceil((hi-lo)/self.log_step))+1)
        roots, dominant_tv, rejected = [], None, []
        if metric['dominant'] is not None:
            roots, dominant_tv, rejected = self.turning_points(gaps, counts, metric['dominant'], lo, hi)
            if not validate:
                return dict(base, length=dominant_tv, quad_error=None, prefix_bound=0., tail_bound=0.,
                            method='dominant_TV_search_only', dominant_roots=roots,
                            rejected_roundoff_brackets=rejected,
                            residual_length_bound=metric['residual_bound'])
            cuts = np.array(sorted(set(cuts.tolist()+roots)))
        prefix = 2*scale*math.exp(lo)
        zfinal = np.exp(np.minimum(hi+np.log(gaps[gaps > 0]), np.log(1e4)))
        tail = float(2*scale*np.sum(counts[gaps > 0]*np.exp(-zfinal))/counts[end].sum())
        if validate:
            value, error = 0., 0.
            warning_messages = []
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                for a, b in zip(cuts[:-1], cuts[1:]):
                    self.check_budget()
                    v, e = quad(lambda x: float(self.integrand(x, gaps, counts, metric['factor'])[0]),
                                a, b, epsabs=1e-11*scale/len(cuts), epsrel=1e-10, limit=150)
                    value += v
                    error += e
                warning_messages = [str(w.message) for w in caught]
        else:
            if self.order not in _GL:
                _GL[self.order] = leggauss(self.order)
            nodes, weights = _GL[self.order]
            mid = (cuts[:-1]+cuts[1:])/2
            half = np.diff(cuts)/2
            xs = (mid[:, None]+half[:, None]*nodes).ravel()
            vals = self.integrand(xs, gaps, counts, metric['factor']).reshape(len(half), self.order)
            value = float(np.sum(half*(vals@weights)))
            error, warning_messages = None, []
        return dict(base, length=float(value+prefix+tail), integral=float(value), quad_error=error,
                    prefix_bound=prefix, tail_bound=tail, x_lower=lo, x_upper=hi,
                    cutoff_s=math.exp(hi) if hi < 709 else None,
                    segments=len(cuts)-1, warnings=warning_messages,
                    dominant_roots=roots, dominant_TV=dominant_tv,
                    rejected_roundoff_brackets=rejected,
                    residual_length_bound=metric['residual_bound'] if dominant_tv is not None else None)

    def cone_rates(self, k, t, rational=False):
        left, right = self.edges[k-1], self.edges[k]
        if rational:
            t = Q(float(t))
            rates = [(1-t)*a+t*b for a, b in zip(left['gaps'], right['gaps'])]
            u = tuple((1-t)*a+t*b for a, b in zip(left['direction'], right['direction']))
        else:
            rates = (1-t)*np.array([float(v) for v in left['gaps']])+t*np.array([float(v) for v in right['gaps']])
            u = None
        return rates, u

    @staticmethod
    def direction_fields(u):
        d = np.array([float(v) for v in u])
        unit = d/np.max(np.abs(d))
        unit /= np.linalg.norm(unit)
        return dict(direction_rational=[str(v) for v in u], direction_unit_float=unit.tolist())

    def validated_vertex(self, k, t):
        rates, u = self.cone_rates(k, t, rational=True)
        result = self.ray(rates, validate=True)
        return dict(result, kind='vertex', cone=k, t=float(t), attained=True,
                    vertex_indices=self.groups[self.hull[k]], **self.direction_fields(u))

    def calculate(self):
        all_active = list(range(len(self.points)))
        faces, limits, cones = [self.partial[key] for key in ['faces', 'boundary_limits', 'cones']]
        vertices = []
        geometry_check = None
        for e in self.edges:
            rr = self.ray(e['gaps'], validate=True)
            faces.append(dict(rr, kind='face', face_id=e['id'], attained=True,
                              face_indices=self.original_indices(e['support']),
                              near_face_indices=self.original_indices(e['near']),
                              **self.direction_fields(e['direction'])))
        for k, v in enumerate(self.hull):
            self.partial['active_cone'] = k
            self.check_budget()
            # Completar el ínfimo abierto con sus dos límites laterales.
            for edge_id, other_id in [((k-1) % len(self.edges), k), (k, (k-1) % len(self.edges))]:
                e, other = self.edges[edge_id], self.edges[other_id]
                tail = self.ray(other['gaps'], active=e['support'], validate=True)
                face = faces[edge_id]
                lim = dict(kind='vertex_limit', cone=k, vertex_indices=self.groups[v],
                           face_id=edge_id, face_indices=face['face_indices'], attained=False,
                           length=face['length']+tail['length'],
                           quad_error=face['quad_error']+tail['quad_error'],
                           prefix_bound=face['prefix_bound']+tail['prefix_bound'],
                           tail_bound=face['tail_bound']+tail['tail_bound'],
                           face_component=face, edge_tail_component=tail,
                           **self.direction_fields(e['direction']))
                limits.append(lim)
            ts = np.linspace(self.margin, 1-self.margin, self.grid)
            cache = {}
            def objective(t):
                t = float(t)
                if t not in cache:
                    self.check_budget(count=True)
                    rates, _ = self.cone_rates(k, t)
                    cache[t] = self.ray(rates)['length']
                return cache[t]
            vals = [objective(t) for t in ts]
            selected = [float(ts[int(np.argmin(vals))])]
            attempts = []
            for center in np.linspace(.25, .75, self.starts):
                a, b = max(self.margin, center-.25), min(1-self.margin, center+.25)
                op = minimize_scalar(objective, bounds=(a, b), method='bounded',
                                     options=dict(maxiter=self.maxiter, xatol=self.xatol))
                selected.append(float(op.x))
                attempts.append(dict(bounds=[a, b], t=float(op.x), fast_length=float(op.fun),
                                     success=bool(op.success), message=str(op.message), nfev=int(op.nfev)))
            candidates = [self.validated_vertex(k, t) for t in sorted(set(selected))]
            vertices.extend(candidates)
            cones.append(dict(cone=k, vertex_indices=self.groups[v], grid=ts.tolist(),
                              fast_values=vals, optimizer_attempts=attempts,
                              candidates=candidates, best=min(candidates, key=lambda a: a['length'])))
            if geometry_check is None:
                rates, u = self.cone_rates(k, .5, rational=True)
                physical = np.array([float(z) for z in u])
                J = self.geometry.jac(np.zeros((1, 2)))[0]
                beta = J@physical
                original = math.sqrt(max(0., float(beta@self.M@beta)))
                gaps = np.array([float(z) for z in rates])
                weights = self.counts/self.counts.sum()
                bv = weights*(weights@gaps-gaps)
                own = float(np.linalg.norm(bv[:-1]@self.metric(all_active)['factor']))
                geometry_check = dict(jac0_speed_original=original, speed_contrast=own,
                                      absolute_error=abs(original-own))
        vert = min(vertices+limits, key=lambda a: a['length'])
        face = min(faces, key=lambda a: a['length'])
        total = min([vert, face], key=lambda a: a['length'])
        return dict(status='VALID_NUMERICAL_ESTIMATE', rho_vert=vert['length'], rho_caras=total['length'],
                    implementation_version=IMPLEMENTATION_VERSION,
                    rho_edge_min=face['length'], rho_vert_winner=vert, rho_caras_winner=total,
                    faces=faces, cones=cones, boundary_limits=limits, geometry_check=geometry_check,
                    unique_feature_points=len(self.points), geometric_vertices=len(self.hull),
                    duplicate_groups=[v for v in self.groups if len(v) > 1],
                    exact_membership_tolerance=0, near_face_alert=1e-10,
                    min_input_eigenvalue=float(self.input_eigenvalues[0]),
                    contrast_rounding_max=max(m['clipped'] for m in self.metric_cache.values()),
                    evaluations=self.evaluations, seconds=time.perf_counter()-self.start,
                    geometry_sha256=GEOMETRY_SHA256, global_optimum_certified=False)


def rho_borde_v2(M, f, **options):
    """Devuelve estimaciones separadas y trazables; ValueError ante input inválido.

    Un ganador vertex_limit describe el límite de un cono; attained=false se
    refiere a ese candidato, no prueba que no exista otro rayo que empate.
    """
    instrument = _Instrument(M, f, **options)
    try:
        return instrument.calculate()
    except BudgetExceeded as e:
        return dict(status='INCONCLUSIVE_BUDGET', reason=str(e), rho_vert=None, rho_caras=None,
                    evaluations=instrument.evaluations, seconds=time.perf_counter()-instrument.start,
                    partial=instrument.partial,
                    global_optimum_certified=False)
