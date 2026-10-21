#!/usr/bin/env python3
"""Figura derivada exclusivamente de tablas archivadas."""
import argparse,csv,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'leviathan-mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'leviathan-cache'))
for key in ['MPLCONFIGDIR','XDG_CACHE_HOME']:Path(os.environ[key]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def main(out,preview):
    rows=list(csv.DictReader((ROOT/'results/run_v1/hausdorff.csv').open()))
    plt.rcParams.update({'svg.hashsalt':'E16-N','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for label,folder,color in [('M uniforme',ROOT.parent/'M/results/run_v2','#D55E00'),('N graduada',ROOT/'results/run_v1','#0072B2')]:
        vv=list(csv.DictReader((folder/'vertices.csv').open()));r=sorted([r for r in vv if r['lineage']=='Q0' and r['segments']=='128'],key=lambda r:float(r['t']))
        axes[0].plot([0]+[float(r['t']) for r in r]+[1],[0]+[float(r['s']) for r in r]+[0],color=color,label=label)
        rr=[r for r in rows if r['lineage']=='Q0' and r['family']==('M_refinement' if label.startswith('M') else 'N_refinement')]
        axes[1].plot([64,128],[float(r['upper']) for r in rr],'o-',color=color,label=label)
    axes[0].set(xlabel='Posición longitudinal t',ylabel='Desplazamiento normal / cuerda s',title='Q0: caminos con 128 segmentos')
    axes[1].axhline(.001,color='#555555',ls='--',label='Umbral 0,001');axes[1].set_yscale('log');axes[1].set_xticks([64,128]);axes[1].set(xlabel='Segmentos de la malla fina',ylabel='Cota superior Hausdorff / cuerda',title='Comparación con la malla anterior')
    for ax in axes:ax.legend();ax.grid(alpha=.2)
    fig.suptitle('E16-N · menor separación, umbral todavía incumplido')
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(x.rstrip() for x in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/comparison.svg');p.add_argument('--preview',type=Path);a=p.parse_args();main(a.out,a.preview)
