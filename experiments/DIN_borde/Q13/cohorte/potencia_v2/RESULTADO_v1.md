# DIN-Q13 v2 — planificación: primer tamaño elegible, 800 splits

**REQUIRES_CONFIRMATION.** Se detiene antes de plan y entrenamiento de cohorte.
El primer N que satisface ambas condiciones congeladas es **800**, con tres
brazos (A0, LS=.005 y WD=.2): serían **12.000 trayectorias**. No se entrenó ninguna.

| N | Éxitos control /400 | Wilson95 inferior control | Éxitos CAE completo /400 | Wilson95 inferior CAE | Elegible |
|---:|---:|---:|---:|---:|---|
|200|347|.830754|74|.150007|No|
|256|368|.889245|138|.300088|No|
|320|383|.932998|144|.314498|No|
|400|396|.974573|219|.498501|No|
|512|399|.985977|274|.637901|No|
|640|400|.990488|311|.734209|No|
|800|400|.990488|338|.806269|Sí|

El criterio exige ambos límites inferiores ≥.8. No se rescata 640 ni se elige
un tamaño fuera de la rejilla. El margen de CAE en 800 es sólo .006269 sobre
el umbral; sigue siendo una estimación Monte Carlo bajo un modelo condicional.

## Qué se simuló

Método C2: piloto G3 s=.8 por SHA, covariables remuestreadas por splits completos,
ruido gaussiano y efectos prefijados {0,.006,.012}; cuatro marcos por tamaño,
100 realizaciones de ruido por marco. Los efectos comparten ruido y covariables
dentro de una realización, como en C2. La condición CAE usa el contraste pareado
entre .012 en el control y 0 en el brazo reducido; ambas condiciones del intervalo
se aplican literalmente mediante clasificar del analista congelado.

Cada realización lleva 500 bootstrap de splits (copias de un original siempre
en su mismo bloque) y el estimando exacto con 1999 permutaciones. Se conservaron
todos los efectos, intervalos, remuestreos, ruido y resultados simulados. Tiempo
de las siete celdas de tamaño: 211.164 s; dos procesos de un hilo BLAS.

Controles: motor batched idéntico por AST al de C2 frente a primaria congelada,
y bootstrap agrupado frente a D_punto con copias explícitas. Máximo error de
punto 2.23e-16; de bootstrap 8.89e-16; probabilidades de permutación idénticas.
El cálculo agrupado sólo evita repetir álgebra de las mismas filas, sin alterar
la CV ni aproximar los intervalos. Todos los controles PASS.

No es potencia universal para LS/WD: supone el modelo gaussiano, soporte piloto
y ruido compartido. Cuatro marcos de covariables no capturan toda su incertidumbre;
los intervalos Wilson son la regla fijada, no un certificado de potencia futura.
No se estimó ninguna asociación en calibración ni cohorte nueva, no se leyó C2,
y no se ejecutó main/analizar de Q13. Sus funciones sólo se usaron en simulaciones.

## Detención y aprobación requerida

El [diseño v1, §6](../../../DISENO_DIN_Q13_v1_CONGELADO.md), vigente por referencia
en v2, exige: **«Si N > 400, el agente pide confirmación al responsable antes de
entrenar.»** El encargo también ordena detenerse en ese paso. Se solicita en el PR
confirmación para N=800 y 12.000 trayectorias; no se emite plan ni se entrena hasta
recibirla. No se ejecuta compuerta/cohorte/analista durante la pausa.

[Protocolo operativo previo](PROCEDIMIENTO_CONGELADO_v1.md) ·
[resumen íntegro](results_v1/summary.json) · [controles](results_v1/controls.json) ·
[arrays externos](external_manifest.csv).
