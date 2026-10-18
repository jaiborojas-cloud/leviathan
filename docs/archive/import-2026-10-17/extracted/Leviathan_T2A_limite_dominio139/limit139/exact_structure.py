from fractions import Fraction as Q
from pathlib import Path
import numpy as np,json,time
from scipy.spatial import ConvexHull
start=time.perf_counter();d=np.load('Windows_RIPG_T2A_CP90/data/state.npz');M=d['M'];f=d['f'];n=len(M)
R=[[Q(float(x)) for x in row] for row in M];F=[[Q(float(x)) for x in row] for row in f]
assert all(R[i][j]==R[j][i] for i in range(n) for j in range(n))
L=[[Q(int(i==j)) for j in range(n)] for i in range(n)];D=[]
for j in range(n):
 dj=R[j][j]-sum(L[j][k]**2*D[k] for k in range(j));assert dj>0;D.append(dj)
 for i in range(j+1,n):L[i][j]=(R[i][j]-sum(L[i][k]*L[j][k]*D[k] for k in range(j)))/dj
A=[[F[k][j]-F[13][j] for j in range(2)] for k in [6,20]];det=A[0][0]*A[1][1]-A[0][1]*A[1][0];assert det!=0
betas=[]
for k in range(n):
 u,v=[F[k][j]-F[13][j] for j in range(2)];beta=(-u*A[0][1]+v*A[0][0])/det;betas.append(beta)
assert betas[6]==betas[13]==0 and betas[20]==1
assert min(betas[k] for k in range(n) if k not in [6,13,20])>8
edges=[]
for i,j in ConvexHull(f).simplices:
 delta=[F[j][k]-F[i][k] for k in range(2)];cross=[delta[0]*(F[k][1]-F[i][1])-delta[1]*(F[k][0]-F[i][0]) for k in range(n)];assert all(x>=0 for x in cross) or all(x<=0 for x in cross);assert [k for k,x in enumerate(cross) if x==0]==sorted([int(i),int(j)]);edges.append([int(i),int(j)])
res={'arithmetic':'exact fractions of the stored binary64 entries, no floating comparisons in proofs','M_symmetric':True,'M_positive_definite_exact_LDL':True,'positive_pivots':n,'LDL_pivots':[str(x) for x in D],'chart_determinant':str(det),'other_beta_min':str(min(betas[k] for k in range(n) if k not in [6,13,20])),'all_8_exposed_edges_verified':edges,'wall':time.perf_counter()-start,'scope':'certifies algebraic boundary structure and positive metric extension of fixed stored model; does NOT certify trajectories or continuous angular first-hit radius'}
Path('limit139/exact_structure.json').write_text(json.dumps(res,indent=2));print({k:v for k,v in res.items() if k!='LDL_pivots'})
