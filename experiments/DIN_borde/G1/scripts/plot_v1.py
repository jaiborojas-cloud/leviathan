"""Figura descriptiva exportable; medianas/IQR, no intervalos de confianza."""
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/din-g1-mpl-v1')
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from support_v1 import STAGE, RUN


def main():
    out = STAGE/'figures'
    out.mkdir(exist_ok=False)
    rows = [json.loads(p.read_text()) for p in sorted((RUN/'states').glob('*.json'))]
    updates = [5, 10, 20, 30, 50, 150, 250]
    colors = dict(R27='#167a67', P60='#d36a16', W27='#7563aa')
    labels = dict(R27='R27 · 64/32, panel27', P60='P60 · 64/32, panel60', W27='W27 · 128/64, panel27')
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for family in colors:
        rr = [r for r in rows if r['family'] == family and r.get('metrics', {}).get('M_valid')]
        for ax, metric in zip(axes.ravel(), ['c', 'q', 'acc', 'rho']):
            quartiles = []
            for t in updates:
                state = [r for r in rr if r['update'] == t]
                if metric == 'acc':
                    values = [r['train']['acc'] for r in state]
                elif metric == 'rho':
                    values = [r['rho']['rho_borde'] for r in state if r.get('rho_valid')]
                else:
                    values = [r['metrics'][metric] for r in state]
                quartiles.append(np.quantile(values, [.25, .5, .75]) if values else [np.nan]*3)
            q = np.array(quartiles)
            ax.plot(updates, q[:, 1], marker='o', markersize=4, color=colors[family],
                    label=labels[family], linewidth=1.8)
            ax.fill_between(updates, q[:, 0], q[:, 2], color=colors[family], alpha=.12)
            ax.set_xscale('log')
            ax.set_xticks(updates, [str(t) for t in updates])
            ax.set_xlabel('Update')
            ax.grid(alpha=.18)
    axes[0, 0].axhline(.8, color='#777777', linestyle='--', linewidth=1)
    axes[0, 0].set(title='Concentración en un ejemplo', ylabel='máx diag(M) / tr M', ylim=(0, 1.03))
    axes[0, 1].axhline(.05, color='#777777', linestyle='--', linewidth=1)
    axes[0, 1].set(title='Masa fuera de diagonal', ylabel='||M − diag M||F / ||M||F', ylim=(0, 1.03))
    axes[1, 0].axhline(.99, color='#777777', linestyle='--', linewidth=1)
    axes[1, 0].set(title='Precisión de entrenamiento', ylabel='Fracción correcta', ylim=(0, 1.03))
    axes[1, 1].set(title='ρ nativo · 720 direcciones / orden400', ylabel='ρ bruto (escala log)', yscale='log')
    axes[0, 0].legend(frameon=False, fontsize=9)
    fig.suptitle('DIN-G1 · Iris · mediana y rango intercuartil', fontsize=15)
    fig.supxlabel('100 trayectorias por familia; R27 y P60 comparten pesos. Sin inferencia confirmatoria.', fontsize=10)
    fig.savefig(out/'trayectorias.png', dpi=170)
    fig.savefig(out/'trayectorias.svg', metadata={'Date': '2026-10-25'})
    plt.close(fig)


if __name__ == '__main__':
    main()
