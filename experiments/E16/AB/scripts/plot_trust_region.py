#!/usr/bin/env python3
"""Figura de resultados finales archivados, incluyendo inconclusos."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-ab-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-ab-cache')
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main(preview):
 paths=list(csv.DictReader((ROOT/'results/run_v1/paths.csv').open()));comp=list(csv.DictReader((ROOT/'results/run_v1/comparisons.csv').open()));fig,axes=plt.subplots(1,2,figsize=(14,4.8),constrained_layout=True);plt.rcParams['svg.hashsalt']='e16-ab-v1'
 for eligible,color,label in [('True','#287fa7','Comparación elegible'),('False','#cf802b','No elegible')]:
  selected=[(j,p) for j,p in enumerate(paths) if p['stationary_comparison_eligible']==eligible]
  if selected:
   axes[0].scatter([j for j,p in selected],[max(1e-40,float(p['final_KKT'])) for j,p in selected],c=color,label=label,marker='s')
   usable=[(j,p) for j,p in selected if p['minimum_mass']];axes[1].scatter([j+.06 for j,p in usable],[float(p['minimum_mass']) for j,p in usable],c=color,marker='s',label='AB final · '+label)
 axes[1].scatter(np.arange(len(paths))-.06,[float(next(c for c in comp if c['path']==p['path'])['AA_initial_minimum_mass']) for p in paths],c='.55',marker='o',label='AA inicial, KKT estricto inconcluso')
 axes[0].axhline(1e-7,c='.4',ls='--',label='Umbral físico 1e-7');axes[0].set_yscale('symlog',linthresh=1e-8);axes[0].set_ylabel('KKT físico final');axes[0].set_title('Cumplimiento de primer orden')
 axes[1].set_yscale('symlog',linthresh=1e-5);axes[1].axhline(0,c='.5',lw=.7);axes[1].set_ylabel('Mínimo restringido con masa fija');axes[1].set_title('Todos los puntos devueltos, sin filtrar outcomes')
 for ax in axes:
  ax.set_xticks(range(len(paths)),[p['path'].replace('/','\n') for p in paths],fontsize=7);ax.grid(axis='y',alpha=.2);ax.legend(fontsize=7)
 fig.suptitle('E16-AB · parada numérica no certifica mínimos')
 p=ROOT/'figures/trust_region_comparison.svg';p.parent.mkdir(exist_ok=True);fig.savefig(p,metadata={'Date':None});p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
