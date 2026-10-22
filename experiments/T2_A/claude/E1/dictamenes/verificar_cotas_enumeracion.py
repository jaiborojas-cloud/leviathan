"""Verifica por enumeracion exhaustiva (aritmetica racional) los extremos de precision, tasa base, diferencia y lift sobre
completaciones binarias libres (dictamen tecnico IA v1, seccion 2), y si la regla de E1 6.3 ("dentro -> 0, fuera -> 1")
da el minimo de la tasa base. Exploratorio de apoyo documental; no es el script de la seccion 6."""
import random
from fractions import Fraction as F

def extremos_enumerados(N, m, a, b, u, v):
    vals = {k: [] for k in "PBDL"}
    for x in range(u + 1):
        for y in range(v + 1):
            P, B = F(a + x, m), F(a + b + x + y, N)
            vals["P"].append(P); vals["B"].append(B); vals["D"].append(P - B)
            if a + b + x + y > 0:
                vals["L"].append(P / B)
    return {k: (min(s), max(s)) for k, s in vals.items() if s}

def extremos_formula(N, m, a, b, u, v):
    f = {"P": (F(a, m), F(a + u, m)), "B": (F(a + b, N), F(a + b + u + v, N)),
         "D": (F(a, m) - F(a + b + v, N), F(a + u, m) - F(a + b + u, N))}
    if a + b > 0:
        f["L"] = (F(N * a, m * (a + b + v)), F(N * (a + u), m * (a + b + u)))
    return f

if __name__ == "__main__":
    random.seed(1); n = 3000; ok = 0; e1 = 0
    for _ in range(n):
        N = random.randint(2, 40); m = random.randint(1, N); a = random.randint(0, m); b = random.randint(0, N - m)
        u = random.randint(0, m - a); v = random.randint(0, N - m - b)
        en, fo = extremos_enumerados(N, m, a, b, u, v), extremos_formula(N, m, a, b, u, v)
        ok += all(en[k] == fo[k] for k in fo)
        e1 += F(a + b + v, N) == en["B"][0]
    print(f"formulas del dictamen exactas en {ok} de {n} casos; regla E1 6.3 da el minimo de la tasa base en {e1} de {n}")
    print("ejemplo E1 (N=800, m=80, a=12, b=28, u=10, v=100):", {k: tuple(float(x) for x in t) for k, t in extremos_formula(800, 80, 12, 28, 10, 100).items()})
