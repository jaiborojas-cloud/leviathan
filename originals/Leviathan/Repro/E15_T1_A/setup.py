from pathlib import Path
import shutil,json,hashlib
P=Path(__file__).resolve().parent; W=P.parent
C=W/'unpacked/Leviathan_E15_C1_codigo_resultados/E15_C1'; A=W/'unpacked/Leviathan_E15_C1_A2_codigo_resultados/E15_C1_A2'
for n in ['geometry.py','audit.py']:shutil.copy2(A/n,P/n)
shutil.copytree(A/'source_core',P/'source_core',dirs_exist_ok=True)
for n in ['protocol_C1_frozen.json','protocol_frozen_B7_B8.json','checkpoint_manifest.json','results_states.csv']:
 shutil.copy2(C/n,P/('inherited_'+n))
shutil.copy2(A/'protocol_A2_frozen.json',P/'inherited_protocol_A2_frozen.json')
protocol=dict(version='T1-A-1',purpose='descriptive full panel; no confirmatory inference',population={'splits':list(range(8)),'initializations':list(range(5)),'regimes':['true','random']},center=[0,0],rho=1e-4,target_area=.02,domain='each exact C1 nominal radius, no extension or shrinking of C1',nominal='reuse independently hashed C1 calibration; A2 for two failed C1 domains',geometry='unchanged A2 geometry.py and exact saved M/f; verify reconstruction from each checkpoint',DOP853={'rtol':2e-10,'atol':2e-12},level1={'boundary_rays':[512,1024],'jacobi_angles':[256,512],'phases_cells':[0,.5],'radial_boundary_samples':128,'radial_jacobi_samples':512},candidate_gate={'any_boundary_intersection':True,'any_jacobi_positive_root_or_sign_change':True,'min_abs_intrinsic_det_below':.05,'max_intrinsic_condition_above':100,'numerical_exception_or_resolution_inconsistency':True},level2={'boundary_rays':[2048,4096,8192],'jacobi_angles':[1024],'phases_cells':[0,.5],'RK4_steps':[128,256,512],'RK4_rays':2048},level3={'boundary_rays':[16384],'phases_cells':[0,.5],'trigger':'inconsistent event presence across level2 phases/resolutions or first onset spread >1e-4 R, or no stable Jacobi evidence despite persistent boundary crossing'},stability={'onset_relative_to_R':1e-4,'conjugate_relative_to_R':1e-4,'area_relative':.005},area={'rule':'degree5 Dunavant 32 and 64 rings, 8192 rays for positives; use min first conjugate / first crossing; censored at nominal for no events','no_global_certificate':True},classification={'positive':'stable boundary event and/or stable conjugate zero with sign change before R under refinement; SPD valid; contradictory evidence INCONCLUSIVE','injective':'no sampled loss and stable screening; observational only','numerical_failure':'coarse anomaly disappears consistently under refinement attributable to discretization','inconclusive':'exceptions or unresolved inconsistency'},reuse='10 A2 states reuse complete verified stronger resolution phase and RK4 evidence; no rerun required',rinj='only numerical upper bound from positive events; no certified lower bound fabricated',cut_locus='persistent collisions without detected conjugate => probable only; independent distance minimization deferred T1-B',budget='finite predefined matrix, no replacements; exceptions documented; cap at level3; nominal radius only',persistence='atomic state result; immutable per-state diagnostic ZIP before progress commit; small batches at most 4; stop on upload failure',analysis='regime x split descriptive counts; initialization counts; censored area separate; Spearman and Pearson with available C1 metrics, no imputation; no p values',continuation='more than known 2 positive states => open T1-B; only known2 => specific case series, not population T1-B')
f=P/'protocol_T1_A_frozen.json'
if not f.exists():f.write_text(json.dumps(protocol,indent=2))
(P/'protocol_T1_A_frozen.sha256').write_text(hashlib.sha256(f.read_bytes()).hexdigest())
for s in range(8):
 for j in range(5):
  for r in ['true','random']:
   name=f'split{s}_j{j}_{r}';d=P/'states'/name;d.mkdir(parents=True,exist_ok=True);src=C/'cases'/f'split{s}_init{j}_{r}'
   for n in ['state.npz','checkpoint.json']:shutil.copy2(src/n,d/n)
   shutil.copy2(C/'checkpoints'/f'wine_split{s}_j{j}_{r}.pt',d/'checkpoint.pt')
   nominal=src/'disk.json' if (src/'disk.json').exists() else A/'states'/f'j{j}_{r}'/'nominal.json'
   shutil.copy2(nominal,d/'nominal.json')
   if s==0:
    for sub in ['boundary','jacobi','rk4']:shutil.copytree(A/'states'/f'j{j}_{r}'/sub,d/sub,dirs_exist_ok=True)
    (d/'reuse.json').write_text(json.dumps({'source_archive_sha256':'18dbde0b50fe998274c105ef59618420413d7fbae49100628831527f1fa98648','source_state':f'j{j}_{r}','note':'verified A2 evidence, retained without recalculation'}))
print('80 states staged; frozen protocol',hashlib.sha256(f.read_bytes()).hexdigest())
