"""Visualización de las ocho estimaciones ya archivadas; no contraste nuevo."""
import csv
from support_v1 import STAGE,RUN,code_guard,guard


def main():
    code_guard();guard()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=list(csv.DictReader((RUN/'estimates.csv').open()))
    pick=lambda d,m:next(r for r in rows if r['dataset']==str(d) and r['model']==m)
    ds=[0,1,2,'aggregate'];labels=['s=.25','s=.5','s=.8\nprimaria','agregado\ndescriptivo'];pos=[0,1,2,3]
    fig,axes=plt.subplots(1,2,figsize=(11,4.7),layout='constrained')
    for model,shift,color in [('B1',-.18,'#326c93'),('BR',.18,'#468c70')]:
        axes[0].bar([x+shift for x in pos],[float(pick(d,model)['D_base']) for d in ds],width=.34,color=color,label=model)
        axes[1].bar([x+shift for x in pos],[float(pick(d,model)['D']) for d in ds],width=.34,color=color,label=model)
    axes[0].set_title('Adecuación de la base');axes[0].set_ylabel('D_base frente a cero')
    axes[1].set_title('Incremento del candidato residualizado');axes[1].set_ylabel('D adicional');axes[1].axhline(.01,ls='--',lw=1,color='#777',label='umbral .01')
    for ax in axes:
        ax.set_xticks(pos,labels);ax.axhline(0,lw=.8,color='#555');ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True);ax.legend(fontsize=8)
    fig.suptitle('D9g-c · mismo test250 · ridge con CV anidada · s=.8 decide')
    folder=STAGE/'figures';folder.mkdir(exist_ok=False);fig.savefig(folder/'ridge_lectura.png',dpi=160);fig.savefig(folder/'ridge_lectura.svg');plt.close(fig)
    print('PASS: figura de resultados existentes')

if __name__=='__main__':main()
