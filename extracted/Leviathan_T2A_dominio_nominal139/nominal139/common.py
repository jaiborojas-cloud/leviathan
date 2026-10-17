import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,zipfile,pickle,io,json,hashlib
from pathlib import Path
import numpy as np
from scipy.integrate import OdeSolution
from scipy.special import softmax
sys.path.insert(0,str(Path('Windows_RIPG_T2A_CP90/source').resolve()))
from geometry import Geometry,area7,triangles
O=Path('nominal139')
with zipfile.ZipFile('Windows_RIPG_T2A_CP90/data/origin_mpfr_step_000090.zip') as z:b=pickle.loads(z.read('replay.pkl'))
with zipfile.ZipFile('upload/RIPG_RESULTADOS_PC.zip') as z:
 ix=json.loads(z.read('output/index.json'));m=json.loads(z.read('output/return_manifest.json'))
 for n,h in m['files'].items():assert hashlib.sha256(z.read('output/'+n)).hexdigest()==h
 for rec in ix['segments']:
  with zipfile.ZipFile(io.BytesIO(z.read('output/'+rec['file']))) as q:assert q.testzip() is None;d=pickle.loads(q.read('replay.pkl'))
  assert d['start_step']==len(b['steps']) and d['start_t']==b['ts'][-1]
  for k in ['steps','ts','interpolants']:b[k].extend(d[k])
  b['solver']=d['solver']
sol=OdeSolution(np.array(b['ts']),b['interpolants']);r=float(b['solver']['t'])
with np.load('Windows_RIPG_T2A_CP90/data/state.npz') as d:g=Geometry(d['M'],d['f'])
