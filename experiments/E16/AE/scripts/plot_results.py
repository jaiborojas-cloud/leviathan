#!/usr/bin/env python3
"""Figura descriptiva derivada exclusivamente de tablas archivadas."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/e16-ae-mpl')
os.environ.setdefault('XDG_CACHE_HOME','/tmp/e16-ae-cache')
from metric_v1 import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import SymLogNorm
import argparse

def main(preview):
 grid=[r for r in rows(ROOT/'results/phase0_v1/grid.csv') if r['group']=='grid'];raw=ROOT/'results/main_v1';prof=[r for r in rows(raw/'profiles.csv') if r['n']=='1024'];byray={}
 for r in prof:byray.setdefault(int(r['ray']),[]).append(r)
 plt.rcParams['svg.hashsalt']='e16-ae-v1';fig,axes=plt.subplots(1,3,figsize=(16,4.8),constrained_layout=True)
 x=sorted({float(r['x']) for r in grid});y=sorted({float(r['y']) for r in grid});K=np.array([[float(next(r['K'] for r in grid if float(r['x'])==a and float(r['y'])==b)) for a in x] for b in y]);im=axes[0].pcolormesh(x,y,K,cmap='coolwarm',norm=SymLogNorm(.05,vmin=-7,vmax=.05),shading='nearest');fig.colorbar(im,ax=axes[0],label='K, escala simétrica logarítmica');axes[0].scatter([0],[0],c='black',marker='x',label='P0 fijado');axes[0].set_title('Curvatura de fase0 · familia no plana');axes[0].set_xlabel('P1');axes[0].set_ylabel('P2');axes[0].legend(fontsize=8)
 for i in range(0,1024,16):
  rr=byray[i];axes[1].plot([float(r['p0']) for r in rr],[float(r['p1']) for r in rr],color='#5a86a0',lw=.5,alpha=.5)
 for radius in [.125,.25,.5,.65625]:
  rr=[next(r for r in byray[i] if float(r['r'])==radius) for i in range(1024)];points=np.array([[float(r['p0']),float(r['p1'])] for r in rr]);points=np.vstack([points,points[0]]);axes[1].plot(points[:,0],points[:,1],lw=1,label=f'r={radius:g}')
 axes[1].scatter([0],[0],color='black',s=12);axes[1].set_xlim(-4,4);axes[1].set_ylim(-4,4);axes[1].set_aspect('equal');axes[1].set_title('Rayos hasta salida y frentes completos');axes[1].set_xlabel('P1');axes[1].set_ylabel('P2');axes[1].legend(fontsize=7)
 allprof=rows(raw/'profiles.csv');summary=rows(raw/'resolutions.csv')
 for n in [512,1024]:
  pp=[r for r in allprof if int(r['n'])==n];acc={}
  for r in pp:
   rad=float(r['r'])
   if rad<=.6875:acc.setdefault(rad,[]).append(float(r['I']))
  samples=sorted((r,2*np.pi/n*sum(v)) for r,v in acc.items() if len(v)==n);axes[2].plot([r for r,a in samples],[a for r,a in samples],label=f'{n} rayos',ls='-' if n==512 else '--');q=next(r for r in summary if int(r['n'])==n);axes[2].scatter([float(q['r_safe_common'])],[float(q['A_safe_common'])],s=25)
 xx=np.linspace(0,.6875,100);axes[2].plot(xx,np.pi*xx**2,c='.5',lw=.8,label='πr², referencia plana');axes[2].set_xlabel('r con cobertura completa');axes[2].set_ylabel('Integral polar estimada');axes[2].set_title('A(r seguro) · A(r_deg) desconocida');axes[2].legend(fontsize=8);fig.suptitle('E16-AE · Q1/Q2/Q3 INCONCLUSIVE · censura conservada')
 target=ROOT/'figures/geometry_and_censoring.svg';target.parent.mkdir(exist_ok=True);fig.savefig(target,metadata={'Date':None});target.write_text('\n'.join(s.rstrip() for s in target.read_text().splitlines())+'\n')
 if preview:fig.savefig(preview,dpi=150)
 plt.close(fig)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--preview',type=Path);main(p.parse_args().preview)
