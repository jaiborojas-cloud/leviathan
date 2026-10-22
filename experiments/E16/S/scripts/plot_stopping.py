#!/usr/bin/env python3
"""Auditorías discretas y comparación histórica desde CSV guardados."""
import argparse,csv,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'leviathan-mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'leviathan-cache'))
for key in ['MPLCONFIGDIR','XDG_CACHE_HOME']:Path(os.environ[key]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((ROOT/'results/run_v1'/name).open()))
def main(out,preview):
    audits=rows('audits.csv');paths=rows('paths.csv');historical=rows('historical.csv')
    plt.rcParams.update({'svg.hashsalt':'E16-S','font.size':9,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(15,4.4),layout='constrained')
    styles=[('Q0','reference','#D55E00','o'),('Q0','scaled','#0072B2','s'),('Q1','reference','#CC79A7','^'),('Q1','scaled','#009E73','x')]
    for ax,m in zip(axes[:2],[132,264]):
        for lin,arm,color,marker in styles:
            name=f'{lin}/{arm}/{m}';r=[z for z in audits if z['path']==name and z['verified']=='True']
            ax.scatter([int(z['iteration']) for z in r],[float(z['physical_kkt']) for z in r],s=22,c=color,marker=marker,label=f'{lin} · {arm}',alpha=.75)
            stop=[z for z in r if z['stop_requested']=='True']
            if stop:ax.scatter([int(z['iteration']) for z in stop],[float(z['physical_kkt']) for z in stop],s=95,c=color,marker='*',edgecolors='black',linewidths=.5)
        unknown=sum(z['verified']!='True' for z in audits if z['path'].endswith('/'+str(m)))
        if unknown:ax.text(.02,.97,f'{unknown} auditorías no verificadas: consultar CSV',transform=ax.transAxes,va='top',fontsize=8)
        ax.axhline(1e-5,color='#555555',ls='--');ax.set(yscale='log',xlim=(-100,4900),xlabel='Iteraciones aceptadas',ylabel='KKT físico MP',title=f'{m} segmentos · ★ parada auditada');ax.legend(fontsize=7)
    groups=[('Q0','reference'),('Q0','scaled'),('Q1','reference'),('Q1','scaled')];x=np.arange(4)
    previous=[sum(int(z['R_iterations']) for z in historical if z['comparison'].startswith(f'{lin}/{arm}/')) for lin,arm in groups]
    current=[sum(int(z['iterations']) for z in paths if z['lineage']==lin and z['arm']==arm) for lin,arm in groups]
    axes[2].bar(x-.18,previous,.34,label='R archivado',color='#999999');axes[2].bar(x+.18,current,.34,label='S monitorizado',color='#0072B2')
    axes[2].set_xticks(x,[f'{lin}\n{arm}' for lin,arm in groups]);axes[2].set(ylabel='Suma de iteraciones 132 + 264',title='Comparación histórica, no de tiempo total');axes[2].legend(fontsize=8)
    for ax in axes:ax.grid(alpha=.2,axis='y')
    fig.suptitle('E16-S · comprobaciones muestreadas; no garantizan el intervalo entre muestras')
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(z.rstrip() for z in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/audited_stopping.svg');p.add_argument('--preview',type=Path);a=p.parse_args();main(a.out,a.preview)
