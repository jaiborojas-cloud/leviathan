#!/usr/bin/env python3
"""Figura de mínimos y normas archivados, sin mediciones nuevas."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-y-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-y-cache')
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main(preview):
 paths=list(csv.DictReader((ROOT/'results/run_v1/paths.csv').open()));names=[r['path'] for r in paths if r['level']=='coarse' and r['lineage']!='C0'];fig,axes=plt.subplots(1,2,figsize=(13,4.6),constrained_layout=True);plt.rcParams['svg.hashsalt']='e16-y-v1'
 for level,color,marker,shift in [('coarse','#c47428','o',-.08),('fine','#287fa7','s',.08)]:
  rs=[next(r for r in paths if r['path']==name and r['level']==level) for name in names];xx=[j+shift for j in range(len(rs))];axes[0].scatter(xx,[float(r['minimum_mass']) for r in rs],label=level,c=color,marker=marker);axes[1].scatter(xx,[float(r['gradient_norm']) for r in rs],label=level,c=color,marker=marker)
 axes[0].set_yscale('symlog',linthresh=1e-4);axes[0].axhline(0,color='.5',lw=.7);axes[0].set_ylabel('Mínimo restringido con norma de masa');axes[0].set_title('Misma imagen, espacio de variaciones ampliado')
 axes[1].set_yscale('log');axes[1].set_ylabel('Norma euclídea del gradiente');axes[1].set_title('Nuevas variables: estacionariedad no conservada')
 for ax in axes:
  ax.set_xticks(range(len(names)),[n.replace('/','\n') for n in names],fontsize=7);ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8)
 fig.suptitle('E16-Y · subdivisión sin reoptimización; no prueba de convergencia')
 p=ROOT/'figures/mass_refinement.svg';p.parent.mkdir(exist_ok=True);fig.savefig(p,metadata={'Date':None});p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
