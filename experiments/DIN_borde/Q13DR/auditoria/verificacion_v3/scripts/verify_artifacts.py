"""Asserts de aceptación de los resultados ya archivados y manifiestos reproducibles."""
import csv
import hashlib
import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np
import scipy
from support import ROOT, STAGE, CFG, EXTERNAL, sha, write, code_guard


def main():
    code_guard()
    cases=json.loads((STAGE/'results/cases/summary.json').read_text())['cases']
    cs={c['case']:c for c in cases}
    old=json.loads((STAGE/'sources/verificacion_v2/results/cases/summary.json').read_text())['cases']
    assert len(cases)==51 and set(cs)=={c['case'] for c in old}
    checks=[]
    def expect(name,actual,expected=True):
        assert actual==expected,(name,actual,expected)
        checks.append(dict(name=name,actual=actual,expected=expected,status='PASS'))
    def result(name):return cs[name]['result']
    def answer(v):
        v=v.get('target_result',v.get('target',v))
        return v.get('veredicto',v.get('status'))
    for previous in old:
        name=previous['case'];new=cs[name]
        if name in ('v1_duplicate_ID','v1_foreign_ID'):
            expect(name,new.get('exception'),'Aborta');continue
        expect(name+'_returned',new['status'],'RETURNED')
        if name=='new_constant_decimal_c_common80':expect(name,answer(new['result']),'INCONCLUSIVE')
        elif name in ('new_plan_huge_integer_eps','new_plan_missing_file','new_plan_directory','new_table_missing_file'):
            expect(name,answer(new['result']),'ABORTA')
        else:expect(name+'_verdict',answer(new['result']),answer(previous['result']))
    expect('N01_decimal_all_rejected',result('new_constant_decimal_c_rules')['all_rejected'])
    b=result('new_reversed_common_c_range')['bootstrap']
    expect('N02_range',b['rango_c'],.3);expect('N02_margin',b['margen_dD_equivalencia'],.006)
    expect('N02_endpoint_difference',b['diferencia_c_L0_L5'],-.3)
    b=result('new_degenerate_logging_300')
    expect('N05_all_indices',b['all_failed_indices_saved']);expect('N05_count',b['output_failed_count'],116)
    expect('N05_saved',b['output_error_records'],116);expect('N05_no_redraw',b['draw_calls'],300)
    expect('F01_common_point',result('F01_valid_95percent_common')['point_c_equals_common'])
    t=result('v1_bootstrap_trace_pairing_folds_D_c_beta')
    for k in ('same_paired_draws','copies_in_original_fold','D_c_recomputed','c_changed_in_bootstrap'):expect('F01_trace_'+k,t[k])
    expect('F01_beta_matches_OLS',t['beta_OLS_max_error']<1e-10)
    for name in ('new_plan_huge_integer_eps','new_plan_missing_file','new_plan_directory','new_table_missing_file','new_summary_missing_file',
                 'v1_plan_zero_crash','v1_plan_fractional_n_accepted','v1_plan_wrong_eps_accepted','v1_plan_missing_eps_accepted','v1_plan_missing_nivel_crash','v1_plan_wrong_levels_rejected'):
        r=result(name)
        expect(name+'_exit',r['returncode'],3);expect(name+'_prefix',r['stderr'].startswith('ABORTA:'))
        expect(name+'_no_traceback','Traceback' not in r['stderr'])
    expect('JSON_complete_CLI',result('new_CLI_complete')['strict_JSON_no_NaN'])
    domain=json.loads((STAGE/'results/checks/domain_and_rules.json').read_text())
    expect('domain',domain['status'],'PASS');expect('domain_count',len(domain['domain']),27)
    expect('Spearman_count',len(domain['spearman']),4)
    diffs=json.loads((STAGE/'results/diffs/summary.json').read_text())
    ds={r['case']:r for r in diffs['cases']}
    expect('diffs_no_exception',all(r['status']=='RETURNED' for r in ds.values()))
    for k in ('analizar_only_declared_diagnostics','pendiente_assignments_and_return_unchanged'):
        expect('AST_'+k,ds['structural']['result'][k])
    expect('AST_C1_Q13_unchanged',all(ds['structural']['result']['reused_sources_identical'].values()))
    for k in ('all_exact','all_nondegenerate'):expect('compatibility_'+k,ds['compatibility_10']['result'][k])
    expect('slopes_all_exact',ds['slopes_and_ranges']['result']['all_exact'])
    expect('slopes_invalid_rejected',ds['slopes_and_ranges']['result']['all_invalid_rejected'])
    expect('plans_all_ok',ds['plans']['result']['all_ok']);expect('plans_count',len(ds['plans']['result']['cases']),87)
    b=ds['bootstrap_constant_c']['result']
    expect('N01_bootstrap_verdict',b['target_result']['veredicto'],'INCONCLUSIVE')
    expect('N01_bootstrap_all_indices',b['exactly_saved_indices']);expect('N01_bootstrap_errors',b['all_errors_are_constant_c'])
    expect('N01_bootstrap_failed_count',b['target_result']['bootstrap']['replicas_fallidas'],271)
    expect('N01_bootstrap_no_redraw',b['draw_calls'],300)
    for name,r in ds.items():
        if name.endswith(('directory','utf8','json','too_large')):expect(name+'_ABORTA',r['result']['ok'])
    for s in json.loads((STAGE/'sources/provenance.json').read_text())['sources']:expect('sha_'+s['snapshot'],sha(STAGE/s['snapshot']),s['sha256'])
    # Full diff scope: previous stages and production sources must remain unchanged.
    base=json.loads((STAGE/'sources/provenance.json').read_text())['base_revision']
    changed=subprocess.check_output(['git','diff','--name-only',base,'HEAD'],cwd=ROOT,text=True).splitlines()
    expect('only_new_stage_committed',all(x.startswith(str(STAGE.relative_to(ROOT))+'/') for x in changed))
    dirty=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    expect('no_tracked_changes_elsewhere',not dirty)
    environment=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),
        fecha_local=datetime.now(ZoneInfo('America/Mexico_City')).isoformat(),
        BLAS_threads=1,synthetic_only=True,original_suite_executed=False,monte_carlo_repeated=False,
        diff_suite_seconds=diffs['seconds'],cases_wall_time='No instrumentado; logs completos conservados')
    write(STAGE/'environment.json',environment)
    ext=[]
    for p in sorted(EXTERNAL.rglob('*')):
        if p.is_file():ext.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
    with (STAGE/'external_manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader();w.writerows(ext)
    write(STAGE/'verification.json',dict(status='PASS_REGRESSION_SCOPE',target_revision=CFG['target_revision'],analysis_sha256=CFG['analysis_sha256'],
        tests_sha256=CFG['tests_sha256'],N01_N05='RESUELTOS_EN_CASOS_REPRODUCIBLES',F01_F06='SIN_REGRESIONES_EN_MATRIZ_COMPLETA',
        new_defects_observed=[],checks=checks,external_files=len(ext),monte_carlo_repeated=False,
        freeze_authorized=False,note='Confirmación técnica del alcance probado; la aprobación de congelación corresponde al responsable.'))
    files=[p for p in sorted(STAGE.rglob('*')) if p.is_file() and p.name not in ('manifest.csv','manifest.sha256')]
    assert not any(p.suffix in ('.npz','.npy','.pt','.pth','.zip') for p in files)
    with (STAGE/'manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','bytes','sha256']);w.writeheader()
        for p in files:w.writerow(dict(path=str(p.relative_to(STAGE)),bytes=p.stat().st_size,sha256=sha(p)))
    with (STAGE/'manifest.sha256').open('x') as f:
        for p in files+[STAGE/'manifest.csv']:f.write(sha(p)+'  '+str(p.relative_to(STAGE))+'\n')
    print(json.dumps(dict(status='PASS_REGRESSION_SCOPE',checks=len(checks),manifest_files=len(files)+1,external_files=len(ext))))


if __name__=='__main__':main()
