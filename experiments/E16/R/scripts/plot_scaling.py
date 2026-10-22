#!/usr/bin/env python3
"""Todos los casos cuadráticos desde CSV; no reoptimiza ni calcula Hessianos."""
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
def main(out,preview):
    paths=list(csv.DictReader((ROOT/'results/run_v1/paths.csv').open()))
    plt.rcParams.update({'svg.hashsalt':'E16-R','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained');groups=[('Q0',132),('Q0',264),('Q1',132),('Q1',264)];x=np.arange(4)
    for arm,color,offset in [('reference','#D55E00',-.18),('scaled','#0072B2',.18)]:
        rows=[next(z for z in paths if z['lineage']==lin and z['arm']==arm and int(z['segments'])==m) for lin,m in groups]
        axes[0].bar(x+offset,[float(z['physical_kkt']) for z in rows],width=.34,color=color,label=arm)
        axes[1].bar(x+offset,[int(z['nfev']) for z in rows],width=.34,color=color,label=arm)
    axes[0].set_yscale('log');axes[0].axhline(1e-5,color='#555555',ls='--',label='Umbral físico');axes[0].set(ylabel='Residual KKT en coordenadas físicas',title='Umbral KKT: scaled 4/4; reference 2/4')
    axes[1].set(ylabel='Evaluaciones del objetivo L',title='Sin incluir preparación del precondicionador',ylim=(0,6000))
    for ax in axes:ax.set_xticks(x,[f'{lin}\n{m} segmentos' for lin,m in groups]);ax.legend(fontsize=8);ax.grid(alpha=.2,axis='y')
    fig.suptitle('E16-R · los ocho candidatos cuadráticos agotan 4800 iteraciones')
    out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out,metadata={'Date':None});out.write_text('\n'.join(z.rstrip() for z in out.read_text().splitlines())+'\n')
    if preview:fig.savefig(preview,dpi=140)
    plt.close(fig)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'figures/scaling_comparison.svg');p.add_argument('--preview',type=Path);a=p.parse_args();main(a.out,a.preview)
