"""NEM1 — Ejecución del protocolo de estabilidad de la métrica de perspectivas.

Implementación en Python puro (biblioteca estándar), sin dependencias externas.

Protocolo:
1. Red lineal pequeña sin entrenamiento (regresión logística multiclase).
2. Panel base mu0 y familia de perspectivas {p_a}.
3. Paneles perturbados mu_epsilon = (1-eps)*mu0 + eps*delta_mu.
4. Modos debiles de Fisher (autovalores < tau, algoritmo de Jacobi).
5. Medir variacion de h = B C B^T y distancia SPD.
6. Correlacionar variacion con componente sobre el nucleo aproximado de Fisher.

Datasets soportados:
- synthetic: red 4-4-3 con entradas aleatorias (run_v1).
- wine: dataset Wine de UCI (13 características, 3 clases) sin entrenamiento.

Uso:
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/run.py --output results/run_v1 --dataset synthetic
    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 scripts/run.py --output results/run_v2_wine --dataset wine
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import urllib.request

# ---------------------------------------------------------------------------
# Descarga del dataset Wine (UCI) si no hay disponible localmente
# ---------------------------------------------------------------------------

WINE_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/wine/wine.data"


def load_wine_dataset():
    """Carga el dataset Wine de UCI.

    Formato wine.data: clase, alcohol, malic_acid, ash, alcalinity_of_ash,
    magnesium, total_phenols, flavanoids, nonflavanoid_phenols, proanthocyanins,
    color_intensity, hue, od280/od315, proline.

    Devuelve (xs, ys) con xs lista de listas de floats y ys lista de ints (0..2).
    """
    try:
        with urllib.request.urlopen(WINE_URL, timeout=20) as resp:
            data = resp.read().decode("utf-8")
    except Exception as exc:
        raise RuntimeError(f"No se pudo descargar Wine desde UCI: {exc}")

    xs = []
    ys = []
    for line in data.strip().splitlines():
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) != 14:
            continue
        cls = int(parts[0]) - 1  # clases 1,2,3 -> 0,1,2
        feats = [float(p) for p in parts[1:]]
        xs.append(feats)
        ys.append(cls)
    return xs, ys


# ---------------------------------------------------------------------------
# Álgebra lineal en Python puro
# ---------------------------------------------------------------------------

def mat_mul(A, B):
    """Multiplicación de matrices: A (m×n) × B (n×p) -> (m×p)."""
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


def mat_inv(A):
    n = len(A)
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(A)]
    for col in range(n):
        max_row = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[max_row][col]) < 1e-14:
            raise ValueError(f"Matriz singular en columna {col}")
        aug[col], aug[max_row] = aug[max_row], aug[col]
        piv = aug[col][col]
        aug[col] = [v / piv for v in aug[col]]
        for r in range(n):
            if r != col:
                factor = aug[r][col]
                aug[r] = [a - factor * b for a, b in zip(aug[r], aug[col])]
    return [row[n:] for row in aug]


def mat_add(A, B):
    return [[a + b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mat_sub(A, B):
    return [[a - b for a, b in zip(ra, rb)] for ra, rb in zip(A, B)]


def mat_scale(A, s):
    return [[s * v for v in row] for row in A]


def mat_fro_norm(A):
    return math.sqrt(sum(v * v for row in A for v in row))


def vec_dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def jacobi_eigen_symmetric(A, tol=1e-12, max_iter=100):
    """Valores y vectores propios de una matriz simétrica (algoritmo de Jacobi)."""
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
# Modelo lineal (regresión logística multiclase) sin entrenamiento
# ---------------------------------------------------------------------------

def build_linear_model(n_features, n_classes, seed=0):
    """Pesos aleatorios fijos (no entrenados). d = (n_features + 1) * n_classes."""
    rng = random.Random(seed)
    W = [[rng.gauss(0, 1.0 / math.sqrt(n_features)) for _ in range(n_features)]
         for _ in range(n_classes)]
    b = [0.0] * n_classes
    return (W, b)


def forward_linear(params, x):
    """Logits = W x + b."""
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
    """Gradiente numérico de log p_theta(y|x) respecto a parámetros aplanados."""
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
# Panel y Fisher
# ---------------------------------------------------------------------------

def build_panel_from_data(xs, ys):
    return list(xs), list(ys)


def perturb_panel(xs, ys, sigma=0.1, seed=1):
    """Perturba las entradas del panel con ruido gaussiano."""
    rng = random.Random(seed)
    xs_pert = []
    for x in xs:
        xs_pert.append([x[i] + rng.gauss(0, sigma) for i in range(len(x))])
    return xs_pert, list(ys)


def fisher_matrix(params, xs, ys, n_features, n_classes):
    scores = []
    for x, y in zip(xs, ys):
        s = log_prob_grad_num(params, x, int(y), n_features=n_features, n_classes=n_classes)
        scores.append(s)
    n = len(scores)
    d = len(scores[0])
    F = [[0.0] * d for _ in range(d)]
    for i in range(d):
        for j in range(d):
            F[i][j] = sum(scores[k][i] * scores[k][j] for k in range(n)) / n
    return F


# ---------------------------------------------------------------------------
# Perspectivas y métrica h
# ---------------------------------------------------------------------------

def build_perspectives(n_perspectives, d, seed=2):
    rng = random.Random(seed)
    V = [[rng.gauss(0, 1) for _ in range(d)] for _ in range(n_perspectives)]
    return V  # B = V


def compute_h(B, C):
    Bt = mat_transpose(B)
    BC = mat_mul(B, C)
    return mat_mul(BC, Bt)


def spd_distance_pure(G0, G1):
    n = len(G0)
    w0, V0 = jacobi_eigen_symmetric(G0)
    w0_inv_sqrt = [1.0 / math.sqrt(max(w, 1e-12)) for w in w0]
    V0T = mat_transpose(V0)
    D = [[w0_inv_sqrt[i] if i == j else 0.0 for j in range(n)] for i in range(n)]
    V0D = mat_mul(V0, D)
    G0_inv_sqrt = mat_mul(V0D, V0T)

    M = mat_mul(mat_mul(G0_inv_sqrt, G1), G0_inv_sqrt)
    wM, VM = jacobi_eigen_symmetric(M)
    wM_log = [math.log(max(w, 1e-12)) for w in wM]
    Dlog = [[wM_log[i] if i == j else 0.0 for j in range(n)] for i in range(n)]
    VMD = mat_mul(VM, Dlog)
    VMt = mat_transpose(VM)
    logM = mat_mul(VMD, VMt)
    return mat_fro_norm(logM)


def perturb_B(B, xs, ys, xs_pert, ys_pert, params, epsilon, n_features, n_classes, seed=4):
    """B(mu_epsilon) = B0 + epsilon * delta_B.

    delta_B deriva de la diferencia de medias de entradas entre panel base y
    panel perturbado, proyectada sobre el espacio de observables.
    """
    n_pers, d = len(B), len(B[0])
    n = len(xs)
    input_dim = len(xs[0])
    mean_base = [sum(xs[k][i] for k in range(n)) / n for i in range(input_dim)]
    mean_pert = [sum(xs_pert[k][i] for k in range(n)) / n for i in range(input_dim)]
    delta_mean = [mean_pert[i] - mean_base[i] for i in range(input_dim)]

    rng = random.Random(seed)
    delta_B = [[0.0] * d for _ in range(n_pers)]
    for a in range(n_pers):
        for i in range(d):
            dm = delta_mean[i % input_dim] if input_dim > 0 else 0.0
            delta_B[a][i] = rng.gauss(0, 0.5) * dm
    return mat_add(B, mat_scale(delta_B, epsilon))


# ---------------------------------------------------------------------------
# Ejecución principal
# ---------------------------------------------------------------------------

def run_protocol(output_dir, dataset="synthetic"):
    os.makedirs(output_dir, exist_ok=True)

    # Configuración congelada
    epsilon_max = 0.2
    n_epsilon = 11
    tau = 1e-6
    n_perspectives = 4
    seed_net = 0
    seed_panel = 1

    if dataset == "wine":
        xs, ys = load_wine_dataset()
        n_features = len(xs[0])
        n_classes = 3
        layer_sizes = None
        input_dim = n_features
        n_inputs = len(xs)
        model_seed = 42
    elif dataset == "synthetic":
        layer_sizes = (4, 4, 3)
        n_inputs = 20
        n_classes = 3
        input_dim = layer_sizes[0]
        n_features = input_dim
        model_seed = seed_net
        # Construir datos sintéticos
        rng = random.Random(seed_panel)
        xs = [[rng.gauss(0, 1) for _ in range(input_dim)] for _ in range(n_inputs)]
        ys = [rng.randint(0, n_classes - 1) for _ in range(n_inputs)]
    else:
        raise ValueError(f"Dataset desconocido: {dataset}")

    # 1. Modelo lineal sin entrenamiento
    params = build_linear_model(n_features, n_classes, seed=model_seed)
    d = len(flatten_params(params))

    # 2. Panel base y panel perturbado
    xs_pert, ys_pert = perturb_panel(xs, ys, sigma=0.1, seed=seed_panel + 100)

    # 3. Fisher del panel base
    F0 = fisher_matrix(params, xs, ys, n_features, n_classes)
    eigvals0, eigvecs0 = jacobi_eigen_symmetric(F0)
    weak_modes = [i for i, w in enumerate(eigvals0) if w < tau]
    n_weak = len(weak_modes)

    # 4. Matriz B base y cométrica C (identidad dxd)
    B0 = build_perspectives(n_perspectives, d, seed=2)
    C = mat_eye(d)

    # 5. Métrica base
    h0 = compute_h(B0, C)

    # 6. Fisher del panel perturbado
    F_pert = fisher_matrix(params, xs_pert, ys_pert, n_features, n_classes)

    # 7. Recorrer epsilon
    epsilons = [epsilon_max * i / (n_epsilon - 1) for i in range(n_epsilon)]
    results = []

    for eps in epsilons:
        F_mix = mat_add(mat_scale(F0, 1.0 - eps), mat_scale(F_pert, eps))

        B_eps = perturb_B(B0, xs, ys, xs_pert, ys_pert, params, eps,
                          n_features, n_classes)
        h_eps = compute_h(B_eps, C)

        delta_h = mat_fro_norm(mat_sub(h_eps, h0))
        if eps == 0.0:
            d_spd = 0.0
        else:
            d_spd = spd_distance_pure(h0, h_eps)

        # Proyección sobre modos débiles de Fisher
        dF = mat_sub(F_mix, F0)
        if n_weak > 0:
            P = [[0.0] * d for _ in range(d)]
            for wi in weak_modes:
                vec = eigvecs0[wi]
                for i in range(d):
                    for j in range(d):
                        P[i][j] += vec[i] * vec[j]
            proj_weak = 0.0
            for i in range(d):
                for j in range(d):
                    proj_weak += dF[i][j] * P[i][j]
        else:
            proj_weak = 0.0

        results.append({
            "epsilon": round(eps, 6),
            "delta_h_fro": round(delta_h, 10),
            "spd_distance": round(d_spd, 10),
            "n_weak_modes": n_weak,
            "proj_on_weak_modes": round(proj_weak, 10),
            "max_eigenvalue_F": round(eigvals0[0], 10),
            "min_eigenvalue_F": round(eigvals0[-1], 10),
        })

    # 8. Guardar resultados
    summary = {
        "experiment": "NEM1",
        "dataset": dataset,
        "description": "Estabilidad de la métrica de perspectivas frente al panel y modos debiles de Fisher",
        "config": {
            "dataset": dataset,
            "n_inputs": n_inputs,
            "n_classes": n_classes,
            "n_features": n_features,
            "n_params": d,
            "n_perspectives": n_perspectives,
            "epsilon_max": epsilon_max,
            "n_epsilon": n_epsilon,
            "tau": tau,
        },
        "fisher_base": {
            "max_eigenvalue": eigvals0[0],
            "min_eigenvalue": eigvals0[-1],
            "n_weak_modes": n_weak,
        },
        "results": results,
    }

    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(output_dir, "stability.csv")
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "epsilon", "delta_h_fro", "spd_distance", "n_weak_modes",
            "proj_on_weak_modes", "max_eig_F", "min_eig_F",
        ])
        for r in results:
            writer.writerow([
                r["epsilon"], r["delta_h_fro"], r["spd_distance"],
                r["n_weak_modes"], r["proj_on_weak_modes"],
                r["max_eigenvalue_F"], r["min_eigenvalue_F"],
            ])

    print(f"Dataset: {dataset}")
    print(f"Resultados guardados en {output_dir}")
    print(f"Resumen: {summary_path}")
    print(f"Tabla: {csv_path}")
    print(f"Parametros: {d}, Entradas: {n_inputs}, Clases: {n_classes}, Features: {n_features}")
    print(f"Modos debiles de Fisher (tau={tau}): {n_weak}")
    max_delta = max(r["delta_h_fro"] for r in results)
    print(f"Delta h maximo: {max_delta:.6e}")

    return 0


def main():
    parser = argparse.ArgumentParser(description="NEM1 — protocolo de estabilidad de h")
    parser.add_argument("--output", required=True, help="Directorio de salida para resultados")
    parser.add_argument("--dataset", default="synthetic",
                        choices=["synthetic", "wine"],
                        help="Dataset a utilizar")
    args = parser.parse_args()
    return run_protocol(args.output, args.dataset)


if __name__ == "__main__":
    import sys
    sys.exit(main())
