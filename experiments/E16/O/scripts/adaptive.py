"""Marcado determinista y comparaciones sobre mallas explícitas."""
import numpy as np

def mark(scores,fraction,cap):
    scores=np.asarray(scores,float);weights=scores*scores;total=float(np.sum(weights))
    assert np.all(np.isfinite(weights)) and np.all(weights>=0)
    if total==0:return [],0.
    order=sorted(range(len(weights)),key=lambda j:(-weights[j],j));selected=[];mass=0.
    for j in order[:cap]:
        selected.append(j);mass+=float(weights[j])
        if mass>=fraction*total:break
    return sorted(selected),mass/total

def shape(t0,s0,t1,s1):
    t=np.unique(np.r_[t0,t1]);delta=np.interp(t,t1,np.r_[0,s1,0])-np.interp(t,t0,np.r_[0,s0,0])
    return t,delta,float(np.max(np.abs(delta)))

def controls():
    assert mark([4,3,2,1],.5,32)==([0],16/30)
    assert mark([0,0],.5,32)==([],0.)
    chosen,mass=mark(np.ones(100),.5,32);assert chosen==list(range(32)) and mass==.32
    t0=np.array([0.,.3,1.]);t1=np.array([0.,.15,.3,.65,1.]);s0=np.array([.1]);s1=np.interp(t1[1:-1],t0,[0,.1,0])
    assert shape(t0,s0,t1,s1)[2]<1e-15
    return True
