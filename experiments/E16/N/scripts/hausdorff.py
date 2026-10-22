"""Hausdorff de polígonos: acotación Lipschitz adaptativa en float64."""
import heapq
import numpy as np

def segment_distances(p,target):
    a=target[:-1];v=target[1:]-a;vv=np.sum(v*v,axis=1)
    z=np.divide(np.sum((p-a)*v,axis=1),vv,out=np.zeros(len(vv)),where=vv>0)
    return np.linalg.norm(p-(a+np.clip(z,0,1)[:,None]*v),axis=1)

def point_distance(p,target):return float(np.min(segment_distances(p,target)))

def directed(source,target,gap,cap):
    lower=max(point_distance(p,target) for p in source);heap=[];counter=0
    def add(a,b):
        nonlocal lower,counter
        mid=(a+b)/2;d=point_distance(mid,target);lower=max(lower,d)
        upper=min(d+float(np.linalg.norm(b-a))/2,float(np.min(np.maximum(segment_distances(a,target),segment_distances(b,target)))))
        counter+=1;heapq.heappush(heap,(-upper,counter,a,b))
    for a,b in zip(source,source[1:]):add(a,b)
    splits=0
    while max(lower,-heap[0][0])-lower>gap and splits<cap:
        _,_,a,b=heapq.heappop(heap);mid=(a+b)/2;add(a,mid);add(mid,b);splits+=1
    return lower,max(lower,-heap[0][0]),splits

def hausdorff(a,b,gap,cap):
    ab=directed(a,b,gap,cap);ba=directed(b,a,gap,cap)
    return max(ab[0],ba[0]),max(ab[1],ba[1]),ab[2]+ba[2]

def controls():
    a=np.array([[0.,0.],[1.,0.]])
    examples=[('subdivision',a,np.array([[0.,0.],[.3,0.],[1.,0.]]),0.),
              ('parallel',a,a+[0.,.02],.02),
              ('interior_peak',a,np.array([[0.,0.],[.5,.5],[1.,0.]]),.5)]
    rows=[]
    for name,a,b,expected in examples:
        lo,hi,n=hausdorff(a,b,1e-5,200000)
        assert lo-1e-12<=expected<=hi+1e-12 and hi-lo<=1e-5+1e-12,(name,lo,hi)
        if name=='interior_peak':
            # Directed horizontal->V has a positive interior maximum, zero at vertices.
            dlo,dhi,_=directed(a,b,1e-5,200000)
            assert dlo>.35 and all(point_distance(p,b)==0 for p in a)
        rows.append({'name':name,'lower':lo,'upper':hi,'expected':expected,'splits':n})
    return rows

def analyze(old,new,cfg):
    controls();rows=[]
    def curve(data,lin,m):
        r=sorted([z for z in data if z['lineage']==lin and int(z['segments'])==m],key=lambda z:float(z['t']))
        assert len(r)==m-1
        return np.array([[0.,0.]]+[[float(z['t']),float(z['s'])] for z in r]+[[1.,0.]])
    def compare(name,family,lin,a,b):
        t=np.unique(np.r_[a[:,0],b[:,0]]);shape=float(np.max(np.abs(np.interp(t,a[:,0],a[:,1])-np.interp(t,b[:,0],b[:,1]))))
        lo,hi,n=hausdorff(a,b,float(cfg['hausdorff_gap']),cfg['hausdorff_max_splits']);tol=float(cfg['hausdorff_tolerance'])
        status='PASS_NUMERICAL' if hi<=tol and hi-lo<=float(cfg['hausdorff_gap']) else ('EXCEEDS_THRESHOLD' if lo>tol else 'INCONCLUSIVE')
        rows.append({'comparison':name,'family':family,'lineage':lin,'same_t_sup':shape,'lower':lo,'upper':hi,'gap':hi-lo,'splits':n,'diagnosis':status})
    for lin in ['Q0','Q1','C0']:
        for label,data in [('M',old),('N',new)]:
            for m0,m1 in [(32,64),(64,128)]:compare(f'{label}_{lin}_{m0}_{m1}',label+'_refinement',lin,curve(data,lin,m0),curve(data,lin,m1))
        for m in [32,64,128]:compare(f'M_N_{lin}_{m}','M_N',lin,curve(old,lin,m),curve(new,lin,m))
    return rows
