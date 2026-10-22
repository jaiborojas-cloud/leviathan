#!/usr/bin/env python3
"""Figura derivada de CSV; no vuelve a optimizar ni evalúa h."""
import argparse,csv,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'leviathan-mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'leviathan-cache'))
for key in ['MPLCONFIGDIR','XDG_CACHE_HOME']:Path(os.environ[key]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def main(out,preview):
    plt.rcParams.update({'svg.hashsalt':'E16-O','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    vv=rows('vertices.csv');tt=rows('transitions.csv');tails=rows('tails.csv');mm=rows('marking.csv')
    fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained');colors=['#999999','#56B4E9','#009E73','#D55E00','#0072B2']
    for round_id,color in enumerate(colors):
        r=sorted([z for z in vv if z['lineage']=='Q0' and int(z['round'])==round_id],key=lambda z:float(z['t']))
        axes[0].plot([0]+[float(z['t']) for z in r]+[1],[0]+[float(z['s']) for z in r]+[0],color=color,label=f'R{round_id}')
    axes[0].set(xlim=(.98,.987),xlabel='Posición longitudinal t',ylabel='Desplazamiento normal / cuerda s',title='Q0: detalle de la zona refinada');axes[0].legend(fontsize=8,ncol=2)
    for lin,color,style in [('Q0','#0072B2','-'),('Q1','#D55E00','--')]:
        r=[z for z in tt if z['lineage']==lin]
        axes[1].plot([int(z['round_to']) for z in r],[float(z['hausdorff_upper']) for z in r],marker='o',ls=style,color=color,label=f'{lin} · Hausdorff')
        axes[1].plot([int(z['round_to']) for z in r],[float(z['shape_error']) for z in r],ls=':',color=color,label=f'{lin} · mismo t')
        r=[z for z in tails if z['lineage']==lin and z['cutoff']=='0.9']
        axes[2].plot([int(z['round']) for z in r],[float(z['max_euclidean_speed']) for z in r],marker='o',ls=style,color=color,label=lin)
    axes[1].axhline(.001,color='#555555',ls='--',label='Umbral 0,001');axes[1].set(yscale='log',xlabel='Ronda adaptativa',ylabel='Separación normalizada',title='Transiciones entre rondas');axes[1].set_xticks([1,2,3,4]);axes[1].legend(fontsize=8)
    axes[2].set(yscale='log',xlabel='Ronda adaptativa',ylabel='Máxima velocidad euclídea / cuerda',title='Pendiente creciente cerca de t≈0,9844');axes[2].set_xticks([0,1,2,3,4]);axes[2].legend()
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('E16-O · Hausdorff pasa; forma e indicador local siguen pendientes')
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(z.rstrip() for z in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/adaptive_comparison.svg');p.add_argument('--preview',type=Path);a=p.parse_args();main(a.out,a.preview)
