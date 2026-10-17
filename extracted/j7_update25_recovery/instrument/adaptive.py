import numpy as np
from geometry import children,quadrature,measures

def integrate(geo,t,max_rounds=18,tol=0.0005,verbose=None,area_only=False):
    q=quadrature(geo,t)
    c=children(t); qc=quadrature(geo,c).reshape(-1,4,3)
    history=[]; stable=0; prev=None
    for it in range(max_rounds+1):
        sums=qc[:,:,:2].sum(1)
        err=np.abs(sums-q[:,:2]); total=sums.sum(0)
        m=measures(qc.reshape(-1,3))
        m.update(round=it,energy_error_est=float(err[:,1].sum()/total[1]),area_error_est=float(err[:,0].sum()/total[0]))
        if prev is None: delta=np.inf; conc=np.inf
        else:
            delta=abs(m['C_A']/prev['C_A']-1)
            conc=max(abs(m[k]-prev[k]) for k in ['lambda_1pct','lambda_01pct','frac50','frac90'])
            conc=max(conc,abs(m['R_eff']/prev['R_eff']-1))
        m.update(relative_change_C=delta,concentration_change=conc)
        history.append(m)
        if verbose: verbose(m)
        score=err[:,0]/total[0] if area_only else np.maximum(err[:,1]/total[1],err[:,0]/total[0])
        # Require globally estimated error, two stable rounds, and concentration stability.
        passed=(m['area_error_est']<tol if area_only else m['energy_error_est']<tol and delta<tol and conc<0.001)
        stable=stable+1 if passed else 0
        if (stable>=2 or it==max_rounds or len(c)>1200000): break
        order=np.argsort(-score)
        count=np.searchsorted(np.cumsum(score[order]),.8*score.sum())+1
        sel=order[:max(1,count)]
        keep=np.ones(len(t),bool); keep[sel]=False
        newt=c.reshape(-1,4,3,2)[sel].reshape(-1,3,2); newq=qc[sel].reshape(-1,3)
        newc=children(newt); newqc=quadrature(geo,newc).reshape(-1,4,3)
        t=np.concatenate([t[keep],newt]); q=np.concatenate([q[keep],newq])
        c=np.concatenate([c.reshape(-1,4,3,2)[keep].reshape(-1,3,2),newc]); qc=np.concatenate([qc[keep],newqc])
        prev=m
    return m,history,c,qc.reshape(-1,3)
