from pathlib import Path
import csv,json,hashlib
P=Path(__file__).resolve().parent
p=json.loads((P/'protocol.json').read_text())
def table(name,cols,where=lambda r:True):
 rows=[r for r in csv.DictReader((P/name).open()) if where(r)]
 return '| '+' | '.join(cols)+' |\n|'+'|'.join(['---']*len(cols))+'|\n'+'\n'.join('| '+' | '.join(r[c] for c in cols)+' |' for r in rows)
text='''# Leviathan / RIPG — T2-A0: prerregistro temporal y sensibilidad de potencia

**Estado: protocolo cerrado antes de abrir estados nuevos. T2-A NO iniciado.**

Una única hipótesis primaria: **Opción A, predicción temporal**. Fase: **pilot prospective validation** sobre Wine. El producto A0 es el diseño; no contiene evidencia confirmatoria nueva.

## 1. Antecedentes y enmienda prospectiva explícita

T1-A conserva 78 estados INJECTIVE_AT_NOMINAL_RADIUS y dos GEOMETRIC_NONINJECTIVITY, ambos split0/true (j1,j3). T1-B conserva80 estados y320 combinaciones estado/radio PASS. La correlación true admisible0.954918 frente a0.971769 nominal es EXPECTED_GEOMETRIC_CONTROL; los7/38 residuos y rangos1/2 de los positivos son exploratorios. Nunca cuentan como validación del ensayo nuevo. C1-A sigue INCONCLUSIVE.

El diseño anterior E15-T2 queda archivado íntegro con su hash. Su asociación entre r* y dominio nominal **en un mismo estado no era temporal**. Este A0 lo sustituye para la siguiente ejecución, antes de estados nuevos: cambia el objetivo a incidencia durante entrenamiento, la cohorte a800 trayectorias true, la programación temporal, la métrica primaria y las compuertas informativas. La cola10%, el radio exacto, Dexp y las definiciones geométricas se conservan. No se sobrescribe el antecedente ni se presenta como si hubiera prerregistrado temporalidad.

## 2. Hipótesis primaria, población y estimando

H-A: en trayectorias Wine true nuevas, libres de no inyectividad observada en t0 y con r* geométricamente admisible, la cola superior10% del acondicionamiento temprano tiene una precisión para eventos futuros al menos triple de la incidencia de la cohorte, con límite inferior positivo del intervalo jerárquico de precisión menos incidencia.

Dirección: X mayor, mayor riesgo futuro. Es una hipótesis de predicción, no causalidad ni ley geométrica nueva. El estimando es la precisión de una regla de **selección por rango en una cohorte**, no un umbral absoluto listo para desplegar en un estado aislado.

**Población natural, sin enriquecimiento.** 160 splits nuevos, s=8..167, cinco inicializaciones distintas por split: k=0..4, j=5+5(s−8)+k. Total fijo800 trayectorias true; no se programa cohorte random en esta fase. Las semillas se fijan en cohort_seeds.csv: split1000+s, init2000+j, minibatches4000+10s+j. Son distintas de las utilizadas en T1. Las inicializaciones no se reutilizan entre splits para preservar anidamiento. Los ejemplos Wine sí se solapan: la inferencia se limita al mecanismo de partición e inicialización sobre este dataset fijo.

No se seleccionan trayectorias por X, accuracy ni resultado. No se sustituyen fallos ni se amplía hasta reunir eventos. Los800 son candidatos inscritos, no garantía de800 elegibles. Se exigen al menos640 elegibles distribuidos en128 splits. La incidencia reportada se condiciona a la población basal elegible; se reportan además todos los excluidos y prevalentes basales, sin llamarla prevalencia natural universal.

## 3. Tiempo, entrenamiento y secuencia ciega

- t0 = **5 updates completos de Adam**. Temprano significa2% del presupuesto fijo250, independientemente de precisión o geometría.
- Horizonte = **update250**. Visitas futuras **25,50,75,100,125,150,175,200,225,250**. La primera separación temporal es20 updates.
- Guardar también inicialización t=0 para replay, sin analizarla como predictor alternativo.
- Arquitectura13→64→32→3 ReLU, float64, Adam0.006, batch64; mismas transformaciones de datos, inicialización y generador de minibatches heredados.
- Cambio longitudinal autorizado y explícito: para estas trayectorias nuevas se sustituye la parada C1 por accuracy>=.99 por un horizonte fijo250, incluso si se alcanza antes esa accuracy. No cambia el algoritmo de cada update ni ningún resultado C1. No detener por evento, X o resultado favorable.
- Antes de estados nuevos, la implementación futura debe verificar prefijo de5 updates contra el núcleo original en semillas antiguas (error máximo parámetros<=1e−12). Esto es control técnico, no validación; A0 no entrena redes.

Orden obligatorio: (1) guardar y verificar A0; (2) preparar/adaptar instrumentación y verificar replay sin cambiar el diseño; (3) entrenar todos los candidatos sólo hasta5, guardando pesos, estado Adam y RNG; (4) auditar elegibilidad basal, medir X y comparadores, guardar tablas, cola y hashes; (5) únicamente entonces continuar las mismas trayectorias hasta250 y clasificar cada visita; (6) abrir la tabla de desenlaces y ejecutar una única evaluación primaria. El clasificador futuro sólo recibe checkpoints y protocolo, no rangos ni resultados de comparadores. Nunca ajustar el diseño en esta secuencia.

## 4. Predictor exacto y criterios heredados

**X = máximo angular intrínseco de κ(Dexp) en el borde de r*=0.05697156262709151**, que es el valor completo archivado;0.05697156 es sólo presentación redondeada. CentroP0=(0,0),rho=1e−4.

Campo exacto G_rho, parámetros/checkpoint y convenciones intactos. Jacobi: j″+K(γ)j=0,j(0)=0,j′(0)=1. detDexp=j/r en marcos intrínsecos;κ=max(1,|j/r|)/min(1,|j/r|). Máximo conjunto de512 ángulos por fase, fases0 y media celda; comparación256. DOP853 rtol2e−10,atol2e−12. Compuertas T1-B: SPD, determinante firmado positivo en prefijos muestreados, borde simple, discrepanciaκ<=1e−6+.005|κ512−1|, discrepanciadet<=1e−6+.005|det512|. No se reduce r*, no se imputa infinito ni se cambia a máximo interior.

La definición regional de C_A y concentración sigue B7/B8 y sus seis fuentes: C_A=sqrt(∫K²dA/A); Λ_q=fracción de energíaK² en el q de área intrínseca de mayorK², con interpolación fraccional; R_eff=(∫K²dA)²/(A∫K⁴dA). No sustituir por métricas de celdas ni cambiar convenciones si la energía es nula: un observable indefinido queda ausente. Las copias exactas de protocolos, núcleo y clasificadores quedan en inherited_definitions.zip y sus hashes en input_verification.json.

## 5. Elegibilidad, evento y datos faltantes

En update5 se requiere INJECTIVE_AT_NOMINAL_RADIUS para entrar en el conjunto en riesgo. Los GEOMETRIC_NONINJECTIVITY basales se documentan como prevalentes y se excluyen de la incidencia por definición previa; no se reemplazan. Una incompatibilidad geométrica estable con r* se documenta como exclusión estructural antes de abrir el futuro. Si no puede distinguirse de error numérico, no se excluye limpiamente: bloquea la evaluación como INCONCLUSIVE.

**Y=1 si al menos una visita futura programada tiene GEOMETRIC_NONINJECTIVITY**, con criterios íntegros T1-A/C1-A2. **Y=0 sólo si las10 visitas son INJECTIVE_AT_NOMINAL_RADIUS**. No se afirma ausencia de eventos transitorios entre visitas ni después250. El resultado es incidencia acumulada detectada en visitas, no el evento continuo para todo t.

Jerarquía heredada: screening de borde512/1024 y Jacobi256/512, ambas fases. Candidatos si intersección, raíz/cambio de signo Jacobi, |det|min<.05,κmax>100 o excepción/inconsistencia. Confirmación de borde2048/4096/8192, Jacobi1024, ambas fases y RK4 128/256/512 pasos con2048 rayos. Nivel16384 sólo bajo disparadores heredados (inconsistencia, dispersión de inicio>1e−4R o cruce persistente sin evidencia Jacobi estable). Positivo exige evidencia geométrica estable bajo refinamiento y SPD válido; discordancia sigue INCONCLUSIVE. Radio nominal en cada checkpoint: calibración heredada A=.02, sin reducirlo para rescatarlo.

NUMERICAL_FAILURE e INCONCLUSIVE no son ceros. Un positivo futuro confirmado puede resolver Y=1 pese a otra visita desconocida, pero cualquier auditoría obligatoria faltante o fallida mantiene la compuerta técnica global INCONCLUSIVE. Una trayectoria interrumpida sin evento no es negativa. Una secuencia negativa completa termina administrativamente en250; no se extrapola más allá. No habrá confirmación sobre supervivientes numéricos. Las exclusiones estructurales basales definidas de antemano son distintas de fallos técnicos posteriores y se reportan íntegramente.

## 6. Métrica primaria, cola y comparadores

**Primaria única: precision@upper10%**. q=.10 se conserva del diseño anterior por continuidad y para mantener≈80 observaciones en cola si800 son elegibles; no se eligió optimizando nuevos resultados. Seleccionar ceil(.1Neligible) mayoresX, incluir empates exactos completos y publicar tamaño real. Si los empates hacen la cola>15%, INCONCLUSIVE por falta de resolución, sin desempatar usandoY.

Comparadores en el mismo update5, con igual cola: C_A descendente, Λ_0.1% descendente y R_eff ascendente. Se calculan en su dominio nominal admisibleD0.02, con las seis fuentes y compuertas originales; ningún valor tardío ni imputación. La falta de un comparador bloquea la conclusión incremental, no cambia X ni rescata/falla retrospectivamente la primaria si ésta está completa.

Secundarias: PR-AUC definida como **average precision escalonada no interpolada**, suma Δrecall×precision agrupando empates; recall@10%,lift, precisión y tasas por split, primera visita positiva y diferencias pareadas contra comparadores. ROC-AUC, si se muestra, es suplementaria exploratoria y no decide éxito.

OpciónB es secundaria descriptiva: criterio práctico fijado de utilidad incremental = mejora absoluta de precisión>=.05 respecto de **cada** comparador y costeCPU autónomo deX <=2 veces el del comparador más barato. Medir también coste marginal con caché compartida y pared en hardware/hilos idénticos. No se presupone que C_A sea barato ni se confunde coste de auditoría del evento con coste del predictor. Un resultado secundario favorable no convierte un FAIL primario en PASS.

## 7. Jerarquía, incertidumbre y decisión cerrada

Una observación analítica por trayectoria, con un únicoY; checkpoints nunca tratados como réplicas independientes. Inicializaciones anidadas en split y dependencia temporal preservada al resumir las visitas. Bootstrap20000 muestras de splits completos con reemplazo, semilla220020, percentiles2.5/97.5 por interpolación lineal. Se remuestrean conjuntamente X,Y y comparadores; se vuelve a aplicar la reglaq al score dentro de cada remuestreo, incluyendo empates, sin optimizarq. Publicar IC95% para precision, tasa base y su diferencia. El IC de la diferencia incorpora que la cola está dentro de la misma cohorte; no comparar dos intervalos como si fueran muestras independientes.

**PASS_PROSPECTIVE_PILOT** sólo si conjuntamente:
1. Todas las verificaciones técnicas primarias y auditorías requeridas están completas; sin fallos excluidos para confirmar.
2. Neligible>=640 y al menos128 splits elegibles; cola real<=15%.
3. Al menos30 trayectorias con evento futuro en al menos10 splits.
4. Lift observado precision/tasa base>=3.
5. Límite inferior del IC95% jerárquico de precision−tasa base>0.
6. Precision−tasa base>0 al retirar cualquier split, reaplicando la misma regla de cola.

**FAIL** si pasan las compuertas técnicas/informativas pero falla4,5 o6. No equivale a probar ausencia de asociación. **INCONCLUSIVE** si fallan compuertas técnicas, cobertura, eventos, distribución por splits, empates o IC no finito/degenerado. Si se interrumpe por recursos, conservar parciales sin reducirN ni cambiar umbrales. No expandir el ensayo por una decisión inconclusa.

El IC bootstrap tiene cobertura aproximada bajo el mecanismo de remuestreo de splits; no es exacto ni una garantía sobre tareas independientes. Sólo una decisión primaria, sin búsqueda entre tiempos/radios/colas. Intervalos secundarios son descriptivos sin declaración confirmatoria por multiplicidad. La pasada operacional aporta soporte prospectivo limitado sobre Wine; no prueba utilidad universal ni mecanismo causal.

## 8. Tamaño y sensibilidad antes de estados nuevos

Se fija **N=800 candidatos true** como compromiso operativo:160 bloques, cola nominal80, once auditorías geométricas por trayectoria (basal+10 futuras), máximo8800 auditorías más comparadores basales. No hay presupuesto de cómputo garantizado; el coste extremo depende del número de candidatos a refinamiento. No se promete completar el ensayo dentro de una sesión. La denominación piloto responde a la incertidumbre de incidencia y potencia, no autoriza cambiar las reglas.

El2/80 de T1 es frecuencia de estados finales mezclando regímenes; en true fue2/40. Ninguna es estimación de incidencia entre updates5 y250. Se usan los cuatro valores solicitados como **escenarios**, no pronósticos calibrados.

Escenario de800 elegibles, independencia condicional (intervalo predictivo central95% del número de eventos, no IC para una tasa ya observada):

'''
text+=table('event_sensitivity.csv',['p','expected','count_low95','count_high95','prob_at_least30'],lambda r:r['N']=='800' and r['within_split_ICC']=='0')
text+='''

Para esperar10/20/30 positivos, N=ceil(k/p). También se calculaN mínimo con probabilidad80% y90% de reunir al menosk mediante colas binomiales exactas:

'''
text+=table('sample_size_sensitivity.csv',['p','target_events','N_for_expectation','N_for_80pct_probability_iid','N_for_90pct_probability_iid'])
text+='''

A p=.025,800 elegibles dan20 eventos esperados y sólo≈2.04% de probabilidad de llegar a30. Para tener90% de probabilidad de30 bajo independencia harían falta1484 elegibles. Ese cálculo no justifica ampliar este ensayo después de verlo: confirma de antemano que el escenario bajo será probablemente inconcluso. A p=.05 la probabilidad es≈96.06%; con sólo640 elegibles baja a≈66.69%.

Para dependencia intrapartición se convolucionan distribuciones beta-binomiales de bloques de5 con ICC0,.1,.3, en800 y640; no se usa sólo varianza asintótica. A800,p=.025,ICC.3, intervalo de eventos9–34; a p=.05,23–59. La correlación amplía incertidumbre; aumentar una cola de la distribución no significa mayor información efectiva. El modelo de ICC es sensibilidad, no estimación a partir de dos eventos antiguos.

Intervalos exactos Clopper–Pearson ilustran la imprecisión con pocos eventos: se guardan ejemplos con denominadores10,20,30 y80. Son ilustraciones iid para sensibilidad/precisión, no sustitutos de los intervalos por split del ensayo.

La prevalencia por sí sola no determina potencia predictiva. optimistic_power_benchmark.csv añade efectos supuestos lift1,2,3,5 mediante enumeración de dos binomiales (cola80 y resto720), umbral de eventos30, lift observado>=3 y contraste hipergeométrico unilateral<.025. Es un **benchmark idealizado**, no la potencia del criterio completo bootstrap+jerarquía+exclusiones ni una cota matemática garantizada. Para p=.05,lift3 da≈.481 y lift5≈.965; p=.025,lift3≈.0097 por la compuerta de eventos. No se afirma80% de potencia del ensayo. Un efecto real justo en el umbral práctico puede pasar aproximadamente la mitad de las veces aun con información suficiente.

Fuentes de implementación estadística: SciPy binom, betabinom y BinomTestResult.proportion_ci(method='exact'); documentación oficial https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats._result_classes.BinomTestResult.proportion_ci.html . Scripts y versiones acompañan tablas; no hay resultados de estados nuevos en estas simulaciones/cálculos.

## 9. Confirmatorio, exploratorio y T2-B externo

El único análisis prospectivo primario prerregistrado es X en5→Y en visitas25..250 con precision@10% y las compuertas anteriores. Su alcance es soporte condicional de piloto; no validación de una regla descubierta y probada en los mismos80 estados.

Comparadores, PR-AUC, costes, primera detección, residuos y variables de concentración son secundarios descriptivos/exploratorios. No constituyen otra primaria. Nuevos modelos, umbrales, agregados deK o selección de tiempos surgidos enT2-A requieren otra muestra independiente.

T2-B se reserva para una tarea y/o arquitectura externa, transferencia de escala y calibración absoluta, generalización de la regla, utilidad incremental con potencia propia y cualquier mecanismo nuevo de residuos. Antes debe fijar dataset,arquitectura,geometría,normalización de r*,t0,horizonte,cohorte,comparadores y éxito. No se supone que0.05697156 tenga significado idéntico en otra geometría. No se inicia T2-B automáticamente.

## 10. Integridad, persistencia y continuación

Esta ejecución verifica1169/1169 entradas del manifiesto T1-B, CRC de81 ZIP, hash externo de su resumen y80 checkpoints contra los hashes heredados; conserva320 filas de resultados. El resumen T1-A coincide con SHA externo, su tabla final es idéntica a la usada enT1-B y se verifican45 archivos accesibles de su manifiesto. No se afirma haber redescargado sus780 arrays enA0; la auditoría completa previa queda archivada. Se mantiene la salvedad de un temporal histórico ausente, con su final íntegro. Los80 checkpoints sí se verifican nuevamente.

A0 contiene protocolo.json, semillas, criterios exactos, análisis de potencia, scripts y hashes, fuentes heredadas y este documento. Manifest y paquete verifican los bytes. Antes deT2-A comprobar todos los hashes; desarrollar sólo la instrumentación conforme al contrato congelado y verificar replay. Una incompatibilidad requiere enmienda versionada **antes de estados nuevos**; nunca corregir el contrato retrospectivamente tras resultados.

DuranteT2-A guardar por checkpoint/lote<=4: pesos,Adam,RNG,campos,diagnósticos,clasificación,errores,CPU/pared,manifest yprogress con último paso válido; escritura atómica y paquetes inmutables, detener al fallar persistencia. Restaurar exactamente desde checkpoint válido sin sustituir ni reentrenar corridas confirmadas. Guardar la tabla basal con SHA antes de continuación temporal. Mantener predictores y evaluadores separados. Ningún resultado incompleto sustituye uno válido.

**Cierre A0: protocolo congelado. Ejecución T2-A: NO INICIADA.**
'''
(P/'Leviathan_RIPG_T2-A0_preregistro.md').write_text(text)
print('Preregistration written',len(text))
