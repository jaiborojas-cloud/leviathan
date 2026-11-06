import importlib.util, json, tempfile, pathlib, types, contextlib, io, zipfile
root=pathlib.Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('q15',root/'cribado_llm.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
# No network or model call is permitted by this harness.
m.urllib.request.urlopen=lambda *a,**k: (_ for _ in ()).throw(AssertionError('NETWORK DISABLED'))
out={}
out['prompt']=repr(m.prompt_sistema()[0])
out['prompt_length']=len(m.prompt_sistema()[0])
out['schema_cases']=[{'input':x,'accepted':m.interpretar(json.dumps(x)) is not None} for x in [
 {'decision':'CONTEXTO','razon':'Sintetica','dudoso':False},
 {'decision':'CONTEXTO','puntos':'INVALID','razon':'Sintetica','dudoso':False},
 {'decision':'CONTEXTO','puntos':['99'],'razon':'Sintetica','dudoso':False}]]
with tempfile.TemporaryDirectory(prefix='q15_audit_') as tmp:
 p=pathlib.Path(tmp)
 def write(n,obj): (p/n).write_text(json.dumps(obj)+'\n',encoding='utf-8')
 def quiet(fn,a):
  with contextlib.redirect_stdout(io.StringIO()): fn(types.SimpleNamespace(**a))
 write('entrada_validacion.jsonl',{'obra_id':'S1','titulo':'Synthetic study','resumenes':['Entirely invented abstract for software checks.']})
 quiet(m.cmd_probar,dict(datos=tmp,host='disabled',simular=True))
 quiet(m.cmd_etiquetar,dict(datos=tmp,entrada=str(p/'entrada_validacion.jsonl'),config='C1',host='disabled',simular=True))
 write('referencia.jsonl',{'obra_id':'S1','ref':'EXCLUIR_FUERA_TEMA','mitad':'validacion'})
 write('eleccion.json',{'elegida':'C1'})
 quiet(m.cmd_validar,dict(datos=tmp))
 out['simulation_can_be_APTO']=json.loads((p/'veredicto.json').read_text())['veredicto']
 s=json.loads((p/'salida_validacion_C1.jsonl').read_text()); s.update(config='C4',modelo='WRONG',prompt_sha256='WRONG',opciones={})
 write('salida_validacion_C1.jsonl',s)
 quiet(m.cmd_etiquetar,dict(datos=tmp,entrada=str(p/'entrada_validacion.jsonl'),config='C1',host='disabled',simular=True))
 quiet(m.cmd_validar,dict(datos=tmp))
 out['wrong_provenance_reused_and_APTO']=json.loads((p/'veredicto.json').read_text())['veredicto']
 # Interrupted JSON line is retained, separated and redone.
 (p/'salida_validacion_C1.jsonl').write_text('{"obra_id":',encoding='utf-8')
 quiet(m.cmd_etiquetar,dict(datos=tmp,entrada=str(p/'entrada_validacion.jsonl'),config='C1',host='disabled',simular=True))
 out['truncated_line_recovery']=list(m.leer_salida(p/'salida_validacion_C1.jsonl'))
 (p/'salida_validacion_C1.jsonl').unlink()
 try: quiet(m.cmd_validar,dict(datos=tmp))
 except SystemExit as e: out['missing_validation']=str(e)
 out['stale_verdict_after_missing']=json.loads((p/'veredicto.json').read_text())['veredicto']
 # Synthetic evidence only; no actual delivery packages.
 z=p/'synthetic.zip'
 data=[{'obra_id':'S1','record':{'title':'Synthetic','abstract':'A short abstract.'}}, {'obra_id':'S2','records':[{'title':'Synthetic','abstract':'A longer abstract nested without a repeated obra_id.'}]}]
 with zipfile.ZipFile(z,'w') as zz: zz.writestr('evidence.json',json.dumps(data))
 out['evidence_short_or_nested']=dict(m.resumenes_de_evidencia(z,'evidence.json'))
 ref={str(i):'INCLUIR_PARA_TEXTO' if i<24 else ('CONTEXTO' if i<27 else 'EXCLUIR_FUERA_TEMA') for i in range(75)}
 sal={o:{'decision':('EXCLUIR_FUERA_TEMA' if r=='CONTEXTO' else r),'segundos':1} for o,r in ref.items()}
 out['all_context_excluded']=m.metricas(ref,sal)
outpath=root/'resultados_sinteticos.json'
outpath.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(out,indent=2,ensure_ascii=True))
