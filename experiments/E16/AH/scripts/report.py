#!/usr/bin/env python3
"""Informe derivado sólo de archivos AH ya cerrados, sin medir curvas."""
from ah_common import *
from collections import Counter

def main():
 result=ROOT/'results/run_v1';summary=json.loads((result/'summary.json').read_text());groups=rows(result/'groups.csv');assert summary['valid']==80 and summary['status']=='VALID_EXPLORATORY';states=rows(result/'states.csv');cand=rows(result/'candidates.csv');opts=rows(result/'optimizers.csv');resources=json.loads((result/'resources.json').read_text())
 if (ROOT/'CONCLUSION.md').exists():raise FileExistsError('conservar informes')
 diag={'native_optimizers':len(opts),'optimizer_success':sum(x['success']=='True' for x in opts),'optimizer_messages':dict(Counter(x['message'] for x in opts)),'quad_candidates':len(cand),'MP_pass':sum(x['MP_status']=='PASS' for x in cand),'MP_inconclusive':sum(x['MP_status']=='INCONCLUSIVE' for x in cand),'max_selected_MP_error':max(float(s['numeric_relative_error']) for s in states if s['numeric_relative_error']),'max_fast_evaluations':max(int(s['evaluations']) for s in states),'selected_box_boundary':sum(max(abs(float(s['q1'])),abs(float(s['q2'])))>=12-1e-6 for s in states if s['status']=='PASS'),'arrays':len(rows(result/'arrays.csv')),'worker_blocked_T2_reads':sum(x['blocked_T2_reads'] for x in resources['worker_resources']),'seconds':resources['seconds']}
 diag['selected_box_boundary_by_group']={g:sum(max(abs(float(x['q1'])),abs(float(x['q2'])))>=12-1e-6 for x in states if x['group']==g and x['status']=='PASS') for g in ['triangle','AF']}
 write(result/'derived_diagnostics.json',diag)
 table_text='| Grupo | Estados válidos | Mediana cociente | Máximo cociente | Spearman | tρ0 mediano(s) | t1 total mediano(s) | Mediana t1/tρ0 |\n|---|---:|---:|---:|---:|---:|---:|---:|\n'
 for g in groups:
  table_text+=f"| {g['group']} | {g['valid']}/{g['states']} | {float(g['median_ratio']):.9f} | {float(g['max_ratio']):.9f} | {float(g['spearman']):.9f} | {float(g['median_rho0_seconds']):.6f} | {float(g['median_total_seconds']):.6f} | {float(g['median_cost_ratio']):.6f} |\n"
 t=groups[0];af=groups[1];verdict=' · '.join(f"Q{i} {summary['Q'+str(i)]}" for i in range(1,6))
 text=f'''# E16-AH · conclusión exploratoria v1

**{verdict}.** Corrida {summary['status']}; {summary['valid']}/80 estados con
curva testigo validada,13/13 controles previos PASS y
{summary['null_controls_pass']}/80 controles de quiebre nulo PASS. No se
sustituyeron estados ni se adaptó el presupuesto después de observar resultados.

## Resultado y comparación por grupo

Se estudiaron exactamente los 40 triángulos AG y 40 AF. En triangle el cociente
es hatρ1/d_borde y la correlación es Spearman(hatρ1,d_borde). En AF son
hatρ1/ρ0 y Spearman(hatρ1,ρ0); **d_borde AF sigue UNKNOWN**.

{table_text}
Las medianas de tiempos y la mediana de sus cocientes son estadísticas
separadas. Los tiempos incluyen la búsqueda basal contemporánea; no son
comparaciones con un tiempo histórico en otra máquina.

**Q1 {summary['Q1']}:** los 40 triángulos conservan hatρ1≥d_borde dentro del
error fijado. Cada valor seleccionado corresponde a un segmento y una
semirrecta al infinito, con soporte, extremo, parámetros, integral y resto de
cola archivados. También se conserva hatρ1≤ρ0 validada por inclusión del
camino Q=0, sin recortar resultados al valor verdadero.

**Q2 {summary['Q2']}:** la mediana baja de≈1.998884 en AG a
{float(t['median_ratio']):.9f}, y el máximo de≈4.266419 a
{float(t['max_ratio']):.9f}. Los umbrales congelados son mediana≤1.2 y máximo≤1.5.
Hay mejora respecto a la semirrecta desde0, pero la búsqueda ejecutada no
cumple ambos requisitos. Esto **no prueba** que el ínfimo matemático de todos
los caminos con un quiebre incumpla esos umbrales: no se certifica un mínimo
global ni se explora Q fuera de la caja fijada. No se añade retrospectivamente
la sensibilidad opcional de dos quiebres.

**Q3 {summary['Q3']}:** Spearman frente a la distancia exacta es
{float(t['spearman']):.9f}, frente a≈.939212 de AG; el umbral previo era≥.95.
Las cuatro escalas de cada semilla están emparejadas; no hay p-valores de40
réplicas independientes ni evidencia de transferencia.

**Q4 {summary['Q4']}:** el criterio descriptivo previo aceptaba un sobrecoste
mediano total de hasta10× la búsqueda de ρ0 en ambos grupos. Los factores
medidos son {float(t['median_cost_ratio']):.6f} en triángulos y
{float(af['median_cost_ratio']):.6f} en AF. El criterio evalúa ese presupuesto, **no que el método sea más rápido** que ρ0. El total
incluye optimización, quad, MP y archivo del perfil, además de la base; no es
un benchmark aislado repetido ni una predicción universal de coste.

**Q5 {summary['Q5']}, descriptivo AF:** cociente mediano
{float(af['median_ratio']):.9f}, máximo {float(af['max_ratio']):.9f};
Spearman frente a ρ0={float(af['spearman']):.9f}. Cambian de orden
{summary['AF_inversions']} de {summary['AF_pairs']} pares. Los estados sin
mejora conservan el basal. Esa asociación no mide orden frente a d_borde real.

## Qué curva se valida

El instrumento reporta **hatρ1**, mínimo de sus candidatos validados, no el
mínimo global ρ1. La familia tiene un quiebre, caja q=BQ∈[−12,12]²,
inicializaciones de rejilla y base, ramas de arista y sectores abiertos.
Se conserva el camino sin quiebre. Cada cola usa su offset fQ: su extremo en
una arista cambia con Q y no es el de una semirrecta desde0.

Las aristas se definen algebraicamente por los rasgos, no interpretando una
normal decimal casi empatada como un empate exacto. Véanse las
[convenciones de reconstrucción](WITNESS_CONVENTIONS.md). La integral llega
al borde infinito con una cota explícita del resto desde U, no al umbral150.
Las longitudes de los candidatos se validan con quad y las tres menores más
la base con MP80 (nodos/pesos MP, dos órdenes, integral completa y cola).

Se registraron {diag['native_optimizers']} optimizadores, de los cuales
{diag['optimizer_success']} declararon convergencia nativa. Los límites y
salidas no convergentes permanecen en optimizers.csv: una curva factible con
longitud validada no se convierte por eso en un punto estacionario. Hubo
{diag['MP_pass']} contrastes MP PASS y{diag['MP_inconclusive']} inconclusos;
el error relativo máximo de los testigos seleccionados fue
{diag['max_selected_MP_error']:.4g}. No hubo selección de estados ni sustitución
de candidatos inválidos por valores inventados.

En {diag["selected_box_boundary"]}/80 testigos el quiebre alcanza el límite de la caja
({diag["selected_box_boundary_by_group"]["triangle"]} triángulos y {diag["selected_box_boundary_by_group"]["AF"]} AF). No se deduce que ampliar
la caja o el presupuesto no pueda mejorar la cota.

## Controles, archivo y límites

13/13 controles previos PASS: triángulo trivial en baricentro, quiebre nulo
analítico y MP; origen afín; curvas de arista/genéricas en primeros
triángulo/AF con cambio de carta; velocidades frente a J original; K plano AD
y lectura de longitud continua AC archivada. No se reejecutaron AD/AC.
Los 80 basales nulos contrastan quad/MP y los valores cerrados de AG.

Tiempo de corrida {resources['seconds']:.6f}s, dos procesos y BLAS/OMP1.
{diag['arrays']} arrays originales fuera de Git con SHA; todas las longitudes,
candidatos, estados nativos y recursos se conservan. Los testigos MP y las
versiones originales no se sobrescriben. [Resultados](results/run_v1),
[recursos](results/run_v1/resources.json), [diagnósticos derivados](results/run_v1/derived_diagnostics.json).

Historia: diseño d62326a → código dad765e → mediciones. Se verificó el SHA
de geometry.py antes de importarlo, sin modificar su fuente; la guarda AF
permanece activa sin excepciones de acceso T2. No se leyó ningún dato T2 ni
se modificaron estados o resultados de otras etapas.

No se afirma certificado riguroso (quad/MP no son intervalos), mínimo global,
igualdadρ1=d_borde ni transferencia a T2. El ajuste que falta puede motivar
un protocolo nuevo de dos quiebres o búsqueda más amplia, declarado como
sensibilidad exploratoria o con estados independientes para confirmar. La corrida conserva sus reglas y resultados, incluidos los fallos de ajuste.
'''
 (ROOT/'CONCLUSION.md').write_text(text)
 print(json.dumps(diag,indent=2))
if __name__=='__main__':main()
