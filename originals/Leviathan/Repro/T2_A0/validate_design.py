from pathlib import Path
import json,csv,hashlib
import numpy as np
from scipy.stats import binom
from primary_analysis import tail,average_precision,evaluate
P=Path(__file__).resolve().parent
p=json.loads((P/'protocol.json').read_text());seeds=list(csv.DictReader((P/'cohort_seeds.csv').open()))
assert len(seeds)==800 and len({r['trajectory'] for r in seeds})==800
assert len({r['init_seed'] for r in seeds})==800 and len({r['batch_seed'] for r in seeds})==800
assert len({r['split_seed'] for r in seeds})==160
assert p['time']['t0']==5 and p['time']['future_checkpoints']==list(range(25,251,25))
assert p['predictor']['r_star']==.05697156262709151
assert tail(np.arange(800)).sum()==80
assert tail([1]*800).sum()==800
assert average_precision([1,2,3],[0,0,1])==1
assert evaluate(np.repeat(np.arange(160),5),np.arange(800),np.zeros(800,int))['decision']=='INCONCLUSIVE'
split=np.repeat(np.arange(160),5);y=(np.arange(800)%10==0).astype(int)
assert evaluate(split,np.arange(800),y,reps=1000)['decision']=='FAIL'
x=y+np.arange(800)*1e-6
assert evaluate(split,x,y,reps=1000)['decision']=='PASS_PROSPECTIVE_PILOT'
rows=list(csv.DictReader((P/'event_sensitivity.csv').open()));r=next(r for r in rows if r['N']=='800' and r['p']=='0.025' and r['within_split_ICC']=='0')
assert abs(float(r['prob_at_least30'])-binom.sf(29,800,.025))<1e-12
report={'status':'PASS','synthetic_only':True,'new_neural_states':0,'checks':['800 distinct future initializations and streams;160splits','rstar exact;time fixed','tie handling','single-positive AP','information gate','synthetic null-like FAIL','synthetic strong-separation PASS','exact event probability consistency'],'not_power_validation':'Synthetic checks validate logic only; no empirical performance claim.'}
(P/'design_validation.json').write_text(json.dumps(report,indent=2));print(report)
