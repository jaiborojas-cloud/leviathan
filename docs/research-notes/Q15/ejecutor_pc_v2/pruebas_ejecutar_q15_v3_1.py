#!/usr/bin/env python3
"""Pruebas solo con metadatos sintéticos y transporte sin internet."""
from __future__ import annotations

import argparse
import copy
import gzip
import importlib.util
import io
import json
import math
import socket
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("q15_executor_audit", HERE / "ejecutar_q15_v3.py")
Q = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = Q
SPEC.loader.exec_module(Q)


class FakeClock:
    def __init__(self):
        self.now, self.sleeps = 0.0, []
    def monotonic(self):
        return self.now
    def sleep(self, seconds):
        if seconds < 0:
            raise AssertionError("Pausa negativa")
        self.sleeps.append(seconds)
        self.now += seconds


def rec(i, title=None, year=2025, abstract="Texto sintético sin palabras clave"):
    return {"id": str(i), "paperId": str(i), "title": title or f"Documento sintético {i}",
            "year": year, "abstract": abstract, "authors": ["Autor Sintético"]}


def atom(total, records):
    from xml.sax.saxutils import escape
    entries = "".join(f'<entry><id>https://arxiv.org/abs/0000.{i:05d}</id><title>{escape(r["title"])}</title><summary>Resumen sintético</summary><author><name>Autor Sintético</name></author><published>2025-01-01T00:00:00Z</published></entry>' for i,r in enumerate(records))
    return f'<feed xmlns="http://www.w3.org/2005/Atom" xmlns:o="http://a9.com/-/spec/opensearch/1.1/"><o:totalResults>{total}</o:totalResults>{entries}</feed>'.encode()


def paged(n, total=True, error_offset=None):
    calls = []
    def fetch(offset, size):
        calls.append((offset,size))
        if offset == error_offset:
            raise Q.AccessError("fallo sintético en página")
        end = offset + size >= n
        return Q.Page([rec(i) for i in range(offset,min(n,offset+size))], n if total else None,
                      None if end else offset+size,end,f"fixture-page-{offset}")
    return fetch,calls


class Offline(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)
        self.store = Q.Store(self.path / "salida")
        self.clock = FakeClock()
    def tearDown(self):
        self.temp.cleanup()
    def client(self, mapping, **kwargs):
        transport = Q.FixtureTransport(mapping)
        client = Q.Http(self.store,transport,self.clock,**kwargs)
        return client,transport
    def inputs(self):
        return Q.load_inputs(Q.Q15_DEFAULT)


class InputsAndURLs(Offline):
    def test_inputs_reales_son_solo_documentos_congelados(self):
        inputs=self.inputs()
        self.assertEqual((55,294,19),(len(inputs['queries']),len(inputs['plan']),len(inputs['seeds'])))

    def test_input_alterado_no_se_acepta(self):
        copied=self.path/'inputs'
        for name in Q.EXPECTED:
            file=copied/name;file.parent.mkdir(parents=True,exist_ok=True)
            file.write_bytes((Q.Q15_DEFAULT/name).read_bytes())
        with (copied/'consultas_v2.csv').open('ab') as f:f.write(b'\n')
        with self.assertRaises(Q.IntegrityError):Q.load_inputs(copied)

    def test_urls_arxiv_conservan_consulta_y_orden(self):
        query='(ti:"Fisher" OR abs:"Fisher") AND submittedDate:[190001010000 TO 202611022359]'
        params=parse_qs(urlparse(Q.arxiv_url(query,200,1)).query)
        self.assertEqual(params['search_query'],[query])
        self.assertEqual(params['sortBy'],['relevance'])
        self.assertEqual(params['sortOrder'],['descending'])
        self.assertEqual(params['max_results'],['1'])

    def test_url_s2_bulk_no_quita_booleanos(self):
        params=parse_qs(urlparse(Q.s2_bulk_url('"Fisher" + ("early" | "confidence")',1900)).query)
        self.assertIn('+',params['query'][0])
        self.assertEqual(params['year'],['1900-2026'])

    def test_google_scholar_omitida_55(self):
        plan=Q.prepare_urls(self.inputs())
        gs=[r for r in plan if r['base']=='GoogleScholar']
        self.assertEqual(len(gs),55)
        self.assertTrue(all(r['estado']=='OMITIDA_OPCIONAL' and not r['url_primera_pagina'] for r in gs))

    def test_s2_bulk_sin_relevancia_ni_bloqueo_obsoleto(self):
        inputs=self.inputs();row=next(r for r in inputs['plan'] if r['base']=='SemanticScholar')
        url=Q.s2_bulk_url(row['cadena_exacta'],int(row['fecha_desde'][:4]))
        http,transport=self.client({url:{'body':{'total':0,'data':[]}}})
        result=Q.Runner(inputs,self.store,http).native(row)
        self.assertEqual(result['estado'],'COMPLETA')
        self.assertEqual(transport.calls,[url])
        self.assertEqual(result['tipo_total'],'ESTIMADO_PROVEEDOR')


class StorageAndHTTP(Offline):
    def test_escritura_exclusiva_preserva_marcador(self):
        path=self.path/'marca'
        Q.exclusive_write(path,b'marcador')
        with self.assertRaises(FileExistsError):Q.exclusive_write(path,b'nuevo')
        self.assertEqual(path.read_bytes(),b'marcador')

    def test_bloqueo_evitar_dos_productores(self):
        with Q.output_lock(self.path/'lock'):
            with self.assertRaises(Q.Q15Error):
                with Q.output_lock(self.path/'lock'):pass

    def test_respuesta_cache_no_hace_solicitud_ni_sobrescribe(self):
        http,transport=self.client({'https://example.test/page':{'body':{'data':[]}}})
        first=http.get('https://example.test/page')
        before={str(p):p.read_bytes() for p in self.store.root.rglob('*') if p.is_file()}
        second=http.get('https://example.test/page')
        self.assertEqual(first,second)
        self.assertEqual(len(transport.calls),1)
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.store.root.rglob('*') if p.is_file()})

    def test_sha_crudo_alterado_aborta(self):
        http,_=self.client({'https://example.test/page':{'body':'real-sintético'}})
        _,meta,_=http.get('https://example.test/page')
        (self.store.root/meta['body_file']).write_bytes(b'alterado')
        with self.assertRaises(Q.IntegrityError):http.get('https://example.test/page')

    def test_huerfano_de_cuerpo_reserva_indice(self):
        url='https://example.test/p'
        directory='raw/'+Q.digest(url.encode())
        Q.exclusive_write(self.store.root/directory/'attempt_000001.body',b'parcial de corte')
        http,_=self.client({url:{'body':'completa'}})
        _,meta,_=http.get(url)
        self.assertTrue(meta['body_file'].endswith('000002.body'))
        self.assertEqual((self.store.root/directory/'attempt_000001.body').read_bytes(),b'parcial de corte')

    def test_429_retry_after_y_cuerpos_preservados(self):
        url='https://api.semanticscholar.org/graph/v1/paper/sintetico'
        http,transport=self.client({url:[{'status':429,'headers':{'Retry-After':'7'},'body':'limite'}, {'body':{'ok':True}}]})
        _,meta,_=http.get(url)
        self.assertEqual(meta['status'],200)
        self.assertEqual(len(transport.calls),2)
        self.assertGreaterEqual(self.clock.now,7)
        statuses=[json.loads(p.read_text())['status'] for p in sorted(self.store.root.glob('raw/*/*.json'))]
        self.assertEqual(statuses,[429,200])

    def test_pausa_semantic_minimo_un_segundo(self):
        urls=['https://api.semanticscholar.org/a','https://api.semanticscholar.org/b']
        http,_=self.client({u:{'body':'ok'} for u in urls},s2_pause=1)
        for u in urls:http.get(u)
        self.assertGreaterEqual(self.clock.now,1)
        with self.assertRaises(ValueError):Q.Http(self.store,s2_pause=.99)

    def test_pausa_arxiv_tres_segundos(self):
        urls=['https://export.arxiv.org/a','https://export.arxiv.org/b']
        http,_=self.client({u:{'body':'ok'} for u in urls})
        for u in urls:http.get(u)
        self.assertGreaterEqual(self.clock.now,3)

    def test_429_agotado_no_se_vuelve_cero_resultados(self):
        url='https://example.test/rate'
        http,transport=self.client({url:[{'status':429,'body':'uno'},{'status':429,'body':'dos'}]},retries=1)
        with self.assertRaises(Q.AccessError):http.get(url)
        self.assertEqual(len(transport.calls),2)
        self.assertEqual(len(list(self.store.root.glob('raw/*/*.json'))),2)

    def test_403_sin_reintento_y_reanudacion_explicita(self):
        url='https://example.test/forbidden'
        http,transport=self.client({url:[{'status':403,'body':'prohibido'},{'body':'ahora si'}]})
        with self.assertRaises(Q.AccessError):http.get(url)
        with self.assertRaises(Q.AccessError):http.get(url)
        self.assertEqual(len(transport.calls),1)
        http.retry_failed=True
        self.assertEqual(http.get(url)[0],b'ahora si')
        self.assertEqual(len(list(self.store.root.glob('raw/*/*.body'))),2)

    def test_fixture_ausente_nunca_recurre_a_red(self):
        http,transport=self.client({},retries=0)
        with self.assertRaises(Q.AccessError):http.get('https://example.test/faltante')
        self.assertEqual(transport.calls,['https://example.test/faltante'])

    def test_cabeceras_no_guardan_api_key(self):
        url='https://api.semanticscholar.org/p'
        http,_=self.client({url:{'body':'ok','headers':{'Set-Cookie':'NO-GUARDAR'}}})
        with patch.dict(Q.os.environ,{'S2_API_KEY':'SECRETO_SINTETICO'}):
            http.get(url)
        dump=''.join(p.read_text() for p in self.store.root.glob('raw/*/*.json'))
        self.assertNotIn('SECRETO_SINTETICO',dump)
        self.assertNotIn('NO-GUARDAR',dump)

    def test_identidad_impide_mezclar_simulado_y_real(self):
        Q.bind_identity(self.store,self.inputs(),'SIMULADO','hash-fixture')
        with self.assertRaises(Q.IntegrityError):Q.bind_identity(self.store,self.inputs(),'RED',None)

    def test_resultado_terminado_no_repite_trabajo(self):
        result=self.store.job('job',lambda:{'estado':'COMPLETA','n':3})
        self.assertEqual(self.store.job('job',lambda:self.fail('se reejecutó'),True),result)

    def test_resultado_fallido_se_conserva_al_corregir(self):
        self.store.job('job',lambda:{'estado':'PARCIAL','error':'fallo'})
        self.store.job('job',lambda:{'estado':'COMPLETA'},True)
        files=sorted((self.store.root/'jobs/job').glob('result_*.json'))
        self.assertEqual(len(files),2)
        self.assertEqual(json.loads(files[0].read_text())['result']['error'],'fallo')

    def test_resultado_tamper_se_detecta(self):
        self.store.job('job',lambda:{'estado':'COMPLETA','n':1})
        path=next((self.store.root/'jobs/job').glob('*.json'))
        data=json.loads(path.read_text());data['result']['n']=999;path.write_text(json.dumps(data))
        with self.assertRaises(Q.IntegrityError):self.store.job('job',lambda:{'estado':'COMPLETA'})

    def test_json_nan_infinity_y_overflow_rechazados(self):
        for body in [b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1e999}']:
            with self.subTest(body=body),self.assertRaises(Q.SchemaError):Q.strict_json(body)


class PaginationAndParsers(Offline):
    def test_exactamente_500_se_conservan_todos(self):
        fetch,calls=paged(500);r=Q.collect_pages(fetch)
        self.assertEqual((r['estado'],r['n_seleccionados']),('COMPLETA',500))
        self.assertEqual(len(calls),5)

    def test_501_declara_tope_200_sin_recuperar_501(self):
        fetch,calls=paged(501);r=Q.collect_pages(fetch)
        self.assertEqual((r['estado'],r['n_recuperados'],r['n_seleccionados']),('TRUNCADA_DECLARADA',200,200))
        self.assertEqual(len(calls),2)

    def test_sondeo_desconocido_hasta_501_no_600(self):
        fetch,calls=paged(900,total=False);r=Q.collect_pages(fetch)
        self.assertEqual((r['n_recuperados'],r['n_seleccionados']),(501,200))
        self.assertEqual(calls[-1],(500,1))
        self.assertIsNone(r['total_declarado'])

    def test_desconocido_con_fin_real_menor_de_500(self):
        fetch,_=paged(350,total=False);r=Q.collect_pages(fetch)
        self.assertEqual((r['estado'],r['n_seleccionados']),('COMPLETA',350))

    def test_fallo_de_segunda_pagina_conserva_primera(self):
        fetch,_=paged(400,error_offset=100);r=Q.collect_pages(fetch)
        self.assertEqual(r['estado'],'PARCIAL')
        self.assertEqual(r['n_recuperados'],100)

    def test_total_cambiante_no_declara_completa(self):
        def fetch(offset,size):return Q.Page([rec(i) for i in range(offset,offset+size)],600+offset,offset+size,False)
        r=Q.collect_pages(fetch)
        self.assertEqual(r['estado'],'PARCIAL')
        self.assertIn('TOTAL_CAMBIO_ENTRE_PAGINAS',r['issues'])

    def test_fin_prematuro_no_es_catalogo_completo(self):
        r=Q.collect_pages(lambda o,s:Q.Page([],None,None,True),known_total=700,forced_cap=200)
        self.assertEqual(r['estado'],'PARCIAL')
        self.assertIn('FIN_ANTES_DEL_TOTAL_DECLARADO',r['issues'])

    def test_pagina_repetida_y_sin_avance(self):
        r=Q.collect_pages(lambda o,s:Q.Page([rec(0)],None,o+1,False))
        self.assertEqual(r['estado'],'PARCIAL')
        self.assertTrue(any('REPETIDA' in x for x in r['issues']))
        r=Q.collect_pages(lambda o,s:Q.Page([rec(0)],None,0,False))
        self.assertIn('PAGINACION_SIN_AVANCE',r['issues'])

    def test_duplicados_consumen_posiciones(self):
        def fetch(offset,size):
            rows=[rec(i) for i in range(offset,offset+size)]
            if offset==0:rows[1]=copy.deepcopy(rows[0])
            return Q.Page(rows,1000,offset+size,False)
        r=Q.collect_pages(fetch)
        self.assertEqual(r['n_seleccionados'],200)
        self.assertEqual(len({i['record']['id'] for i in r['records']}),199)

    def test_arxiv_atom_y_cero_legitimo(self):
        page=Q.parse_arxiv(atom(1,[rec(0)]),0,100)
        self.assertEqual(page.total,1)
        self.assertEqual(len(page.records),1)
        self.assertTrue(Q.parse_arxiv(atom(0,[]),0,100).end)

    def test_html_login_no_pasa_como_atom_vacio(self):
        for body in [b'<html><body>Login</body></html>',b'<feed xmlns="http://www.w3.org/2005/Atom"></feed>']:
            with self.subTest(body=body),self.assertRaises(Q.SchemaError):Q.parse_arxiv(body,0,100)

    def test_s2_esquema_y_vecino_nulo_conserva_posicion(self):
        page=Q.parse_s2({'data':[{'citingPaper':None}],'next':1},'citingPaper')
        self.assertEqual(len(page.records),1)
        self.assertTrue(page.records[0]['missing'])
        with self.assertRaises(Q.SchemaError):Q.parse_s2({'error':'API error'})
        with self.assertRaises(Q.SchemaError):Q.parse_s2({'data':[],'total':True})


class FiltersAndCatalogues(Offline):
    def test_din_limites_de_palabra_guiones_unicode_y_campos(self):
        terms=['early','Fisher','max margin','confidence']
        cases=[({'title':'nearly finished','abstract':'nada'},'FUERA_FILTRO_DIN'),
               ({'title':'Ｆｉｓｈｅｒ–Rao','abstract':None},'COINCIDE_DIN'),
               ({'title':'max—margin','abstract':None},'COINCIDE_DIN'),
               ({'title':'otro','abstract':None},'PENDIENTE_FILTRO'),
               ({'title':'otro','abstract':'confidence'},'COINCIDE_DIN')]
        for record,wanted in cases:self.assertEqual(Q.din_status(record,terms),wanted)

    def test_fechas_parciales_no_inventan_dia(self):
        cases=[({'year':2026},'PENDIENTE_FECHA'),({'year':2025},'INCLUIBLE'),
               ({'publicationDate':'2026-11-03'},'FUERA_FECHA'),({'publicationDate':'2026-11-02'},'INCLUIBLE'),
               ({'publicationDate':'2026-11'},'PENDIENTE_FECHA'),({'publicationDate':'2026-10'},'INCLUIBLE'),
               ({'publicationDate':'2025/7/6'},'INCLUIBLE'),({'year':True},'PENDIENTE_FECHA')]
        for r,wanted in cases:self.assertEqual(Q.record_date_status(r,'1900-01-01','2026-11-02'),wanted)

    def test_autor_es_postfiltro_y_no_rellena_cupo(self):
        r={'records':[{'selected':True,'record':{'year':2025,'authors':['Persona ajena']}},
                      {'selected':False,'record':{'year':2025,'authors':['Jastrzebski']}}]}
        Q.annotate_selected(r,{'fecha_desde':'1990-01-01','fecha_hasta':'2026-11-02','filtro_autor_metadatos':'Jastrzębski|Jastrzebski'})
        self.assertTrue(all(not row['incluible_para_cribado'] for row in r['records']))

    def test_booleano_literal_sin_stemming_y_sin_frase_entre_campos(self):
        self.assertEqual(Q.boolean_status({'title':'Fisher','abstract':'kernel'},[['Fisher kernel']]),'NO_COINCIDE')
        self.assertEqual(Q.boolean_status({'title':'Fisher kernel','abstract':None},[['Fisher'],['kernel']]),'COINCIDE')
        self.assertEqual(Q.boolean_status({'title':'otro','abstract':None},[['Fisher']]),'PENDIENTE_RESUMEN')

    def test_actas_orden_ano_desc_y_desempates_antes_tope(self):
        query={'grupos_json':'[["Fisher"]]','fecha_desde':'1900-01-01','fecha_hasta':'2026-11-02','filtro_autor_metadatos':''}
        rows=[rec(i,'Fisher '+str(1000-i),2024) for i in range(500)]+[rec('nuevo','Fisher A',2025)]
        result=Q.catalogue_result(rows,query,[])
        self.assertEqual(result['estado'],'TRUNCADA_DECLARADA')
        self.assertEqual(result['n_seleccionados'],200)
        self.assertEqual(result['records'][0]['record']['id'],'nuevo')
        ties=[rec('z','Fisher A'),rec('a','Fisher A')]
        result=Q.catalogue_result(ties,query,[])
        self.assertEqual([r['record']['id'] for r in result['records']],['a','z'])

    def test_resumen_ausente_no_es_cero_coincidencias_certificado(self):
        query={'grupos_json':'[["Fisher"]]','fecha_desde':'1900-01-01','fecha_hasta':'2026-11-02'}
        result=Q.catalogue_result([rec(0,'Otro título',abstract=None)],query,[])
        self.assertEqual(result['estado'],'PARCIAL_CATALOGO')
        self.assertIsNone(result['total_declarado'])
        self.assertEqual(len(result['pendientes_concordancia']),1)

    def test_parser_html_inline_y_abstract_heading(self):
        body=b'<h1>Logit<em>Norm</em></h1><h4>Abstract</h4><p>Fisher early text.</p>'
        record=Q.parse_article(body,'https://example.test/p',2025)
        self.assertEqual(record['title'],'LogitNorm')
        self.assertEqual(record['abstract'],'Fisher early text.')

    def test_pmlr_contexto_fuera_del_enlace_y_solo_icml(self):
        root='https://proceedings.mlr.press/'
        volume=root+'v70/'
        paper=root+'v70/sintetico.html'
        mapping={root:{'body':'<ul><li><a href="/v70/">Volume 70</a> Proceedings ICML 2017</li><li><a href="/v999/">Volume 999</a> Workshop ajeno 2025</li></ul>'},
                 volume:{'body':'<a href="sintetico.html">abs</a>'},
                 paper:{'body':'<meta name="citation_title" content="Fisher sintético"><div class="abstract">early confidence</div>'}}
        http,transport=self.client(mapping)
        result=Q.Runner(self.inputs(),self.store,http).html_catalogue('ICML')
        self.assertEqual(len(result['records']),1)
        self.assertNotIn(root+'v999/',transport.calls)
        self.assertIn('HISTORICO_ICML_ANTERIOR_A_PMLR_NO_RECUPERADO',result['issues'])

    def test_indice_vacio_es_error_no_catalogo_vacio(self):
        http,_=self.client({'https://proceedings.neurips.cc/':{'body':'<html>Loading</html>'}})
        with self.assertRaises(Q.SchemaError):Q.Runner(self.inputs(),self.store,http).html_catalogue('NeurIPS')

    def test_openreview_aceptados_v1_v2_y_no_workshops(self):
        for wrapped in [False,True]:
            def wrap(v):return {'value':v} if wrapped else v
            note={'id':'sintetico','content':{'venueid':wrap('ICLR.cc/2025/Conference'),'title':wrap('Fisher'),'abstract':wrap('early')}}
            self.assertIsNotNone(Q.parse_openreview_note(note,'ICLR.cc/2025/Conference',2025))
            note['content']['venueid']=wrap('ICLR.cc/2025/Workshop')
            self.assertIsNone(Q.parse_openreview_note(note,'ICLR.cc/2025/Conference',2025))

    def test_openreview_publication_date_y_borrado(self):
        note={'id':'x','pdate':1735689600000,'content':{'venueid':'ICLR.cc/2025/Conference','title':'X','abstract':'A'}}
        result=Q.parse_openreview_note(note,'ICLR.cc/2025/Conference',2025)
        self.assertEqual(result['publicationDate'],'2025-01-01')
        note['ddate']=1
        self.assertIsNone(Q.parse_openreview_note(note,'ICLR.cc/2025/Conference',2025))


class GraphAndCLI(Offline):
    def test_grafo_conteo_500_sin_filtro_y_501_con_filtro(self):
        inputs=self.inputs();seed=inputs['seeds'][0]
        for count in [500,501,None]:
            with self.subTest(count=count):
                store=Q.Store(self.path/str(count))
                mapping={}
                target=200 if count is None or count>500 else 500
                for offset in range(0,target,100):
                    items=[]
                    for i in range(offset,offset+100):
                        paper=rec(i,'early text' if i==0 else 'otro',abstract=None)
                        items.append({'citingPaper':paper})
                    data={'data':items}
                    if offset+100<target or target==200:data['next']=offset+100
                    mapping[Q.s2_graph_url('id','ADELANTE',offset,100)]={'body':data}
                transport=Q.FixtureTransport(mapping);http=Q.Http(store,transport,self.clock)
                runner=Q.Runner(inputs,store,http)
                result=runner.graph(seed,{'paper':{'paperId':'id','citationCount':count}},'ADELANTE')
                self.assertEqual(result['n_seleccionados'],target)
                heavy=count is None or count>500
                self.assertEqual(result['filtro_DIN_activado'],heavy)
                if heavy:
                    self.assertEqual(sum(x['incluible_para_cribado'] for x in result['records']),1)
                    self.assertEqual(result['records'][1]['filtro_DIN'],'PENDIENTE_FILTRO')
                    self.assertEqual(len(transport.calls),2)
                else:self.assertEqual(len(transport.calls),5)

    def test_resolver_s0_no_toma_titulo_cercano_distinto(self):
        inputs=self.inputs();seed=inputs['seeds'][0]
        ident='ARXIV:'+seed['arxiv_version_leida'].split('v')[0]
        http,_=self.client({Q.s2_paper_url(ident):{'body':{'paperId':'mal','title':'Otro artículo','authors':[{'name':'Toneva'}]}}})
        result=Q.Runner(inputs,self.store,http).resolve_seed(seed)
        self.assertNotEqual(result['estado'],'COMPLETA')

    def test_s0_snapshot_precede_toda_expansion_y_no_recursion(self):
        inputs=self.inputs();inputs['seeds']=inputs['seeds'][:1];seed=inputs['seeds'][0]
        metadata={'paperId':'s0','title':seed['titulo_verificado'],'authors':[{'name':'Mariya Toneva'}],'citationCount':0,'referenceCount':1}
        ident='ARXIV:'+seed['arxiv_version_leida'].split('v')[0]
        mapping={Q.s2_paper_url(ident):{'body':metadata},
                 Q.s2_graph_url('s0','ATRAS',0,100):{'body':{'data':[{'citedPaper':rec('vecino')}]}},
                 Q.s2_graph_url('s0','ADELANTE',0,100):{'body':{'data':[]}}}
        fixture=Q.FixtureTransport(mapping)
        def transport(url,headers,timeout):
            if '/citations?' in url or '/references?' in url:
                self.assertTrue(list((self.store.root/'S0').glob('resolved_*.json')))
            return fixture(url,headers,timeout)
        http=Q.Http(self.store,transport,self.clock)
        result=Q.Runner(inputs,self.store,http).citations()
        self.assertEqual(len(result),2)
        self.assertEqual(len(fixture.calls),3)
        self.assertFalse(any('vecino' in u for u in fixture.calls))

    def test_cli_preparar_python_aislado_sin_red(self):
        out=self.path/'cli'
        with contextlib_stdout():
            code=Q.main(['--out',str(out),'--fase','preparar'])
        self.assertEqual(code,0)
        result=json.loads(next((out/'runs').glob('*.json')).read_text())
        self.assertEqual(len(result['result']['plan']),294)
        self.assertFalse(list(out.glob('raw/*')))

    def test_cli_solo_s2_55_bulk_simuladas_y_reanudacion(self):
        out=self.path/'cli_s2';inputs=self.inputs()
        mapping={Q.s2_bulk_url(r['cadena_exacta'],int(r['fecha_desde'][:4])):{'body':{'total':0,'data':[]}}
                 for r in inputs['plan'] if r['base']=='SemanticScholar'}
        fixture=self.path/'bulk_fixture.json';fixture.write_text(json.dumps(mapping))
        args=['--out',str(out),'--fase','consultas','--bases','SemanticScholar','--fixtures',str(fixture)]
        with patch.object(Q,'Clock',FakeClock),contextlib_stdout():code=Q.main(args)
        self.assertEqual(code,2)
        result=json.loads(next((out/'runs').glob('*.json')).read_text())
        self.assertEqual(result['conteos']['COMPLETA'],55)
        self.assertNotIn('PENDIENTE_ENMIENDA_S2',result['conteos'])
        before={str(p):p.read_bytes() for p in out.glob('raw/*/*')}
        with patch.object(Q,'Clock',FakeClock),contextlib_stdout():self.assertEqual(Q.main(args),2)
        self.assertEqual(before,{str(p):p.read_bytes() for p in out.glob('raw/*/*')})


class AdditionalIntegration(Offline):
    def test_indice_con_un_solo_ano_no_se_declara_historia_completa(self):
        root='https://proceedings.neurips.cc/'
        volume=root+'paper_files/paper/2025'
        paper=root+'paper_files/paper/2025/hash/fixture-Abstract-Conference.html'
        mapping={root:{'body':'<li><a href="/paper_files/paper/2025">NeurIPS 2025 Main Conference</a></li>'},
                 volume:{'body':'<a href="/paper_files/paper/2025/hash/fixture-Abstract-Conference.html">Fisher</a>'},
                 paper:{'body':'<h1>Fisher</h1><h4>Abstract</h4><p>early</p>'}}
        http,_=self.client(mapping)
        with contextlib_stdout():result=Q.Runner(self.inputs(),self.store,http).html_catalogue('NeurIPS')
        self.assertEqual(result['estado'],'PARCIAL_CATALOGO')
        self.assertIn(1987,result['anios_no_listados'])
        self.assertIn(2026,result['anios_no_listados'])
        self.assertEqual(len(result['records']),1)

    def test_rama_publicacion_windows_no_reemplaza_destino_simulada(self):
        def windows_rename(source,target):
            # Simula la semántica exclusiva de os.rename en Windows, sin pretender ejecutarlo allí.
            Q.os.link(source,target)
            source.unlink()
        destination=self.path/'windows-marker'
        with patch.object(Q.os,'name','nt'),patch.object(Q.os,'rename',side_effect=windows_rename):
            Q.exclusive_write(destination,b'marcador')
            with self.assertRaises(FileExistsError):Q.exclusive_write(destination,b'no reemplazar')
        self.assertEqual(destination.read_bytes(),b'marcador')

    def test_catalogo_fecha_desconocida_no_declara_total_exacto(self):
        query={'grupos_json':'[["Fisher"]]','fecha_desde':'1900-01-01','fecha_hasta':'2026-11-02'}
        result=Q.catalogue_result([rec(0,'Fisher',2026)],query,[])
        self.assertEqual(result['estado'],'PARCIAL_CATALOGO')
        self.assertIsNone(result['total_declarado'])
        self.assertEqual(result['n_fecha_pendiente'],1)
        self.assertFalse(result['records'][0]['incluible_para_cribado'])
    def test_redireccion_s2_se_declara_sin_seguir_solicitud_oculta(self):
        handler=Q.SafeRedirect()
        req=Request('https://api.semanticscholar.org/p',headers={'x-api-key':'SECRETO_SINTETICO'})
        result=handler.redirect_request(req,None,302,'Found',{},'https://api.semanticscholar.org/nuevo')
        self.assertIsNone(result)
        self.assertEqual(len(handler.events),1)

    def test_redireccion_externa_no_envia_credenciales(self):
        handler=Q.SafeRedirect()
        req=Request('https://example.test/p',headers={'x-api-key':'SECRETO_SINTETICO','Authorization':'SECRETO','Cookie':'COOKIE'})
        result=handler.redirect_request(req,None,302,'Found',{},'https://other.test/p')
        keys={k.lower() for k,v in result.header_items()}
        self.assertFalse(keys & {'x-api-key','authorization','cookie'})

    def test_no_se_sigue_redireccion_a_http(self):
        handler=Q.SafeRedirect()
        self.assertIsNone(handler.redirect_request(Request('https://example.test/p'),None,302,'Found',{},'http://example.test/p'))

    def test_gzip_se_guarda_crudo_y_se_verifica_antes_de_decodificar(self):
        encoded=gzip.compress(b'{"synthetic":true}')
        http=Q.Http(self.store,lambda *a:(200,{'Content-Encoding':'gzip'},encoded),self.clock)
        decoded,meta,evidence=http.get('https://example.test/gzip')
        self.assertEqual(decoded,b'{"synthetic":true}')
        self.assertEqual(meta['sha256'],Q.digest(encoded))
        self.assertEqual((self.store.root/meta['body_file']).read_bytes(),encoded)

    def test_url_final_y_cadena_redirecciones_se_guardan(self):
        details={'url_final':'https://example.test/final','redirects':[{'status':301,'desde':'https://example.test/start','hacia':'https://example.test/final'}]}
        http=Q.Http(self.store,lambda *a:(200,{},b'ok',details),self.clock)
        _,meta,_=http.get('https://example.test/start')
        self.assertEqual(meta['url_final'],details['url_final'])
        self.assertEqual(len(meta['redirects']),1)

    def test_corte_guardando_metadata_deja_partial_sin_sobrescritura(self):
        url='https://example.test/corte';directory='raw/'+Q.digest(url.encode())
        Q.exclusive_write(self.store.root/directory/'attempt_000001.json.partial-fixture',b'{"corte":')
        http,_=self.client({url:{'body':'ok'}})
        _,meta,_=http.get(url)
        self.assertTrue(meta['body_file'].endswith('000002.body'))
        self.assertEqual((self.store.root/directory/'attempt_000001.json.partial-fixture').read_bytes(),b'{"corte":')

    def test_error_inesperado_se_archiva_como_fallo(self):
        def bad():raise TypeError('defecto sintético')
        result=self.store.job('defecto',bad)
        self.assertEqual(result['tipo_error'],'TypeError')
        self.assertIn('defecto sintético',result['traceback'])

    def test_tope_forzado_fuera_de_200_no_aceptado(self):
        for cap in [0,500,True,float('nan')]:
            with self.subTest(cap=cap),self.assertRaises(ValueError):
                Q.collect_pages(lambda o,s:Q.Page([],0,None,True),forced_cap=cap)

    def test_pausa_no_finita_error_cli_sin_archivos(self):
        for value in ['nan','0.5']:
            out=self.path/('bad_'+value)
            import contextlib
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(Q.main(['--out',str(out),'--pausa-s2',value]),1)
            self.assertFalse(out.exists())

    def test_resolucion_doi_y_title_match_solo_si_identidad_coincide(self):
        inputs=self.inputs();mapping={}
        seeds=[s for s in inputs['seeds'] if s['ancla_id'] in ['S18','S19']]
        for seed in seeds:
            if seed['ancla_id']=='S18':url=Q.s2_paper_url('DOI:'+seed['url_primaria'].split('doi.org/')[1])
            else:url='https://api.semanticscholar.org/graph/v1/paper/search/match?'+urlencode({'query':seed['titulo_verificado'],'fields':Q.S2_FIELDS})
            paper={'paperId':seed['ancla_id'],'title':seed['titulo_verificado'],'authors':[{'name':seed['autores_verificados'].split(';')[0]}],'citationCount':None,'referenceCount':None}
            mapping[url]={'body':paper if seed['ancla_id']=='S18' else {'data':[paper]}}
        http,_=self.client(mapping);runner=Q.Runner(inputs,self.store,http)
        self.assertTrue(all(runner.resolve_seed(s)['estado']=='COMPLETA' for s in seeds))

    def test_openreview_catalogo_pagina_v2_y_historicos_pendientes(self):
        mapping={}
        for year in range(2013,2027):
            api='https://api2.openreview.net' if year>=2024 else 'https://api.openreview.net'
            group=f'ICLR.cc/{year}/Conference'
            mapping[api+'/groups?'+urlencode({'id':group})]={'body':{'groups':[{'id':group}]} if year==2025 else {'groups':[]}}
            if year==2025:
                mapping[api+'/notes?'+urlencode({'content.venueid':group,'limit':1000,'offset':0})]={'body':{'count':1,'notes':[{'id':'fixture-note','pdate':1735689600000,'content':{'venueid':{'value':group},'title':{'value':'Fisher sintético'},'abstract':{'value':'early'}}}]}}
        http,_=self.client(mapping);runner=Q.Runner(self.inputs(),self.store,http)
        result=runner.openreview_catalogue()
        self.assertEqual(len(result['records']),1)
        self.assertEqual(result['years']['2025'],'COMPLETA')
        self.assertEqual(result['estado'],'PARCIAL_CATALOGO')
        self.assertEqual(len(result['issues']),13)

    def test_cli_consultas_arxiv_fixture_55_y_reanudacion(self):
        inputs=self.inputs();rows=[r for r in inputs['plan'] if r['base']=='arXiv']
        mapping={}
        for i,row in enumerate(rows):
            url=Q.arxiv_url(row['cadena_exacta'],0,100)
            mapping[url]={'body':atom(600 if i==0 else 0,[rec(j) for j in range(100)] if i==0 else []).decode()}
            if i==0:
                mapping[Q.arxiv_url(row['cadena_exacta'],100,100)]={'body':atom(600,[rec(j) for j in range(100,200)]).decode()}
        fixture=self.path/'transport.json';fixture.write_text(json.dumps(mapping))
        out=self.path/'end_to_end'
        args=['--out',str(out),'--fixtures',str(fixture),'--fase','consultas','--bases','arXiv']
        with patch.object(Q,'Clock',FakeClock),contextlib_stdout():code=Q.main(args)
        self.assertEqual(code,2)  # Fases/bases restantes no se hacen pasar por ejecutadas.
        raw_before={str(p):p.read_bytes() for p in out.glob('raw/*/*') if p.is_file()}
        with patch.object(Q,'Clock',FakeClock),contextlib_stdout():self.assertEqual(Q.main(args),2)
        self.assertEqual(raw_before,{str(p):p.read_bytes() for p in out.glob('raw/*/*') if p.is_file()})
        runs=sorted((out/'runs').glob('run_*.json'))
        self.assertEqual(len(runs),2)
        data=json.loads(runs[-1].read_text())
        self.assertEqual(data['modo'],'SIMULADO')
        self.assertEqual(data['conteos']['COMPLETA'],54)
        self.assertEqual(data['conteos']['TRUNCADA_DECLARADA'],1)
        table=out/'runs'/runs[-1].stem/'busquedas.csv'
        import csv
        with table.open(encoding='utf-8-sig') as f:self.assertEqual(len(list(csv.DictReader(f))),294)


class BulkV31(Offline):
    def bulk(self, pages):
        calls=[]
        def fetch(token):
            calls.append(token)
            value=pages[token]
            if isinstance(value,Exception):raise value
            rows,total,nxt=value
            return rows,total,nxt,'fixture-'+str(token)
        return Q.collect_s2_bulk(fetch),calls

    def rows(self,n,start=0):
        return [{**rec(i),'citationCount':100000-i} for i in range(start,start+n)]

    def test_55_urls_literales_y_orden_exacto(self):
        for r in self.inputs()['plan']:
            if r['base']!='SemanticScholar':continue
            url=Q.s2_bulk_url(r['cadena_exacta'],int(r['fecha_desde'][:4]))
            params=parse_qs(urlparse(url).query)
            self.assertTrue(urlparse(url).path.endswith('/paper/search/bulk'))
            self.assertEqual(params['query'],[r['cadena_exacta']])
            self.assertEqual(params['sort'],['citationCount:desc'])
            self.assertEqual(params['fields'],[Q.S2_FIELDS])
            self.assertEqual(params['year'],[r['fecha_desde'][:4]+'-2026'])
            self.assertFalse({'token','limit','offset'} & set(params))

    def test_token_opaco_con_signos_escapado_sin_perdida(self):
        token='a+/=&? hélice'
        params=parse_qs(urlparse(Q.s2_bulk_url('"a" + ("b" | "c")',1990,token)).query)
        self.assertEqual(params['token'],[token])
        self.assertEqual(params['sort'],['citationCount:desc'])
        for bad in ('',False,3):
            with self.assertRaises(Q.SchemaError):Q.s2_bulk_url('q',1990,bad)

    def test_0_200_500_501_1000(self):
        for n in (0,200,500,501,1000):
            with self.subTest(n=n):
                result,calls=self.bulk({None:(self.rows(n),n,'mas' if n==1000 else None)})
                self.assertEqual(calls,[None])
                self.assertEqual(result['n_recuperados'],n)
                self.assertEqual(result['n_seleccionados'],200 if n>500 else n)
                self.assertEqual(result['estado'],'TRUNCADA_DECLARADA' if n>500 else 'COMPLETA')
                self.assertEqual(len(result['records']),n)

    def test_menos_500_en_dos_paginas_recupera_todo(self):
        r,c=self.bulk({None:(self.rows(200),450,'siguiente'), 'siguiente':(self.rows(250,200),450,None)})
        self.assertEqual(c,[None,'siguiente']);self.assertEqual(r['estado'],'COMPLETA')
        self.assertEqual(r['n_seleccionados'],450)

    def test_mas_500_no_pide_token_al_llegar_a_200(self):
        r,c=self.bulk({None:(self.rows(100),600,'a'),'a':(self.rows(100,100),600,'b')})
        self.assertEqual(c,[None,'a']);self.assertEqual(r['estado'],'TRUNCADA_DECLARADA')
        self.assertEqual(r['token_siguiente_no_solicitado'],'b')

    def test_total_ausente_sondeo_501(self):
        r,c=self.bulk({None:(self.rows(500),None,'a'),'a':(self.rows(1,500),None,'b')})
        self.assertEqual(c,[None,'a']);self.assertIsNone(r['total_declarado'])
        self.assertEqual(r['estado'],'TRUNCADA_DECLARADA');self.assertEqual(r['n_seleccionados'],200)

    def test_total_ausente_agotado_menor_500(self):
        r,_=self.bulk({None:(self.rows(250),None,None)})
        self.assertEqual(r['estado'],'COMPLETA');self.assertEqual(r['n_seleccionados'],250)

    def test_estimaciones_inexactas_mismo_lado_no_son_conteos_exactos(self):
        r,_=self.bulk({None:(self.rows(400),450,None)})
        self.assertEqual(r['estado'],'COMPLETA');self.assertEqual(r['tipo_total'],'ESTIMADO_PROVEEDOR')

    def test_estimacion_cruza_umbral_no_declara_completitud(self):
        for observed,estimate in ((600,450),(400,600)):
            with self.subTest(observed=observed):
                r,_=self.bulk({None:(self.rows(observed),estimate,None)})
                self.assertEqual(r['estado'],'PARCIAL')
                self.assertIn('ESTIMACION_Y_OBSERVACION_CRUZAN_UMBRAL_BULK',r['issues'])
                self.assertEqual(r['n_seleccionados'],200)

    def test_estimacion_cambia_se_conserva_y_es_parcial(self):
        r,_=self.bulk({None:(self.rows(100),450,'a'),'a':(self.rows(100,100),451,None)})
        self.assertEqual(r['estado'],'PARCIAL');self.assertEqual(r['totales_observados'],[450,451])

    def test_token_repetido_y_vacio_con_token(self):
        cases=[{None:(self.rows(1),400,'a'),'a':(self.rows(1,1),400,'a')},
               {None:([],400,'a')}]
        for pages in cases:
            r,_=self.bulk(pages);self.assertEqual(r['estado'],'PARCIAL')

    def test_fallo_posterior_conserva_posiciones(self):
        r,_=self.bulk({None:(self.rows(100),450,'a'),'a':Q.AccessError('429 conservado')})
        self.assertEqual(r['estado'],'PARCIAL');self.assertEqual(r['n_recuperados'],100)

    def test_ids_repetidos_no_rellenan_cupos(self):
        rows=self.rows(1000);rows[199]=copy.deepcopy(rows[198])
        r,_=self.bulk({None:(rows,2000,'a')})
        self.assertEqual(r['estado'],'PARCIAL');self.assertEqual(r['n_seleccionados'],200)
        self.assertEqual(r['records'][199]['record']['paperId'],r['records'][198]['record']['paperId'])
        self.assertFalse(r['records'][200]['selected'])

    def test_orden_citas_ascendente_o_nulo_en_medio_es_parcial(self):
        for counts in ([2,3],[3,None,2]):
            rows=[{**rec(i),'citationCount':c} for i,c in enumerate(counts)]
            r,_=self.bulk({None:(rows,2,None)})
            self.assertEqual(r['estado'],'PARCIAL')

    def test_empates_y_nulos_al_final_conservan_orden_proveedor(self):
        rows=[{**rec(i),'citationCount':c} for i,c in zip(['a','b','c','d'],[3,3,None,None])]
        r,_=self.bulk({None:(rows,4,None)})
        self.assertEqual(r['estado'],'COMPLETA')
        self.assertEqual([x['record']['paperId'] for x in r['records']],['a','b','c','d'])

    def test_esquemas_invalidos_no_son_cero(self):
        cases=[{}, {'data':None},{'data':[None]}, {'data':[{'paperId':'x','citationCount':True}]},
               {'data':[],'total':True},{'data':[],'token':0},{'data':self.rows(1001)}]
        for data in cases:
            with self.subTest(data=str(data)[:80]),self.assertRaises(Q.SchemaError):Q.parse_s2_bulk(data)

    def test_postfiltros_no_reponen_201(self):
        r,_=self.bulk({None:(self.rows(1000),2000,'a')})
        r['records'][0]['record']['publicationDate']='2027-01-01'
        query={'fecha_desde':'1900-01-01','fecha_hasta':'2026-11-02','filtro_autor_metadatos':''}
        Q.annotate_selected(r,query)
        self.assertFalse(r['records'][0]['incluible_para_cribado'])
        self.assertEqual(sum(x['incluible_para_cribado'] for x in r['records']),199)
        self.assertFalse(r['records'][200]['incluible_para_cribado'])

    def test_reanudacion_pagina_fallida_sin_repetir_primera(self):
        inputs=self.inputs();row=next(r for r in inputs['plan'] if r['base']=='SemanticScholar')
        url=Q.s2_bulk_url(row['cadena_exacta'],int(row['fecha_desde'][:4]))
        next_url=Q.s2_bulk_url(row['cadena_exacta'],int(row['fecha_desde'][:4]),'a')
        http,transport=self.client({url:{'body':{'data':self.rows(100),'total':400,'token':'a'}},
            next_url:[{'status':429,'body':'bloqueada'},{'body':{'data':self.rows(100,100),'total':400}}]},retries=0)
        runner=Q.Runner(inputs,self.store,http)
        first=self.store.job('consulta',lambda:runner.native(row))
        self.assertEqual(first['estado'],'PARCIAL')
        http.retry_failed=True
        second=self.store.job('consulta',lambda:runner.native(row),True)
        self.assertEqual(second['estado'],'COMPLETA')
        self.assertEqual(transport.calls.count(url),1);self.assertEqual(transport.calls.count(next_url),2)


class CacheV2(Offline):
    def test_bulk_200_json_con_esquema_invalido_se_puede_recuperar(self):
        inputs=self.inputs();row=next(r for r in inputs['plan'] if r['base']=='SemanticScholar')
        url=Q.s2_bulk_url(row['cadena_exacta'],int(row['fecha_desde'][:4]))
        http,t=self.client({url:[{'body':{'data':None}},{'body':{'total':0,'data':[]}}]})
        runner=Q.Runner(inputs,self.store,http)
        self.assertEqual(self.store.job('q',lambda:runner.native(row))['estado'],'PARCIAL')
        http.retry_failed=True
        self.assertEqual(self.store.job('q',lambda:runner.native(row),True)['estado'],'COMPLETA')
        self.assertEqual(len(t.calls),2)

    def test_catalogo_y_consulta_verifican_dependencia_cruda_indirecta(self):
        root='https://proceedings.neurips.cc/';volume=root+'paper_files/paper/2025'
        paper=volume+'/hash/sintetico-Abstract-Conference.html'
        body='<meta name="citation_title" content="Fisher"><div id="abstract">early confidence</div>'
        http,t=self.client({root:{'body':'<a href="'+volume+'">2025</a>'},
                           volume:{'body':'<a href="'+paper+'">Fisher</a>'},paper:{'body':body}})
        inputs=self.inputs();inputs['plan']=[r for r in inputs['plan'] if r['base']=='NeurIPS'][:1]
        runner=Q.Runner(inputs,self.store,http)
        with contextlib_stdout():Q.execute(runner,'catalogos',{'NeurIPS'})
        # La consulta depende del catálogo; el catálogo, de volúmenes y artículos.
        key=Q.digest(paper.encode());next((self.store.root/'raw'/key).glob('*.body')).unlink()
        with contextlib_stdout(),self.assertRaises(Q.IntegrityError):Q.execute(runner,'catalogos',{'NeurIPS'})

    def test_200_no_json_se_recupera_exclusivo_con_reintento(self):
        url='https://example.test/bulk'
        http,t=self.client({url:[{'body':'<html>bloqueada</html>'},{'body':{'data':[]}}]})
        def work():
            data,ev=http.json(url);return {'estado':'COMPLETA','evidence':ev}
        first=self.store.job('q',work)
        old={str(p):p.read_bytes() for p in self.store.root.glob('raw/*/attempt_*')}
        self.assertEqual(first['estado'],'PENDIENTE_ACCESO_O_ESQUEMA')
        http.retry_failed=True
        self.assertEqual(self.store.job('q',work,True)['estado'],'COMPLETA')
        self.assertEqual(len(t.calls),2)
        self.assertTrue(all(Path(p).read_bytes()==b for p,b in old.items()))

    def test_200_atom_erroneo_reintento_conserva_primer_fallo(self):
        inputs=self.inputs();row=next(r for r in inputs['plan'] if r['base']=='arXiv')
        url=Q.arxiv_url(row['cadena_exacta'],0,100)
        http,t=self.client({url:[{'body':'<html>bloqueada</html>'},{'body':atom(0,[]).decode()}]})
        runner=Q.Runner(inputs,self.store,http)
        self.assertEqual(self.store.job('q',lambda:runner.native(row))['estado'],'PARCIAL')
        http.retry_failed=True
        self.assertEqual(self.store.job('q',lambda:runner.native(row),True)['estado'],'COMPLETA')
        self.assertEqual(len(t.calls),2)

    def test_terminal_reanudado_detecta_cuerpo_alterado_o_ausente(self):
        for remove in (False,True):
            with self.subTest(remove=remove):
                store=Q.Store(self.path/str(remove));url='https://example.test/q'
                http=Q.Http(store,Q.FixtureTransport({url:{'body':{'data':[]}}}),self.clock)
                def work():
                    _,ev=http.json(url);return {'estado':'COMPLETA','evidence':ev}
                store.job('q',work)
                body=next(store.root.glob('raw/*/*.body'))
                if remove:body.unlink()
                else:body.write_bytes(b'alterada')
                with self.assertRaises(Q.IntegrityError):store.job('q',work,True)

    def test_dependencia_indirecta_verificada(self):
        url='https://example.test/q';http,_=self.client({url:{'body':{'data':[]}}})
        def child():
            http.json(url);return {'estado':'COMPLETA'}
        self.store.job('parent',lambda:self.store.job('child',child))
        next(self.store.root.glob('raw/*/*.body')).write_bytes(b'alterada')
        with self.assertRaises(Q.IntegrityError):self.store.job('parent',lambda:self.fail('no reejecutar'))

    def test_rechazo_200_sin_flag_no_gasta_intento_nuevo(self):
        url='https://example.test/q';http,t=self.client({url:[{'body':'no json'},{'body':{}}]})
        with self.assertRaises(Q.SchemaError):http.json(url)
        with self.assertRaises(Q.SchemaError):http.json(url)
        self.assertEqual(len(t.calls),1)


def contextlib_stdout():
    import contextlib
    return contextlib.redirect_stdout(io.StringIO())


class RecordedResult(unittest.TextTestResult):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.rows=[]
    def addSuccess(self,test):
        super().addSuccess(test);self.rows.append({'caso':test.id(),'estado':'PASS'})
    def addFailure(self,test,err):
        super().addFailure(test,err);self.rows.append({'caso':test.id(),'estado':'FAIL','detalle':self._exc_info_to_string(err,test)})
    def addError(self,test,err):
        super().addError(test,err);self.rows.append({'caso':test.id(),'estado':'ERROR','detalle':self._exc_info_to_string(err,test)})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    stream=io.StringIO()
    # Guard global adicional: si cualquier código intenta internet, la prueba falla.
    with patch.object(socket,'create_connection',side_effect=AssertionError('RED_PROHIBIDA_EN_PRUEBAS')), \
         patch.object(Q,'build_opener',side_effect=AssertionError('RED_PROHIBIDA_EN_PRUEBAS')):
        result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=RecordedResult).run(suite)
    report={'tipo':'SOLO_RESPUESTAS_SIMULADAS','estado':'PASS' if result.wasSuccessful() else 'FAIL',
            'tests':result.testsRun,'casos':result.rows,'fallos':len(result.failures),'errores':len(result.errors),
            'script_sha256':Q.digest((HERE/'ejecutar_q15_v3.py').read_bytes()),
            'pruebas_sha256':Q.digest(Path(__file__).read_bytes()),'inputs_sha256':Q.EXPECTED,
            'sin_conexiones_de_red':True,**Q.stamp()}
    Q.exclusive_write(args.out,Q.json_bytes(report))
    Q.exclusive_write(args.out.with_suffix('.log'),stream.getvalue().encode())
    print(json.dumps({k:report[k] for k in ['tipo','estado','tests','fallos','errores']},ensure_ascii=False))
    if not result.wasSuccessful():print(stream.getvalue())
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
