"""NEM2 — Curvatura y holonomía en el espacio de perspectivas.

Implementación en Python puro (biblioteca estándar), sin dependencias externas.

Protocolo:
1. Modelo lineal de regresión logística sin entrenamiento.
2. Familia no lineal de perspectivas (softmax de rasgos fijos, forma E12).
3. Para cada punto de la grid en el espacio de perspectivas (2D):
   - Calcular B(p), h(p) = B C B^T.
   - Calcular derivadas numéricas de h.
   - Construir conexión de Levi-Civita Γ.
   - Calcular tensor de curvatura R y curvatura de Gauss K.
4. Holonomía: transporte paralelo alrededor de lazo cuadrado pequeño.
5. Comparar θ_hol con K(p0) * delta^2.

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
    """Inversa de una matriz 2x2."""
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
# Modelo lineal (regresión logística multiclase) sin entrenamiento
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
# Panel y datos
# ---------------------------------------------------------------------------

def build_synthetic_panel(n_inputs, n_features, n_classes, seed=1):
    rng = random.Random(seed)
    xs = [[rng.gauss(0, 1) for _ in range(n_features)] for _ in range(n_inputs)]
    ys = [rng.randint(0, n_classes - 1) for _ in range(n_inputs)]
    return xs, ys


def build_features(xs, seed=2):
    """Rasgos fijos f_n en R^2 para cada muestra (usados por la familia de perspectivas)."""
    rng = random.Random(seed)
    # Usar una proyección aleatoria de las entradas a R^2
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
    """Softmax de p · f_n para cada muestra n."""
    scores = [vec_dot(p, f) for f in f_n]
    m = max(scores)
    exps = [math.exp(s - m) for s in scores]
    s = sum(exps)
    return [v / s for v in exps]


def compute_B(params, xs, ys, f_n, p, n_features, n_classes):
    """Calcula B(p) para la familia no lineal.

    B_{ai} = Σ_n a_n (f_{na} - μ_a) (r_n)_i
    """
    n_persp = len(p)
    d = len(flatten_params(params))
    n = len(xs)

    a = compute_a(f_n, p)  # lista de longitud n
    # μ_a = Σ_n a_n f_{na}
    mu = [0.0] * n_persp
    a_sum = sum(a)
    for aa in range(n_persp):
        mu[aa] = sum(a[k] * f_n[k][aa] for k in range(n)) / a_sum if a_sum > 0 else 0.0

    # Scores r_n para cada muestra
    scores = []
    for x, y in zip(xs, ys):
        r = log_prob_grad_num(params, x, int(y),
                              n_features=n_features, n_classes=n_classes)
        scores.append(r)

    # B_{ai} = Σ_n a_n (f_{na} - μ_a) (r_n)_i
    B = [[0.0] * d for _ in range(n_persp)]
    for aa in range(n_persp):
        for i in range(d):
            total = 0.0
            for k in range(n):
                total += a[k] * (f_n[k][aa] - mu[aa]) * scores[k][i]
            B[aa][i] = total
    return B


def compute_h(B, C):
    """h = B C B^T"""
    Bt = mat_transpose(B)
    BC = mat_mul(B, C)
    return mat_mul(BC, Bt)


# ---------------------------------------------------------------------------
# Curvatura y holonomía
# ---------------------------------------------------------------------------

def compute_connection(h, dh, eps=1e-5):
    """Γ^a_bc = 1/2 * h^{ad} * (∂_b h_cd + ∂_c h_bd - ∂_d h_bc)

    h es 2x2, dh[a][b][c][d] = ∂_a h_{cd} (derivada de h_cd respecto a p^a).
    """
    n = 2
    h_inv = mat_inv2(h)
    Gamma = [[[0.0] * n for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            for c in range(n):
                total = 0.0
                for d_ in range(n):
                    # ∂_b h_cd + ∂_c h_bd - ∂_d h_bc
                    term = (dh[b][c][d_] + dh[c][b][d_] - dh[d_][b][c])
                    total += h_inv[a][d_] * term
                Gamma[a][b][c] = 0.5 * total
    return Gamma


def compute_curvature(h, Gamma, dGamma, eps=1e-5):
    """R^a_bcd = ∂_c Γ^a_bd - ∂_d Γ^a_bc + Γ^e_bd Γ^a_ec - Γ^e_bc Γ^a_ed

    dGamma[c][a][b][d] = ∂_c Γ^a_bd
    Devuelve R_{1212} y det(h).
    """
    n = 2
    R1212 = 0.0
    # R^a_{bcd} con a=1, b=2, c=1, d=2 (índices 0-based: a=0? no, usamos 1,2 -> 0,1)
    # Queremos R_{1212} = h_{1e} R^e_{212}
    # En 0-based: R_{0101} = h_{0e} R^e_{101}
    for e in range(n):
        # R^e_{101} = ∂_0 Γ^e_{11} - ∂_1 Γ^e_{10} + Γ^m_{11} Γ^e_{0m} - Γ^m_{10} Γ^e_{1m}
        # dGamma[c][a][b][d] = ∂_c Γ^a_bd
        # ∂_0 Γ^e_{11} = dGamma[0][e][1][1]
        # ∂_1 Γ^e_{10} = dGamma[1][e][1][0]
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


def compute_dGamma(h_func, p, eps=1e-5):
    """Calcula dGamma[c][a][b][d] = ∂_c Γ^a_bd por diferencias finitas."""
    n = 2
    dGamma = [[[[0.0] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for c in range(n):
        p_plus = list(p)
        p_minus = list(p)
        p_plus[c] += eps
        p_minus[c] -= eps
        h_plus = h_func(p_plus)
        h_minus = h_func(p_minus)
        # dh/dp^c
        dh_c = mat_sub(h_plus, h_minus)
        dh_c = mat_scale(dh_c, 1.0 / (2.0 * eps))

        # Necesitamos dh en todas las direcciones para computar Γ en p+eps*e_c y p-eps*e_c
        # Pero para dGamma necesitamos ∂_c Γ, que requiere Γ en p±eps*e_c
        # Γ depende de h y de ∂ h, así que necesitamos ∂h en p±eps*e_c también
        # Esto se vuelve recursivo; aproximamos ∂_c Γ ≈ (Γ(p+eps e_c) - Γ(p-eps e_c)) / (2 eps)
        # Para eso necesitamos computar Γ en p+eps e_c y p-eps e_c

        # Computar Γ en p_plus
        dh_plus = compute_all_dh(h_func, p_plus, eps)
        Gamma_plus = compute_connection(h_plus, dh_plus, eps)

        # Computar Γ en p_minus
        dh_minus = compute_all_dh(h_func, p_minus, eps)
        Gamma_minus = compute_connection(h_minus, dh_minus, eps)

        for a in range(n):
            for b in range(n):
                for d_ in range(n):
                    dGamma[c][a][b][d_] = (Gamma_plus[a][b][d_] - Gamma_minus[a][b][d_]) / (2.0 * eps)

    return dGamma


def compute_all_dh(h_func, p, eps=1e-5):
    """Devuelve dh[a][b][c][d] = ∂_a h_{cd} para todas las direcciones a."""
    n = 2
    dh = [[[[0.0] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for a in range(n):
        p_plus = list(p)
        p_minus = list(p)
        p_plus[a] += eps
        p_minus[a] -= eps
        h_plus = h_func(p_plus)
        h_minus = h_func(p_minus)
        for b in range(n):
            for c in range(n):
                dh[a][b][c][d_] = 0.0  # placeholder, se remplaza abajo
        for i in range(n):
            for j in range(n):
                dh[a][i][j][j] = 0.0
        # Rellenar correctamente:
        for b in range(n):
            for c in range(n):
                dh[a][b][c][0] = (h_plus[b][c] - h_minus[b][c]) / (2.0 * eps) if False else 0.0
    # Reescribir de forma correcta y simple:
    dh = [[[[0.0] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for a in range(n):
        p_plus = list(p)
        p_minus = list(p)
        p_plus[a] += eps
        p_minus[a] -= eps
        h_plus = h_func(p_plus)
        h_minus = h_func(p_minus)
        for b in range(n):
            for c in range(n):
                dh[a][b][c][0] = 0.0
                dh[a][b][c][1] = 0.0
        # dh[a][b][c][d_] no tiene sentido con 4 índices para ∂_a h_{bc}
        # Corregir: dh[a][b][c] = ∂_a h_{bc}
    return dh


def compute_all_dh_correct(h_func, p, eps=1e-5):
    """Devuelve dh[a][b][c] = ∂_a h_{bc} (3 índices)."""
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


def compute_connection_correct(h, dh, eps=1e-5):
    """Γ^a_bc = 1/2 * h^{ad} * (∂_b h_cd + ∂_c h_bd - ∂_d h_bc)

    dh[a][b][c] = ∂_a h_{bc}
    """
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
    """dGamma[c][a][b][d] = ∂_c Γ^a_{bd} por diferencias finitas de Γ."""
    n = 2
    dGamma = [[[[0.0] * n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for c in range(n):
        p_plus = list(p)
        p_minus = list(p)
        p_plus[c] += eps
        p_minus[c] -= eps

        h_plus = h_func(p_plus)
        dh_plus = compute_all_dh_correct(h_func, p_plus, eps)
        Gamma_plus = compute_connection_correct(h_plus, dh_plus, eps)

        h_minus = h_func(p_minus)
        dh_minus = compute_all_dh_correct(h_func, p_minus, eps)
        Gamma_minus = compute_connection_correct(h_minus, dh_minus, eps)

        for a in range(n):
            for b in range(n):
                for d_ in range(n):
                    dGamma[c][a][b][d_] = (Gamma_plus[a][b][d_] - Gamma_minus[a][b][d_]) / (2.0 * eps)
    return dGamma


def parallel_transport(h_func, Gamma_func, p_start, v_start, path, eps=1e-5, n_steps=20):
    """Transporta un vector v a lo largo de un path dado por lista de puntos p.

    dv/dt + Γ(v, dp/dt) = 0 -> v_{k+1} = v_k - Γ(p_k) v_k Δp
    """
    v = list(v_start)
    for k in range(len(path) - 1):
        p0 = path[k]
        p1 = path[k + 1]
        dp = [p1[i] - p0[i] for i in range(len(p0))]

        h = h_func(p0)
        dh = compute_all_dh_correct(h_func, p0, eps)
        Gamma = compute_connection_correct(h, dh, eps)

        # Δv^a = - Γ^a_bc v^b dp^c
        dv = [0.0] * len(v)
        for a in range(len(v)):
            for b in range(len(v)):
                for c in range(len(dp)):
                    dv[a] -= Gamma[a][b][c] * v[b] * dp[c]
        v = [v[i] + dv[i] for i in range(len(v))]

    return v


def compute_holonomy(h_func, p_center, delta, eps=1e-5, n_steps=20):
    """Calcula holonomía alrededor de un cuadrado de lado delta centrado en p_center.

    Devuelve el ángulo de rotación en radianes.
    """
    x0, y0 = p_center
    # Esquinas del cuadrado
    p_bl = [x0 - delta / 2, y0 - delta / 2]
    p_br = [x0 + delta / 2, y0 - delta / 2]
    p_tr = [x0 + delta / 2, y0 + delta / 2]
    p_tl = [x0 - delta / 2, y0 + delta / 2]

    # Path: bl -> br -> tr -> tl -> bl
    path = [p_bl, p_br, p_tr, p_tl, p_bl]

    v_start = [1.0, 0.0]
    v_end = parallel_transport(h_func, None, p_bl, v_start, path, eps=eps, n_steps=n_steps)

    # Ángulo entre v_start y v_end
    dot = vec_dot(v_start, v_end)
    n1 = vec_norm(v_start)
    n2 = vec_norm(v_end)
    if n1 == 0 or n2 == 0:
        return float('nan')
    cos_theta = max(-1.0, min(1.0, dot / (n1 * n2)))
    theta = math.acos(cos_theta)
    return theta


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------

def run_protocol(output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # Configuración congelada (DESIGN_FROZEN / mathematical_spec)
    n_features = 3
    n_classes = 2
    n_inputs = 15
    n_persp = 2
    epsilon_fd = 1e-5
    delta_values = [0.1, 0.2]
    n_steps_transport = 20
    spd_threshold = 1e-12
    seed_net = 0
    seed_panel = 1
    seed_feat = 2

    # Grid de perspectivas
    grid_size = 9
    p_range = [-1.0, 1.0]
    step = (p_range[1] - p_range[0]) / (grid_size - 1)
    p_values = [p_range[0] + i * step for i in range(grid_size)]

    # 1. Modelo lineal sin entrenamiento
    params = build_linear_model(n_features, n_classes, seed=seed_net)
    d = len(flatten_params(params))

    # 2. Panel sintético
    xs, ys = build_synthetic_panel(n_inputs, n_features, n_classes, seed=seed_panel)

    # 3. Rasgos fijos f_n en R^2
    f_n = build_features(xs, seed=seed_feat)

    # 4. Cométrica C (identidad dxd)
    C = mat_eye(d)

    # 5. Función h(p)
    def h_func(p):
        B = compute_B(params, xs, ys, f_n, p, n_features, n_classes)
        return compute_h(B, C)

    # 6. Recorrer grid y calcular K
    curvature_results = []
    holonomy_results = []

    for i, p1 in enumerate(p_values):
        for j, p2 in enumerate(p_values):
            p = [p1, p2]
            try:
                h = h_func(p)
                det_h = mat_det2(h)
                if abs(det_h) < spd_threshold:
                    curvature_results.append({
                        "p1": round(p1, 6),
                        "p2": round(p2, 6),
                        "det_h": det_h,
                        "K": None,
                        "R1212": None,
                        "spd": False,
                    })
                    continue

                dh = compute_all_dh_correct(h_func, p, epsilon_fd)
                Gamma = compute_connection_correct(h, dh, epsilon_fd)
                dGamma = compute_dGamma_correct(h_func, p, epsilon_fd)
                K, det_h_val, R1212 = compute_curvature(h, Gamma, dGamma, epsilon_fd)

                curvature_results.append({
                    "p1": round(p1, 6),
                    "p2": round(p2, 6),
                    "det_h": det_h_val,
                    "K": K,
                    "R1212": R1212,
                    "spd": True,
                })
            except Exception as exc:
                curvature_results.append({
                    "p1": round(p1, 6),
                    "p2": round(p2, 6),
                    "det_h": None,
                    "K": None,
                    "R1212": None,
                    "spd": False,
                    "error": str(exc)[:100],
                })

    # 7. Holonomía en puntos seleccionados (centro y algunas esquinas)
    holonomy_points = [
        [0.0, 0.0],
        [0.5, 0.5],
        [-0.5, -0.5],
    ]

    for p_center in holonomy_points:
        for delta in delta_values:
            try:
                theta_hol = compute_holonomy(h_func, p_center, delta,
                                             eps=epsilon_fd, n_steps=n_steps_transport)
                # K en el centro
                h_center = h_func(p_center)
                dh_center = compute_all_dh_correct(h_func, p_center, epsilon_fd)
                Gamma_center = compute_connection_correct(h_center, dh_center, epsilon_fd)
                dGamma_center = compute_dGamma_correct(h_func, p_center, epsilon_fd)
                K_center, det_h_center, R1212_center = compute_curvature(
                    h_center, Gamma_center, dGamma_center, epsilon_fd)

                expected = K_center * delta * delta if K_center is not None else None

                holonomy_results.append({
                    "p1": p_center[0],
                    "p2": p_center[1],
                    "delta": delta,
                    "theta_hol": theta_hol,
                    "K_center": K_center,
                    "expected_K_delta2": expected,
                    "diff": (theta_hol - expected) if (expected is not None and theta_hol is not None) else None,
                })
            except Exception as exc:
                holonomy_results.append({
                    "p1": p_center[0],
                    "p2": p_center[1],
                    "delta": delta,
                    "theta_hol": None,
                    "K_center": None,
                    "expected_K_delta2": None,
                    "diff": None,
                    "error": str(exc)[:100],
                })

    # 8. Guardar resultados
    summary = {
        "experiment": "NEM2",
        "description": "Curvatura y holonomía en el espacio de perspectivas",
        "config": {
            "n_features": n_features,
            "n_classes": n_classes,
            "n_inputs": n_inputs,
            "n_params": d,
            "n_persp": n_persp,
            "grid_size": grid_size,
            "p_range": p_range,
            "epsilon_fd": epsilon_fd,
            "delta_values": delta_values,
            "n_steps_transport": n_steps_transport,
            "spd_threshold": spd_threshold,
        },
        "curvature_grid": curvature_results,
        "holonomy": holonomy_results,
    }

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # CSV de curvatura
    csv_path = os.path.join(output_dir, "curvature_grid.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["p1", "p2", "det_h", "K", "R1212", "spd"])
        for r in curvature_results:
            writer.writerow([
                r["p1"], r["p2"],
                r["det_h"] if r["det_h"] is not None else "",
                r["K"] if r["K"] is not None else "",
                r["R1212"] if r["R1212"] is not None else "",
                r["spd"],
            ])

    # CSV de holonomía
    holo_csv_path = os.path.join(output_dir, "holonomy.csv")
    with open(holo_csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["p1", "p2", "delta", "theta_hol", "K_center", "expected_K_delta2", "diff"])
        for r in holonomy_results:
            writer.writerow([
                r["p1"], r["p2"], r["delta"],
                r["theta_hol"] if r["theta_hol"] is not None else "",
                r["K_center"] if r["K_center"] is not None else "",
                r["expected_K_delta2"] if r["expected_K_delta2"] is not None else "",
                r["diff"] if r["diff"] is not None else "",
            ])

    print(f"Resultados guardados en {output_dir}")
    print(f"Resumen: {summary_path}")
    print(f"Curvatura: {csv_path}")
    print(f"Holonomía: {holo_csv_path}")
    spd_count = sum(1 for r in curvature_results if r["spd"])
    print(f"Puntos SPD: {spd_count}/{len(curvature_results)}")
    K_vals = [r["K"] for r in curvature_results if r["K"] is not None]
    if K_vals:
        print(f"K rango: [{min(K_vals):.6e}, {max(K_vals):.6e}]")
    holo_count = sum(1 for r in holonomy_results if r["theta_hol"] is not None)
    print(f"Holonomía calculada: {holo_count}/{len(holonomy_results)}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="NEM2 — curvatura y holonomía")
    parser.add_argument("--output", required=True, help="Directorio de salida para resultados")
    args = parser.parse_args()
    return run_protocol(args.output)


if __name__ == "__main__":
    import sys
    sys.exit(main())
