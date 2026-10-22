#!/usr/bin/env python3
"""Figura de tablas v2: no ejecuta optimizaciones ni recalcula Hessianos."""
import argparse,csv,os,tempfile
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'leviathan-mpl'))
os.environ.setdefault('XDG_CACHE_HOME',str(Path(tempfile.gettempdir())/'leviathan-cache'))
for key in ['MPLCONFIGDIR','XDG_CACHE_HOME']:Path(os.environ[key]).mkdir(parents=True,exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def rows(name):return list(csv.DictReader((ROOT/'results/run_v2'/name).open()))
def main(out,preview):
    energies=rows('energies.csv');paths=rows('paths.csv');spectra=rows('spectra.csv')
    plt.rcParams.update({'svg.hashsalt':'E16-Q','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(14,4),layout='constrained')
    for arm,color in [('length','#D55E00'),('energy','#0072B2')]:
        r=[next(z for z in energies if z['point']==f'Q0/{arm}/{m}') for m in [132,264]]
        axes[0].plot([132,264],[float(z['affine_arc_gap']) for z in r],'o-',color=color,label=arm)
    axes[0].set(yscale='log',xlabel='Segmentos',ylabel='Energía afín − L²/2',title='Q0: menor desigualdad de velocidad');axes[0].set_xticks([132,264]);axes[0].legend()
    for lin,color,style in [('Q0','#0072B2','-'),('Q1','#D55E00','--')]:
        r=sorted([z for z in paths if z['lineage']==lin and z['arm']=='energy'],key=lambda z:int(z['segments']))
        axes[1].plot([int(z['segments']) for z in r],[float(z['kkt_length']) for z in r],marker='o',ls=style,color=color,label=f'{lin} · KKT longitud')
        axes[1].plot([int(z['segments']) for z in r],[float(z['kkt_energy']) for z in r],marker='s',ls=':',color=color,label=f'{lin} · KKT energía')
    axes[1].axhline(1e-5,color='#555555',ls='--',label='Umbral');axes[1].set(yscale='log',xlabel='Segmentos',ylabel='Residual KKT de candidatos energy',title='Pasar energía no basta para longitud');axes[1].set_xticks([132,264]);axes[1].legend(fontsize=8)
    rr=[next(z for z in spectra if z['point']=='C0/source' and z['objective']==target) for target in ['length','arc','energy']]
    axes[2].bar(['L','L²/2','E afín'],[int(z['near_zero']) for z in rr],color=['#D55E00','#999999','#0072B2'])
    axes[2].set(ylabel='Modos casi nulos al umbral fijado',title='Control C0 · Hessianos en 132');axes[2].set_ylim(0,150)
    for j,r in enumerate(rr):axes[2].text(j,int(r['near_zero'])+3,r['near_zero'],ha='center')
    for ax in axes:ax.grid(alpha=.2,axis='y')
    fig.suptitle('E16-Q · la energía afín cambia el problema discreto; global inconcluso')
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(z.rstrip() for z in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/energy_conditioning.svg');p.add_argument('--preview',type=Path);a=p.parse_args();main(a.out,a.preview)
