# Pruebas del ejecutor PC Q15 v3

2026-11-02 (America/Mexico_City). **Último lote: 66/66 PASS, 0 fallos, 0 errores.**

Fuentes vigentes: productor v1.1 en `7056e0dd05cb8ed2b280c2c877d5f6cd7b75487c`, SHA `d561cb0bdccdd40fb91e5d0553ac85dbc58adc13e7487c7f1a1c226b2af1ee41`; suite vigente `pruebas_ejecutar_q15_v3_v1_1.py`, SHA `f9fd933d0d3f6417874fca7cb855d9951380baa4a6c3eb2629781f9ed2916671`.

Se ejecutó con Python 3.12.14 en Linux, mediante `python -I`. Todas las respuestas son fixtures/metadatos sintéticos; se bloquean globalmente la apertura de conexiones y la construcción del transporte de red. El reloj y sus esperas son simulados. No se ejecutó una consulta bibliográfica del plan, no se probó internet normal ni se incorporaron artículos nuevos a la extracción Q15. La consulta de documentación técnica para comprobar contratos de API es una actividad separada, no una medición del productor.

## Casos decisivos cubiertos

| Grupo | Qué comprueba |
|---|---|
| Insumos y URL | 55 consultas, 294 combinaciones, 19 anclas, SHA; cambio de un byte rechazado; consultas exactas conservadas en URL; 55 Scholar omitidas. |
| Incompatibilidad S2 | Cadenas/ranking incompatibles quedan `PENDIENTE_ENMIENDA_S2`, sin HTTP ni falsa ejecución de cero resultados. |
| Topes | 500 se conservan; 501 activa K=200; total desconocido se sondea solo hasta 501; duplicados y postfiltros no rellenan cupos. |
| Paginación | Segunda página fallida conserva primera; total cambiante, fin prematuro, repetición y falta de avance no se etiquetan completos. |
| Respuestas | Atom válido y cero legítimo; HTML de login no pasa por Atom vacío; esquemas JSON incorrectos, vecinos nulos, NaN/Infinity/overflow. |
| Actas | Año descendente antes del tope; título/ID ascendentes; contexto PMLR fuera del enlace «Volume»; no confundir otro venue con ICML; índice parcial/anios ausentes y resúmenes ausentes quedan pendientes. |
| OpenReview | Notas aceptadas con campos v1/v2; exclusión de workshops y borradas; fecha pública; formato histórico no recuperado queda pendiente, no cero. |
| Citantes | Umbral exacto 500/501; conteo desconocido; ruta local primeras 200 y después filtro; no reponer; límites de palabra, NFKC y guiones Unicode; falta de resumen. |
| S0 | Resolución por arXiv/DOI/título; título discordante rechazado; snapshot previo al grafo; un solo nivel, sin recursión sobre vecinos. |
| Transporte | Pausas ≥1 s S2 y ≥3 s arXiv; 429, Retry-After, agotamiento, 403, reanudación explícita; gzip crudo con SHA; URL final/redirecciones; no guardar clave ni cookie. |
| Conservación | Colisión con marcador, bloqueo de dos productores, SHA alterado, cuerpo/temporal huérfano, versiones de fallos, huella de simulación distinta de red. |
| CLI e integración | Preparación sin red; recorrido sintético de 55 consultas arXiv con un truncamiento y 54 ceros válidos; segunda ejecución conserva respuestas byte por byte; CSV de las 294 entradas; código 2 con pendientes. |
| Windows | Rama de publicación exclusiva simulada: no reemplaza marcador. No se presenta como prueba del sistema operativo real. |

El conteo se refiere a métodos de prueba; varios incluyen más de un subcaso. Se prueban contratos y fallos observables, no que un servicio vivo acepte una interfaz histórica ni que la revisión sea exhaustiva.

## Historial conservado

| Lote | Resultado | Fuentes |
|---|---|---|
| [run_01](pruebas_simuladas/run_01.json) | 51/51 PASS | Código inicial `ed4d3323`; suite histórica incorporada en `20377eca`. |
| [run_02](pruebas_simuladas/run_02.json) | 63/63 PASS | Productor y suite en `9c9fe8a2`. |
| [run_03](pruebas_simuladas/run_03.json) | 65/65 PASS | [Snapshots](pruebas_simuladas/fuentes_run03/) de la versión intermedia, contrastados con los SHA del reporte. |
| [run_04](pruebas_simuladas/run_04.json) | 66/66 PASS | Fuentes vigentes en `7056e0dd`, con control adicional de índice histórico parcial. |

Se conservaron JSON y log de todos los lotes; no hubo fallos ocultados. Los snapshots de run_03 se reconstruyeron a partir del diff intermedio y se verificaron byte por byte contra sus SHA; no se repitió aquel lote para sustituirlo. Los otros lotes se vinculan a sus commits exactos. La suite histórica inicial no es compatible con todos los detalles del productor actual; ejecutar únicamente la suite **vigente v1.1** para esta auditoría.

La prueba final no habilita automáticamente usar red ni corrige el protocolo S2. Es un borrador para revisión de Claude. No se modificaron las fuentes congeladas ni el primer lote bibliográfico.
