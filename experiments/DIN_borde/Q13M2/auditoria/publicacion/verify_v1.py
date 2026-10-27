"""Verificación de archivos y resúmenes existentes; no ejecuta el analista."""
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import subprocess
import numpy as np

S = Path(__file__).resolve().parents[1]
ROOT = S.parents[3]
CFG = json.loads((S/'config.json').read_text())
P = json.loads((S/'sources/provenance.json').read_text())
E = Path(CFG['external_root'])
R = S/'results'
checks = {}


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):
    def bad(x): raise ValueError('JSON no estricto: '+x)
    return json.loads(Path(p).read_text(), parse_constant=bad)
def result(name): return load(R/('cases/'+name+'.json'))['result']
def check(name, condition):
    checks[name] = bool(condition)
    if not condition: raise AssertionError(name)
def write(p, value):
    with p.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2, ensure_ascii=False, allow_nan=False); f.write('\n')
def wilson(k, n):
    z=1.959963984540054; p=k/n; den=1+z*z/n
    mid=(p+z*z/(2*n))/den; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [k/n, mid-h, mid+h]


def main():
    rel=str(Path(__file__).resolve().relative_to(ROOT))
    check('publication_code_committed', Path(__file__).read_bytes()==subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT))
    check('snapshots_SHA', all(sha(S/x['snapshot'])==x['sha256'] for x in P['sources']))
    check('LS_original_SHA_unchanged', sha(ROOT/P['LS_reference']['path'])==P['LS_reference']['sha256'])
    check('independent_kernel_unchanged', sha(S/'scripts/kernels.py')==sha(S/'sources/reference/kernels.py'))
    for p in R.rglob('*.json'): load(p)
    check('results_strict_JSON', True)
    trace=result('bootstrap_trace')
    check('shared_bootstrap_original_folds_A0_recalculation', all(trace[x] for x in ['same_draws_all_levels','copies_original_fold','A0_exactly_shared','D_c_beta_recomputed','draws_match_seed','c_changes_in_bootstrap']))
    check('primary_quantiles_exact', all(x['exact'] for x in trace['ci975'].values()))
    ct=result('compatibility_trace')
    check('same_LS_reference_and_correct_differences', ct['same_LS_in_both'] and ct['differences_correct'])
    for name, arms in [('WD4_bootstrap_degenerate',['WD']),('A0_bootstrap_degenerate',['LP','WD'])]:
        x=result(name)
        check(name+'_all_failures_saved_no_replacement', x['draw_count']==300 and len(x['expected_failed_indices'])==94 and all(x['saved'][a]==x['expected_failed_indices'] for a in arms))
    check('healthy_LP_no_bootstrap_failures', result('WD4_bootstrap_degenerate')['saved']['LP']==[])
    x=result('LS_failures_do_not_change_primaries')
    check('LS_23_failures_preserved_primaries_unchanged',x['LS_failed']==23 and x['full_LS_errors_saved'] and x['primaries_unchanged'])
    base=result('baseline'); bad=result('WD3_Y_constant')
    healthy=[n for n in base['primaria'] if n=='A0' or n.startswith('LP')]
    check('F01_healthy_LP_point_statistics_identical', all(base['primaria'][n]==bad['primaria'][n] for n in healthy))
    check('F01_global_failure_reproduced', bad['veredicto_conjunto']=='INCONCLUSIVE' and bad['por_manipulador']=={} and base['por_manipulador']['LP']['veredicto']=='MODULA')
    gate=result('WD_bad_gate')
    check('gate_isolation_positive_control',gate['veredicto_conjunto']=='INCONCLUSIVE_PARCIAL' and gate['por_manipulador']['LP']['veredicto']=='MODULA')
    collision=load(R/'validation/output_collision.json')['result']
    check('F02_overwrite_reproduced', collision['returncode']==0 and not collision['output_marker_preserved'] and collision['JSON_strict'])
    schema=load(R/'validation/schema.json')
    check('plan_109_checks',len(schema['cases'])==109 and schema['all_ok'])
    dom=load(R/'domain/domain.json')
    check('domain_27_checks',len(dom['checks'])==27 and dom['status']=='PASS')
    check('identical_levels_no_false_MODULA',dom['identical_levels']['veredicto_conjunto']=='NO_REPRODUCIDA')
    ls=load(R/'reference_LS/reference.json'); num=load(R/'reference_LS/numeric_comparison.json')
    check('LS_bootstrap_seed_960002_all_2000_no_failure',ls['all_draws_match_seed'] and ls['seed']==960002 and ls['bootstrap']==2000 and ls['failed']==[])
    check('LS_archive_SHA',sha(ls['archive']['path'])==ls['archive']['sha256'])
    check('F04_literal_mismatch_numerical_agreement', not ls['exact_reproduction'] and num['point_vectors_identical'] and num['within_1e_12'])
    evidence=load(S/'sources/target/Q13M2/pruebas_Q13M2.json')
    check('F03_stale_evidence_SHA', '15ca7b428110f0b7bff1520d93587c7438e8ea0959394f98c91ac37653d95332' in json.dumps(evidence) and 'c195ec50f77fc6382983d170c6ddff2624ab4c0943461b0224805023959ac9e0' in json.dumps(evidence))
    mc=load(R/'monte_carlo_v1/summary.json')
    check('MC_completed_800_nominal',mc['status']=='COMPLETED' and mc['replicates']==800 and mc['permutations']==5000 and mc['bootstrap']==2000 and not (R/'monte_carlo_v1/FAILURE.json').exists())
    check('independent_algebra_controls_PASS',load(R/'monte_carlo_v1/controls.json')['status']=='PASS')
    rates=[]; total=0
    c=np.array(CFG['c']); arms={'LP':[0,1,2,3,4,5],'WD':[0,6,7,8,9,10]}
    for cell in mc['cells']:
        rho=cell['rho']; rows=[]
        for i in range(400):
            x=load(R/f'monte_carlo_v1/null_rho{rho:g}_N320_r{i:04d}.json'); rows.append(x)
            p=Path(x['array']['path'])
            check(f'array_rho{rho:g}_{i}_SHA',sha(p)==x['array']['sha256'])
            with np.load(p,allow_pickle=False) as a:
                if not (a['X'].shape==(1600,) and a['L'].shape==(1600,) and a['Y'].shape==(1600,11) and a['all_D'].shape==(5001,11) and a['bootstrap_D'].shape==(2000,11)):
                    raise AssertionError('dimensiones '+str(p))
                for value in a.values():
                    if not np.isfinite(value).all(): raise AssertionError('no finito '+str(p))
                cp=bool(a['p'][0]<.05 and a['D'][0]>0 and a['slopes'][0]>0)
                if cp!=x['control_PASS']: raise AssertionError('control')
                for arm,ix in arms.items():
                    cc=c[ix]-c[ix].mean(); b=a['bootstrap_D'][:,ix]
                    beta=np.sum(cc*(b-b.mean(axis=1,keepdims=True)),axis=1)/np.sum(cc*cc)
                    if not np.array_equal(beta,a['beta_'+arm]): raise AssertionError('beta')
                    ci=np.quantile(beta,[.0125,.9875])
                    if not np.array_equal(ci,x['IC975'][arm]): raise AssertionError('cuantiles')
                    label='INCONCLUSIVE_SIN_SENAL_CONTROL' if not cp else 'MODULA' if ci[0]>0 else 'NO_CONCLUYENTE'
                    if label!=x['labels'][arm]: raise AssertionError('etiqueta')
            lp=x['labels']['LP']=='MODULA'; wd=x['labels']['WD']=='MODULA'
            if x['family_error']!=(lp or wd) or x['both_false']!=(lp and wd): raise AssertionError('union/interseccion')
            total+=1
        for scope,rr in [('global_rates',rows),('conditional_on_control_PASS',[r for r in rows if r['control_PASS']])]:
            for key in ['false_MODULA_LP','false_MODULA_WD','family_error','both_false']:
                k=sum(r[key] for r in rr); v=wilson(k,len(rr)); reported=cell[scope][key]
                if not (reported['k']==k and reported['n']==len(rr) and np.allclose(v,[reported['rate'],reported['lower'],reported['upper']],atol=1e-15,rtol=0)):raise AssertionError('Wilson')
                rates.append(dict(rho=rho,scope=scope,metric=key,k=k,n=len(rr),rate=v[0],Wilson95_low=v[1],Wilson95_high=v[2]))
        for arm in arms:
            if dict(collections.Counter(r['labels'][arm] for r in rows))!=cell['labels'][arm]:raise AssertionError('conteo')
    check('MC_all_arrays_finite_dimensions_CI_labels_Wilson',total==800)
    with (S/'rates.csv').open('x',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rates[0]));w.writeheader();w.writerows(rates)
    with (S/'external_manifest.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(['path_relative_to_external_root','bytes','sha256'])
        for p in sorted(E.rglob('*')):
            if p.is_file():w.writerow([p.relative_to(E).as_posix(),p.stat().st_size,sha(p)])
    write(S/'verification.json',dict(status='PASS_AUDIT_INTEGRITY',analyst_approved_for_freeze=False,checks=checks,
        notes=['PASS verifica la integridad de esta auditoría; no aprueba el analista.','F01–F04 documentados, sin corregir fuentes.'],
        checks_count=len(checks),MC_replicates=total,new_real_cohort_data=False))
    print(json.dumps(dict(status='PASS_AUDIT_INTEGRITY',checks=len(checks),MC_replicates=total)))


if __name__=='__main__':main()
