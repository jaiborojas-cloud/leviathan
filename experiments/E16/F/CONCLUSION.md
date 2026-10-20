# Conclusión E16-F — Validación parcial de longitudes

**Estado global INCONCLUSIVE:** 239/324 longitudes cumplen todos los criterios;
85/324 no alcanzan la validación exigida. No se alteró el protocolo después de
medir. La primera corrida y su código se preservaron en `3a0f6a3`.

| Métrica | PASS_NUMERICAL | INCONCLUSIVE | Total |
|---|---:|---:|---:|
| Suma | 108 | 0 | 108 |
| Producto | 66 | 42 | 108 |
| Cuadrática | 65 | 43 | 108 |

## Qué se pudo establecer

La representación polinómica del tensor, el transporte bajo tres cartas lineales,
la fórmula cerrada para suma y los controles de métrica constante pasaron.
El negativo detectó una métrica positiva en extremos pero singular en el interior.
Las 9 510 comprobaciones de identidad pasaron, con error normalizado máximo
5,66e-81. Las 1 620 comparaciones de precisión 80/120 cifras también pasaron,
con error máximo 1,16e-78. Esas cifras son observaciones numéricas, no garantías
rigurosas de exactitud.

De las 1 296 comprobaciones de cuadratura, inversión y reparametrización,
224 fueron inconclusas y 1 072 pasaron. El error normalizado máximo fue
1,59e-4 frente a una tolerancia fijada de 1e-10. Aumentar cifras no resolvió
la insuficiencia del refinamiento de integración especificado.

## Diagnóstico de los 85 casos inconclusos

- 45 no alcanzaron todos los criterios de integración, aunque la positividad
  global sí pasó su comprobación numérica.
- 40 no alcanzaron los criterios de integración y tampoco la comprobación
  global de positividad mediante los 64 subintervalos fijados.
- Ningún caso fue inconcluso por desacuerdo entre precisiones.

Una cota Bernstein no positiva no demuestra que el tensor pierda rango: el
criterio es suficiente, no necesario. No se observó aquí una singularidad
certificada. Tampoco basta ver valores positivos en los nodos de cuadratura.

Por segmento, hubo 10 inconclusos en 0→1, 72 en 1→2 y tres en 2→0. Los 72 casos
no lineales de 1→2 fueron inconclusos; sus 36 longitudes bajo suma sí pasaron.
Como explicación geométrica posterior, ese segmento pasa cerca de p=0, donde
los B no lineales de este diseño se anulan. Esto motiva estudiar resolución
cerca de mínimos de rapidez; no prueba por sí mismo la causa de cada error ni
justifica cambiar retrospectivamente el protocolo.

## Comparaciones que sí pasaron

Se conservan las 216 razones, con indicador de validez, incluidas las no
validadas. Sólo 131/216 comparaciones emparejadas cumplen el protocolo:

| Composición respecto a suma | Válidas/total | Razón mediana [mín.; máx.] | Más corta / más larga |
|---|---:|---|---:|
| Producto | 66/108 | 0,4229 [0,1677; 1,2801] | 61 / 5 |
| Cuadrática | 65/108 | 0,6262 [0,2954; 1,4860] | 54 / 11 |

“Más corta/larga” usa separación numérica de 1e-8 respecto a razón 1.
Estos resúmenes están condicionados a validación numérica: **no representan
la muestra completa ni permiten confirmar una tendencia general.** Los paneles
tienen resultados distintos y comparten estados; no son réplicas independientes.
No se convierten los supervivientes en evidencia confirmatoria.

## Alcance y siguiente pregunta

Las diferencias de métrica pueden acumularse en longitudes distintas de caminos
fijados en los casos validados. La fase completa todavía no proporciona una
comparación validada para los 216 pares. Los resultados dependen de las funciones,
unidades, cométrica regularizada y caminos declarados, sin entrenamiento ni
predicción evaluada. No se minimizó sobre caminos: no son distancias geodésicas.

Antes de abordar geodésicas, conviene un protocolo nuevo para la integración
cerca de mínimos de rapidez y para cotas globales de positividad más fuertes.
Como ahora se conocen los casos difíciles, ese desarrollo sería diagnóstico;
una confirmación necesitaría configuraciones independientes. E16-F conserva su
estado INCONCLUSIVE y sus criterios originales. No se modifica T2-A.
