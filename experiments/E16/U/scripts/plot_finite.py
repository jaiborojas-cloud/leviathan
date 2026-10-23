#!/usr/bin/env python3
"""Visualización de resultados escalares archivados, sin cálculo científico nuevo."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-u-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-u-cache')
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main(preview):
 pairs=list(csv.DictReader((ROOT/'results/run_v1/pairs.csv').open()));trials=list(csv.DictReader((ROOT/'results/run_v1/trials.csv').open()));fig,axes=plt.subplots(1,2,figsize=(13,4.7),constrained_layout=True);plt.rcParams['svg.hashsalt']='e16-u-v1'
 for color,(lin,arm) in zip(['#176ba0','#d46a16','#3a8f4a','#9752a0'],[(l,a) for l in ['Q0','Q1'] for a in ['reference','scaled']]):
  for m,style,marker in [(132,'--','o'),(264,'-','s')]:
   rs=[r for r in pairs if r['path']==f'{lin}/{arm}/{m}' and r['direction']=='full_min' and r['state']=='VALID'];rs.sort(key=lambda r:float(r['step']))
   axes[0].plot([float(r['step']) for r in rs],[float(r['even_change']) for r in rs],color=color,ls=style,marker=marker,label=f'{lin} {arm} · {m}')
 axes[0].set_xscale('log');axes[0].set_yscale('symlog',linthresh=1e-20);axes[0].axhline(0,color='.4',lw=.8);axes[0].set_xlabel('Paso h');axes[0].set_ylabel('Cambio par normalizado E(h)');axes[0].set_title('Dirección mínima completa · todos los cuadráticos');axes[0].legend(fontsize=7,ncol=2);axes[0].grid(alpha=.2)
 names=['full_min','tangent_min','normal_min','tangent_sine','normal_sine'];bottom=np.zeros(5)
 for status,color in [('CHANGED','#287aa5'),('UNRESOLVED','#e7aa44'),('WITHIN_TOLERANCE','#6aa16b'),('UNKNOWN','#999999')]:
  values=np.array([sum(r['direction']==d and r['geometry_status']==status for r in trials) for d in names]);axes[1].bar(np.arange(5),values,bottom=bottom,color=color,label=status);bottom+=values
 axes[1].set_xticks(range(5),[n.replace('_','\n') for n in names]);axes[1].set_ylabel('Número de ensayos (incluye C0)');axes[1].set_title('Cambio de imagen según cotas numéricas');axes[1].legend(fontsize=8)
 fig.suptitle('E16-U · pasos y signos prefijados; diagnóstico exploratorio')
 p=ROOT/'figures/finite_descent.svg';p.parent.mkdir(exist_ok=True);fig.savefig(p,metadata={'Date':None});p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
