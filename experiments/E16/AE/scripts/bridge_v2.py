#!/usr/bin/env python3
"""Corrección derivada de censura y candidatos de colisión; no reintegra rayos."""
from metric_v1 import *
import argparse,time,resource
BRCFG=json.loads((ROOT/'bridge_v2_config.json').read_text())
def all_crossings(poly):
 n=len(poly);vectors=np.roll(poly,-1,axis=0)-poly;found=[]
 def cross(a,b):return a[...,0]*b[...,1]-a[...,1]*b[...,0]
 for i in range(n-2):
  js=np.arange(i+2,n)
  if i==0:js=js[js!=n-1]
  if not len(js):continue
  w=vectors[js];den=cross(vectors[i],w);valid=abs(den)>1e-14;js=js[valid];w=w[valid];den=den[valid]
  if not len(js):continue
  delta=poly[js]-poly[i];t=cross(delta,w)/den;u=cross(delta,vectors[i])/den
  for j in js[(t>1e-9)&(t<1-1e-9)&(u>1e-9)&(u<1-1e-9)]:found.append((i,int(j)))
 return found

def main(out,source=None):
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);started=time.monotonic();src=source or ROOT/BRCFG['source']
 for path,h in BRCFG['sources'].items():
  if source is not None and path.endswith('resources.json'):continue
  assert sha(src/Path(path).name)==h,path
 raw=rows(src/'rays.csv');rr=rows(src/'resolutions.csv');prof=rows(src/'profiles.csv');positions={}
 for q in prof:positions.setdefault((int(q['n']),int(q['ray'])),{})[float(q['r'])]=np.array([float(q['p0']),float(q['p1'])])
 control_rows=[];crossed=np.array([[-1.,-1.],[1.,1.],[-1.,1.],[1.,-1.]]);angles=np.linspace(0,2*np.pi,64,endpoint=False);circle=np.column_stack([np.cos(angles),np.sin(angles)]);control_rows.append({'control':'all_crossings/crossed','status':'PASS' if len(all_crossings(crossed))==1 else 'FAIL'});control_rows.append({'control':'all_crossings/circle','status':'PASS' if not all_crossings(circle) else 'FAIL'})
 candidates=[];perray=[];bridge=[]
 for res in rr:
  n=int(res['n']);rs=sorted([q for q in raw if int(q['n'])==n],key=lambda q:int(q['ray']));coverage=min(float(q['coverage']) for q in rs);first={};last=0.;previous=0.
  for r in np.linspace(0,BRCFG['r_max'],BRCFG['radial_levels']):
   if r>coverage:break
   if r<BRCFG['collision_radius_min']:previous=float(r);last=float(r);continue
   if any(float(r) not in positions.get((n,i),{}) for i in range(n)):break
   poly=np.array([positions[(n,i)][float(r)] for i in range(n)])
   for i,j in all_crossings(poly):
    candidates.append({'n':n,'segment_i':i,'segment_j':j,'r_lower':previous,'r_upper':float(r),'type':'PROPER_POLYGON_CROSSING'})
    for ray in [i,(i+1)%n,j,(j+1)%n]:
     if ray not in first:first[ray]=(previous,float(r),i,j)
   previous=float(r);last=float(r)
  safe=event_count=censored=0
  for q in rs:
   i=int(q['ray']);conj=float(q['conjugate']) if q['conjugate'] else None;collision=first.get(i);joint=min(float(q['coverage']),last);event_values=[v for v in [conj,collision[1] if collision else None] if v is not None and v<=joint];event=min(event_values) if event_values else None;radius=BRCFG['r_fixed'];ambiguous=bool(collision and collision[0]<=radius<collision[1])
   if event is not None and event<=radius:state='OBSERVED_EVENT_CANDIDATE';event_count+=1
   elif joint>=radius and not ambiguous and q['status']!='INCONCLUSIVE_NUMERICAL':state='OBSERVED_NO_EVENT_TO_FIXED';safe+=1
   else:state='RIGHT_CENSORED_OR_UNKNOWN';censored+=1
   perray.append({'n':n,'ray':i,'angle':float(q['angle']),'conjugate':conj,'collision_lower':collision[0] if collision else None,'collision_upper':collision[1] if collision else None,'collision_segments':f'{collision[2]},{collision[3]}' if collision else '', 'collision_nature':'INCIDENT_POLYGON_SEGMENT_CANDIDATE' if collision else 'RIGHT_CENSORED','individual_coverage':float(q['coverage']),'collision_coverage':last,'joint_coverage':joint,'first_event_candidate':event,'state_at_fixed':state,'domain_status':q['status']})
  assert safe+event_count+censored==n
  observed_deg=res['r_deg']!='';bridge.append({'n':n,'r_fixed':BRCFG['r_fixed'],'r_deg':float(res['r_deg']) if observed_deg else None,'A_deg':float(res['A_deg']) if observed_deg else None,'degeneration_status':'OBSERVED_SAMPLED_CANDIDATE' if observed_deg else 'RIGHT_CENSORED_UNKNOWN','no_event_on_sampled_front_to':last,'first_domain_censor':coverage,'r_safe':float(res['r_safe_common']),'A_safe':float(res['A_safe_common']),'conjugate_events':sum(bool(q['conjugate']) for q in rs),'collision_candidates':sum(q['n']==n for q in candidates),'known_no_event_at_fixed':safe,'known_event_at_fixed':event_count,'censored_at_fixed':censored,'fraction_observed_no_event':safe/n,'fraction_event_free_lower':safe/n,'fraction_event_free_upper':1-event_count/n,'v1_individual_coverage_without_conjugate':float(res['fraction_at_fixed'])})
 table(out/'per_ray.csv',perray);table(out/'collisions.csv',candidates,['n','segment_i','segment_j','r_lower','r_upper','type']);table(out/'bridge.csv',bridge);table(out/'controls.csv',control_rows);parent=json.loads((src/'summary.json').read_text());write(out/'summary.json',{'status':'VALID_DERIVATION' if all(q['status']=='PASS' for q in control_rows) else 'INVALID','Q1':parent['Q1'],'Q2':parent['Q2'],'Q3':parent['Q3'],'note':'v1 preserved; coverage/Jacobi fraction is not joint event-free survival; front sampled censoring retained','geodesics_reintegrated':0});write(out/'environment.json',{'config_sha256':sha(ROOT/'bridge_v2_config.json'),'code_sha256':sha(Path(__file__)),'source_scientific_hashes':{Path(q).name:h for q,h in BRCFG['sources'].items() if not q.endswith('resources.json')}});write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024});print((out/'bridge.csv').read_text())
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/bridge_v2');p.add_argument('--source',type=Path);a=p.parse_args();main(a.out,a.source)
