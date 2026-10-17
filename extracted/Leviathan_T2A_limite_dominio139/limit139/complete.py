exec(open('limit139/refine.py').read().split('for j in np.linspace')[0])
from scipy.optimize import minimize_scalar
from scipy.spatial import ConvexHull
trace=[]
def fun(j):
 d=compute(float(j),.01,266);trace.append(d);(OUT/'minimum_trace.json').write_text(json.dumps(trace,indent=2));return d['boundary_r']
res=minimize_scalar(fun,bounds=(1775.25,1775.5),method='bounded',options={'xatol':1e-5});best=min(trace,key=lambda x:x['boundary_r'])
# geometric lower distances to every exposed support edge for ALL sampled points.
ss=states[139];P,V=ss['y'].reshape(2,-1,2)
from scipy.special import softmax
W=softmax(P@f.T,axis=1);hull=ConvexHull(f);edges=hull.simplices;dist=[]
for i,j in edges:
 ei=np.eye(27)[i];ej=np.eye(27)[j];direction=ei-ej;alpha=np.clip(((W-ej)@M@direction)/(direction@M@direction),0,1);D=W-(ej+alpha[:,None]*direction);dist.append(np.sqrt(np.maximum(np.einsum('ni,ij,nj->n',D,M,D),0)))
dist=np.array(dist).T;minimum=dist.min(axis=1)
with (OUT/'sampled_boundary_distances.csv').open('w') as fh:
 fh.write('ray,ambient_distance_to_boundary,edge_i,edge_j\n')
 for n in range(2048):
  i,j=edges[dist[n].argmin()];fh.write(f'{n},{minimum[n]:.17g},{i},{j}\n')
result={'local_minimum':best,'optimizer_success':bool(res.success),'sector_bounds':[1775.25,1775.5],'sampled_minimum_ambient_distance':float(minimum.min()),'sampled_minimum_ambient_ray':int(minimum.argmin()),'sampled_minimum_ambient_radius_estimate':float(ss['t']+minimum.min()),'edges':edges.tolist(),'interpretation':'Ambient distance is a lower bound on remaining intrinsic path length for exact points and unit-speed paths; float computations and origin states are not interval-certified; not a continuous angular bound.'}
(OUT/'final_results.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
