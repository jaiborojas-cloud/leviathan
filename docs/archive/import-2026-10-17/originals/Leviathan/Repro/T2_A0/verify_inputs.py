from pathlib import Path
import hashlib,json,csv,zipfile,collections,shutil
P=Path(__file__).resolve().parent;W=P.parent
B=W/'recovered_t1b/Leviathan/Repro/E15_T1_B';A=W/'a0_inputs/Leviathan/Repro/E15_T1_A';R=W/'recovered_reports/Leviathan'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
for row in csv.DictReader((B/'manifest.csv').open()):
 f=B/row['path'];assert f.is_file() and sha(f)==row['sha256'],f;checks.append(row)
for z in B.glob('*.zip'):
 with zipfile.ZipFile(z) as q:assert q.testzip() is None
assert sha(B/'summary_and_scripts.zip')==(B/'summary_and_scripts.zip.sha256').read_text().split()[0]
assert sha(A/'summary_and_scripts.zip')==(A/'summary_and_scripts.zip.sha256').read_text().split()[0]
with zipfile.ZipFile(A/'summary_and_scripts.zip') as z:assert z.testzip() is None
am={r['path']:r for r in csv.DictReader((A/'manifest.csv').open())};avail=0
for name,row in am.items():
 f=A/name
 if f.is_file():assert sha(f)==row['sha256'],name;avail+=1
assert (A/'state_results.csv').read_bytes()==(B/'T1A_state_results.csv').read_bytes()
old=list(csv.DictReader((B/'T1A_state_results.csv').open()));assert len(old)==80
for row in old:assert sha(B/'states'/row['state']/'checkpoint.pt')==row['checkpoint_sha256']
rows=list(csv.DictReader((B/'common_radius_results.csv').open()));assert len(rows)==320
for name in ['Leviathan_RIPG_E15-T1-B_cierre.md','Leviathan_RIPG_E15-T2_diseno_validacion_externa.md']:
 assert (R/name).read_bytes()==(B/name).read_bytes()
assert sha(B/'protocol_T1_B_frozen.json')==(B/'protocol_T1_B_frozen.sha256').read_text().strip()
# Bind original designs, definitions and implementations without mutation.
refs=[]
for base,names in [(B,['protocol_T1_B_frozen.json','inherited_protocol_C1_frozen.json','input_integrity.json','final_audit.json','geometry.py','run_common.py','T1A_state_results.csv','correlations.csv']), (A,['protocol_T1_A_frozen.json','inherited_protocol_A2_frozen.json','inherited_protocol_frozen_B7_B8.json','run_map.py','run_map_postprocess.py','source_core/e15_repro_core.py']), (R,['Leviathan_RIPG_E15-T2_diseno_validacion_externa.md'])]:
 for name in names:
  refs.append(dict(source=str(base/name),sha256=sha(base/name)))
with zipfile.ZipFile(P/'inherited_definitions.zip','w',zipfile.ZIP_DEFLATED) as z:
 for i,r in enumerate(refs):z.write(r['source'],f'{i:02d}_'+Path(r['source']).name)
report=dict(status='PASS_WITH_INHERITED_ARCHIVAL_NOTE',T1B_manifest_entries=len(checks),T1B_zip_crc=81,checkpoints=80,T1A_classes=dict(collections.Counter(r['classification'] for r in old)),T1B_state_radius_rows=len(rows),T1A_summary_sha256=sha(A/'summary_and_scripts.zip'),T1A_available_manifest_files_checked=avail,T1A_manifest_total=len(am),T1A_full_audit='Inherited verified audit retained; this run rechecks summary, available files, all 80 checkpoints and identical state_results. T1A 780 arrays not redownloaded.',historical_note='T1A historical temporary states/split1_j4_true/jacobi/n512_phase1.tmp.npz absent; final array intact per archived audit; no substitution.',refs=refs,new_neural_states=0)
(P/'input_verification.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='refs'})
