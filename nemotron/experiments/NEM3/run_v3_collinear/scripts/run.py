"""NEM3 run_v3_collinear — Observables geométricos con dataset sintético colineal.

Implementación en Python puro (biblioteca estándar), sin dependencias externas.

Protocolo:
1. Genera dataset sintético con colinearidad entre características (induce modos débiles de Fisher).
2. Modelo lineal de regresión logística sin entrenamiento.
3. Familia no lineal de perspectivas (softmax de rasgos fijos, forma E12).
4. Para cada punto de la grid en el espacio de perspectivas (2D):
   - Calcular B(p), h(p) = B C B^T.
   - Calcular derivadas numéricas de h.
   - Construir conexión de Levi-Civita Γ.
   - Calcular tensor de curvatura R y curvatura de Gauss K.
5. Observables geométricos sobre el dominio:
   - Área A, energía E, energía media E_K, C_A = sqrt(E_K).
   - Concentración espacial Lambda_q para q in {0.25, 0.5, 0.75}.
   - Participación efectiva R_eff = E^2 / (A * ∫ K^4 dA).
6. Detecta modos débiles de Fisher (autovalor < tau).
7. Ejecuta para panel base y panel perturbado (epsilon = 0.2).

Uso:
    python3 scripts/run.py --output results/run_v1
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random

# ---------------------------------------------------------------------------
# Álgebra lineal en Python puro
# ---------------------------------------------------------------------------

def mat_mul(A, B):
    m, n = len(A), len(A[0])
    p = len(B[0])
    result = [[0.0] * p for _ in range(m)]
    for i in range(m):
        for k in range(n):
            aik = A[i][k]
            if aik == 0.0:
                continue
            for j in range(p):
                result[i][j] += aik * B[k][j]
    return result


def mat_transpose(A):
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]


def mat_eye(n):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def mat_inv2(A):
    a, b = A[0][0], A[0][1]
    c, d = A[1][0], A[1][1]
    det = a * d - b * c
    if abs(det) < 1e-14:
        raise ValueError("Matriz 2x2 singular")
    return [[d / det, -b / det], [-c / det, a / det]]


def mat_det2(A):
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def mat_add(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mat_sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mat_scale(A, s):
    return [[s * v for v in row] for row in A]


def vec_dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def vec_norm(u):
    return math.sqrt(sum(v * v for v in u))


# ---------------------------------------------------------------------------
# Modelo lineal sin entrenamiento
# ---------------------------------------------------------------------------

def build_linear_model(n_features, n_classes, seed=0):
    rng = random.Random(seed)
    W = [[rng.gauss(0, 1.0 / math.sqrt(n_features)) for _ in range(n_features)]
         for _ in range(n_classes)]
    b = [0.0] * n_classes
    return (W, b)


def forward_linear(params, x):
    W, b = params
    return [sum(W[i][k] * x[k] for k in range(len(x))) + b[i] for i in range(len(W))]


def softmax(logits):
    m = max(logits)
    exps = [math.exp(v - m) for v in logits]
    s = sum(exps)
    return [v / s for v in exps]


def flatten_params(params):
    W, b = params
    flat = []
    for row in W:
        flat.extend(row)
    flat.extend(b)
    return flat


def unflatten_params(flat, n_features, n_classes):
    W = []
    idx = 0
    for i in range(n_classes):
        W.append(list(flat[idx:idx + n_features]))
        idx += n_features
    b = list(flat[idx:idx + n_classes])
    idx += n_classes
    return (W, b)


def log_prob_grad_num(params, x, y, eps=1e-6, n_features=None, n_classes=None):
    flat = flatten_params(params)
    d = len(flat)
    grad = [0.0] * d

    def log_prob_from_flat(f):
        p = unflatten_params(f, n_features, n_classes)
        logits = forward_linear(p, x)
        probs = softmax(logits)
        return math.log(max(probs[y], 1e-300))

    for i in range(d):
        f_plus = flat[:]
        f_minus = flat[:]
        f_plus[i] += eps
        f_minus[i] -= eps
        lp_plus = log_prob_from_flat(f_plus)
        lp_minus = log_prob_from_flat(f_minus)
        grad[i] = (lp_plus - lp_minus) / (2.0 * eps)

    return grad


# ---------------------------------------------------------------------------
# Dataset sintético colineal
# ---------------------------------------------------------------------------

def build_collinear_panel(n_inputs, n_features, n_classes, seed=1):
    """Genera un dataset sintético con colinearidad estructurada.

    x2 = 0.95 * x1 + ruido
    x3 = 0.90 * x1 + 0.50 * x2 + ruido
    x4, x5 = ruido independiente

    Esto induce autovalores de Fisher cercanos a cero (modos débiles).
    """
    rng = random.Random(seed)
    xs = []
    ys = []
    for _ in range(n_inputs):
        x1 = rng.gauss(0, 1)
        x2 = 0.95 * x1 + rng.gauss(0, 0.1)
        x3 = 0.90 * x1 + 0.50 * x2 + rng.gauss(0, 0.1)
        x4 = rng.gauss(0, 1)
        x5 = rng.gauss(0, 1)
        xs.append([x1, x2, x3, x4, x5])
        ys.append(rng.randint(0, n_classes - 1))
    return xs, ys


def build_features(xs, seed=2):
    """Rasgos fijos f_n en R^2 para cada muestra (usados por la familia de perspectivas)."""
    rng = random.Random(seed)
    n_features = len(xs[0])
    W_feat = [[rng.gauss(0, 1) for _ in range(n_features)] for _ in range(2)]
    f_n = []
    for x in xs:
        f_n.append([sum(W_feat[a][k] * x[k] for k in range(n_features)) for a in range(2)])
    return f_n


# ---------------------------------------------------------------------------
# Familia de perspectivas y métrica h
# ---------------------------------------------------------------------------

def compute_a(f_n, p):
    scores = [vec_dot(p, f) for f in f_n]
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    s = sum(exps)
    return [v / s for v in exps]


def compute_B(params, xs, ys, f_n, p, n_features, n_classes):
    n_persp = len(p)
    d = len(flatten_params(params))
    n = len(xs)

    a = compute_a(f_n, p)
    mu = [0.0] * n_persp
    a_sum = sum(a)
    for aa in range(n_persp):
        mu[aa] = sum(a[k] * f_n[k][aa] for k in range(n)) / a_sum if a_sum > 0 else 0.0

    scores = []
    for x, y in zip(xs, ys):
        r = log_prob_grad_num(params, x, int(y),
                              n_features=n_features, n_classes=n_classes)
        scores.append(r)

    B = [[0.0] * d for _ in range(n_persp)]
    for aa in range(n_persp):
        for i in range(d):
            total = 0.0
            for k in range(n):
                total += a[k] * (f_n[k][aa] - mu[aa]) * scores[k][i]
            B[aa][i] = total
    return B


def compute_h(B, C):
    Bt = mat_transpose(B)
    BC = mat_mul(B, C)
    return mat_mul(BC, Bt)


# ---------------------------------------------------------------------------
# Curvatura (mismo método que NEM2/NEM3 run_v1)
# ---------------------------------------------------------------------------

def compute_all_dh_correct(h_func, p, eps=1e-5):
    n = 2
    dh = [[[0.0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        p_plus = list(p)
        p_minus = list(p)
        p_plus[a] += eps
        p_minus[a] -= eps
        h_plus = h_func(p_plus)
        h_minus = h_func(p_minus)
        for b in range(n):
            for c in range(n):
                dh[a][b][c] = (h_plus[b][c] - h_minus[b][c]) / (2.0 * eps)
    return dh


def compute_connection_correct(h, dh):
    n = 2
    h_inv = mat_inv2(h)
    Gamma = [[[0.0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                total = 0.0
                for d_ in range(n):
                    term = (dh[b][c][d_] + dh[c][b][d_] - dh[d_][b][c])
                    total += h_inv[a][d_] * term
                Gamma[a][b][c] = 0.5 * total
    return Gamma


def compute_dGamma_correct(h_func, p, eps=1e-5):
    n = 2
    dGamma = [[[[0.0] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for c in range(n):
        p_plus = list(p)
        p_minus = list(p)
        p_plus[c] += eps
        p_minus[c] -= eps

        h_plus = h_func(p_plus)
        dh_plus = compute_all_dh_correct(h_func, p_plus, eps)
        Gamma_plus = compute_connection_correct(h_plus, dh_plus)

        h_minus = h_func(p_minus)
        dh_minus = compute_all_dh_correct(h_func, p_minus, eps)
        Gamma_minus = compute_connection_correct(h_minus, dh_minus)

        for a in range(n):
            for b in range(n):
                for d_ in range(n):
                    dGamma[c][a][b][d_] = (Gamma_plus[a][b][d_] - Gamma_minus[a][b][d_]) / (2.0 * eps)
    return dGamma


def compute_K(h, Gamma, dGamma):
    n = 2
    R1212 = 0.0
    for e in range(n):
        term1 = dGamma[0][e][1][1]
        term2 = dGamma[1][e][1][0]
        term3 = 0.0
        term4 = 0.0
        for m in range(n):
            term3 += Gamma[m][1][1] * Gamma[e][0][m]
            term4 += Gamma[m][1][0] * Gamma[e][1][m]
        R_e_101 = term1 - term2 + term3 - term4
        R1212 += h[0][e] * R_e_101

    det_h = mat_det2(h)
    K = R1212 / det_h if abs(det_h) > 1e-14 else float('nan')
    return K, det_h, R1212


# ---------------------------------------------------------------------------
# Observables geométricos
# ---------------------------------------------------------------------------

def compute_observables(grid_points, h_func, K_func, step):
    n = len(grid_points)
    dA_list = []
    e_list = []
    K_list = []
    det_h_list = []
    spd_list = []

    for p in grid_points:
        try:
            h = h_func(p)
            det_h = mat_det2(h)
            if abs(det_h) < 1e-12:
                dA_list.append(0.0)
                e_list.append(0.0)
                K_list.append(float('nan'))
                det_h_list.append(det_h)
                spd_list.append(False)
                continue
            dA = math.sqrt(det_h) * step * step
            K = K_func(p)
            e = K * K if K == K else 0.0
            dA_list.append(dA)
            e_list.append(e)
            K_list.append(K)
            det_h_list.append(det_h)
            spd_list.append(True)
        except Exception:
            dA_list.append(0.0)
            e_list.append(0.0)
            K_list.append(float('nan'))
            det_h_list.append(float('nan'))
            spd_list.append(False)

    A = sum(dA_list)
    E = sum(e * dA for e, dA in zip(e_list, dA_list))
    E2 = sum(e * e * dA for e, dA in zip(e_list, dA_list))

    E_K = E / A if A > 0 else float('nan')
    C_A = math.sqrt(E_K) if E_K == E_K and E_K >= 0 else float('nan')
    R_eff = (E * E) / (A * E2) if A > 0 and E2 > 0 else float('nan')

    # Concentración espacial Lambda_q
    indexed = list(zip(e_list, dA_list, spd_list))
    indexed.sort(key=lambda x: x[0], reverse=True)

    lambda_q = {}
    for q in [0.25, 0.5, 0.75]:
        target_area = q * A
        acc_area = 0.0
        acc_e = 0.0
        for e_i, dA_i, spd_i in indexed:
            if not spd_i:
                continue
            if acc_area + dA_i <= target_area:
                acc_area += dA_i
                acc_e += e_i * dA_i
            else:
                remaining = target_area - acc_area
                if remaining > 0:
                    frac = remaining / dA_i
                    acc_area += remaining
                    acc_e += e_i * remaining
                break
        lambda_q[q] = acc_e / E if E > 0 else float('nan')

    return {
        "A": A,
        "E": E,
        "E_K": E_K,
        "C_A": C_A,
        "R_eff": R_eff,
        "lambda_q": lambda_q,
        "n_points": n,
        "n_spd": sum(1 for s in spd_list if s),
        "points": [
            {
                "p1": grid_points[i][0],
                "p2": grid_points[i][1],
                "K": K_list[i],
                "e": e_list[i],
                "dA": dA_list[i],
                "det_h": det_h_list[i],
                "spd": spd_list[i],
            }
            for i in range(n)
        ],
    }


# ---------------------------------------------------------------------------
# Fisher y modos débiles
# ---------------------------------------------------------------------------

def fisher_matrix(params, xs, ys, n_features, n_classes):
    scores = []
    for x, y in zip(xs, ys):
        s = log_prob_grad_num(params, x, int(y),
                              n_features=n_features, n_classes=n_classes)
        scores.append(s)
    n = len(scores)
    d = len(scores[0])
    F = [[0.0] * d for _ in range(d)]
    for i in range(d):
        for j in range(d):
            F[i][j] = sum(scores[k][i] * scores[k][j] for k in range(n)) / n
    return F


def jacobi_eigen_symmetric(A, tol=1e-12, max_iter=100):
    n = len(A)
    a = [row[:] for row in A]
    v = mat_eye(n)
    for _ in range(max_iter):
        max_off = 0.0
        p, q = 0, 1
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > max_off:
                    max_off = abs(a[i][j])
                    p, q = i, j
        if max_off < tol:
            break
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        if abs(apq) < 1e-15:
            continue
        theta = 0.5 * math.atan2(2.0 * apq, aqq - app)
        c = math.cos(theta)
        s = math.sin(theta)
        for k in range(n):
            if k != p and k != q:
                akp = a[k][p]
                akq = a[k][q]
                a[k][p] = c * akp - s * akq
                a[p][k] = a[k][p]
                a[k][q] = s * akp + c * akq
                a[q][k] = a[k][q]
        app_new = c * c * app + s * s * aqq - 2.0 * c * s * apq
        aqq_new = s * s * app + c * c * aqq + 2.0 * c * s * apq
        a[p][p] = app_new
        a[q][q] = aqq_new
        a[p][q] = 0.0
        a[q][p] = 0.0
        for k in range(n):
            vkp = v[k][p]
            vkq = v[k][q]
            v[k][p] = c * vkp - s * vkq
            v[k][q] = s * vkp + c * vkq
    eigenvalues = [a[i][i] for i in range(n)]
    order = sorted(range(n), key=lambda i: eigenvalues[i], reverse=True)
    eigenvalues = [eigenvalues[i] for i in order]
    eigenvectors = [[v[k][i] for k in range(n)] for i in order]
    return eigenvalues, eigenvectors


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------

def run_protocol(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Configuración congelada
    n_features = 5
    n_classes = 3
    n_inputs = 50
    n_persp = 2
    epsilon_fd = 1e-5
    epsilon_panel = 0.2
    spd_threshold = 1e-12
    tau_weak = 1e-6
    seed_net = 0
    seed_panel = 1
    seed_feat = 2

    grid_size = 9
    p_range = [-1.0, 1.0]
    step = (p_range[1] - p_range[0]) / (grid_size - 1)
    p_values = [p_range[0] + i * step for i in range(grid_size)]
    grid_points = [(p1, p2) for p1 in p_values for p2 in p_values]

    # 1. Modelo lineal sin entrenamiento
    params = build_linear_model(n_features, n_classes, seed=seed_net)
    d = len(flatten_params(params))

    # 2. Paneles: base (colineal) y perturbado
    xs_base, ys_base = build_collinear_panel(n_inputs, n_features, n_classes, seed=seed_panel)
    rng_pert = random.Random(seed_panel + 100)
    xs_pert = []
    for x in xs_base:
        xs_pert.append([x[i] + rng_pert.gauss(0, 0.1) for i in range(len(x))])
    ys_pert = list(ys_base)

    # 3. Rasgos fijos f_n en R^2
    f_n = build_features(xs_base, seed=seed_feat)

    # 4. Cométrica C (identidad dxd)
    C = mat_eye(d)

    def make_h_func(xs, ys):
        def h_func(p):
            B = compute_B(params, xs, ys, f_n, p, n_features, n_classes)
            return compute_h(B, C)
        return h_func

    def make_K_func(h_func):
        def K_func(p):
            h = h_func(p)
            dh = compute_all_dh_correct(h_func, p, epsilon_fd)
            Gamma = compute_connection_correct(h, dh)
            dGamma = compute_dGamma_correct(h_func, p, epsilon_fd)
            K, det_h, R1212 = compute_K(h, Gamma, dGamma)
            return K
        return K_func

    # 5. Fisher y modos débiles para panel base
    F_base = fisher_matrix(params, xs_base, ys_base, n_features, n_classes)
    eigvals_base, _ = jacobi_eigen_symmetric(F_base)
    weak_modes_base = [i for i, w in enumerate(eigvals_base) if w < tau_weak]

    # 6. Fisher y modos débiles para panel perturbado
    F_pert = fisher_matrix(params, xs_pert, ys_pert, n_features, n_classes)
    eigvals_pert, _ = jacobi_eigen_symmetric(F_pert)
    weak_modes_pert = [i for i, w in enumerate(eigvals_pert) if w < tau_weak]

    # 7. Ejecutar observables para panel base
    h_base = make_h_func(xs_base, ys_base)
    K_base = make_K_func(h_base)
    obs_base = compute_observables(grid_points, h_base, K_base, step)

    # 8. Ejecutar observables para panel perturbado
    h_pert = make_h_func(xs_pert, ys_pert)
    K_pert = make_K_func(h_pert)
    obs_pert = compute_observables(grid_points, h_pert, K_pert, step)

    # 9. Guardar resultados
    def rel_change(base_val, pert_val):
        if base_val == 0 or base_val != base_val:
            return None
        return (pert_val - base_val) / abs(base_val)

    summary = {
        "experiment": "NEM3",
        "run": "run_v3_collinear",
        "description": "Observables geometricos con dataset sintético colineal (modos debiles de Fisher)",
        "config": {
            "n_features": n_features,
            "n_classes": n_classes,
            "n_inputs": n_inputs,
            "n_params": d,
            "n_persp": n_persp,
            "grid_size": grid_size,
            "p_range": p_range,
            "step": step,
            "epsilon_fd": epsilon_fd,
            "epsilon_panel": epsilon_panel,
            "spd_threshold": spd_threshold,
            "tau_weak": tau_weak,
            "q_values": [0.25, 0.5, 0.75],
            "dataset": "synthetic_collinear",
        },
        "fisher_base": {
            "max_eigenvalue": eigvals_base[0],
            "min_eigenvalue": eigvals_base[-1],
            "n_weak_modes": len(weak_modes_base),
            "weak_eigenvalues": [w for w in eigvals_base if w < tau_weak],
        },
        "fisher_perturbed": {
            "max_eigenvalue": eigvals_pert[0],
            "min_eigenvalue": eigvals_pert[-1],
            "n_weak_modes": len(weak_modes_pert),
            "weak_eigenvalues": [w for w in eigvals_pert if w < tau_weak],
        },
        "panel_base": {
            "A": obs_base["A"],
            "E": obs_base["E"],
            "E_K": obs_base["E_K"],
            "C_A": obs_base["C_A"],
            "R_eff": obs_base["R_eff"],
            "lambda_q": obs_base["lambda_q"],
            "n_points": obs_base["n_points"],
            "n_spd": obs_base["n_spd"],
        },
        "panel_perturbed": {
            "A": obs_pert["A"],
            "E": obs_pert["E"],
            "E_K": obs_pert["E_K"],
            "C_A": obs_pert["C_A"],
            "R_eff": obs_pert["R_eff"],
            "lambda_q": obs_pert["lambda_q"],
            "n_points": obs_pert["n_points"],
            "n_spd": obs_pert["n_spd"],
        },
        "changes_relative": {
            "A": rel_change(obs_base["A"], obs_pert["A"]),
            "E": rel_change(obs_base["E"], obs_pert["E"]),
            "E_K": rel_change(obs_base["E_K"], obs_pert["E_K"]),
            "C_A": rel_change(obs_base["C_A"], obs_pert["C_A"]),
            "R_eff": rel_change(obs_base["R_eff"], obs_pert["R_eff"]),
            "lambda_q": {
                str(q): rel_change(obs_base["lambda_q"][q], obs_pert["lambda_q"][q])
                for q in [0.25, 0.5, 0.75]
            },
        },
    }

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # CSV de observables por punto (panel base)
    csv_path = os.path.join(output_dir, "observables.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "p1", "p2", "K", "e", "dA", "det_h", "spd",
        ])
        for pt in obs_base["points"]:
            writer.writerow([
                pt["p1"], pt["p2"],
                pt["K"] if pt["K"] == pt["K"] else "",
                pt["e"],
                pt["dA"],
                pt["det_h"] if pt["det_h"] == pt["det_h"] else "",
                pt["spd"],
            ])

    # CSV de resumen
    checks_path = os.path.join(output_dir, "checks.csv")
    with open(checks_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["observable", "panel_base", "panel_perturbed", "relative_change"])
        for key in ["A", "E", "E_K", "C_A", "R_eff"]:
            writer.writerow([
                key,
                summary["panel_base"][key],
                summary["panel_perturbed"][key],
                summary["changes_relative"][key],
            ])
        for q in [0.25, 0.5, 0.75]:
            writer.writerow([
                f"lambda_q_{q}",
                summary["panel_base"]["lambda_q"][q],
                summary["panel_perturbed"]["lambda_q"][q],
                summary["changes_relative"]["lambda_q"][str(q)],
            ])
        writer.writerow([])
        writer.writerow(["fisher_metric", "panel_base", "panel_perturbed"])
        writer.writerow(["max_eigenvalue", summary["fisher_base"]["max_eigenvalue"],
                         summary["fisher_perturbed"]["max_eigenvalue"]])
        writer.writerow(["min_eigenvalue", summary["fisher_base"]["min_eigenvalue"],
                         summary["fisher_perturbed"]["min_eigenvalue"]])
        writer.writerow(["n_weak_modes", summary["fisher_base"]["n_weak_modes"],
                         summary["fisher_perturbed"]["n_weak_modes"]])

    print(f"Resultados guardados en {output_dir}")
    print(f"Resumen: {summary_path}")
    print(f"Observables: {csv_path}")
    print(f"Checks: {checks_path}")
    print(f"Fisher base: max_eig={eigvals_base[0]:.6e}, min_eig={eigvals_base[-1]:.6e}, n_weak={len(weak_modes_base)}")
    print(f"Fisher perturbado: max_eig={eigvals_pert[0]:.6e}, min_eig={eigvals_pert[-1]:.6e}, n_weak={len(weak_modes_pert)}")
    print(f"Panel base: A={obs_base['A']:.6e}, E_K={obs_base['E_K']:.6e}, C_A={obs_base['C_A']:.6e}, R_eff={obs_base['R_eff']:.6e}")
    print(f"Panel perturbado: A={obs_pert['A']:.6e}, E_K={obs_pert['E_K']:.6e}, C_A={obs_pert['C_A']:.6e}, R_eff={obs_pert['R_eff']:.6e}")
    print(f"Lambda_q base: { {q: round(obs_base['lambda_q'][q], 4) for q in [0.25, 0.5, 0.75]} }")
    print(f"Puntos SPD: {obs_base['n_spd']}/{obs_base['n_points']}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="NEM3 run_v3_collinear — observables geometricos con dataset colineal")
    parser.add_argument("--output", required=True, help="Directorio de salida para resultados")
    args = parser.parse_args()
    return run_protocol(args.output)


if __name__ == "__main__":
    import sys
    sys.exit(main())
