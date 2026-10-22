"""Primitiva estable heredada; nodos explícitos y probes con normal global."""
import numpy as np
import autograd.numpy as anp
import mpmath as mp
T=None
def set_nodes(t):
    global T
    T=np.asarray(t,float).copy()
    assert T[0]==0 and T[-1]==1 and np.all(np.diff(T)>0)
def grid(m):
    assert len(T)==m+1
    return T.copy()
def array_length(p,kind,ux,uy):
    v=p[1:]-p[:-1]
    if kind=='sum':
        u=anp.dot(v,ux)
        return anp.sum(anp.sqrt(anp.sum(u*u,axis=1)))
    up=p[:,0,None,None]*ux+p[:,1,None,None]*uy
    u=anp.einsum('ej,ejk->ek',v,up[:-1]);dd=anp.einsum('ej,ejk->ek',v,up[1:]-up[:-1])
    aa=anp.sum(dd*dd,axis=1)
    if anp.any(aa<=0):return anp.inf
    h=anp.sum(u*dd,axis=1)/aa;r=u-h[:,None]*dd;delta=anp.sum(r*r,axis=1)
    if anp.any(delta<=0):return anp.inf
    width=anp.sqrt(delta/aa)
    def pfun(x):return (x*anp.sqrt(aa*x*x+delta)+delta/anp.sqrt(aa)*anp.arcsinh(x/width))/2
    return anp.sum(pfun(h+1)-pfun(h))

def make_objective(a,b,m,kind,ux,uy):
    t=grid(m);v=b-a;normal=np.array([-v[1],v[0]]);base=a+t[:,None]*v
    def length(s):
        p=base+anp.concatenate([anp.zeros(1),s,anp.zeros(1)])[:,None]*normal
        return array_length(p,kind,ux,uy)
    return length

def midpoint_objective(x,y,base,normal,kind,ux,uy):
    def objective(z):return array_length(anp.stack([x,base+z*normal,y]),kind,ux,uy)
    return objective

def points(a,b,s):
    if len(s)==0:return [a,b]
    assert len(T)==len(s)+2
    v=b-a;normal=mp.matrix([-v[1],v[0]])
    return [a]+[a+mp.mpf(float(T[j+1]))*v+z*normal for j,z in enumerate(s)]+[b]

def mp_edges(a,b,s,kind,ux,uy):
    pts=points(a,b,s)
    for x,y in zip(pts,pts[1:]):
        v=y-x
        u0=ux if kind=='sum' else x[0]*ux+x[1]*uy
        u1=ux if kind=='sum' else y[0]*ux+y[1]*uy
        yield u0,u1-u0,(v.T*u0).T,(v.T*(u1-u0)).T

def reference_length(a,b,s,kind,ux,uy):
    total=mp.mpf(0)
    for u0,du,u,dd in mp_edges(a,b,s,kind,ux,uy):
        if kind=='sum':total+=mp.sqrt(mp.fsum(z*z for z in u));continue
        aa=mp.fsum(z*z for z in dd)
        if aa<=0:raise ValueError('nonpositive_a')
        h=mp.fsum(x*y for x,y in zip(u,dd))/aa;r=u-h*dd;delta=mp.fsum(z*z for z in r)
        if delta<=0:raise ValueError('nonpositive_delta')
        width=mp.sqrt(delta/aa)
        def primitive(x):return (x*mp.sqrt(aa*x*x+delta)+delta/mp.sqrt(aa)*mp.asinh(x/width))/2
        total+=primitive(1+h)-primitive(h)
    return total
