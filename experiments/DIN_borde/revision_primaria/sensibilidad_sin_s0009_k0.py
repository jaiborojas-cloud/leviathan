import numpy as np, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sensibilidad_bases as sens
import importlib
sp,X,L,Y=sens.cargar('CIFAR_F1')
import csv
ids=sorted({r['trajectory'] for r in csv.DictReader(open(sens.R+'CIFAR/F1/resultado/cifar_f1_visitas.csv'))})
keep=np.array([t!='cifar_f1_s0009_k0' for t in ids]); sp,X,L,Y=sp[keep],X[keep],L[keep],Y[keep]
fo=sens.folds(sp); idx=[np.where(sp==s)[0] for s in np.unique(sp)]; out={}
for v in ('cubica','cubica_recortada','spline_natural','cubica_rangos'):
    d,eb,ef=sens.D(v,sp,X,L,Y,fo); g=eb**2-ef**2
    rng=np.random.default_rng(260001); nul=np.array([sens.D(v,sp,np.concatenate([[0]]) if False else (lambda Xp:[Xp.__setitem__(ii,X[rng.permutation(ii)]) for ii in idx] and Xp)(X.copy()),L,Y,fo)[0] for _ in range(2000)])
    out[v]=dict(D=float(d),p=float((1+np.sum(nul>=d-1e-15))/2001),fraccion_max_1obs=float(g.max()/g.sum()))
    print(v,{k:round(x,4) for k,x in out[v].items()},flush=True)
json.dump(out,open('cifar_sin_s0009_k0.json','w'),indent=1)
