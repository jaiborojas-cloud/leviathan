# DIN-C2: cohorte publicada, sin análisis

**ENTREGADA_SIN_ANALISIS.** Se generaron 200 splits × 5 inicializaciones = **1.000
trayectorias**, s=.8, y 4.000 visitas (5,10,30,250), sin errores de generación ni
estados inválidos. No es un veredicto de la hipótesis confirmatoria.

## Entradas para el analista

- [Tabla inmutable de 1.000 filas y 12 columnas](cohorte/c2_cohorte.csv).
- [Plan de universo](cohorte/c2_plan.json) y [IDs](cohorte/ids_planificados.txt).
- [Resumen operacional](cohorte/RESUMEN_c2.json).
- [SHA de publicación](cohorte/PUBLICACION_c2.sha256).

| Archivo | SHA-256 |
|---|---|
|c2_cohorte.csv|`afd4783c2505251a1456aed9b3f8583d8f98c186908d2611be7f3dedd64eca19`|
|c2_plan.json|`ad320ac9fdf75a80801f2c44a529de467f1c852ed90cdd3d7181a61151b6aed8`|
|cohorte_scripts/run_v1.py|`41dd0afafc64c860bdaa61636583dfc71171d7df13c0a01096a8bc9b498008a4`|
|analisis_C2.py (no ejecutado)|`d24ac5a7f88b5afd52e13e63bafc179ef046920a27b7144f0ce14cb5fefc1709`|

El agente de cohorte no calculó D, p, W, correlaciones ni asociaciones entre X10
y rho/Y de C2. Tampoco calculó medianas c/q ni la fracción colapsada. Claude ejecuta
el análisis congelado una sola vez sobre esta publicación; el responsable decide
el cierre. El diseño, el analista y sus pruebas permanecen intactos.

## Planificación y controles

[Potencia previa](potencia/RESULTADO_POTENCIA_v1.md): el primer N=200 pasó, potencia
simulada .8675 para D_obj=.012 (inferior Wilson95 .83075); falsos PASS bajo nulo
.0275 (superior .04857). 400 réplicas/celda, 1999 permutaciones; sólo piloto G3.
La potencia es condicional al modelo y soporte piloto, no una garantía universal.

[Compuerta anterior al entrenamiento](cohorte/compuerta_v1/reconstruction.json):
tres reconstrucciones de M desde pesos de modelos de control **sin entrenar**,
error 0 y f idéntica. Semillas C2 611000/621000/631000 disjuntas de G2/G3.
[Equivalencia del código científico con G3](cohorte/source_equivalence_v1.json).

[Verificación de integridad](cohorte/verification.json): **PASS**, 12.407 archivos
externos, tabla copiada exactamente y universo completo. Se conserva el
[fallo de rutas del verificador v1](cohorte/fallos_v1/FAILURE.json), la
[enmienda congelada previa](ENMIENDA_VERIFICACION_v2_CONGELADA.md) y el
[diff v1→v2](cohorte/verify_v1_to_v2.diff). No cambian mediciones ni tabla.

## Archivo y reproducción

[Informe operacional](INFORME_OPERACIONAL_c2.md), [cronología](CRONOLOGIA_COHORTE.json),
[reproducción v1](REPRODUCCION_COHORTE_v1.md) y
[nota de verificación v2](REPRODUCCION_VERIFICACION_v2.md).
Los cuatro [shards de estados](cohorte/run_v1/state_records/) restauran los 4.000
originales bit por bit, sin sobrescribir; [SHA por registro](state_records_manifest.csv).
Todos los [registros de trayectoria](cohorte/run_v1/trajectories/) están publicados.

[Manifiesto externo](cohorte/external_manifest.csv): arrays/pesos/diagnósticos
conservados en rutas locales fuera de Git. Esas rutas no son un alojamiento remoto.
[Manifiesto de archivos](manifest_cohorte.csv) y
[fuentes congeladas](freeze_manifest_cohorte.csv).
Sólo se añadieron archivos en C2. No se usaron Wine, Iris ni datos T2/DIN-C1.
