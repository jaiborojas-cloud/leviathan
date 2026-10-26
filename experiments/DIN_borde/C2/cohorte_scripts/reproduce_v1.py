"""Compuerta previa: serializar/reconstruir tres modelos sin entrenar; no rho."""
import json
import subprocess
import numpy as np
from pathlib import Path
from support_v1 import ROOT, STAGE, CFG, write, sha, frozen, guard, code_guard


def main():
    code_guard()
    seed_sources = {}
    seeds_old = set()
    for name, rel in [('G2','experiments/DIN_borde/G3/sources/G2/config.json'), ('G3','experiments/DIN_borde/G3/config.json')]:
        p = ROOT/rel; old=json.loads(p.read_text()); n=len(old['splits'])
        seeds = (set(range(old['split_seed_base'],old['split_seed_base']+n)) |
                 set(range(old['init_seed_base'],old['init_seed_base']+5*n)) |
                 set(range(old['batch_seed_base'],old['batch_seed_base']+5*n)))
        seeds_old |= seeds
        seed_sources[name] = dict(path=rel,sha256=sha(p),splits=n)
    n=len(CFG['splits'])
    new = (set(range(611000,611000+n)) | set(range(621000,621000+5*n)) |
           set(range(631000,631000+5*n)))
    control_seeds = set(range(641000,641003)) | set(range(651000,651003))
    if new & seeds_old or control_seeds & (new | seeds_old):
        raise RuntimeError('Colisión de semillas')
    guard()
    import torch
    from sklearn.preprocessing import StandardScaler
    from run_v1 import network
    torch.set_num_threads(1); torch.set_num_interop_threads(1)
    core=frozen('core')
    output=STAGE/'cohorte/compuerta_v1'; output.mkdir(exist_ok=False)
    external=Path(CFG['gate_arrays_dir']); external.mkdir(exist_ok=False)
    records=[]
    for j in range(3):
        rng=np.random.default_rng(651000+j)
        means=np.zeros((3,13)); means[:,:2]=[[2.,0.],[-1.,np.sqrt(3)],[-1.,-np.sqrt(3)]]
        y=np.repeat(np.arange(3),39)
        tr=np.array([39*c+i for c in range(3) for i in range(30)])
        va=np.array([39*c+i for c in range(3) for i in range(30,39)])
        raw=means[y]+.8*rng.normal(size=(117,13))
        Z=StandardScaler().fit(raw[tr]).transform(raw)
        torch.manual_seed(641000+j); model=network(torch)
        R,U,fp=core.make_geom_state(model,torch.tensor(Z[va]),torch.tensor(y[va]))
        M=core.subset_M(R,U,[0,1,2]).numpy(); f=fp.numpy()
        weights={k: v.detach().numpy() for k,v in model.state_dict().items()}
        path=external/f'control_{j}.npz'
        with path.open('xb') as file:
            np.savez_compressed(file, M=M,f=f,Z=Z,y=y,panel_ids=va,**{'weight_'+k:v for k,v in weights.items()})
        restored=network(torch)
        with np.load(path,allow_pickle=False) as data:
            restored.load_state_dict({k[7:]:torch.tensor(data[k]) for k in data.files if k.startswith('weight_')})
            R2,U2,fp2=core.make_geom_state(restored,torch.tensor(data['Z'][data['panel_ids']]),torch.tensor(data['y'][data['panel_ids']]))
            M2=core.subset_M(R2,U2,[0,1,2]).numpy()
            err=float(np.linalg.norm(M2-data['M'])/max(np.linalg.norm(data['M']),np.finfo(float).tiny))
            same_f=bool(np.array_equal(fp2.numpy(),data['f']))
        records.append(dict(control=j,weight_seed=641000+j,data_seed=651000+j,relative_M_error=err,
            f_identical=same_f,pass_test=bool(err==0 and same_f),
            array=dict(path=str(path),sha256=sha(path),bytes=path.stat().st_size)))
    result=dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,
        source_seeds=seed_sources,new_seed_count=len(new),seeds_disjoint=True,cohort_training_started=False,
        control_models_trained=False,rho_computed=False,associations_computed=False,
        code_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip())
    write(output/'reconstruction.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['records','source_seeds']},ensure_ascii=False))
    if result['status']!='PASS': raise RuntimeError('Compuerta fallida: no entrenar')

if __name__=='__main__': main()
