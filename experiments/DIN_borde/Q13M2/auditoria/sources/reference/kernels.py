"""Álgebra independiente: C1 por FWL y bootstrap de splits sin fuga."""
import numpy as np


def center(x):
    n=x.shape[0]//5
    shape=(n,5)+x.shape[1:]
    g=x.reshape(shape)
    return (g-g.mean(axis=1,keepdims=True)).reshape(x.shape)


def basis(L):
    z=(L-L.mean())/L.std()
    return np.column_stack([center(z**k) for k in (1,2,3)])


def folds(n):
    perm=np.random.default_rng(260010).permutation(np.arange(n))
    f=np.empty(n,int);f[perm]=np.arange(n)%10
    return np.repeat(f,5)


def permutation_indices(n,count):
    rng=np.random.default_rng(260001)
    out=np.empty((count+1,5*n),np.int32);out[0]=np.arange(5*n)
    groups=[np.arange(5*s,5*s+5) for s in range(n)]
    for b in range(count):
        for s,g in enumerate(groups):out[b+1,5*s:5*s+5]=rng.permutation(g)
    return out


def primary(X,L,Y,indices):
    n=len(X)//5;B=basis(L);yc=center(Y)
    xp=X[indices].reshape(len(indices),n,5)
    xp=(xp-xp.mean(axis=2,keepdims=True)).reshape(len(indices),5*n).T
    f=folds(n);sb=np.zeros(Y.shape[1]);sf=np.zeros((len(indices),Y.shape[1]))
    for k in range(10):
        tr=f!=k;te=~tr;P=np.linalg.pinv(B[tr])
        ax=P@xp[tr];rx=xp[tr]-B[tr]@ax;zx=xp[te]-B[te]@ax
        den=np.sum(rx*rx,axis=0)
        if np.any(den<=1e-25):raise FloatingPointError('Candidato degenerado en motor MC')
        gamma=(rx.T@yc[tr])/den[:,None]
        e=yc[te]-B[te]@(P@yc[tr]);base=np.sum(e*e,axis=0)
        sb+=base;sf+=base[None,:]-2*gamma*(zx.T@e)+gamma*gamma*np.sum(zx*zx,axis=0)[:,None]
    D=1-sf/sb[None,:]
    slope=np.linalg.lstsq(np.column_stack([B,center(X)]),yc,rcond=None)[0][-1]
    p=(1+np.sum(D[1:]>=D[:1]-1e-15,axis=0))/len(indices)
    return dict(D=D[0],p=p,slope=slope,all_D=D,base_SSE=sb)


def bootstrap(X,L,Y,draws):
    n=len(X)//5;nb=len(draws);responses=Y.shape[1]
    B=basis(L);q,_=np.linalg.qr(B);xb=center(X)-B@np.linalg.lstsq(B,center(X),rcond=None)[0]
    C=np.column_stack([q*np.sqrt(5*n),xb/np.sqrt(np.mean(xb*xb))]).reshape(n,5,4)
    yc=center(Y).reshape(n,5,responses)
    gram=np.einsum('nki,nkj->nij',C,C);h=np.einsum('nki,nkr->nir',C,yc);yy=np.sum(yc*yc,axis=1)
    weights=np.zeros((nb,n))
    for b,draw in enumerate(draws):weights[b]=np.bincount(draw,minlength=n)
    G=(weights@gram.reshape(n,16)).reshape(nb,4,4)
    H=(weights@h.reshape(n,4*responses)).reshape(nb,4,responses)
    f=folds(n).reshape(n,5)[:,0];errors=[np.zeros((nb,responses)),np.zeros((nb,responses))]
    for k in range(10):
        wt=weights*(f==k)[None,:]
        ge=(wt@gram.reshape(n,16)).reshape(nb,4,4);he=(wt@h.reshape(n,4*responses)).reshape(nb,4,responses);ye=wt@yy
        for j,d in enumerate((3,4)):
            coeff=np.linalg.solve((G-ge)[:,:d,:d],(H-he)[:,:d])
            errors[j]+=ye-2*np.sum(coeff*he[:,:d],axis=1)+np.einsum('bir,bij,bjr->br',coeff,ge[:,:d,:d],coeff)
    if np.any(errors[0]<=0):raise FloatingPointError('SSE bootstrap no positiva')
    return 1-errors[1]/errors[0]
