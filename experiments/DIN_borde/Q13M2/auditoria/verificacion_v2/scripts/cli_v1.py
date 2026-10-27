"""F02 y nuevas ramas main de v2, sin cohorte real M2."""
import csv
import json
from pathlib import Path
import subprocess
import sys
from support import STAGE,ROOT,CFG,EXT,LS,PROV,sha,write,code_guard,guard,target,fixture


def main():
    code_guard();assert sha(LS)==PROV['LS_reference']['sha256'];guard(True);m=target()
    out=STAGE/'results/cli';out.mkdir(parents=True,exist_ok=False);external=EXT/'cli';external.mkdir(parents=True,exist_ok=False)
    records=[]
    for name,mode in [('marker_original_CLI','marker'),('directory_original_CLI','directory'),('dangling_symlink','symlink'),('exclusive_race','race'),('LS_failure_main_valid_write','write')]:
        d=external/name;d.mkdir();table=d/'table.csv';rows=fixture(20)
        with table.open('x',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
        plan=dict(n_splits=20,niveles=[dict(nivel=n,brazo=b,dosis=z) for n,b,z in m.NIVELES],ids_sha256=__import__('hashlib').sha256('\n'.join(m.universo(20)).encode()).hexdigest())
        pp=d/'plan.json';write(pp,plan);rs=d/'summary.json';write(rs,dict(tabla_sha256=sha(table),plan_sha256=sha(pp)))
        dest=d/'output';dest.mkdir();file=dest/'RESULTADO_Q13M2.json';before=None
        if mode=='marker':file.write_text('PREVIOUS_MARKER_PRESERVE');before=sha(file)
        elif mode=='directory':file.mkdir()
        elif mode=='symlink':file.symlink_to(d/'DOES_NOT_EXIST')
        args=['--tabla',str(table),'--tabla-sha',sha(table),'--plan',str(pp),'--plan-sha',sha(pp),'--resumen',str(rs),'--tabla-ls',str(LS),'--tabla-ls-sha',sha(LS),'--out',str(dest)]
        if mode in ['marker','directory']:
            cmd=[sys.executable,'-I',str(STAGE/'sources/v2/Q13M2/analisis_Q13M2.py')]+args;injection=False
        else:
            cmd=[sys.executable,str(STAGE/'scripts/cli_injection_v1.py'),'--injection','race' if mode=='race' else 'fail']+args;injection=True
        proc=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True)
        (d/'stdout.txt').write_text(proc.stdout);(d/'stderr.txt').write_text(proc.stderr)
        result=dict(case=name,returncode=proc.returncode,stderr=proc.stderr,in_memory_injection=injection,
            operational_budget=dict(B=CFG['case_B'],NB=CFG['case_NB']) if injection else None,
            fixture_dir=str(d),source_analyst_sha256=sha(STAGE/'sources/v2/Q13M2/analisis_Q13M2.py'))
        if mode=='write':
            value=json.loads(file.read_text(),parse_constant=lambda z:(_ for _ in ()).throw(ValueError(z))) if file.exists() else None
            baseline=m.analizar(rows,20,True,'',B=CFG['case_B'],NB=CFG['case_NB'])
            result.update(target_result=value,primaries_identical=value is not None and value['por_manipulador']==baseline['por_manipulador'] and value['primaria']==baseline['primaria'],
                LS_not_defined=value is not None and 'SYNTHETIC_LS_POINT_FAILURE' in value['secundarios']['compatibilidad_LS']['nota'],JSON_strict=value is not None)
        else:
            result['ABORTA3_no_traceback']=proc.returncode==3 and proc.stderr.startswith('ABORTA:') and 'Traceback' not in proc.stderr
            if mode=='marker':result['marker_preserved']=sha(file)==before
            elif mode=='directory':result['directory_preserved']=file.is_dir()
            elif mode=='symlink':result['symlink_preserved']=file.is_symlink() and not file.exists()
            elif mode=='race':result['marker_preserved']=file.read_text()=='RACE_MARKER_PRESERVE'
        write(out/(name+'.json'),result);records.append(result);print(json.dumps(dict(case=name,rc=proc.returncode)),flush=True)
    write(out/'summary.json',dict(cases=records,new_real_cohort=False,real_LS_reference_only=True))


if __name__=='__main__':main()
