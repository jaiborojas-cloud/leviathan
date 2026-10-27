"""Integra resultados ya producidos; no ejecuta analista ni Monte Carlo."""
import csv
import hashlib
import json
import os
import platform
import subprocess
import numpy as np
from support import ROOT,STAGE,CFG,PROV,EXT,LS,sha,write,code_guard


def load(p):
    def bad(x):raise ValueError('JSON no estricto: '+x)
    return json.loads(p.read_text(),parse_constant=bad)


def main():
    code_guard();checks={}
    def check(k,c):
        checks[k]=bool(c)
        if not c:raise AssertionError(k)
    check('LS_source_unchanged',sha(LS)==PROV['LS_reference']['sha256'])
    check('diff_SHA',sha(STAGE/'sources/analista_v1_v2.diff')==PROV['diff_sha256'])
    check('cases_script_byte_exact',sha(STAGE/'scripts/cases_v1.py')==sha(STAGE/'sources/auditoria_v1/scripts/cases_v1.py'))
    check('reference_script_byte_exact',sha(STAGE/'scripts/reference_LS_v1.py')==sha(STAGE/'sources/auditoria_v1/scripts/reference_LS_v1.py'))
    old=load(STAGE/'sources/auditoria_v1/results/cases/summary.json')['cases'];new=load(STAGE/'results/cases/summary.json')['cases']
    check('previous_23_cases_completed',len(old)==len(new)==23)
    om={x['case']:x for x in old};nm={x['case']:x for x in new};comparisons=[]
    expected_change={'WD3_X_constant','WD3_L_constant','WD3_Y_constant','LP3_Y_constant'}
    for name,x in nm.items():
        same=x.get('result')==om[name].get('result') and x.get('exception')==om[name].get('exception') and x.get('message')==om[name].get('message')
        comparisons.append(dict(case=name,unchanged=same,expected_F01_change=name in expected_change,status=x['status']))
        check('regression_'+name,same==(name not in expected_change))
    write(STAGE/'regression_matrix.json',dict(cases=comparisons,non_F01_results_exactly_unchanged=True))
    trace=nm['bootstrap_trace']['result']
    check('shared_draws_blocks_A0_recalculation',all(trace[k] for k in ['same_draws_all_levels','copies_original_fold','A0_exactly_shared','D_c_beta_recomputed','draws_match_seed','c_changes_in_bootstrap']))
    check('quantiles_0125_9875_exact',all(x['exact'] for x in trace['ci975'].values()))
    comp=nm['compatibility_trace']['result'];check('same_LS_replica_correct_differences',comp['same_LS_in_both'] and comp['differences_correct'])
    for name,arms in [('WD4_bootstrap_degenerate',['WD']),('A0_bootstrap_degenerate',['LP','WD'])]:
        r=nm[name]['result'];check(name+'_all94_recorded',r['draw_count']==300 and len(r['expected_failed_indices'])==94 and all(r['saved'][a]==r['expected_failed_indices'] for a in arms))
    changed=load(STAGE/'results/changed_cases/summary.json')['cases'];cm={x['case']:x for x in changed}
    check('changed_cases_20_completed',len(changed)==20)
    for nv in ['WD3','LP3','A0']:
        for kind in ['Y','X','L']:
            r=cm[f'F01_{nv}_{kind}']['result']
            check(f'F01_{nv}_{kind}',r['global_inconclusive'] if nv=='A0' else r['healthy_identical'] and r['localized'])
    both=cm['both_exclusive_bad']['result']
    check('both_bad_not_mislabeled',both['veredicto_conjunto']=='INCONCLUSIVE_PARCIAL' and all(r['veredicto']=='INCONCLUSIVE' for r in both['por_manipulador'].values()))
    err=cm['LS_error_does_not_contaminate']['result']
    check('LS_error_preserves_primaries_LP_WD',err['primaries_identical'] and err['LP_WD_identical'])
    for name in ['compatibility_64_63','compatibility_64_1']:
        check(name+'_clear_ValueError',cm[name]['exception']=='ValueError' and 'distinto tamano' in cm[name]['message'])
    check('compatibility_valid_sizes_RETURNED',cm['compatibility_64_64']['status']=='RETURNED')
    # Deliberadamente no se aprueban APIs fuera del contrato como CLI válidas.
    api_limits={k:dict(status=cm[k]['status'],exception=cm[k].get('exception'),message=cm[k].get('message')) for k in ['bad_size_analyzar_API','compatibility_equal_shape_(2, 32)','compatibility_equal_shape_(0,)']}
    cli=load(STAGE/'results/cli/summary.json')['cases']
    check('CLI_5_completed',len(cli)==5)
    for r in cli:
        if r['case']=='LS_failure_main_valid_write':check(r['case'],r['returncode']==0 and r['primaries_identical'] and r['LS_not_defined'] and r['JSON_strict'])
        else:check(r['case'],r['ABORTA3_no_traceback'] and r.get('marker_preserved',r.get('directory_preserved',r.get('symlink_preserved',False))))
    static=load(STAGE/'results/static/results.json')
    check('F03_binding_and_statistical_AST',static['PASS_static_and_evidence'])
    ref=load(STAGE/'results/reference_LS/reference.json');prior=load(STAGE/'sources/auditoria_v1/results/reference_LS/reference.json')
    check('F04_tolerance_1e_12',abs(ref['beta']-.07692466151365258)<=1e-12)
    check('LS_point_CI_identical_v1',ref['beta']==prior['beta'] and ref['CI95']==prior['CI95'])
    check('LS_seed2000_and_all_draws',ref['seed']==960002 and ref['bootstrap']==2000 and ref['all_draws_match_seed'] and ref['failed']==[])
    check('LS_array_SHA',sha(ref['archive']['path'])==ref['archive']['sha256'])
    findings=[]
    for name,missing in [('two_primary_failures_WD','WD3'),('two_malo_levels_WD','WD3')]:
        r=cm[name]['result'];mot=r['motivos_inconclusive']
        check(name+'_only_first_failure_saved',len(mot)==1 and 'WD2' in mot[0] and missing not in '\n'.join(mot))
        findings.append(dict(case=name,observed_reasons=mot,omitted_level=missing,healthy_verdict=r['por_manipulador']['LP']['veredicto'],joint=r['veredicto_conjunto']))
    write(STAGE/'new_findings.json',dict(N01=dict(severity='MEDIA_TRAZABILIDAD',wrong_verdict_demonstrated=False,description='Se omiten fallos posteriores de un brazo ya inconcluso',cases=findings),
        N02=dict(severity='BAJA_DOCUMENTAL',description='Persisten dos frases de igualdad exacta de beta_LS pese a la tolerancia de cabecera',lines=static['documentary_exact_wording_remaining']),API_limits=api_limits))
    for p in (STAGE/'results').rglob('*.json'):load(p)
    check('all_results_strict_JSON',True)
    check('no_MC_rerun',not (STAGE/'results/monte_carlo_v1').exists())
    write(STAGE/'environment.json',dict(python=platform.python_version(),numpy=np.__version__,platform=platform.platform(),commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),BLAS_threads=1,MC_repeated=False))
    with (STAGE/'external_manifest.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['path','kind','bytes','sha256','target'],lineterminator='\n');w.writeheader()
        for p in sorted(EXT.rglob('*')):
            if p.is_symlink():
                target=os.readlink(p);raw=target.encode();w.writerow(dict(path=p.relative_to(EXT).as_posix(),kind='symlink',bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),target=target))
            elif p.is_file():w.writerow(dict(path=p.relative_to(EXT).as_posix(),kind='file',bytes=p.stat().st_size,sha256=sha(p),target=''))
    write(STAGE/'verification.json',dict(status='PASS_VERIFICATION_WITH_FINDINGS',F01='RESUELTO',F02='RESUELTO',F03='RESUELTO_VINCULACION',F04='RESUELTO_NUMERICAMENTE',
        checks=checks,checks_count=len(checks),new_findings=['N01','N02'],MC_repeated=False,not_an_approval_to_freeze=True,analyst_modified=False,new_real_data=False,
        reference_array_SHA_identical_v1=ref['archive']['sha256']==prior['archive']['sha256']))
    print(json.dumps(dict(status='PASS_VERIFICATION_WITH_FINDINGS',checks=len(checks),new_findings=['N01','N02'],MC_repeated=False)))


if __name__=='__main__':main()
