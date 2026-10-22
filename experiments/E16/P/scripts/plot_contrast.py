#!/usr/bin/env python3
"""Contraste gráfico derivado de CSV; no evalúa objetivos ni reoptimiza."""
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
    vertices=rows('vertices.csv');paths=rows('paths.csv')
    plt.rcParams.update({'svg.hashsalt':'E16-P','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
    for arm,m,color,style,label in [('fixed',264,'#D55E00','-','Q0 · fixed 264'),('free',132,'#56B4E9','--','Q0 · free 132'),('free',264,'#0072B2','-','Q0 · free 264')]:
        r=sorted([z for z in vertices if z['lineage']=='Q0' and z['arm']==arm and int(z['segments'])==m],key=lambda z:int(z['index']))
        for ax in axes[:2]:ax.plot([float(z['t']) for z in r],[float(z['s']) for z in r],ls=style,color=color,lw=1.5,label=label)
    axes[0].set(xlabel='Coordenada longitudinal t',ylabel='Coordenada normal s',title='Candidatos completos; free inconcluso')
    axes[1].set(xlabel='Coordenada longitudinal t',ylabel='Coordenada normal s',xlim=(.975,1.002),ylim=(-.15,.01),title='Detalle: posición longitudinal liberada')
    for lin,color in [('Q0','#0072B2'),('Q1','#D55E00')]:
        for arm,style in [('fixed',':'),('free','-')]:
            r=sorted([z for z in paths if z['lineage']==lin and z['arm']==arm],key=lambda z:int(z['segments']))
            axes[2].plot([int(z['segments']) for z in r],[float(z['kkt']) for z in r],marker='o',ls=style,color=color,label=f'{lin} · {arm}')
    axes[2].axhline(1e-5,color='#555555',ls='--',label='Umbral KKT');axes[2].set(yscale='log',xlabel='Segmentos',ylabel='Residual KKT proyectado',title='free: 4800 iteraciones en ambas mallas');axes[2].set_xticks([132,264])
    for ax in axes:ax.legend(fontsize=8);ax.grid(alpha=.2)
    fig.suptitle('E16-P · cambiar la familia cambia candidatos; optimización libre pendiente')
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(z.rstrip() for z in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/representation_contrast.svg');p.add_argument('--preview',type=Path);a=p.parse_args();main(a.out,a.preview)
