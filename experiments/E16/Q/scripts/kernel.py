"""Longitud heredada de P y energía afín exacta, sin asumir equivalencia discreta."""
import numpy as np
import autograd.numpy as anp
import mpmath as mp

def array_length(p,kind,ux,uy):
    v=p[1:]-p[:-1]
    if anp.any(anp.sum(v*v,axis=1)==0):return anp.inf
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


def subdivide(z):
    out=np.empty((2*len(z)-1,2));out[::2]=z;out[1::2]=(z[:-1]+z[1:])/2
    return out

def pack(z,arm):return np.asarray(z[1:-1,1] if arm=='fixed' else z[1:-1].reshape(-1),float)

def coords(x,arm,t):
    middle=anp.stack([t[1:-1],x],axis=1) if arm=='fixed' else anp.reshape(x,(-1,2))
    return anp.concatenate([anp.array([[0.,0.]]),middle,anp.array([[1.,0.]])],axis=0)

class Objective:
    def __init__(self,a,b,arm,t,kind,ux,uy,target="length"):
        self.a=a;self.v=b-a;self.normal=np.array([-self.v[1],self.v[0]]);self.arm=arm;self.t=t.copy();self.kind=kind;self.ux=ux;self.uy=uy
        self.target=target
        self.rejections={'zero_edge':0,'invalid_primitive':0}
    def value(self,x):
        z=coords(x,self.arm,self.t);p=self.a+z[:,0,None]*self.v+z[:,1,None]*self.normal
        return array_energy(p,self.kind,self.ux,self.uy) if self.target=="energy" else array_length(p,self.kind,self.ux,self.uy)
    def fun(self,x):
        value=float(self.value(x))
        if not np.isfinite(value):
            z=np.asarray(coords(x,self.arm,self.t),float)
            reason='zero_edge' if np.any(np.sum(np.diff(z,axis=0)**2,axis=1)==0) else 'invalid_primitive'
            self.rejections[reason]+=1
        return value

def mp_points(a,b,z):
    v=b-a;normal=mp.matrix([-v[1],v[0]])
    return [a+mp.mpf(float(t))*v+mp.mpf(repr(float(s)))*normal for t,s in z]

def mp_edges(pts,kind,ux,uy):
    for x,y in zip(pts,pts[1:]):
        v=y-x
        if mp.fsum(z*z for z in v)==0:raise ValueError('zero_edge')
        u0=ux if kind=='sum' else x[0]*ux+x[1]*uy
        u1=ux if kind=='sum' else y[0]*ux+y[1]*uy
        yield u0,u1-u0,(v.T*u0).T,(v.T*(u1-u0)).T

def reference(pts,kind,ux,uy):
    total=mp.mpf(0)
    for u0,du,u,dd in mp_edges(pts,kind,ux,uy):
        if kind=='sum':total+=mp.sqrt(mp.fsum(z*z for z in u));continue
        aa=mp.fsum(z*z for z in dd)
        if aa<=0:raise ValueError('nonpositive_a')
        h=mp.fsum(x*y for x,y in zip(u,dd))/aa;r=u-h*dd;delta=mp.fsum(z*z for z in r)
        if delta<=0:raise ValueError('nonpositive_delta')
        width=mp.sqrt(delta/aa)
        def primitive(x):return (x*mp.sqrt(aa*x*x+delta)+delta/mp.sqrt(aa)*mp.asinh(x/width))/2
        total+=primitive(1+h)-primitive(h)
    return total


def array_energy(p,kind,ux,uy):
    v=p[1:]-p[:-1]
    if anp.any(anp.sum(v*v,axis=1)==0):return anp.inf
    if kind=='sum':
        u=anp.dot(v,ux);dd=anp.zeros_like(u)
    else:
        up=p[:,0,None,None]*ux+p[:,1,None,None]*uy
        u=anp.einsum('ej,ejk->ek',v,up[:-1]);dd=anp.einsum('ej,ejk->ek',v,up[1:]-up[:-1])
    return len(v)/2*anp.sum(u*u+u*dd+dd*dd/3)

def segment_A(u,dd):return mp.fsum(x*x+x*y+y*y/3 for x,y in zip(u,dd))

def reference_energy(pts,kind,ux,uy):
    return (len(pts)-1)/mp.mpf(2)*mp.fsum(segment_A(u,dd) for u0,du,u,dd in mp_edges(pts,kind,ux,uy))

def energy_values(pts,kind,ux,uy):
    aa=[segment_A(u,dd) for u0,du,u,dd in mp_edges(pts,kind,ux,uy)]
    length=reference(pts,kind,ux,uy)
    return {'length':length,'energy':len(aa)/mp.mpf(2)*mp.fsum(aa),'duration_energy':mp.fsum(mp.sqrt(x) for x in aa)**2/2,'arc_energy':length*length/2}
