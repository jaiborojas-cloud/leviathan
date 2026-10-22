#!/usr/bin/env python3
"""Figura derivada exclusivamente de los escalares archivados en T."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-t-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-t-cache')
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def main(preview):
 rows=list(csv.DictReader((ROOT/'results/run_v1/paths.csv').open()));fig,axes=plt.subplots(1,2,figsize=(13,4.4),constrained_layout=True);plt.rcParams['svg.hashsalt']='e16-t-v1'
 groups=[(l,a) for l in ['Q0','Q1','C0'] for a in ['reference','scaled']]
 for m,shift,color,marker in [(132,-.09,'#176ba0','o'),(264,.09,'#cb6217','s')]:
  selected=[next(r for r in rows if r['lineage']==l and r['arm']==a and int(r['segments'])==m) for l,a in groups]
  xx=np.arange(6)+shift;ratio=[float(r['full_min'])/float(r['full_threshold']) for r in selected]
  axes[0].scatter(xx,ratio,c=color,marker=marker,label=f'{m} segmentos',s=55,zorder=3)
  axes[1].scatter(xx[:4],[max(1e-16,1-float(r['full_min_tangent_fraction'])) for r in selected[:4]],c=color,marker=marker,s=55)
 axes[0].axhspan(-1,1,color='.9',label='Banda casi nula ±τ');axes[0].axhline(-1,color='.3',ls='--');axes[0].axhline(0,color='.5',lw=.7);axes[0].set_yscale('symlog',linthresh=1);axes[0].set_ylabel('λ mínimo completo / τ');axes[0].set_title('Curvatura en coordenadas físicas');axes[0].legend(fontsize=8)
 axes[1].set_yscale('log');axes[1].set_ylabel('Fracción normal del autovector mínimo');axes[1].set_title('Modos débiles predominantemente tangenciales')
 for ax,count in [(axes[0],6),(axes[1],4)]:
  ax.set_xticks(range(count),[f'{l}\n{a}' for l,a in groups[:count]]);ax.grid(axis='y',alpha=.2)
 fig.suptitle('E16-T · diagnóstico numérico local; no certificado de mínimo')
 out=ROOT/'figures/second_order.svg';out.parent.mkdir(exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(s.rstrip() for s in out.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
