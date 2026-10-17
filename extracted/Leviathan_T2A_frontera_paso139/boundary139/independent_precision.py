# High precision chart jets; no changes to production.
exec(open('boundary139/analyze.py').read().split('results=[]')[0])
mp.mp.dps=100
MM=mp.matrix(M.tolist());co=[(CC[k,0],CC[k,1]) for k in range(27)];co[6]=(mp.mpf(1),mp.mpf(0));co[13]=(mp.mpf(0),mp.mpf(0));co[20]=(mp.mpf(0),mp.mpf(1))
def calc(a,b,V):
 a,b=mp.mpf(float(a)),mp.mpf(float(b));V=mp.matrix([mp.mpf(float(x)) for x in V]);t=[];dt=[];ht=[]
 for k,(al,be) in enumerate(co):
  if k==13:tk=mp.mpf(1);d=[mp.mpf(0)]*2;hh=[[mp.mpf(0)]*2 for _ in range(2)]
  elif k==6:tk=mp.exp(a);d=[tk,mp.mpf(0)];hh=[[tk,mp.mpf(0)],[mp.mpf(0),mp.mpf(0)]]
  elif k==20:tk=b;d=[mp.mpf(0),mp.mpf(1)];hh=[[mp.mpf(0)]*2 for _ in range(2)]
  elif b==0:tk=mp.mpf(0);d=[mp.mpf(0)]*2;hh=[[mp.mpf(0)]*2 for _ in range(2)]
  else:
   tk=mp.exp(al*a)*b**be;d=[al*tk,be*tk/b];hh=[[al*al*tk,al*be*tk/b],[al*be*tk/b,be*(be-1)*tk/b**2]]
  t.append(tk);dt.append(d);ht.append(hh)
 S=sum(t);ds=[sum(d[j] for d in dt) for j in range(2)];hs=[[sum(h[i][j] for h in ht) for j in range(2)] for i in range(2)]
 J=mp.matrix([[dt[k][i]/S-t[k]*ds[i]/S**2 for i in range(2)] for k in range(27)])
 H=[mp.matrix([ht[k][i][j]/S-(dt[k][i]*ds[j]+dt[k][j]*ds[i]+t[k]*hs[i][j])/S**2+2*t[k]*ds[i]*ds[j]/S**3 for k in range(27)]) for i,j in [(0,0),(0,1),(1,1)]]
 G=J.T*MM*J;normal=[h-J*mp.lu_solve(G,J.T*MM*h) for h in H];K=((normal[0].T*MM*normal[2])[0]-(normal[1].T*MM*normal[1])[0])/mp.det(G)
 aa=mp.lu_solve(G,-J.T*MM*(H[0]*V[0]**2+2*H[1]*V[0]*V[1]+H[2]*V[1]**2));eig=mp.eigsy(G,eigvals_only=True)
 return dict(curvature=str(K),eigenvalues=[str(x) for x in eig],speed2=str((V.T*G*V)[0]),acceleration=[float(x) for x in aa])
checks=[]
for i in [1775,1776]:
 for step in [130,139]:
  r,a,b,V,_,_=initial(step,i);c=calc(a,b,V);c.update(ray=i,step=step,acceleration_difference=float(np.max(abs(np.array(c['acceleration'])-acc(a,b,V)))));checks.append(c)
 for br in json.loads((O/'results.json').read_text())['boundary']:
  if br['ray']==i and br['start_step']==139 and br['tolerance_factor']==1:
   c=calc(br['boundary_a'],0,[br['boundary_va'],br['boundary_vb']]);c.update(ray=i,step='boundary');checks.append(c)
(O/'independent_precision.json').write_text(json.dumps(checks,indent=2));print(json.dumps(checks,indent=2))
