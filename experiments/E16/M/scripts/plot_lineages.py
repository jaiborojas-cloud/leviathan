#!/usr/bin/env python3
"""Figura derivada de tablas: no ejecuta optimizaciones ni evalúa la métrica."""
import argparse
import csv
import os
from pathlib import Path
import tempfile
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'leviathan-mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'leviathan-cache'))
Path(os.environ['MPLCONFIGDIR']).mkdir(parents=True,exist_ok=True)
Path(os.environ['XDG_CACHE_HOME']).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]

def main(out,preview=None):
    result=ROOT/'results/run_v2';vertices=list(csv.DictReader((result/'vertices.csv').open()))
    diffs=list(csv.DictReader((result/'shape_nodes.csv').open()));local=list(csv.DictReader((result/'localization.csv').open()))
    plt.rcParams.update({'svg.hashsalt':'E16-M-lineages','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(12,4),layout='constrained')
    for m,color in [(32,'#D55E00'),(64,'#009E73'),(128,'#0072B2')]:
        for lineage,style in [('Q0','-'),('Q1','--')]:
            rr=sorted([r for r in vertices if r['lineage']==lineage and r['segments']==str(m)],key=lambda r:int(r['index']))
            axes[0].plot([0]+[float(r['t']) for r in rr]+[1],[0]+[float(r['s']) for r in rr]+[0],color=color,ls=style,lw=1.6,label=f'{lineage} · {m}')
    axes[0].set_title('Q0 y Q1 coinciden en cada malla fina')
    axes[0].set_ylabel('Desplazamiento normal / cuerda (s)')
    axes[0].legend(ncol=2,fontsize=8)
    for lineage,color,style in [('Q0','#0072B2','-'),('Q1','#D55E00','--')]:
        key=f'{lineage}_64_128'
        rr=sorted([r for r in diffs if r['comparison']==key],key=lambda r:int(r['index']))
        mass=float(next(r['tail_fraction'] for r in local if r['comparison']==key and r['cutoff']=='0.9'))
        axes[1].plot([float(r['t']) for r in rr],[float(r['difference']) for r in rr],color=color,ls=style,lw=1.8,label=f'{lineage} · masa en cola: {100*mass:.1f} %')
    axes[1].axvspan(.9,1,color='#999999',alpha=.15,label='Cola t ≥ 0,90')
    axes[1].set_title('Cambio 64→128: pico cercano al extremo')
    axes[1].set_ylabel('Diferencia normal / cuerda (Δs)')
    axes[1].legend(fontsize=8)
    for ax in axes:
        ax.set_xlim(0,1);ax.set_xlabel('Posición longitudinal t');ax.axhline(0,color='gray',lw=.7,ls=':');ax.grid(alpha=.15)
    fig.suptitle('E16-M · coincidencia entre linajes no implica convergencia de forma',fontsize=12)
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None})
    if out.suffix.lower()=='.svg':out.write_text('\n'.join(line.rstrip() for line in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,default=ROOT/'figures/lineage_comparison.svg');parser.add_argument('--preview',type=Path)
    args=parser.parse_args();main(args.out,args.preview)
