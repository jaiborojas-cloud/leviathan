#!/usr/bin/env python3
from metric_v1 import *
import time,platform,resource

def main():
 out=ROOT/'results/phase0_v1'
 if out.exists():raise FileExistsError(out)
 out.mkdir(parents=True);started=time.monotonic();metric,prep=prepare();grid=[('grid',x,y) for x in np.linspace(*CFG['grid_region'],CFG['grid_count']) for y in np.linspace(*CFG['grid_region'],CFG['grid_count'])]+[('candidate',x,y) for x in CFG['center_candidates'] for y in CFG['center_candidates']];records=[];candidates=[]
 for group,x,y in grid:
  p=np.array([x,y]);r={'group':group,'x':x,'y':y,'status':'UNKNOWN','K':'','K_MP50':'','K_MP80':'','det':'','lambda_min':'','condition':'','float_error':'','MP_error':'','reason':''}
  try:
   h,G,K=metric.geometry(p);eigs=np.linalg.eigvalsh(h);r.update(K=float(K),det=float(np.linalg.det(h)),lambda_min=float(eigs[0]),condition=float(np.linalg.cond(h)));geos=[]
   for digits in CFG['mp_digits']:
    with mp.workdps(digits):geos.append(prep[digits].geometry(np.array([mp.mpf(float(z)) for z in p],object)))
   with mp.workdps(80):
    error=max(abs(mp.mpf(float(h[i,j]))-geos[-1][0][i,j])/max(1,abs(geos[-1][0][i,j])) for i in range(2) for j in range(2));error=max(error,abs(mp.mpf(float(K))-geos[-1][2])/max(1,abs(geos[-1][2])),max(abs(mp.mpf(float(G[i,j,k]))-geos[-1][1][i,j,k])/max(1,abs(geos[-1][1][i,j,k])) for i in range(2) for j in range(2) for k in range(2)));errmp=max(abs(geos[0][2]-geos[1][2])/max(1,abs(geos[1][2])),max(abs(geos[0][0][i,j]-geos[1][0][i,j])/max(1,abs(geos[1][0][i,j])) for i in range(2) for j in range(2)));ok=error<=CFG['K_agreement'] and errmp<=mp.mpf(CFG['MP_agreement']);r.update(status='PASS' if ok else 'INCONCLUSIVE',K_MP50=mp.nstr(geos[0][2],60),K_MP80=mp.nstr(geos[1][2],80),float_error=float(error),MP_error=mp.nstr(errmp,50))
   if group=='candidate' and ok and r['condition']<=CFG['condition_limit']:candidates.append(r)
  except Exception as e:r['reason']=str(e)
  records.append(r)
 valid=all(r['status']=='PASS' for r in records) and any(abs(r['K'])>CFG['nonflat_threshold'] for r in records if r['status']=='PASS');chosen=sorted(candidates,key=lambda q:(-q['K'],q['x'],q['y']))[0] if candidates and max(q['K'] for q in candidates)>0 else next((q for q in candidates if q['x']==q['y']==0),None)
 table(out/'grid.csv',records);write(out/'summary.json',{'status':'PASS_GEOMETRY' if valid and chosen else 'INCONCLUSIVE','center':[chosen['x'],chosen['y']] if chosen else None,'K_center':chosen['K'] if chosen else None,'K_min':min(q['K'] for q in records if q['status']=='PASS'),'K_max':max(q['K'] for q in records if q['status']=='PASS'),'region':CFG['region'],'positive':sum(q['K']>0 for q in records if q['status']=='PASS'),'negative':sum(q['K']<0 for q in records if q['status']=='PASS'),'points':len(records),'sources':CFG['sources']});write(out/'environment.json',{'python':platform.python_version(),'numpy':np.__version__,'mpmath':mp.__version__,'features':metric.f.tolist(),'whitened_scores':metric.R.tolist(),'config_sha256':sha(ROOT/'phase0_config.json'),'code_sha256':sha(Path(__file__))});write(out/'resources.json',{'seconds':time.monotonic()-started,'max_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024});print((out/'summary.json').read_text())
if __name__=='__main__':main()
