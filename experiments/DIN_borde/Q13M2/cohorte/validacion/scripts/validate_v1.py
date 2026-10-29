"""Validación sin entrenar: tres reconstrucciones, IO y ejecutor falso."""
import ast
import concurrent.futures as cf
import contextlib
import csv
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import numpy as np

ROOT=Path(__file__).resolve().parents[6]
STAGE=ROOT/'experiments/DIN_borde/Q13M2/cohorte'
OUT=STAGE/'validacion/results_v1'
EXT=ROOT.parent/'work/din-q13m2-producer-validation-v2'
SCRIPT=STAGE/'scripts/cohorte_v2.py'


def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False);f.write('\n')


def run(name,args):
    p=subprocess.run([sys.executable,'-I','-B',str(SCRIPT)]+args,capture_output=True,text=True)
    write(OUT/(name+'.json'),dict(returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
    if p.returncode!=0:raise RuntimeError(p.stderr)
    return p


def main():
    for p in [SCRIPT,STAGE/'validacion/scripts/validate_v1.py']:
        assert p.read_bytes()==subprocess.check_output(['git','show','HEAD:'+str(p.relative_to(ROOT))],cwd=ROOT)
    OUT.mkdir(parents=True,exist_ok=False);EXT.mkdir(parents=True,exist_ok=False)
    try:
        # Actual untrained random controls only. Never run --limite>0.
        run('gate',['--parte','compuerta','--procesos','2','--out',str(EXT/'gate')])
        gate=json.loads((EXT/'gate/COMPUERTA_q13m2.json').read_text())
        assert gate['PASA'] is True and gate['entrenamientos']==0
        assert len(gate['reconstrucciones'])==3 and all(r['relative_M_error']==0 and r['f_identical'] for r in gate['reconstrucciones'])
        write(OUT/'COMPUERTA_linux_sin_entrenar.json',gate)
        spec=importlib.util.spec_from_file_location('producer_fixture',SCRIPT);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        ctx=m.preflight(EXT/'io_fixture');m.bind_output(ctx)
        m.exclusive_json(EXT/'io_fixture/COMPUERTA_q13m2.json',gate)
        tasks=m.universe(ctx['plan']);assert len(tasks)==17600
        ids=[x[0] for x in tasks];assert hashlib.sha256('\n'.join(ids).encode()).hexdigest()==ctx['plan']['ids_sha256']
        schedule,done,total=m.pending_tasks(ctx)
        expected=[(f'q13m2_{l["nivel"]}_s{s:04d}_k{k}',l['nivel'],s,k) for s in range(320) for k in range(5) for l in ctx['plan']['niveles']]
        assert schedule==expected and done==0 and total==17600
        # Record fixtures are explicitly not measurements or trained trajectories.
        for i,error in [(0,''),(1,'SYNTHETIC_FIXTURE_FAILURE')]:
            t=tasks[i];row=m.empty_row(t,error)
            if not error:
                for key in m.COLUMNS[4:-1]:row[key]=.25
            rec=m.seal_record(dict(row=row,script_sha256=ctx['script_sha256'],plan_sha256=m.PLAN_SHA,seconds=0,fixture=True))
            m.exclusive_json(Path(ctx['out'])/'trajectories'/(t[0]+'.json'),rec)
        with (Path(ctx['out'])/'trajectories'/(tasks[2][0]+'.json')).open('xb') as f:f.write(b'{truncated fixture')
        # A pre-existing interrupted claim must be preserved, not trained.
        m.exclusive_json(Path(ctx['out'])/'claims'/(tasks[3][0]+'.json'),dict(fixture=True))
        m.CTX=dict(ctx,np=np)
        interrupted=m.run_trajectory(tasks[3]);assert interrupted['error'] and not interrupted['skipped']
        resumed=m.run_trajectory(tasks[3]);assert resumed['skipped']
        pending,done,total=m.pending_tasks(ctx,33)
        assert done==4 and total==17596 and len(pending)==33 and not {t[0] for t in tasks[:4]}&{t[0] for t in pending}
        capture=io.StringIO()
        with contextlib.redirect_stdout(capture):m.table(ctx)
        table=Path(ctx['out'])/'q13m2_cohorte.csv';old=table.read_bytes()
        with table.open(newline='') as f:
            reader=csv.DictReader(f);rows=list(reader);assert reader.fieldnames==m.COLUMNS
        assert len(rows)==17600 and [r['trajectory'] for r in rows]==ids and len(m.COLUMNS)==15
        assert rows[0]['X10']=='0.25' and rows[1]['error']=='SYNTHETIC_FIXTURE_FAILURE'
        assert rows[2]['error']=='RECORD_INCOMPLETE_PRESERVED'
        assert 'INTERRUPTED_CLAIM_PRESERVED' in rows[3]['error'] and rows[4]['error']=='TRAJECTORY_MISSING'
        with contextlib.redirect_stdout(capture):m.table(ctx)
        assert table.read_bytes()==old
        summary=json.loads((Path(ctx['out'])/'RESUMEN_q13m2.json').read_text())
        assert summary==dict(tabla_sha256=hashlib.sha256(old).hexdigest(),plan_sha256=m.PLAN_SHA,script_sha256=ctx['script_sha256'])
        try:m.cohort(ctx,12,0)
        except RuntimeError as e:assert 'Tabla ya publicada' in str(e)
        else:raise AssertionError('Se permitió añadir después de tabla')
        # Exclusive writes and locking; no model or worker is invoked.
        race=EXT/'race.json';barrier=threading.Barrier(2)
        def attempt(i):
            barrier.wait()
            try:m.exclusive_json(race,dict(i=i));return 'OK'
            except FileExistsError:return 'EXISTS'
        with cf.ThreadPoolExecutor(max_workers=2) as pool:assert sorted(pool.map(attempt,[0,1]))==['EXISTS','OK']
        with m.FileLock(EXT/'lock'):
            try:
                with m.FileLock(EXT/'lock'):raise AssertionError('Doble lock permitido')
            except RuntimeError:pass
        class Pool:
            def __init__(self,fail=False):self.sent=[];self.fail=fail;self.shutdowns=[]
            def submit(self,fn,task):
                self.sent.append(task);f=cf.Future()
                if self.fail:f.set_exception(RuntimeError('SYNTHETIC_SCHEDULER_INTERRUPTION'))
                else:f.set_result(dict(id=task[0],error=False))
                return f
            def shutdown(self,**kw):self.shutdowns.append(kw)
        pool=Pool();got=[];m.collect_bounded(pool,expected,12,got.append)
        assert pool.sent==expected and len(got)==17600
        pool=Pool(True)
        try:m.collect_bounded(pool,expected,12,lambda x:None)
        except RuntimeError:pass
        else:raise AssertionError('Interrupción no propagada')
        assert len(pool.sent)==12 and pool.shutdowns==[dict(wait=True,cancel_futures=True)]
        # Scientific functions and archive measurement must remain exact to parent.
        parent=ast.parse((ROOT/'experiments/DIN_borde/Q13DR/cohorte/scripts/cohorte_v3.py').read_text());child=ast.parse(SCRIPT.read_text())
        funcs=lambda t:{n.name:n for n in t.body if isinstance(n,ast.FunctionDef)}
        pf,cfns=funcs(parent),funcs(child)
        for key in ('measure','checkpoint','reconstruct','collect_bounded','exclusive_bytes','FileLock'):
            if key=='FileLock':
                a=next(n for n in parent.body if isinstance(n,ast.ClassDef) and n.name==key)
                b=next(n for n in child.body if isinstance(n,ast.ClassDef) and n.name==key)
            else:a,b=pf[key],cfns[key]
            assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
        for key,name in [('RECIPE_SOURCE','recipe'),('SUPPORT_SOURCE','support'),('LP_SOURCE','LP')]:
            n=next(n for n in child.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id==key)
            assert ast.literal_eval(n.value).encode()==(ROOT/m.ORIGINALS[name]['path']).read_bytes()
        # Se ejecuta el adaptador LP con espías; no hay tensores, red ni optimizador reales.
        spy_calls=[]
        class Value:
            def __init__(self,x):self.x=x
            def __pow__(self,x):return Value(('pow',self.x,x))
            def sum(self,dim):return Value(('sum',self.x,dim))
            def mean(self):return Value(('mean',self.x))
            def __rmul__(self,x):return Value(('mul',x,self.x))
            def __add__(self,x):return Value(('add',self.x,x.x))
            def backward(self):spy_calls.append(('backward',self.x))
        class Optimizer:
            def zero_grad(self):spy_calls.append('zero')
            def step(self):spy_calls.append('fake_step_no_weights')
        class Batch:
            def __len__(self):return 90
            def __getitem__(self,ix):return self
        import types
        torch_fake=types.SimpleNamespace(nn=types.SimpleNamespace(functional=types.SimpleNamespace(cross_entropy=lambda z,y:Value('CE'))),isfinite=lambda x:True)
        e=dict(np=np,original_update=lambda *a:spy_calls.append(('delegate',a[-3],a[-2])))
        node=next(n for n in ast.parse(m.LP_SOURCE).body if isinstance(n,ast.FunctionDef) and n.name=='update_m2')
        exec(compile(ast.get_source_segment(m.LP_SOURCE,node),'<LP intacto con espías>','exec'),e)
        batches=hashlib.sha256();e['update_m2'](lambda x:Value('z'),Optimizer(),Batch(),Batch(),np.random.default_rng(905201),batches,'LP',.003,torch_fake)
        assert spy_calls==['zero',('backward',('add','CE',('mul',.003,('mean',('sum',('pow','z',2),1))))),'fake_step_no_weights']
        for arm,dose in [('A0',0),('WD',.709)]:e['update_m2'](None,None,None,None,None,None,arm,dose,torch_fake)
        assert spy_calls[-2:]==[('delegate','A0',0),('delegate','WD',.709)]
        result=dict(status='PASS',training_updates=0,new_cohort_trajectories_trained=0,gate_reconstructions=3,
                    measure_AST_identical=True,embedded_sources_byte_identical=True,planned_ids=17600,columns=m.COLUMNS,
                    paired_schedule_exact=True,table_complete_and_idempotent=True,preserve_failure_truncation_claim=True,
                    exclusive_race_pass=True,locks_pass=True,scheduler_normal_17600=True,scheduler_interruption_sent=12,
                    versions=ctx['versions'],script_sha256=ctx['script_sha256'],plan_sha256=m.PLAN_SHA,
                    native_Windows_tested=False,python_I_spawn_Linux_tested=True,fixture_data_not_cohort=True,LP_spy_formula_and_delegation=True,no_cohort_CLI_executed=True)
        write(OUT/'verification.json',result)
        entries=[]
        for p in sorted(EXT.rglob('*')):
            if p.is_file():entries.append(dict(path=str(p),bytes=p.stat().st_size,sha256=m.sha(p)))
        with (OUT/'external_manifest.csv').open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['path','bytes','sha256'],lineterminator='\n');w.writeheader();w.writerows(entries)
        print(json.dumps(result),flush=True)
    except Exception:
        import traceback
        write(OUT/'FAILURE.json',dict(error=traceback.format_exc(),cohort_trained=False));raise


if __name__=='__main__':main()
