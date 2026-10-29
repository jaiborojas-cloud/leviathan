import csv, numpy as np, json, sys
from scipy.stats import norm, rankdata
R=str(__import__('pathlib').Path(__file__).resolve().parents[1])+'/'
def cen(v,sp):
    v=np.asarray(v,float).copy()
    for s in np.unique(sp): v[sp==s]-=v[sp==s].mean()
    return v
def cargar(nombre):
    if nombre=='C1':
        rows=[r for r in csv.DictReader(open(R+'C1/cohorte/c1_cohorte.csv')) if not r['error'] and r['X'] and r['rho_u10'] and r['rho_u250']]
        sp=np.array([int(r['trajectory'].split('_')[0][5:]) for r in rows]); X=np.array([float(r['X']) for r in rows])
        L=np.log([float(r['rho_u10']) for r in rows]); Y=np.log([float(r['rho_u250']) for r in rows])
    elif nombre=='C2':
        rows=[r for r in csv.DictReader(open(R+'C2/cohorte/c2_cohorte.csv')) if not r['error'] and r['X10'] and r['rho_caras_10'] and r['rho_caras_250']]
        sp=np.array([int(r['split']) for r in rows]); X=np.array([float(r['X10']) for r in rows])
        L=np.log([float(r['rho_caras_10']) for r in rows]); Y=np.log([float(r['rho_caras_250']) for r in rows])
    else:
        m={(r['trajectory'],r['update']):r for r in csv.DictReader(open(R+'CIFAR/F1/resultado/cifar_f1_visitas.csv'))}
        ids=sorted({t for t,_ in m}); sp=np.array([int(t.split('_')[2][1:]) for t in ids])
        X=np.array([float(m[t,'10']['X']) for t in ids]); L=np.log([float(m[t,'10']['rho_caras']) for t in ids]); Y=np.log([float(m[t,'250']['rho_caras']) for t in ids])
    # splits con >=3
    u,c=np.unique(sp,return_counts=True); ok=np.isin(sp,u[c>=3])
    return sp[ok],X[ok],L[ok],Y[ok]
def rcs(x,knots):
    k=knots; K=len(k); cols=[x]
    d=lambda v,t: np.maximum(v-t,0)**3
    for j in range(K-2):
        cols.append(d(x,k[j])-d(x,k[K-2])*(k[K-1]-k[j])/(k[K-1]-k[K-2])+d(x,k[K-1])*(k[K-2]-k[j])/(k[K-1]-k[K-2]))
    return np.column_stack(cols)/ (k[-1]-k[0])**np.array([1]+[3]*(K-2))
def base(variant,L,sp,tr,te):
    """Devuelve matrices (centradas dentro del split) para train y test; los parámetros de la transformación salen solo de L (nunca de Y)."""
    if variant=='cubica':
        z=(L-L.mean())/L.std(); Bm=np.column_stack([cen(z**g,sp) for g in (1,2,3)])
    elif variant=='cubica_recortada':
        z=(L-L.mean())/L.std(); zc=z.copy(); zc[te]=np.clip(z[te],z[tr].min(),z[tr].max())
        Bm=np.column_stack([cen(zc**g,sp) for g in (1,2,3)])
    elif variant=='spline_natural':
        kn=np.quantile(L[tr],[.05,.35,.65,.95]); Bm=rcs(L,kn); Bm=np.column_stack([cen(Bm[:,j],sp) for j in range(Bm.shape[1])])
    elif variant=='cubica_rangos':
        z=norm.ppf((rankdata(L)-.5)/len(L)); Bm=np.column_stack([cen(z**g,sp) for g in (1,2,3)])
    return Bm
def folds(sp):
    f={s:i%10 for i,s in enumerate(np.random.default_rng(260010).permutation(np.unique(sp)))}; return np.array([f[s] for s in sp])
def errores(variant,sp,X,L,Y,fo):
    yc,xc=cen(Y,sp),cen(X,sp); eb=np.empty(len(Y)); ef=np.empty(len(Y))
    for k in range(10):
        tr,te=fo!=k,fo==k; B=base(variant,L,sp,tr,te); F=np.column_stack([B,xc])
        eb[te]=yc[te]-B[te]@np.linalg.lstsq(B[tr],yc[tr],rcond=None)[0]
        ef[te]=yc[te]-F[te]@np.linalg.lstsq(F[tr],yc[tr],rcond=None)[0]
    return eb,ef
def D(variant,sp,X,L,Y,fo):
    eb,ef=errores(variant,sp,X,L,Y,fo); return 1-(ef**2).sum()/(eb**2).sum(),eb,ef
def _main():
  pass
if __name__=='__main__':
    out={}
    B=int(sys.argv[1]) if len(sys.argv)>1 else 2000
    for nombre in ('C1','C2','CIFAR_F1'):
        sp,X,L,Y=cargar(nombre); fo=folds(sp); us=np.unique(sp); idx=[np.where(sp==s)[0] for s in us]
        zmax=float(np.abs((L-L.mean())/L.std()).max())
        out[nombre]=dict(n=len(Y),splits=len(us),max_abs_z_L=zmax)
        for v in ('cubica','cubica_recortada','spline_natural','cubica_rangos'):
            d,eb,ef=D(v,sp,X,L,Y,fo); g=eb**2-ef**2; top=np.argmax(g)
            keep=np.ones(len(Y),bool); keep[top]=False
            sp2=sp[keep]; d_sin=D(v,sp2,X[keep],L[keep],Y[keep],folds(sp2))[0]
            rng=np.random.default_rng(260001); nul=np.empty(B)
            for b in range(B):
                Xp=X.copy()
                for ii in idx: Xp[ii]=X[rng.permutation(ii)]
                nul[b]=D(v,sp,Xp,L,Y,fo)[0]
            p=(1+np.sum(nul>=d-1e-15))/(1+B)
            out[nombre][v]=dict(D=float(d),p=float(p),q95=float(np.quantile(nul,.95)),fraccion_max_1obs=float(g[top]/g.sum()) if g.sum()>0 else None,D_sin_obs_mas_influyente=float(d_sin))
            print(nombre,v,{k:round(x,4) if isinstance(x,float) else x for k,x in out[nombre][v].items()},flush=True)
    json.dump(out,open('sensibilidad_bases.json','w'),indent=1)
