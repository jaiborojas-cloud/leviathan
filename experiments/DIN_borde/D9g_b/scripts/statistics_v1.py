"""Bases de polinomios ajustadas por bloque y FWL/OLS, sin tuning externo."""
import numpy as np
from support_v1 import CFG


def center(a,group):
    z=np.array(a,dtype=float,copy=True)
    for s in np.unique(group):z[group==s]-=z[group==s].mean(axis=0)
    return z


def folds(split):
    order=np.random.default_rng(CFG['fold_seed']).permutation(np.unique(split));m={s:i%10 for i,s in enumerate(order)}
    return np.array([m[s] for s in split])


def design(cheap,extra,group,train,base):
    mean=cheap[train].mean(0);std=cheap[train].std(0);std=np.where(std==0,1.,std)
    z=(cheap-mean)/std
    columns=[z];names=['q0','q1','q2','q3']
    if base>=2:
        columns.extend([z*z,z*z*z]);names += [f'q{i}^2' for i in range(4)]+[f'q{i}^3' for i in range(4)]
    if base>=3:
        columns.append(np.column_stack([z[:,i]*z[:,j] for i in range(4) for j in range(i+1,4)]));names += [f'q{i}q{j}' for i in range(4) for j in range(i+1,4)]
    emean=estd=None
    if base>=4:
        emean=extra[train].mean(0);estd=extra[train].std(0);estd=np.where(estd==0,1.,estd)
        columns.append((extra-emean)/estd);names+=['margin','entropy','weight_norm']
    matrix=center(np.column_stack(columns),group)
    scale=np.sqrt(np.mean(matrix[train]**2,axis=0));scale=np.where(scale==0,1.,scale);matrix/=scale
    sv=np.linalg.svd(matrix[train],compute_uv=False);tol=np.finfo(float).eps*max(matrix[train].shape)*(sv[0] if len(sv) else 0)
    rank=int(np.sum(sv>tol));cond=float(sv[0]/sv[rank-1]) if rank else None
    metadata=dict(mean=mean,std=std,extra_mean=emean,extra_std=estd,term_scale=scale,columns=names,rank=rank,condition_nonzero=cond,n_train=int(train.sum()))
    return matrix,metadata


def _pinv(B):return np.linalg.pinv(B,rcond=np.finfo(float).eps*max(B.shape))


def compute(group,split,cheap,extra,X,Y,base,permutations=2000,negative=False,direct=False):
    yc=center(Y,group);xc=center(X,group);fo=folds(split)
    raw=np.empty((len(X),permutations+1));raw[:,0]=xc
    rng=np.random.default_rng(CFG['permutation_seed']);ids=[np.flatnonzero(group==s) for s in np.unique(group)]
    for b in range(permutations):
        xp=X.copy()
        for ix in ids:xp[ix]=X[rng.permutation(ix)]
        raw[:,b+1]=xp
    if permutations:raw[:,1:]=center(raw[:,1:],group)
    sb=0.;sf=np.zeros(permutations+1);frames=[];aliases=[];fallbacks=0
    for k in range(10):
        tr,te=fo!=k,fo==k;B,meta=design(cheap,extra,group,tr,base);frames.append(dict(fold=k,**meta))
        C=raw.copy()
        if negative:
            if permutations:raise ValueError('Control de alias sin p interpretativa')
            C[:,0]=B@np.linalg.lstsq(B[tr],xc[tr],rcond=None)[0]
        scales=np.sqrt(np.mean(C[tr]**2,axis=0));scales=np.where(scales==0,1.,scales);C/=scales
        P=_pinv(B[tr]);e=yc[te]-B[te]@(P@yc[tr]);sbase=float(e@e);sb+=sbase
        coef=P@C[tr];rt=C[tr]-B[tr]@coef;re=C[te]-B[te]@coef
        den=np.sum(rt**2,axis=0);relative=np.sqrt(den/np.maximum(np.sum(C[tr]**2,axis=0),np.finfo(float).tiny))
        aliases.append(float(relative[0]))
        if direct:
            for j in range(permutations+1):
                full=np.column_stack([B,C[:,j]]);beta=np.linalg.lstsq(full[tr],yc[tr],rcond=None)[0]
                err=yc[te]-full[te]@beta;sf[j]+=err@err
        else:
            bad=relative<=CFG['alias_tol'];safe=np.where(bad,np.inf,den)
            beta=(rt.T@yc[tr])/safe
            addition=sbase-2*beta*(re.T@e)+beta*beta*np.sum(re*re,axis=0)
            for j in np.flatnonzero(bad):
                full=np.column_stack([B,C[:,j]]);be=np.linalg.lstsq(full[tr],yc[tr],rcond=None)[0]
                err=yc[te]-full[te]@be;addition[j]=err@err;fallbacks+=1
            sf+=addition
    if sb<=0:raise FloatingPointError('SSE_base<=0')
    Ds=1-sf/sb;p=float((1+np.sum(Ds[1:]>=Ds[0]-CFG['tie_tol']))/(1+permutations)) if permutations else None
    Ball,whole=design(cheap,extra,group,np.ones(len(X),bool),base)
    rx=xc-Ball@np.linalg.lstsq(Ball,xc,rcond=None)[0]
    full_alias=bool(np.linalg.norm(rx)<=CFG['alias_tol']*max(np.linalg.norm(xc),np.finfo(float).tiny))
    beta=float(np.linalg.lstsq(np.column_stack([Ball,xc]),yc,rcond=None)[0][-1])
    return dict(D=float(Ds[0]),p=p,beta=None if negative or full_alias else beta,all_D=Ds,SSE_full=sf,SSE_base=sb,
        D_base=float(1-sb/(yc@yc)) if yc@yc>0 else None,frames=frames,whole_frame=whole,
        aliases=aliases,full_alias=bool(full_alias or negative),fallbacks=fallbacks)


def estimate(group,split,cheap,extra,X,Y,base):
    ans=compute(group,split,cheap,extra,X,Y,base)
    halves=[]
    for parity in [0,1]:
        m=split%2==parity;r=compute(group[m],split[m],cheap[m],extra[m],X[m],Y[m],base,0)
        halves.append(dict(parity=parity,n=int(m.sum()),D=r['D'],beta=r['beta'],alias=r['full_alias']))
    stable=not ans['full_alias'] and all(h['beta'] is not None for h in halves) and halves[0]['beta']*halves[1]['beta']>0 and halves[0]['beta']*ans['beta']>0
    ans.update(halves=halves,half_sign_stable=bool(stable),meets=bool(ans['D']>.01 and ans['p']<.05/4 and stable))
    return ans
