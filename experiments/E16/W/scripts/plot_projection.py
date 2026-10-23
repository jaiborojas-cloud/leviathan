#!/usr/bin/env python3
"""Figura de cambios pares archivados; sin nueva medición."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-w-mpl');os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-w-cache')
import argparse,csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main(preview):
 rows=list(csv.DictReader((ROOT/'results/run_v1/pairs.csv').open()));fig,axes=plt.subplots(2,2,figsize=(10,7),constrained_layout=True);plt.rcParams['svg.hashsalt']='e16-w-v1'
 for ax,(lin,arm) in zip(axes.ravel(),[(l,a) for l in ['Q0','Q1'] for a in ['reference','scaled']]):
  for family,color,marker in [('original','#414141','o'),('projected','#217fa8','s')]:
   rs=[r for r in rows if r['path']==f'{lin}/{arm}/264' and r['family']==family and r['state']=='VALID'];rs.sort(key=lambda r:float(r['step']));ax.plot([float(r['step']) for r in rs],[float(r['even_change']) for r in rs],label=family,color=color,marker=marker)
  ax.set_xscale('log');ax.set_yscale('symlog',linthresh=1e-20);ax.axhline(0,color='.5',lw=.7);ax.set_title(f'{lin} · {arm} · 264 segmentos');ax.set_xlabel('Paso h');ax.set_ylabel('Cambio par E');ax.grid(alpha=.2)
 axes[0,0].legend(fontsize=8);fig.suptitle('E16-W · proyectar una dirección no minimiza H sobre g⊥')
 p=ROOT/'figures/projection_effect.svg';p.parent.mkdir(exist_ok=True);fig.savefig(p,metadata={'Date':None});p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
