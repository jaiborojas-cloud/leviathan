import sys,csv,math,time,numpy as np
from scipy.spatial import ConvexHull
sys.path.insert(0,sys.argv[1]+'/sources'); sys.path.append(sys.argv[2])
from geometry import Geometry
import rho_borde as rb
ini,fin,out=int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
rows=list(csv.DictReader(open(sys.argv[6])))[ini:fin]
w=csv.writer(open(out,'w',newline=''));w.writerow(['trajectory','update','rho_nativa','min_normales','th_min','n_dirs','seg'])
for r in rows:
    t=r['trajectory']
    for k in (10,250):
        z=np.load(f"{sys.argv[7]}/estados/{t}/u{k}.npz");M=z['M'].astype(float);f=z['f'].astype(float);g=Geometry(M,f)
        t0=time.time();V=list(ConvexHull(f).vertices);ths=[]
        for i in range(len(V)):
            d=f[V[(i+1)%len(V)]]-f[V[i]];nrm=np.array([d[1],-d[0]])
            c=f.mean(0)
            if nrm@(f[V[i]]-c)<0: nrm=-nrm
            ths.append(math.atan2(nrm[1],nrm[0]))
        ths+= [0,math.pi/2,math.pi,-math.pi/2]
        vals=[(rb.rho_quad(g,th)[0],th) for th in ths]
        m=min(vals)
        w.writerow([t,k,r[f'rho_u{k}'],m[0],m[1],len(ths),round(time.time()-t0,2)])
