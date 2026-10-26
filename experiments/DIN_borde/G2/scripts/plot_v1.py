"""Figura exportable; descriptivos de los seis niveles, sin inferencia."""
import json
import os
from pathlib import Path
import numpy as np
os.environ.setdefault('MPLCONFIGDIR', '/tmp/din-g2-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from support_v1 import STAGE, RUN, guard, code_guard, sha, write


def main():
    code_guard(); guard()
    data = json.loads((RUN/'analysis.json').read_text())
    levels = data['levels']
    s = np.array([l['s'] for l in levels])
    def number(v):
        return np.nan if v is None else float(v)
    V = np.array([number(l['V']) for l in levels])
    D = np.array([number(l['primary'].get('C1_exact', {}).get('D')) for l in levels])
    Dc = np.array([number(l['primary'].get('D7_conditional_R', {}).get('D')) for l in levels])
    Ds = np.array([number(l['secondary'].get('C1_exact', {}).get('D')) for l in levels])
    folder = STAGE/'figures'; folder.mkdir(exist_ok=False)
    fig, ax = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)
    ax[0, 0].plot(s, [number(l['mal_fraction']) for l in levels], 'o-', color='#9d3d36', label='Fracción Mal250')
    ax[0, 0].plot(s, V, 's-', color='#275f97', label='Variancia intra-split V')
    ax[0, 0].axhline(.08, color='#275f97', linestyle=':', linewidth=.8)
    ax[0, 0].axhline(.04, color='#275f97', linestyle=':', linewidth=.8)
    ax[0, 0].set(xscale='log', xlabel='Solapamiento s', ylim=(-.02, 1.02), title='Resolución final del dominante')
    ax[0, 0].legend(fontsize=9)
    ax[0, 1].plot(s, D, 'o-', label='D_X, rho_caras', color='#275f97')
    ax[0, 1].plot(s, Dc, 's--', label='D_X|R, rho_caras', color='#a35c16')
    ax[0, 1].plot(s, Ds, '^:', label='D_X, rho_vert secundario', color='#54644a')
    ax[0, 1].axhline(0, color='.5', linewidth=.8)
    ax[0, 1].set(xscale='log', xlabel='Solapamiento s', ylabel='Reducción fraccional SSE fuera de muestra', title='Estimando C1 y ajuste D7')
    ax[0, 1].legend(fontsize=8)
    ax[1, 0].scatter(V, D, c=np.log(s), cmap='viridis', s=55)
    for x, y, label in zip(V, D, s):
        if np.isfinite(x) and np.isfinite(y):
            ax[1, 0].annotate(f's={label:g}', (x, y), xytext=(5, 5), textcoords='offset points', fontsize=8)
    ax[1, 0].axhline(0, color='.5', linewidth=.8)
    ax[1, 0].set(xlabel='V: media de p_split(1−p_split)', ylabel='D_X (rho_caras)', title='H-var · sólo seis niveles emparejados')
    ax[1, 1].plot(s, [number(l['train_acc250']) for l in levels], 'o-', label='Train mediana')
    ax[1, 1].plot(s, [number(l['val_acc250']) for l in levels], 's-', label='Panel mediana')
    ax[1, 1].set(xscale='log', xlabel='Solapamiento s', ylim=(0, 1.02), title='Precisión al update250')
    ax[1, 1].legend(fontsize=9)
    for a in ax.ravel():
        a.grid(alpha=.18)
    fig.suptitle('DIN-G2 · exploratorio ·20 splits×5 inicios por nivel\n'+data['H_var']['verdict'], fontsize=13)
    fig.savefig(folder/'resolucion.png', dpi=180)
    fig.savefig(folder/'resolucion.svg')
    plt.close(fig)
    write(folder/'provenance.json', dict(source='results/run_v1/analysis.json', sha256=sha(RUN/'analysis.json'),
                   intervals='No son intervalos de confianza; se muestran agregados descriptivos.'))


if __name__ == '__main__':
    main()
