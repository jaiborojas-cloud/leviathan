#!/usr/bin/env python3
"""Figura sólo de comparaciones y ensayos escalares archivados en X."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-x-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-x-cache')
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main(preview):
 comp=list(csv.DictReader((ROOT/'results/run_v1/comparisons.csv').open()));tr=list(csv.DictReader((ROOT/'results/run_v1/trials.csv').open()));names=[f'{l}/{a}/264' for l in ['Q0','Q1'] for a in ['reference','scaled']];cc=[next(r for r in comp if r['path']==name) for name in names];fig,axes=plt.subplots(1,2,figsize=(12,4.6),constrained_layout=True);plt.rcParams['svg.hashsalt']='e16-x-v1'
 axes[0].scatter(range(4),[float(r['W_projected_curvature']) for r in cc],label='W: una dirección proyectada',marker='s',c='#bc6a26',s=55);axes[0].scatter(range(4),[float(r['restricted_min']) for r in cc],label='X: mínimo restringido',marker='o',c='#277eac',s=55);axes[0].set_yscale('symlog',linthresh=1e-6);axes[0].axhline(0,color='.5',lw=.7);axes[0].set_xticks(range(4),[n.replace('/264','').replace('/','\n') for n in names]);axes[0].set_ylabel('Curvatura física');axes[0].legend(fontsize=8);axes[0].set_title('Proyección y mínimo restringido son distintos')
 for name,color in zip(names,['#277eac','#ca6e29','#408e55','#9556a6']):
  for sg,style,marker in [('-1','-','o'),('1','--','x')]:
   rr=[r for r in tr if r['path']==name and r['sign']==sg and r['state']=='VALID'];rr.sort(key=lambda r:float(r['step']));axes[1].plot([float(r['step']) for r in rr],[-float(r['delta']) for r in rr],color=color,ls=style,marker=marker,label=name.replace('/264','')+' '+sg)
 axes[1].set_xscale('log');axes[1].set_yscale('log');axes[1].set_xlabel('Paso h');axes[1].set_ylabel('Descenso normalizado −Δ');axes[1].set_title('Ambos sentidos · cuatro orígenes finos');axes[1].legend(fontsize=7,ncol=2)
 for ax in axes:ax.grid(alpha=.2)
 fig.suptitle('E16-X · diagnóstico numérico en el subespacio del gradiente')
 p=ROOT/'figures/restricted_minimum.svg';p.parent.mkdir(exist_ok=True);fig.savefig(p,metadata={'Date':None});p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
