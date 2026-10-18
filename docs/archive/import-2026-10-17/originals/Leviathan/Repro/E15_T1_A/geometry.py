"""Exact softmax immersion geometry. No regional surrogate or finite differences."""
import numpy as np
from scipy.special import softmax
from scipy.integrate import solve_ivp

class Geometry:
    def __init__(self,M,f):
        self.M=M; self.f=f
    def jet(self,P):
        P=np.atleast_2d(P)
        a=softmax(P@self.f.T,axis=1)
        d=self.f[None,:,:]- (a@self.f)[:,None,:]
        cov=np.einsum('bn,bni,bnj->bij',a,d,d)
        J=a[:,:,None]*d
        H=a[:,:,None,None]*(d[:,:,:,None]*d[:,:,None,:]-cov[:,None,:,:])
        MJ=np.einsum('nm,bmi->bni',self.M,J)
        g=np.einsum('bni,bnj->bij',J,MJ)
        gi=np.linalg.inv(g)
        cross=np.einsum('bni,bnjk->bijk',MJ,H)
        gamma=np.einsum('bil,bljk->bijk',gi,cross)
        return g,gi,H,cross,gamma
    def eval(self,P):
        g,gi,H,cross,gamma=self.jet(P)
        # Gauss equation: normal components of the immersion Hessian.
        normH=H-np.einsum('bni,bijk->bnjk',self.jac(P),gamma)
        n11,n22,n12=normH[:,:,0,0],normH[:,:,1,1],normH[:,:,0,1]
        det=np.linalg.det(g)
        K=(np.einsum('bn,nm,bm->b',n11,self.M,n22)-np.einsum('bn,nm,bm->b',n12,self.M,n12))/det
        return np.sqrt(det),K
    def jac(self,P):
        a=softmax(np.atleast_2d(P)@self.f.T,axis=1)
        return a[:,:,None]*(self.f[None,:,:]-(a@self.f)[:,None,:])
    def rays(self,r,nt,phase=0,rtol=2e-10,atol=2e-12,dense=True):
        g=self.jet(np.zeros((1,2)))[0][0]
        t=np.arange(nt)*2*np.pi/nt+phase
        v=np.linalg.solve(np.linalg.cholesky(g).T,np.array([np.cos(t),np.sin(t)])).T
        def rhs(t,y):
            p,v=y.reshape(2,nt,2)
            gam=self.jet(p)[4]
            return np.concatenate([v,-np.einsum('bkij,bi,bj->bk',gam,v,v)]).ravel()
        sol=solve_ivp(rhs,[0,r],np.concatenate([np.zeros_like(v),v]).ravel(),method='DOP853',rtol=rtol,atol=atol,dense_output=dense)
        if not sol.success: raise RuntimeError(sol.message)
        return sol
    def rk4(self,r,nt,nsteps,phase=0):
        g=self.jet(np.zeros((1,2)))[0][0]
        t=np.arange(nt)*2*np.pi/nt+phase
        v=np.linalg.solve(np.linalg.cholesky(g).T,np.array([np.cos(t),np.sin(t)])).T
        p=np.zeros_like(v); h=r/nsteps; paths=[p.copy()]
        def acc(p,v): return -np.einsum('bkij,bi,bj->bk',self.jet(p)[4],v,v)
        for _ in range(nsteps):
            a1=acc(p,v); v2=v+h*a1/2; a2=acc(p+h*v/2,v2)
            v3=v+h*a2/2; a3=acc(p+h*v2/2,v3)
            v4=v+h*a3; a4=acc(p+h*v3,v4)
            p=p+h*(v+2*v2+2*v3+v4)/6; v=v+h*(a1+2*a2+2*a3+a4)/6
            paths.append(p.copy())
        return np.array(paths)

def triangles(rings):
    nt=rings.shape[1]; j=np.arange(nt); jp=(j+1)%nt
    out=[np.stack([np.zeros((nt,2)),rings[1,j],rings[1,jp]],axis=1)]
    for rr in range(1,len(rings)-1):
        a,b,c,d=rings[rr,j],rings[rr+1,j],rings[rr+1,jp],rings[rr,jp]
        out.extend([np.stack([a,b,c],1),np.stack([a,c,d],1)])
    return np.concatenate(out)

def children(t):
    a,b,c=t[:,0],t[:,1],t[:,2]; ab=(a+b)/2; bc=(b+c)/2; ca=(c+a)/2
    return np.stack([np.stack([a,ab,ca],1),np.stack([ab,b,bc],1),np.stack([ca,bc,c],1),np.stack([ab,bc,ca],1)],axis=1).reshape(-1,3,2)

def quadrature(geo,t,chunk=2048):
    out=[]
    for i in range(0,len(t),chunk):
        tr=t[i:i+chunk]; u=tr[:,1]-tr[:,0]; v=tr[:,2]-tr[:,0]
        area=np.abs(u[:,0]*v[:,1]-u[:,1]*v[:,0])/2
        da,k=geo.eval(tr.mean(1)); w=area*da
        out.append(np.stack([w,w*k*k,k],1))
    return np.concatenate(out)

def area7(geo,t,chunk=4096):
    # Seven-point Dunavant degree-five rule, weights normalized to one.
    bary=np.array([[1/3,1/3,1/3],[.059715871789770,.470142064105115,.470142064105115],[.470142064105115,.059715871789770,.470142064105115],[.470142064105115,.470142064105115,.059715871789770],[.797426985353087,.101286507323456,.101286507323456],[.101286507323456,.797426985353087,.101286507323456],[.101286507323456,.101286507323456,.797426985353087]])
    weights=np.array([.225]+[.132394152788506]*3+[.125939180544827]*3)
    total=0.
    for i in range(0,len(t),chunk):
        tr=t[i:i+chunk]; u=tr[:,1]-tr[:,0]; v=tr[:,2]-tr[:,0]; area=np.abs(u[:,0]*v[:,1]-u[:,1]*v[:,0])/2
        P=np.einsum('qi,bij->bqj',bary,tr).reshape(-1,2)
        J=geo.jac(P); G=np.einsum('bni,nm,bmj->bij',J,geo.M,J,optimize=True)
        da=np.sqrt(np.linalg.det(G)).reshape(-1,7)
        total+=np.sum(area*(da@weights))
    return total

def measures(q):
    w,e=q[:,0],q[:,1]; A=w.sum(); E=e.sum(); z=e/E
    # Legacy cell-count metrics for comparison only; mesh-dependent by construction.
    zs=np.sort(z)[::-1]; n=len(z)
    o=np.argsort(-(e/w)); wa=w[o]/A; za=z[o]
    cw=np.r_[0,np.cumsum(wa)]; ce=np.r_[0,np.cumsum(za)]
    return dict(area=A,energy=E,C_A=np.sqrt(E/A),lambda_1pct=float(np.interp(.01,cw,ce)),lambda_01pct=float(np.interp(.001,cw,ce)),frac50=float(np.interp(.5,ce,cw)),frac90=float(np.interp(.9,ce,cw)),R_eff=float(E*E/(A*np.sum(e*e/w))),legacy_lambda_1pct=zs[:int(np.ceil(.01*n))].sum(),legacy_R_eff=1/(n*np.sum(z*z)),max_abs_K=np.abs(q[:,2]).max(),cells=n)
