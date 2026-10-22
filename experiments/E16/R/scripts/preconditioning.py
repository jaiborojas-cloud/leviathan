"""Escalado diádico congelado: x=D y, sin alterar objetivo ni cajas."""
import numpy as np
import time
from autograd import hessian

def scales_from_hessian(h,cfg):
    if not np.all(np.isfinite(h)):raise ValueError('nonfinite Hessian')
    diag=np.diag(h).copy();absolute=abs(diag);positive=absolute[absolute>0]
    mu=float(np.median(positive)) if len(positive) else 1.
    ratio=np.sqrt(mu/np.maximum(absolute,cfg['preconditioner_floor_relative']*mu))
    exponent=np.clip(np.rint(np.log2(ratio)),*cfg['scale_exponent_bounds']).astype(int)
    return np.exp2(exponent.astype(float)),exponent,mu,diag

def prepare(name,obj,z,cfg):
    ts=time.monotonic()
    x=z[1:-1].reshape(-1);h=np.asarray(hessian(obj.value)(x),float);d,exponent,mu,diag=scales_from_hessian(h,cfg)
    algorithm_seconds=time.monotonic()-ts;ts=time.monotonic()
    bounds=np.array([bb for j in range(len(z)-2) for bb in [cfg['t_bounds'],cfg['s_bounds']]])
    inactive=np.minimum(abs(x-bounds[:,0]),abs(x-bounds[:,1]))>float(cfg['boundary_tolerance'])
    rows=[{'reference':name,'index':j//2+1,'coordinate':'t' if j%2==0 else 's','diagonal':repr(float(v)),'median_positive_abs_diagonal':repr(mu),'exponent':int(e),'scale':repr(float(s))} for j,(v,e,s) in enumerate(zip(diag,exponent,d))]
    spectra=[]
    for target,matrix in [('physical',h),('scaled',d[:,None]*h*d[None,:])]:
        reduced=matrix[np.ix_(inactive,inactive)];vals=np.linalg.eigvalsh((reduced+reduced.T)/2)
        if not len(vals):raise ValueError('empty inactive Hessian block')
        floor=cfg['spectral_relative_floor']*max(1,float(np.max(abs(vals))));positive=vals[vals>floor];negative=vals[vals<-floor];zero=vals[abs(vals)<=floor]
        spectra.append({'reference':name,'coordinates':target,'dimension':len(x),'inactive_dimension':int(np.sum(inactive)),
            'min_eigenvalue':repr(float(vals[0])),'max_eigenvalue':repr(float(vals[-1])),'threshold':repr(floor),
            'negative':len(negative),'near_zero':len(zero),'positive':len(positive),
            'positive_spectrum_ratio':repr(float(positive[-1]/positive[0])) if len(positive) else '',
            'classification':'INDEFINITE' if len(negative) else ('NEAR_SINGULAR' if len(zero) else 'POSITIVE_AT_THRESHOLD')})
    return d,rows,spectra,{"hessian_and_scaling_seconds":algorithm_seconds,"spectral_diagnostics_seconds":time.monotonic()-ts}
