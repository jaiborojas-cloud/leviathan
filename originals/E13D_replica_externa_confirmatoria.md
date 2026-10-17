# E13-D — réplica externa confirmatoria en Wine

**Estado:** **inconcluso por la regla prerregistrada de faltantes**.  
**Fecha:** 23 de septiembre de 2026.  
**Prerregistro:** E13-A; estados y compuerta geométrica: E13-C.

## Resultado ejecutivo

E13-D no puede confirmar ni refutar la hipótesis primaria. Sólo **3/40 pares** superaron conjuntamente la construcción de las tres áreas, la positividad del jet métrico y el refinamiento. La pérdida fue **92.5%**, muy por encima del máximo prerregistrado de 10%, y sólo **0/8 particiones** conservaron al menos cuatro pares (se exigían seis).

La causa de exclusión de los otros 37 pares fue numérica y estructural: el jet métrico analítico de segundo orden de la rama `true` dejó de ser definido positivo antes de encerrar las áreas objetivo. No se ampliaron áreas, no se cambió el centro, no se sustituyeron semillas y no se recurrió al campo exacto para rescatar casos.

## Flujo de inclusión

| Etapa | Pares conservados | Pares excluidos |
|---|---:|---:|
| Estados E13-C emparejados | 40 | 0 |
| Tres áreas en malla principal | 3 | 37 |
| Refinamiento y cambio <0.5% | 3 | 37 |
| Regla de faltantes | **fallida** | — |

## Contraste confirmatorio

Los cinco criterios direccionales no se evaluaron: la compuerta de faltantes se aplica antes del contraste. En particular, no se presenta un valor p confirmatorio ni un intervalo BCa basado en las dos únicas particiones supervivientes. Hacerlo convertiría un subconjunto seleccionado por estabilidad numérica en la muestra confirmatoria.

| Regla previa | Resultado | Estado |
|---|---:|---|
| Pérdida máxima de pares <=10% | 92.5% | falla |
| >=6/8 splits con >=4 pares | 0/8 | falla |
| Decisión E13-D | — | **inconclusa** |

## Descripción de los pares supervivientes (no confirmatoria)

En los 3 pares supervivientes, la mediana descriptiva fue: 

| Estimando primario | Mediana |
|---|---:|
| $C_{0.02}^{true}$ | 5.29388 |
| $C_{0.02}^{random}$ | 0.00107556 |
| $\Delta C_{0.02}$ | 5.29281 |

Estas cifras no reparan la pérdida ni autorizan inferencia confirmatoria.

## Auditoría numérica y de frontera

- Error relativo máximo de área entre estados integrados: 9.66e-07.
- Cambio máximo principal–refinamiento entre estados incluidos: 9.07e-05 (umbral 0.005).
- Determinante métrico mínimo: 0.204; condición máxima: 9.
- La auditoría exacta no selectiva cubrió 48 puntos de frontera: ocho direcciones por cada estado de los 3 pares.
- En la comparación exacta pareada de magnitudes, `true > random` ocurrió en 24/24 direcciones. Es un control secundario limitado a los casos supervivientes.

## Interpretación

E13-D identifica un límite del procedimiento fijado en E13-B/C: para la arquitectura profunda y Wine, el jet cuadrático local no sostiene discos de las áreas congeladas en la mayoría de estados `true`, aunque E13-C verificó positividad del campo exacto en su malla. Eso no constituye evidencia contra la hipótesis curvatural; constituye evidencia de que la aproximación local preregistrada no entrega el estimando externo con cobertura suficiente.

Las ocho particiones, además, son remuestreos del mismo dataset Wine y no ocho datasets independientes. Incluso sin la pérdida, la generalización habría sido a esta tarea y protocolo, no una ley universal.

## Cierre

La conclusión formal es:

> **E13-D queda inconcluso por fallo de cobertura del jet métrico local.** No se confirma ni se refuta $\Delta C_{0.02}>0$ y no se modifican retrospectivamente áreas, mallas, semillas o criterios.

Un estudio posterior tendría que prerregistrar una reconstrucción del campo métrico exacto o una aproximación de orden/atlas distinta y volver a comenzar con un nuevo identificador; no sería una continuación confirmatoria de E13-D.
