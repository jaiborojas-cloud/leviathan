"""Descriptores dependientes de carta; no certifican regularidad ni geodésicas."""
import numpy as np

def resample(z,count):
    lengths=np.linalg.norm(np.diff(z,axis=0),axis=1)
    if np.any(lengths==0):raise ValueError('zero edge in arc diagnostic')
    u=np.r_[0,np.cumsum(lengths)];u/=u[-1];v=np.linspace(0,1,count)
    return np.column_stack([np.interp(v,u,z[:,j]) for j in [0,1]])

def compare(a,b,hd,cfg):
    lo,hi,nsplit=hd.hausdorff(a,b,float(cfg['hausdorff_gap']),cfg['hausdorff_max_splits'])
    arc=float(np.max(np.linalg.norm(resample(a,cfg['arc_samples'])-resample(b,cfg['arc_samples']),axis=1)))
    return lo,hi,nsplit,arc

def descriptors(z,source,cfg):
    v=np.diff(z,axis=0);lengths=np.linalg.norm(v,axis=1)
    ratio=np.divide(abs(v[:,0]),lengths,out=np.full(len(lengths),np.nan),where=lengths>0)
    base_index=int(np.argmin(abs(source[:,0]-cfg['hotspot_t'])))
    return {'backtracking_edges':int(np.sum(v[:,0]<-cfg['backtracking_tolerance'])),
        'near_vertical_edges':int(np.sum(ratio<=cfg['vertical_ratio_tolerance'])),
        'min_edge_length':float(np.min(lengths)),'min_longitudinal_ratio':float(np.nanmin(ratio)),
        'max_t_displacement_from_source':float(np.max(abs(z[:,0]-source[:,0]))),
        'hotspot_node_index':base_index,'hotspot_source_t':float(source[base_index,0]),
        'hotspot_t':float(z[base_index,0]),'hotspot_s':float(z[base_index,1])}
