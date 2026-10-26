"""Ridge anidado y c residualizada: selección repetida, sin información retenida."""
import numpy as np
from support_v1 import CFG
from dictionary_v1 import center,design

LAM=np.array(CFG['lambda_grid'])


def folds(split,k=10,seed=None):
    seed=CFG['fold_seed'] if seed is None else seed
    order=np.random.default_rng(seed).permutation(np.unique(split));m={s:i%k for i,s in enumerate(order)}
    return np.array([m[s] for s in split])


def pinv(B):return np.linalg.pinv(B,rcond=np.finfo(float).eps*max(B.shape))


def choose(scores):return int(np.flatnonzero(scores==np.min(scores))[-1])


class InnerCV:
    def __init__(self,cheap,extra,group,split,y):
        self.n=len(y);self.data=[]
        fo=folds(split,5,CFG['inner_fold_seed'])
        for k in range(5):
            tr,va=fo!=k,fo==k;B,meta=design(cheap,extra,group,tr,4)
            u,s,vt=np.linalg.svd(B[tr],full_matrices=False)
            self.data.append(dict(Bv=B[va],s=s,vt=vt,uy=u.T@y[tr],yv=y[va],n=int(tr.sum()),frame=meta))

    def score(self):
        scores=np.zeros(len(LAM))
        for d in self.data:
            filt=d['s'][:,None]/(d['s'][:,None]**2+d['n']*LAM[None,:])
            beta=d['vt'].T@(filt*d['uy'][:,None])
            err=d['yv'][:,None]-d['Bv']@beta;scores+=np.sum(err*err,axis=0)
        return scores

    def repeated_selection(self,repeats):
        all_scores=np.empty((repeats,len(LAM)));indices=np.empty(repeats,dtype=int)
        # Recalcula TODOS los 33 scores y argmin en cada pipeline, no fija lambda.
        for j in range(repeats):
            all_scores[j]=self.score();indices[j]=choose(all_scores[j])
        return LAM[indices],all_scores


def uncached_selection(cheap,extra,group,split,y):
    """Reajusta términos y resuelve 33 sistemas por subbloque desde cero."""
    fo=folds(split,5,CFG['inner_fold_seed']);scores=np.zeros(len(LAM))
    for k in range(5):
        tr,va=fo!=k,fo==k;B,_=design(cheap,extra,group,tr,4)
        gram=B[tr].T@B[tr];rhs=B[tr].T@y[tr]
        for j,lam in enumerate(LAM):
            be=np.linalg.solve(gram+tr.sum()*lam*np.eye(B.shape[1]),rhs)
            err=y[va]-B[va]@be;scores[j]+=err@err
    return float(LAM[choose(scores)]),scores


def ridge_coeff(B,y,lambdas):
    u,s,vt=np.linalg.svd(B,full_matrices=False)
    return vt.T@((s[:,None]/(s[:,None]**2+len(y)*lambdas[None,:]))*(u.T@y)[:,None])


def residual_candidate(B,tr,X):
    A=pinv(B[tr])@X[tr];R=X-B@A
    ratio=np.sqrt(np.sum(R[tr]**2,axis=0)/np.maximum(np.sum(X[tr]**2,axis=0),np.finfo(float).tiny))
    return R,ratio<=CFG['alias_tol'],ratio


def run_cv(group,split,cheap,extra,X,Y,permutations=999,direct=False,check_uncached=False):
    y=center(Y,group);fo=folds(split);n=len(y);m=permutations+1
    C=np.empty((n,m));C[:,0]=center(X,group)
    rng=np.random.default_rng(CFG['permutation_seed']);ids=[np.flatnonzero(group==g) for g in np.unique(group)]
    for b in range(permutations):
        xp=X.copy()
        for ix in ids:xp[ix]=X[rng.permutation(ix)]
        C[:,b+1]=xp
    if permutations:C[:,1:]=center(C[:,1:],group)
    sbase={'B1':np.zeros(m),'BR':np.zeros(m)};sfull={k:np.zeros(m) for k in sbase}
    pred_base={k:np.empty((n,m)) for k in sbase};pred_full={k:np.empty((n,m)) for k in sbase}
    lambda_choices=np.empty((10,m));lambda_scores=np.empty((10,m,len(LAM)));frames=[];uncached=[];alias_counts={k:np.zeros(m,dtype=int) for k in sbase}
    for k in range(10):
        tr,te=fo!=k,fo==k
        cache=InnerCV(cheap[tr],extra[tr],group[tr],split[tr],y[tr])
        lambdas,scores=cache.repeated_selection(m);lambda_choices[k]=lambdas;lambda_scores[k]=scores
        if check_uncached:
            for b in [j for j in [0,1,2] if j<m]:
                lam0,sc0=uncached_selection(cheap[tr],extra[tr],group[tr],split[tr],y[tr])
                err=float(np.max(np.abs(sc0-scores[b])/np.maximum(np.abs(sc0),np.finfo(float).tiny)))
                uncached.append(dict(fold=k,permutation=b,lambda_equal=lam0==lambdas[b],max_relative_score_error=err))
        B4,meta4=design(cheap,extra,group,tr,4);B1,meta1=design(cheap,extra,group,tr,1)
        frames.append(dict(fold=k,BR=meta4,B1=meta1,lambda_observed=float(lambdas[0]),inner_frames=[d['frame'] for d in cache.data]))
        for name,B in [('B1',B1),('BR',B4)]:
            R,alias,ratio=residual_candidate(B,tr,C);alias_counts[name]+=alias
            if name=='B1':coef=np.repeat((pinv(B[tr])@y[tr])[:,None],m,axis=1)
            else:coef=ridge_coeff(B[tr],y[tr],lambdas)
            base_train=B[tr]@coef;base_test=B[te]@coef
            denom=np.sum(R[tr]**2,axis=0)
            gamma=np.sum(R[tr]*(y[tr,None]-base_train),axis=0)/np.where(alias,np.inf,denom)
            full_test=base_test+R[te]*gamma[None,:]
            if direct:
                for j in range(m):
                    if alias[j]:full_test[:,j]=base_test[:,j];continue
                    T=np.column_stack([B[tr],R[tr,j]])
                    if name=='BR':
                        penalty=np.column_stack([np.sqrt(tr.sum()*lambdas[j])*np.eye(B.shape[1]),np.zeros(B.shape[1])])
                        T=np.vstack([T,penalty]);target=np.r_[y[tr],np.zeros(B.shape[1])]
                    else:target=y[tr]
                    bet=np.linalg.lstsq(T,target,rcond=None)[0]
                    full_test[:,j]=np.column_stack([B[te],R[te,j]])@bet
            pred_base[name][te]=base_test;pred_full[name][te]=full_test
            sbase[name]+=np.sum((y[te,None]-base_test)**2,axis=0)
            sfull[name]+=np.sum((y[te,None]-full_test)**2,axis=0)
    s0=float(y@y)
    if s0<=0:raise FloatingPointError('Desenlace sin variación intra-grupo')
    Dbase={name:1-sbase[name]/s0 for name in sbase}
    Ds={name:1-sfull[name]/sbase[name] for name in sbase}
    adequate=Dbase['BR']>=Dbase['B1']-CFG['adequacy_tolerance']
    Ds['reading']=np.where(adequate,Ds['BR'],Ds['B1'])
    p={name:float((1+np.sum(d[1:]>=d[0]-CFG['tie_tolerance']))/m) if permutations else None for name,d in Ds.items()}
    return dict(D={name:float(d[0]) for name,d in Ds.items()},p=p,D_base={name:float(d[0]) for name,d in Dbase.items()},
        all_D=Ds,SSE_base=sbase,SSE_full=sfull,SSE_null=s0,base_predictions=pred_base,full_predictions=pred_full,
        adequate_all=adequate,reading='BR' if adequate[0] else 'B1',lambda_choices=lambda_choices,lambda_scores=lambda_scores,frames=frames,
        uncached_checks=uncached,alias_counts=alias_counts,selection_calls=10*m)


def full_beta(group,split,cheap,extra,X,Y,name):
    y=center(Y,group);xc=center(X,group);B,meta=design(cheap,extra,group,np.ones(len(y),bool),4 if name=='BR' else 1)
    if name=='BR':
        lam,scores=InnerCV(cheap,extra,group,split,y).repeated_selection(1)
        coef=ridge_coeff(B,y,lam)[:,0];lambda0=float(lam[0])
    else:coef=pinv(B)@y;lambda0=None
    R,alias,ratio=residual_candidate(B,np.ones(len(y),bool),xc[:,None]);r=R[:,0]
    beta=None if alias[0] else float(r@(y-B@coef)/(r@r))
    return dict(beta=beta,alias=bool(alias[0]),residual_relative_norm=float(ratio[0]),lambda_selected=lambda0,frame=meta)


def estimate(group,split,cheap,extra,X,Y,permutations=999,check_uncached=False):
    cv=run_cv(group,split,cheap,extra,X,Y,permutations,check_uncached=check_uncached)
    models={}
    halves=[]
    for parity in [0,1]:
        m=split%2==parity
        hcv=run_cv(group[m],split[m],cheap[m],extra[m],X[m],Y[m],0)
        halves.append(dict(parity=parity,n=int(m.sum()),cv=hcv,beta={name:full_beta(group[m],split[m],cheap[m],extra[m],X[m],Y[m],name) for name in ['B1','BR']}))
    for name in ['B1','BR']:
        coeff=full_beta(group,split,cheap,extra,X,Y,name)
        hs=[dict(parity=h['parity'],n=h['n'],D=h['cv']['D'][name],D_base=h['cv']['D_base'][name],**h['beta'][name]) for h in halves]
        stable=coeff['beta'] is not None and all(h['beta'] is not None for h in hs) and hs[0]['beta']*hs[1]['beta']>0 and hs[0]['beta']*coeff['beta']>0
        models[name]=dict(D=cv['D'][name],p=cv['p'][name],D_base=cv['D_base'][name],coefficient=coeff,halves=hs,half_sign_stable=bool(stable),
            meets=bool(cv['D'][name]>.01 and cv['p'][name] is not None and cv['p'][name]<.05 and stable))
    return dict(models=models,reading=cv['reading'],cv=cv)
