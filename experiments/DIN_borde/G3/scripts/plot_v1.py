"""Figuras exportables de potencia y cohorte; sólo descriptivas."""
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/din-g3-mpl')
os.environ.setdefault('XDG_CACHE_HOME', '/tmp/din-g3-cache')
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True, exist_ok=True)
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from support_v1 import STAGE, RUN, write, guard, code_guard, sha


def number(v):
    return np.nan if v is None else float(v)


def main():
    code_guard(); guard()
    data = json.loads((RUN/'analysis.json').read_text())
    power = json.loads((STAGE/'results/power_v1/summary.json').read_text())
    levels = data['levels']; s = np.array([l['s'] for l in levels])
    D = np.array([number(l['primary'].get('C1_exact', {}).get('D')) for l in levels])
    Dc = np.array([number(l['primary'].get('D7_conditional_R', {}).get('D')) for l in levels])
    Ds = np.array([number(l['secondary'].get('C1_exact', {}).get('D')) for l in levels])
    V = np.array([number(l['V_cont']) for l in levels])
    out = STAGE/'figures'; out.mkdir(exist_ok=False)
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    for lev in power['candidates'][-1]['levels']:
        e = lev['estimates'][1:]
        axes[0, 0].errorbar([r['D_target'] for r in e], [r['rate'] for r in e],
              yerr=np.array([[r['rate']-r['lower'] for r in e], [r['upper']-r['rate'] for r in e]]),
              marker='o', capsize=3, label=f"s={lev['s']:g}")
    axes[0, 0].axhline(.8, linestyle=':', color='.4')
    axes[0, 0].set(xlabel='D oráculo simulado (no D CV finito)', ylabel='Fracción PASS simulada', ylim=(0, 1.02),
                    title=f"Planificación previa ·N={power['selected_splits']} splits")
    axes[0, 0].legend(fontsize=9)
    axes[0, 1].plot(s, D, 'o-', label='D_X, rho_caras')
    axes[0, 1].plot(s, Dc, 's--', label='D_X|R, rho_caras')
    axes[0, 1].plot(s, Ds, '^:', label='D_X, rho_vert secundario')
    axes[0, 1].axhline(0, color='.5', linewidth=.8)
    axes[0, 1].set(xlabel='Solapamiento s', ylabel='Reducción SSE fuera de muestra', title='Cohorte nueva · C1 y D7')
    axes[0, 1].legend(fontsize=8)
    for i, lev in enumerate(levels):
        if np.isfinite(V[i]) and np.isfinite(D[i]):
            marker = 'o' if lev['regime'] == 'COLAPSO_OPERACIONAL' else 'x'
            axes[1, 0].scatter(V[i], D[i], marker=marker, s=65, label=f"s={s[i]:g}, {lev['regime']}")
            axes[1, 0].annotate(f's={s[i]:g}', (V[i], D[i]), xytext=(5, 5), textcoords='offset points', fontsize=9)
    axes[1, 0].axhline(0, color='.5', linewidth=.8)
    axes[1, 0].set(xlabel='V_cont: media varianza intra-split de R250', ylabel='D_X, rho_caras',
                     title='Sólo tres niveles · tendencia descriptiva')
    axes[1, 0].legend(fontsize=6)
    axes[1, 1].plot(s, [number(l['median_c250']) for l in levels], 'o-', label='Mediana maxdiag/tr')
    axes[1, 1].plot(s, [number(l['collapsed_fraction']) for l in levels], 's--', label='Fracción c≥.8,q≤.05')
    axes[1, 1].plot(s, [number(l['mal_fraction']) for l in levels], '^:', label='k* mal clasificado')
    axes[1, 1].axhline(.8, linestyle=':', color='.5', linewidth=.8)
    axes[1, 1].set(xlabel='Solapamiento s', ylim=(0, 1.02), title='Régimen y resolución final')
    axes[1, 1].legend(fontsize=8)
    for a in axes.ravel():
        a.grid(alpha=.18)
    fig.suptitle('DIN-G3 · exploratorio ·semillas nuevas\n'+data['reading']['verdict'], fontsize=12)
    fig.savefig(out/'potencia_senal.png', dpi=180)
    fig.savefig(out/'potencia_senal.svg'); plt.close(fig)
    write(out/'provenance.json', dict(analysis_sha256=sha(RUN/'analysis.json'),
       power_sha256=sha(STAGE/'results/power_v1/summary.json'),
       intervals='Sólo Wilson95% Monte Carlo en potencia; no intervalos de la cohorte observada.'))


if __name__ == '__main__':
    main()
