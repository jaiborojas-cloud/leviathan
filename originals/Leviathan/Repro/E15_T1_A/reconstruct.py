import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,hashlib,time
import numpy as np,torch
from sklearn.datasets import load_wine
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'source_core'));import e15_repro_core as core
torch.set_num_threads(1);torch.set_default_dtype(torch.float64);wine=load_wine();out=[];start=time.perf_counter()
for d in sorted((P/'states').iterdir()):
 cp=torch.load(d/'checkpoint.pt',weights_only=False);model=core.WineMLP();model.load_state_dict(cp['model_state_dict']);x=(wine.data-cp['scaler_mean'])/cp['scaler_scale'];ids=cp['val_indices'];R,U,f=core.make_geom_state(model,torch.tensor(x[ids]),torch.tensor(wine.target[ids]));M=core.subset_M(R,U,[0,1,2]).numpy();z=np.load(d/'state.npz');err=float(abs(M-z['M']).max()/abs(z['M']).max());fe=float(abs(f.numpy()-z['f']).max());o=dict(state=d.name,M_relative_max_error=err,f_max_absolute_error=fe,passed=bool(err<1e-8 and fe<1e-12),checkpoint_sha256=hashlib.sha256((d/'checkpoint.pt').read_bytes()).hexdigest());out.append(o);(d/'reconstruction.json').write_text(json.dumps(o,indent=2))
(P/'field_reconstruction.json').write_text(json.dumps({'states':out,'seconds':time.perf_counter()-start},indent=2));print('reconstruction',sum(x['passed'] for x in out),len(out),'max M',max(x['M_relative_max_error'] for x in out));assert all(x['passed'] for x in out)
