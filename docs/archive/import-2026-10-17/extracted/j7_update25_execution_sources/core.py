
import math, numpy as np, torch
from sklearn.datasets import load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from torch.func import jacrev, vmap

torch.set_default_dtype(torch.float64)

RHO=1e-4
LR=0.006
BATCH=64
MAX_STEPS=20000
CHECK_EVERY=25

class WineMLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.l1=torch.nn.Linear(13,64)
        self.l2=torch.nn.Linear(64,32)
        self.l3=torch.nn.Linear(32,3)
    def forward(self,x):
        return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))

def train_branch(init_seed, batch_seed, Xtr, ytarget):
    torch.manual_seed(init_seed)
    m=WineMLP().double()
    opt=torch.optim.Adam(m.parameters(),lr=LR)
    rng=np.random.default_rng(batch_seed)
    step=0
    while step<MAX_STEPS:
        ids=torch.tensor(rng.choice(len(Xtr),size=BATCH,replace=False),dtype=torch.long)
        opt.zero_grad()
        loss=torch.nn.functional.cross_entropy(m(Xtr[ids]),ytarget[ids])
        loss.backward()
        opt.step()
        step+=1
        if step%CHECK_EVERY==0:
            with torch.no_grad():
                acc=(m(Xtr).argmax(1)==ytarget).double().mean().item()
            if acc>=0.99:
                return m,step,acc
    return m,step,acc

def load_split(split_idx):
    wine=load_wine()
    Xall=wine.data.astype(np.float64); yall=wine.target.astype(np.int64)
    idx=np.arange(len(yall))
    itr,itmp=train_test_split(idx,test_size=.30,random_state=1000+split_idx,stratify=yall)
    ival,ite=train_test_split(itmp,test_size=.50,random_state=1000+split_idx,stratify=yall[itmp])
    scaler=StandardScaler().fit(Xall[itr])
    Xs=scaler.transform(Xall)
    return (torch.tensor(Xs[itr]),torch.tensor(yall[itr],dtype=torch.long),
            torch.tensor(Xs[ival]),torch.tensor(yall[ival],dtype=torch.long),
            torch.tensor(Xs[ite]),torch.tensor(yall[ite],dtype=torch.long),
            scaler,itr,ival,ite)

def make_geom_state(model, Xpanel, ypanel):
    W1=model.l1.weight.detach().clone().requires_grad_(True)
    b1=model.l1.bias.detach().clone().requires_grad_(True)
    W2=model.l2.weight.detach().clone().requires_grad_(True)
    b2=model.l2.bias.detach().clone().requires_grad_(True)
    W3r=(model.l3.weight[:2]-model.l3.weight[2:3]).detach().clone().requires_grad_(True)
    b3r=(model.l3.bias[:2]-model.l3.bias[2]).detach().clone().requires_grad_(True)
    blocks=[[W1,b1],[W2,b2],[W3r,b3r]]
    N=len(Xpanel)
    fpanel=Xpanel[:,:2].detach()

    def logits_red(x):
        h1=torch.relu(x@W1.T+b1)
        h2=torch.relu(h1@W2.T+b2)
        z2=h2@W3r.T+b3r
        return torch.cat([z2,torch.zeros((len(x),1),dtype=x.dtype)],1)

    def flat_grads(params, scalar):
        gs=torch.autograd.grad(scalar,params,retain_graph=True)
        return torch.cat([g.reshape(-1) for g in gs])

    Rb=[[] for _ in blocks]; Ub=[[] for _ in blocks]
    for n in range(N):
        logits=logits_red(Xpanel[n:n+1]).squeeze(0)
        logp=torch.log_softmax(logits,0)
        p=logp.exp().detach()
        for bi,params in enumerate(blocks):
            Rb[bi].append(flat_grads(params,logp[ypanel[n]]).detach())
        for c in range(3):
            for bi,params in enumerate(blocks):
                gc=flat_grads(params,logp[c])
                Ub[bi].append((math.sqrt(float(p[c])/N)*gc).detach())
    Rb=[torch.stack(v,0) for v in Rb]
    Ub=[torch.stack(v,0).T.contiguous() for v in Ub]
    return Rb,Ub,fpanel

def subset_M(Rb,Ub,S):
    R=torch.cat([Rb[i] for i in S],1)
    U=torch.cat([Ub[i] for i in S],0)
    gram=U.T@U
    lm=torch.linalg.eigvalsh(gram)[-1].clamp_min(1e-14)
    reg=RHO*lm
    A=gram+reg*torch.eye(gram.shape[0],dtype=gram.dtype)
    AinvRT=(R.T-U@torch.linalg.solve(A,U.T@R.T))/reg
    M=R@AinvRT
    return 0.5*(M+M.T)

def G_from_M(P,M,fpanel):
    a=torch.softmax(fpanel@P,0)
    mu=(a[:,None]*fpanel).sum(0)
    C=a[:,None]*(fpanel-mu)
    return C.T@M@C

def curvature_fast_single(P,M,fpanel):
    def gf(x): return G_from_M(x,M,fpanel)
    g=gf(P); gi=torch.linalg.inv(g)
    dg=jacrev(gf)(P)
    d2g=jacrev(jacrev(gf))(P)
    Gamma=torch.stack([
        torch.stack([
            torch.stack([
                0.5*sum(gi[l,m]*(dg[j,m,i]+dg[i,m,j]-dg[i,j,m]) for m in range(2))
                for j in range(2)])
            for i in range(2)])
        for l in range(2)])
    dginv=torch.stack([
        torch.stack([
            torch.stack([
                -sum(gi[l,a]*dg[a,b,k]*gi[b,m] for a in range(2) for b in range(2))
                for k in range(2)])
            for m in range(2)])
        for l in range(2)])
    dGamma=torch.stack([
        torch.stack([
            torch.stack([
                torch.stack([
                    0.5*sum(
                        dginv[l,m,k]*(dg[j,m,i]+dg[i,m,j]-dg[i,j,m])+
                        gi[l,m]*(d2g[j,m,i,k]+d2g[i,m,j,k]-d2g[i,j,m,k])
                        for m in range(2))
                    for k in range(2)])
                for j in range(2)])
            for i in range(2)])
        for l in range(2)])
    Ric=torch.stack([
        torch.stack([
            sum(
                dGamma[k,i,j,k]-dGamma[k,i,k,j]+
                sum(Gamma[k,i,j]*Gamma[l,k,l]-Gamma[l,i,k]*Gamma[k,j,l] for l in range(2))
                for k in range(2))
            for j in range(2)])
        for i in range(2)])
    return 0.5*torch.sum(gi*Ric)

def gamma_single(P,M,fpanel):
    def gf(x): return G_from_M(x,M,fpanel)
    g=gf(P); gi=torch.linalg.inv(g); dg=jacrev(gf)(P)
    return torch.stack([
        torch.stack([
            torch.stack([
                0.5*sum(gi[l,m]*(dg[j,m,i]+dg[i,m,j]-dg[i,j,m]) for m in range(2))
                for j in range(2)])
            for i in range(2)])
        for l in range(2)])

def accel_batch(P,V,M,fpanel):
    Gams=vmap(lambda x:gamma_single(x,M,fpanel))(P)
    return -torch.einsum('nlij,ni,nj->nl',Gams,V,V)

def exp_map_rays(M,fpanel,radius,ntheta,nsteps,return_paths=True,phase=0.0):
    P0=torch.zeros(2,dtype=torch.float64)
    G0=G_from_M(P0,M,fpanel)
    L=torch.linalg.cholesky(G0)
    th=torch.linspace(0,2*math.pi,ntheta+1,dtype=torch.float64)[:-1]+phase
    U=torch.stack([torch.cos(th),torch.sin(th)],1)
    V=torch.linalg.solve(L.T,U.T).T
    P=P0.repeat(ntheta,1)
    h=radius/nsteps
    paths=[P.clone()]
    for _ in range(nsteps):
        k1P=V; k1V=accel_batch(P,V,M,fpanel)
        k2P=V+0.5*h*k1V
        k2V=accel_batch(P+0.5*h*k1P,V+0.5*h*k1V,M,fpanel)
        k3P=V+0.5*h*k2V
        k3V=accel_batch(P+0.5*h*k2P,V+0.5*h*k2V,M,fpanel)
        k4P=V+h*k3V
        k4V=accel_batch(P+h*k3P,V+h*k3V,M,fpanel)
        P=P+(h/6)*(k1P+2*k2P+2*k3P+k4P)
        V=V+(h/6)*(k1V+2*k2V+2*k3V+k4V)
        if return_paths: paths.append(P.clone())
    return P, torch.stack(paths) if return_paths else None

def explicit_triangles_from_rings(rings):
    nr=rings.shape[0]-1; nt=rings.shape[1]
    tris=[]; O=torch.zeros(2,dtype=rings.dtype)
    for j in range(nt):
        jp=(j+1)%nt
        tris.append(torch.stack([O,rings[1,j],rings[1,jp]],0))
    for rr in range(1,nr):
        for j in range(nt):
            jp=(j+1)%nt
            a,b,c,d=rings[rr,j],rings[rr+1,j],rings[rr+1,jp],rings[rr,jp]
            tris.append(torch.stack([a,b,c],0))
            tris.append(torch.stack([a,c,d],0))
    return torch.stack(tris,0)

def tri_chart_area(tris):
    u=tris[:,1]-tris[:,0]; v=tris[:,2]-tris[:,0]
    return 0.5*torch.abs(u[:,0]*v[:,1]-u[:,1]*v[:,0])

def subdivide4(tris):
    a,b,c=tris[:,0],tris[:,1],tris[:,2]
    ab=(a+b)/2; bc=(b+c)/2; ca=(c+a)/2
    return torch.cat([
        torch.stack([a,ab,ca],1),
        torch.stack([ab,b,bc],1),
        torch.stack([ca,bc,c],1),
        torch.stack([ab,bc,ca],1),
    ],0)

# B6 should add multi-source meshes with angular phase offsets and compare
# independently converged adaptive estimates across sources.
