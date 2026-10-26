"""OLS/C1 con base lineal barata y FWL vectorizado, preservando cada permutación."""
import math
import numpy as np
from support_v1 import CFG


def centered(values,groups):
    ans=np.array(values,dtype=float,copy=True)
    for g in np.unique(groups):ans[groups==g]-=ans[groups==g].mean(axis=0)
    return ans


def folds(split):
    order=np.random.default_rng(CFG['fold_seed']).permutation(np.unique(split))
    assign={s:i%10 for i,s in enumerate(order)}
    return np.array([assign[s] for s in split])


def setup(group,split,B,X,Y):
    yc=centered(Y,group)
    bc=centered(B,group);scaleB=np.sqrt(np.mean(bc**2,axis=0));scaleB=np.where(scaleB==0,1.,scaleB)
    bc/=scaleB
    xc=centered(X,group);scaleX=float(np.sqrt(np.mean(xc**2)))
    xnorm=xc/scaleX if scaleX else xc.copy()
    rx=xnorm-bc@np.linalg.lstsq(bc,xnorm,rcond=None)[0]
    alias=float(np.linalg.norm(rx)/max(np.linalg.norm(xnorm),np.finfo(float).tiny))<=CFG['alias_relative_rms_tol']
    return yc,bc,xnorm,folds(split),scaleB,scaleX,alias


def cv_losses(Y,B,X,fo):
    if Y.ndim==1:Y=Y[:,None]
    sb=np.zeros(Y.shape[1]);sf=sb.copy()
    C=np.column_stack([B,X])
    for k in range(10):
        tr,te=fo!=k,fo==k
        eb=Y[te]-B[te]@np.linalg.lstsq(B[tr],Y[tr],rcond=None)[0]
        ef=Y[te]-C[te]@np.linalg.lstsq(C[tr],Y[tr],rcond=None)[0]
        sb+=np.sum(eb**2,axis=0);sf+=np.sum(ef**2,axis=0)
    return sb,sf


def engine(group,split,B,X,Y,index,Bperm=None):
    if Y.ndim==1:Y=Y[:,None]
    Bperm=CFG['permutations'] if Bperm is None else Bperm
    yc,bc,xc,fo,scaleB,scaleX,alias=setup(group,split,B,X,Y)
    group_ids=[np.flatnonzero(group==g) for g in np.unique(group)]
    rng=np.random.default_rng(CFG['permutation_seed_base']+index)
    candidates=np.empty((len(X),Bperm+1));candidates[:,0]=xc
    for b in range(Bperm):
        xp=X.copy()
        for ids in group_ids:xp[ids]=X[rng.permutation(ids)]
        candidates[:,b+1]=xp
    if Bperm:
        candidates[:,1:]=centered(candidates[:,1:],group)
        if scaleX:candidates[:,1:]/=scaleX
    sb=np.zeros(Y.shape[1]);sf=np.zeros((Bperm+1,Y.shape[1]));fallback=0
    for k in range(10):
        tr,te=fo!=k,fo==k
        Bt,Be=bc[tr],bc[te]
        P=np.linalg.pinv(Bt,rcond=np.finfo(float).eps*max(Bt.shape))
        coeff=P@candidates[tr]
        rt=candidates[tr]-Bt@coeff;re=candidates[te]-Be@coeff
        den=np.sum(rt**2,axis=0)
        tol=(np.finfo(float).eps*max(Bt.shape))**2*np.maximum(np.sum(candidates[tr]**2,axis=0),1e-300)
        bad=den<=tol;safe=np.where(bad,np.inf,den)
        ey=yc[te]-Be@(P@yc[tr]);base=np.sum(ey**2,axis=0)
        beta=(rt.T@yc[tr])/safe[:,None]
        sf+=base[None,:]-2*beta*(re.T@ey)+beta**2*np.sum(re**2,axis=0)[:,None]
        sb+=base
        for j in np.flatnonzero(bad):
            C=np.column_stack([bc,candidates[:,j]])
            coef=np.linalg.lstsq(C[tr],yc[tr],rcond=None)[0]
            exact=np.sum((yc[te]-C[te]@coef)**2,axis=0)
            approximate=base-2*beta[j]*(re[:,j]@ey)+beta[j]**2*np.sum(re[:,j]**2)
            sf[j]+=exact-approximate;fallback+=1
    sse0=np.sum(yc**2,axis=0)
    with np.errstate(divide='ignore',invalid='ignore'):
        all_D=1-sf/sb
        p=(1+np.sum(all_D[1:]>=all_D[:1]-CFG['tie_tolerance'],axis=0))/(Bperm+1)
        Dbase=1-sb/sse0
    _,sse_x=cv_losses(yc,np.empty((len(X),0)),xc,fo)
    with np.errstate(divide='ignore',invalid='ignore'):Dalone=1-sse_x/sse0
    betas=np.linalg.lstsq(np.column_stack([bc,xc]),yc,rcond=None)[0][-1]
    if scaleX:betas/=scaleX
    half=[]
    for parity in [0,1]:
        mask=split%2==parity
        yh,bh,xh,fh,_,sx,ah=setup(group[mask],split[mask],B[mask],X[mask],Y[mask])
        a,b=cv_losses(yh,bh,xh,fh)
        slopes=np.linalg.lstsq(np.column_stack([bh,xh]),yh,rcond=None)[0][-1]
        if sx:slopes/=sx
        with np.errstate(divide='ignore',invalid='ignore'):dh=1-b/a
        half.append(dict(parity=parity,n=int(mask.sum()),D=dh,beta=slopes,alias=ah))
    return dict(D=all_D[0],p=p,beta=betas,D_base=Dbase,D_candidate_alone=Dalone,
        all_D=all_D,SSE_base=sb,SSE_full=sf,SSE_null=sse0,halves=half,
        base_scale=scaleB,candidate_scale=scaleX,alias=alias,
        candidate_constant=bool(np.allclose(centered(X,group),0,atol=CFG['candidate_variation_atol'])),
        fallbacks=fallback)


def direct_null(group,split,B,X,Y,index,Bperm):
    """OLS independiente: todos los ajustes completos; no usa engine ni FWL."""
    yc,bc,xc,fo,_,sx,_=setup(group,split,B,X,Y)
    if yc.ndim==1:yc=yc[:,None]
    result=[];losses=[]
    order=[np.flatnonzero(group==s) for s in np.unique(group)]
    rng=np.random.default_rng(CFG['permutation_seed_base']+index)
    for j in range(Bperm+1):
        if j==0:xx=xc
        else:
            xx=X.copy()
            for ix in order:xx[ix]=X[rng.permutation(ix)]
            xx=centered(xx,group)
            if sx:xx/=sx
        sb,sf=cv_losses(yc,bc,xx,fo)
        result.append(1-sf/sb);losses.append(sf)
    ds=np.array(result)
    p=(1+np.sum(ds[1:]>=ds[:1]-CFG['tie_tolerance'],axis=0))/(Bperm+1)
    return dict(all_D=ds,p=p,SSE_full=np.array(losses))
