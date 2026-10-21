#!/usr/bin/env python3
"""Figura derivada sólo de parámetros guardados; no ejecuta optimizaciones."""
import argparse
import csv
from pathlib import Path
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR",str(Path(tempfile.gettempdir())/"leviathan-mpl"))
os.environ.setdefault("XDG_CACHE_HOME",str(Path(tempfile.gettempdir())/"leviathan-cache"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True,exist_ok=True)
Path(os.environ["XDG_CACHE_HOME"]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]

def main(out,preview=None):
    rows=list(csv.DictReader((ROOT/'results/run_v1/vertices.csv').open()))
    case='h00/0/quadratic'
    def curve(m,source):
        rr=sorted([r for r in rows if r['case']==case and r['segments']==str(m) and r['source']==source],key=lambda r:int(r['index']))
        assert len(rr)==m-1
        return [0]+[float(r['t']) for r in rr]+[1],[0]+[float(r['s']) for r in rr]+[0]
    plt.rcParams.update({'svg.hashsalt':'E16-L-paths','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4),sharex=True,sharey=True,layout='constrained')
    for m,color in [(16,'#0072B2'),(32,'#D55E00'),(64,'#009E73')]:
        x,y=curve(m,'selected');axes[0].plot(x,y,label=f'{m} segmentos',color=color,lw=1.7)
    for index in range(6):
        x,y=curve(32,'start'+str(index))
        axes[1].plot(x,y,label='Heredado L16' if index==5 else f'Inicio frío {index}',lw=2 if index==5 else 1.2,alpha=.85)
    axes[0].set_title('Caminos elegidos al refinar')
    axes[1].set_title('32 segmentos: candidatos estacionarios')
    for ax in axes:
        ax.axhline(0,color='gray',ls=':',lw=.7);ax.set_xlim(0,1);ax.set_ylim(-.27,.27)
        ax.axhline(.25,color='gray',ls='--',lw=.6);ax.axhline(-.25,color='gray',ls='--',lw=.6)
        ax.set_xlabel('Posición longitudinal t');ax.grid(alpha=.15);ax.legend(fontsize=8)
    axes[0].set_ylabel('Desplazamiento normal / cuerda (s)')
    fig.suptitle('E16-L · h00/0/cuadrática: longitud estable, forma sin acuerdo',fontsize=12)
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None})
    if out.suffix.lower()=='.svg':
        out.write_text('\n'.join(line.rstrip() for line in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/path_comparison.svg');p.add_argument('--preview',type=Path)
    args=p.parse_args();main(args.out,args.preview)
