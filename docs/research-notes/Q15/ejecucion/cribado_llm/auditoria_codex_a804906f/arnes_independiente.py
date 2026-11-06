"""Synthetic independent audit. No network; labeling only simular=True."""
import contextlib, importlib.util, io, json, tempfile, pathlib, types, urllib.request, hashlib
from datetime import datetime,timezone,timedelta
R=pathlib.Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('q15',R/'cribado_llm.py')
c=importlib.util.module_from_spec(sp); sp.loader.exec_module(c)
urllib.request.urlopen=lambda *a,**k: (_ for _ in ()).throw(AssertionError('NETWORK FORBIDDEN'))
results={}
def call(fn,**args):
    if fn is c.cmd_etiquetar: args.setdefault('hasta',None)
    try:
        with contextlib.redirect_stdout(io.StringIO()): fn(types.SimpleNamespace(**args))
        return 'OK'
    except BaseException as e: return type(e).__name__+': '+str(e)
def write(p,x): p.write_text(json.dumps(x)+'\n',encoding='utf-8')
def jsonl(p,rows): p.write_text(''.join(json.dumps(x)+'\n' for x in rows),encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8'))
with tempfile.TemporaryDirectory(prefix='q15_codex_reaudit_') as td:
    d=pathlib.Path(td)
    refs=[{'obra_id':('S' if m=='seleccion' else 'X'),'ref':('CONTEXTO' if m=='seleccion' else 'EXCLUIR_FUERA_TEMA'),'mitad':m} for m in ['seleccion','validacion']]
    jsonl(d/'referencia.jsonl',refs)
    for m in ['seleccion','validacion']:
        jsonl(d/f'entrada_{m}.jsonl',[{'obra_id':('S' if m=='seleccion' else 'X'),'titulo':'Synthetic record','resumenes':['Invented abstract.']}])
    hashes={p.name:c.sha(p.read_bytes()) for p in d.glob('*.jsonl')}
    write(d/'particion.json',{'sha256':hashes}); c.PARTICION=d/'particion.json'
    start=datetime.now(timezone.utc)-timedelta(hours=1)
    write(d/'presupuesto.json',{'inicio_utc':start.strftime('%Y-%m-%dT%H:%M:%SZ'),'limite_utc':(start+timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'),'horas':24})
    results['G1']={'length':len(c.prompt_sistema()[0]),'sha':c.prompt_sistema()[1]}
    results['G2_missing_puntos']=c.interpretar('{"decision":"CONTEXTO","razon":"x","dudoso":false}')
    results['M3']=c.mediana([1,100])
    results['M2_underscore_counts']=c.tiene_texto('___')
    # Generate files ONLY through simulation. No actual Ollama.
    for m in ['seleccion','validacion']:
        for cfg in ['C1','C2']:
            assert call(c.cmd_etiquetar,datos=d,entrada=d/f'entrada_{m}.jsonl',config=cfg,host='disabled',simular=True)=='OK'
    assert call(c.cmd_probar,datos=d,host='disabled',simular=True)=='OK'
    pj=read(d/'probar.json'); pj['validas']=['C1','C2']; write(d/'probar.json',pj)
    results['simulation_official_rejected']=call(c.cmd_elegir,datos=d,prueba=False)
    results['simulation_test_election']=call(c.cmd_elegir,datos=d,prueba=True)
    # Artificial metadata fixtures for validator-only checks, not genuine runs.
    pj['simulado']=False; write(d/'probar.json',pj)
    for p in d.glob('salida_*.jsonl'):
        row=read(p); row.update(simulado=False,segundos=1); write(p,row)
    results['synthetic_fixture_election']=call(c.cmd_elegir,datos=d,prueba=False)
    results['synthetic_fixture_validation']=call(c.cmd_validar,datos=d,prueba=False)
    # Unknown uniform script hash accepted; conflicting model and raw response also accepted.
    vp=d/'salida_validacion_C1.jsonl'; original=vp.read_bytes()
    row=read(vp); row['script_sha256']='0'*64; write(vp,row)
    call(c.cmd_validar,datos=d,prueba=False)
    results['G3_unknown_uniform_script']=read(d/'veredicto.json')['veredicto']
    row=json.loads(original); row['modelo_respuesta']='wrong-model'; row['crudo']='not JSON'; write(vp,row)
    call(c.cmd_validar,datos=d,prueba=False)
    results['G3_invalid_raw_and_model']=read(d/'veredicto.json')['veredicto']
    vp.write_bytes(original)
    # JSON control file damage must not leave APTO current.
    call(c.cmd_validar,datos=d,prueba=False)
    ep=d/'eleccion.json'; ebytes=ep.read_bytes(); ep.write_text('{',encoding='utf-8')
    results['G4_malformed_choice_exception']=call(c.cmd_validar,datos=d,prueba=False)
    results['G4_stale_verdict']=read(d/'veredicto.json')['veredicto']
    ep.write_bytes(ebytes)
    # Missing file fixed.
    vp.rename(d/'saved-output')
    call(c.cmd_validar,datos=d,prueba=False)
    results['G4_missing_output']=read(d/'veredicto.json')['veredicto']
    (d/'saved-output').rename(vp)
    # Two outcomes in same second overwrite history.
    real_now=c.ahora; c.ahora=lambda:'2026-11-06T12:00:00Z'
    call(c.cmd_validar,datos=d,prueba=False)
    vp.rename(d/'saved-output'); call(c.cmd_validar,datos=d,prueba=False)
    history=list(d.glob('veredicto_20261106T120000Z_*.json'))
    results['G4_history_collision']={'files':len(history),'retained':[read(p)['veredicto'] for p in history]}
    (d/'saved-output').rename(vp); c.ahora=real_now
    # Time upper bound, reference hash.
    budget=read(d/'presupuesto.json'); bad=dict(budget,limite_utc='2000-01-01T00:00:00Z'); write(d/'presupuesto.json',bad)
    call(c.cmd_validar,datos=d,prueba=False); results['G6_late_row']=read(d/'veredicto.json')['veredicto']
    write(d/'presupuesto.json',budget)
    rf=d/'referencia.jsonl'; rb=rf.read_bytes(); rf.write_bytes(rb+b' ')
    call(c.cmd_validar,datos=d,prueba=False); results['M5_reference']=read(d/'veredicto.json')['veredicto']; rf.write_bytes(rb)
    # Frozen tie rule should not depend on incidental array order.
    pj['validas']=['C2','C1']; write(d/'probar.json',pj)
    call(c.cmd_elegir,datos=d,prueba=False)
    results['tie_reversed_validas']=read(ep)['elegida']
    # Numeric/boolean confusion in signatures.
    row=json.loads(original); row.update(think=0,simulado=0); write(vp,row)
    write(ep,{'veredicto':'ELEGIDA','prueba':False,'elegida':'C1'})
    call(c.cmd_validar,datos=d,prueba=False)
    results['signature_numeric_bool']=read(d/'veredicto.json')['veredicto']
    # Eviction in middle of UTF-8 char, not only ASCII.
    vp.write_bytes(b'{"razon":"\xc3')
    results['resume_partial_utf8']=call(c.cmd_etiquetar,datos=d,entrada=d/'entrada_validacion.jsonl',config='C1',host='disabled',simular=True)
    # Protect all context in the actual 75-work shape.
    ref={str(i):('INCLUIR_PARA_TEXTO' if i<24 else 'CONTEXTO' if i<27 else 'EXCLUIR_FUERA_TEMA') for i in range(75)}
    sal={o:{'decision':('EXCLUIR_FUERA_TEMA' if v=='CONTEXTO' else v),'segundos':1} for o,v in ref.items()}
    results['D1']=c.metricas(ref,(sal,[]))
    # Independent edges of the new validator.
    vp.write_bytes(original)
    row=json.loads(original)
    row['utc']='2026-00-00T99:99:99Z'
    write(vp,row); call(c.cmd_validar,datos=d,prueba=False)
    results['impossible_calendar_date']=read(d/'veredicto.json')['veredicto']
    row=json.loads(original); row['segundos']=-1; write(vp,row)
    call(c.cmd_validar,datos=d,prueba=False)
    results['negative_seconds']=read(d/'veredicto.json')['veredicto']
    row['segundos']=float('nan'); write(vp,row)
    call(c.cmd_validar,datos=d,prueba=False)
    results['nan_seconds']=read(d/'veredicto.json')['veredicto']
    vp.write_bytes(original)
    write(d/'presupuesto.json',dict(budget,limite_utc=None))
    call(c.cmd_validar,datos=d,prueba=False)
    results['null_deadline']=read(d/'veredicto.json')['veredicto']
    write(d/'presupuesto.json',budget)
    vp.write_bytes(b'{garbage}\n'+original)
    call(c.cmd_validar,datos=d,prueba=False)
    results['malformed_interior_line']=read(d/'veredicto.json')['veredicto']
    vp.write_bytes(original+original)
    call(c.cmd_validar,datos=d,prueba=False)
    results['duplicate_row']=read(d/'veredicto.json')['veredicto']
    vp.write_bytes(original)
    # --hasta actually checked before any simulated call.
    vp.unlink()
    results['hasta_expired']=call(c.cmd_etiquetar,datos=d,entrada=d/'entrada_validacion.jsonl',config='C1',host='disabled',simular=True,hasta='2000-01-01T00:00:00Z')
    results['hasta_expired_bytes']=vp.stat().st_size
    results['hasta_malformed']=call(c.cmd_etiquetar,datos=d,entrada=d/'entrada_validacion.jsonl',config='C1',host='disabled',simular=True,hasta='not-a-date')
    results['hasta_malformed_rows']=len(c.lineas_json(vp)[0])
    # A partially written UTF8 row is redone, complete prior row is retained.
    partial=d/'partial.jsonl'; partial.write_bytes(b'{"razon":"\xc3')
    results['lineas_partial_utf8']=c.lineas_json(partial)
    # Exclusive history and atomic current: inspect result and orphan temp files.
    current=d/'atomic.json'; write(current,{'old':True})
    c.escribir(current,{'new':True})
    results['atomic_written']={'value':read(current),'temps':len(list(d.glob('.atomic.json.*.tmp')))}
    # Invalid timing can change the final tie-break in selection.
    for cfg, seconds in [('C1',1),('C2',2)]:
        p=d/f'salida_seleccion_{cfg}.jsonl'; rr=read(p); rr['segundos']=seconds; write(p,rr)
    call(c.cmd_elegir,datos=d,prueba=False)
    results['timing_choice_before']=read(d/'eleccion.json')['elegida']
    p=d/'salida_seleccion_C2.jsonl'; rr=read(p); rr['segundos']=-1; write(p,rr)
    call(c.cmd_elegir,datos=d,prueba=False)
    results['timing_choice_after_negative']=read(d/'eleccion.json')['elegida']
    write(d/'eleccion.json',{'veredicto':'ELEGIDA','prueba':False,'elegida':'C1'})
    vp.write_bytes(b'{garbage}\n')
    call(c.cmd_validar,datos=d,prueba=False)
    results['discard_with_missing_work']=read(d/'veredicto.json')
    results['discard_details_reader']=c.lineas_json(vp)[1]
(R/'resultados_independientes.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(results,indent=2,ensure_ascii=True))
