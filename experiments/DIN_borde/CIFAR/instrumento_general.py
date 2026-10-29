"""Instrumento generalizado de DIN-CIFAR (plan v1, §2-§3).

Reutiliza SIN CAMBIOS `subset_M` del core congelado y `rho_borde_v2` (r3).
Solo generaliza `make_geom_state` a modelo = cuerpo + cabeza Linear de 3
salidas, con la misma parametrización reducida de la cabeza que el original:
W3r = W[:2]-W[2], b3r = b[:2]-b[2], logits = [h W3r^T + b3r, 0].

Este archivo no entrena ni mide nada al importarse.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import types

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
FUENTES = {
    'core': ('docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/core.py',
             'b5251d2f1f082ae014596574e9ab827dde04aec785bf76091005f8149ba31ffd'),
    'rho_v2': ('experiments/DIN_borde/I2/rho_borde_v2.py',
               '2ac015a263afb44616de0fceebd3b1d2a36ad0a76cd466adcdcc7e3adb8b8df0'),
}
_CACHE = {}


def congelado(nombre):
    """Carga una fuente congelada tras verificar su SHA-256 (como el productor de Q13-M2)."""
    if nombre in _CACHE:
        return _CACHE[nombre]
    rel, sha = FUENTES[nombre]
    p = ROOT/rel
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise RuntimeError('Fuente congelada modificada: '+nombre)
    mod = types.ModuleType('cifar_congelado_'+nombre)
    mod.__file__ = str(p)
    exec(compile(data, str(p), 'exec'), mod.__dict__)
    _CACHE[nombre] = mod
    return mod


def bloques_cuerpo(body):
    """Un bloque por submódulo con parámetros propios, en orden de registro."""
    bloques = []
    for nombre, mod in body.named_modules():
        propios = [(nombre+'.'+k if nombre else k, v) for k, v in mod.named_parameters(recurse=False)]
        if propios:
            bloques.append(propios)
    n_total = sum(1 for _ in body.parameters())
    if sum(len(b) for b in bloques) != n_total:
        raise RuntimeError('Parámetros del cuerpo sin bloque')
    if any(True for _ in body.buffers()):
        raise RuntimeError('El cuerpo no debe tener buffers (p. ej. BatchNorm)')
    return bloques


def make_geom_state_general(body, head, Xpanel, ypanel, reducida=True):
    """Devuelve (Rb, Ub) por bloques, compatibles con core.subset_M.

    Bloques: los del cuerpo (en orden) y al final la cabeza [W3r, b3r].
    `reducida=False` usa la cabeza completa [W, b]; existe SOLO como control
    negativo de la compuerta (cambia M aunque las probabilidades sean iguales).
    """
    import torch
    from torch.func import functional_call

    bloques = bloques_cuerpo(body)
    nombres = [[k for k, _ in b] for b in bloques]
    params_cuerpo = [[v.detach().clone().requires_grad_(True) for _, v in b] for b in bloques]
    W = head.weight.detach()
    b = head.bias.detach()
    if W.shape[0] != 3:
        raise ValueError('La cabeza debe tener 3 salidas')
    if reducida:
        Wh = (W[:2]-W[2:3]).clone().requires_grad_(True)
        bh = (b[:2]-b[2]).clone().requires_grad_(True)
    else:
        Wh = W.clone().requires_grad_(True)
        bh = b.clone().requires_grad_(True)
    blocks = params_cuerpo+[[Wh, bh]]
    todos = [p for bl in blocks for p in bl]
    tam = [sum(p.numel() for p in bl) for bl in blocks]
    mapa = {k: v for ks, vs in zip(nombres, params_cuerpo) for k, v in zip(ks, vs)}
    N = len(Xpanel)

    def logits(x):
        h = functional_call(body, mapa, (x,))
        z = h@Wh.T+bh
        if reducida:
            return torch.cat([z, torch.zeros((len(x), 1), dtype=x.dtype)], 1)
        return z

    def grads_por_bloque(escalar):
        gs = torch.autograd.grad(escalar, todos, retain_graph=True)
        plano = torch.cat([g.reshape(-1) for g in gs])
        return list(torch.split(plano, tam))

    Rb = [[] for _ in blocks]
    Ub = [[] for _ in blocks]
    for n in range(N):
        logp = torch.log_softmax(logits(Xpanel[n:n+1]).squeeze(0), 0)
        p = logp.exp().detach()
        for bi, g in enumerate(grads_por_bloque(logp[ypanel[n]])):
            Rb[bi].append(g.detach())
        for c in range(3):
            esc = math.sqrt(float(p[c])/N)
            for bi, g in enumerate(grads_por_bloque(logp[c])):
                Ub[bi].append((esc*g).detach())
    Rb = [torch.stack(v, 0) for v in Rb]
    Ub = [torch.stack(v, 0).T.contiguous() for v in Ub]
    return Rb, Ub


def metrica(body, head, Xpanel, ypanel, reducida=True):
    """M (numpy, n×n) con core.subset_M sobre todos los bloques, y c, q como Q13-M2."""
    core = congelado('core')
    Rb, Ub = make_geom_state_general(body, head, Xpanel, ypanel, reducida=reducida)
    M = core.subset_M(Rb, Ub, list(range(len(Rb)))).numpy()
    return M, *c_q(M)


def c_q(M):
    diag = np.diag(M)
    traza = float(np.trace(M))
    norma = float(np.linalg.norm(M))
    if not np.isfinite(M).all() or traza <= 0 or norma <= 0:
        raise RuntimeError('M inválida')
    return float(diag.max()/traza), float(np.linalg.norm(M-np.diag(diag))/norma)


def perspectivas_pca(Xpanel_pre):
    """f del plan v1 §3: 2 CP del panel preprocesado, sin etiquetas.

    Centrado con la media del panel; puntajes divididos por su desviación
    (ddof=0); cada carga se orienta con suma >= 0 (si es 0 exacto, primer
    elemento no nulo > 0).
    """
    X = np.asarray(Xpanel_pre, dtype=np.float64).reshape(len(Xpanel_pre), -1)
    Xc = X-X.mean(0)
    _, _, Vt = np.linalg.svd(Xc, full_matrices=False)
    V = Vt[:2].copy()
    for i in range(2):
        s = V[i].sum()
        if s < 0 or (s == 0 and V[i][np.flatnonzero(V[i])[0]] < 0):
            V[i] = -V[i]
    Z = Xc@V.T
    sd = Z.std(0)
    if not (sd > 0).all():
        raise RuntimeError('Componente principal degenerada')
    return Z/sd, V
