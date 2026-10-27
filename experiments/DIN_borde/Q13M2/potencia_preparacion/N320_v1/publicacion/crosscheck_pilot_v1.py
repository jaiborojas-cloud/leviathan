"""Contraste adicional del motor con covariables piloto y respuestas SIMULADAS."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[6]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/potencia_preparacion/N320_v1'
sys.path.insert(0,str(STAGE/'scripts'))
from support import CFG,OUT,sha,write,code_guard,guard,source_path,analyst,engine


def main():
    code_guard()
    assert Path(__file__).read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(Path(__file__).relative_to(ROOT))],cwd=ROOT)
    guard();M=analyst();Engine,cen,_=engine();p=json.loads((OUT/'pilot.json').read_text())
    with source_path('pilot').open() as f:rr=sorted([r for r in csv.DictReader(f) if int(r['level'])==2],key=lambda r:(int(r['split']),int(r['k'])))
    Xp=np.array([float(r['X10']) for r in rr]);Lp=np.log([float(r['rho_caras_10']) for r in rr]);records=[]
    for rho,frame in [(0.,0),(.615,3)]:
        rec=json.loads((OUT/f'rho{rho:g}_N320_frame{frame}.json').read_text());assert sha(rec['array']['path'])==rec['array']['sha256']
        with np.load(rec['array']['path'],allow_pickle=False) as z:
            n=CFG['N'];ix=(z['pilot_draw'][:,None]*5+np.arange(5)).ravel();X,L=Xp[ix],Lp[ix];sp=np.repeat(np.arange(n),5)
            e=Engine(sp,X,L,B=0)
            noise=np.sqrt(rho)*z['normal_noise'][:,0:1,0]+np.sqrt(1-rho)*z['normal_noise'][:,1:,0]
            Y=(e.base@np.array(p['alpha']))[:,None]+e.residual_X[:,None]*z['multipliers'][None,:]+np.sqrt(p['sigma2'])*cen(noise,sp)
            err=max(abs(M.Q.D_punto(sp,X,L,Y[:,l])-z['D'][l,0]) for l in range(11))
            ref=M.A.primaria(sp,X,L,Y[:,0],3,260001,1999);psame=ref['p']==float(z['p'][0,0])
            blq=M.Q.bloques(np.arange(n));berr=0.
            for b in range(8):
                draw=z['bootstrap_draw'][b];ii=(draw[:,None]*5+np.arange(5)).ravel();news=np.repeat(np.arange(n),5);fo=np.repeat([blq[s] for s in draw],5)
                for l in range(11):berr=max(berr,abs(M.Q.D_punto(news,X[ii],L[ii],Y[ii,l],fo)-z['bootstrap_D'][b,l,0]))
            records.append(dict(N=n,rho=rho,frame=frame,response_replica=0,bootstrap_draws_checked=8,
                max_point_D_error=float(err),max_bootstrap_D_error=float(berr),A0_p_identical=bool(psame),
                pass_test=bool(err<=1e-10 and berr<=1e-10 and psame)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,
                scope='Covariables G3 piloto, respuestas reconstruidas solo de normales simuladas archivadas; ningún D de cohorte real',
                simulated_replicates_added=0,power_counts_changed=False)
    write(OUT/'crosscheck_pilot_simulated.json',result)
    if result['status']!='PASS':raise RuntimeError('Contraste numérico fallido; no aceptar potencia')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
