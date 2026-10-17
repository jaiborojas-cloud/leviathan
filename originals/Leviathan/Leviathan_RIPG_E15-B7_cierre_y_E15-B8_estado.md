# Leviathan / RIPG — cierre E15-B7 y estado E15-B8

Fecha: 24 septiembre 2026.

## E15-B7 — cierre

**PASS en los dos casos obligatorios**, Wine j=0, con el protocolo B6 congelado, seis fuentes por estado y contorno común de 2048 rayos. Convergencia interna y compuertas multifuente se evaluaron por separado; todas las compuertas de concentración por área también pasaron.

| Caso | C_A mediano | Dispersión multifuente (%) | Estado |
|---|---|---|---|
| split 5 true | 36.7531617773 | 0.00131591828835 | PASS |
| split 6 random | 2.66182702476e-06 | 4.24298450916e-07 | PASS |

Integridad: 28/28 archivos del manifest y 16/16 checkpoints SHA-256 correctos. No hubo reentrenamiento. Se usaron las semillas, índices y escaladores guardados. La geometría y el integrador B6 se copiaron sin modificaciones y sus hashes se verificaron antes de ejecutar. El protocolo y sus criterios se fijaron antes de abrir resultados.

Una excepción de serialización de un booleano NumPy ocurrió al imprimir la clasificación en el log, después de guardar los resultados numéricos. Sólo se corrigió la serialización y se documentaron el código anterior y los hashes del parche. No se cambió ningún observable, tolerancia ni decisión. No hubo excepciones numéricas/SPD registradas en B7.

La validación es numérica fuera del caso primario, en dos checkpoints Wine adicionales. No es una validación estadística ciega ni en otro dataset.

## E15-B8 — transición autorizada y reconstrucción

La compuerta B7 abrió B8 automáticamente. Se reutilizaron sus dos casos y se ejecutaron los 14 restantes, incluido split 6 true de nuevo a 2048 rayos. No se insertó la estimación representativa 8192 en la población a 2048.

**Estado B8: PASS — 16/16 estados y 96 fuentes.**

| Split | Régimen | C_A mediano | Dispersión (%) | Estado |
|---|---|---|---|---|
| 0 | random | 0.000376249257422 | 2.08209731653e-08 | PASS |
| 0 | true | 387.701371651 | 0.000437392343293 | PASS |
| 1 | random | 0.000146135247429 | 2.52196119667e-09 | PASS |
| 1 | true | 329.409044064 | 0.000619029463203 | PASS |
| 2 | random | 0.000256565654265 | 2.72768707215e-08 | PASS |
| 2 | true | 3.04954544051 | 0.00205009213537 | PASS |
| 3 | random | 0.000145072910692 | 1.85441785293e-09 | PASS |
| 3 | true | 14.7854262739 | 0.00129204525587 | PASS |
| 4 | random | 0.00383803858569 | 1.96289129279e-08 | PASS |
| 4 | true | 1.07230364287 | 0.000450826411594 | PASS |
| 5 | random | 0.000413792952761 | 2.08145208872e-09 | PASS |
| 5 | true | 36.7531617773 | 0.00131591828835 | PASS |
| 6 | random | 2.66182702476e-06 | 4.24298450916e-07 | PASS |
| 6 | true | 1053.5743122 | 0.00102494008097 | PASS |
| 7 | random | 0.00406372127556 | 1.77993640927e-07 | PASS |
| 7 | true | 96.2177366389 | 0.000538301746174 | PASS |

### Direcciones poblacionales reconstruidas

| Estimando | Mediana true | Mediana random | Pares válidos | true > random | true < random |
|---|---|---|---|---|---|
| C_A | 66.4854492081 | 0.000316407455844 | 8 | 8 | 0 |
| lambda_1pct | 0.285990497082 | 0.01026477562 | 8 | 8 | 0 |
| lambda_01pct | 0.0366932434953 | 0.00102733379005 | 8 | 8 | 0 |
| frac50 | 0.0230816574874 | 0.494218299569 | 8 | 0 | 8 |
| frac90 | 0.115560212231 | 0.897754722303 | 8 | 0 | 8 |
| R_eff | 0.0652223516778 | 0.999795777652 | 8 | 0 | 8 |

La tabla canónica nueva es `/Leviathan/Repro/E15_B8_poblacion_mesh_independent.csv`. Los valores originales B5 permanecen archivados, no se promedian con B8 ni se convierten en una incertidumbre estadística. Las métricas espaciales son las definidas por área en B6; no equivalen a fracciones de celdas históricas B5.

## Protocolo que debe conservarse al continuar

- Campo exacto RIPG regularizado, ρ=10⁻⁴; sin jets regionales ni surrogates.
- Disco geodésico completo de área 0.02, propio de cada estado y común a sus seis fuentes.
- Contorno de 2048 rayos; fuentes interiores 64×32, 96×48 y 128×64 con fases 0 y π/n.
- DOP853, rtol=2e-10, atol=2e-12. Radio calibrado por cuadratura de área de grado cinco.
- Integrador adaptativo B6: revisar todos los padres, subdividir en cuatro, marcar 80% del error local normalizado; dos rondas estables. Mantener los límites y criterios en `protocol_frozen_B7_B8.json`.
- Compuerta primaria: (máximo C_A−mínimo C_A)/mediana C_A <0.005, además de convergencia interna válida en las seis fuentes.
- C_A=√(∫K²dA/A), concentración por área intrínseca y R_eff=(∫K²dA)²/(A∫K⁴dA). Las cinco compuertas secundarias están congeladas en el mismo JSON.
- Conservar CV entre fuentes como diagnóstico numérico, no inferencia estadística.

## Referencia B6 y límites pendientes

Referencia B6 split 6 true: seis fuentes a 2048, dispersión 0.001025%. Auditoría de una fuente representativa a 8192, C_A=1052.60819. Son dos comprobaciones diferentes. Los valores B4/B5 ≈1362 y ≈1894 se conservan como estimaciones afectadas por aliasing/subresolución, nunca como una banda de incertidumbre estadística.

B7/B8 verifican independencia de la triangulación sobre el contorno fijo de 2048 rayos. No equivalen a una auditoría de contorno 2048→4096→8192 en los 16 estados ni a una demostración de límite continuo. Los errores de área de calibración y por centroides se informan por separado. En particular, la suma por centroides de split 5 true tiene errores relativos de aproximadamente 8e-6 a 1.7e-5; no se ocultaron ni se cambió el integrador.

El resultado sigue siendo descriptivo de los checkpoints Wine j=0, no causal ni universal. No se reejecutó Shapley por capas; las conclusiones previas de distribución profunda no reciben una nueva prueba aquí. No se escalaron los 40 pares.

Siguiente paso metodológico: auditar la resolución del contorno en los estados extremos de la población antes de atribuir precisión de alta resolución a todos los valores. Esa auditoría no se ejecutó automáticamente en este encargo.

## Artefactos persistentes

- `/Leviathan/Repro/Leviathan_RIPG_E15-B7_validacion_externa.md`: todos los valores por fuente de B7, medianas/rangos/CV, errores de área, SPD, excepciones y costes.
- `/Leviathan/Repro/Leviathan_RIPG_E15-B8_reconstruccion_poblacional.md`: población, direcciones y límites.
- `/Leviathan/Repro/Leviathan_E15_B7_B8_codigo_resultados.zip`: scripts, protocolo congelado, checkpoints, manifests, tablas, logs, geometrías y contornos; hashes y muestras deterministas de celdas finales.
- `/Leviathan/Repro/E15_B7_fuentes.csv` y `E15_B7_estadisticas.csv`: tablas completas de los dos casos.
- `/Leviathan/Repro/E15_B8_poblacion_mesh_independent.csv`: sustituto canónico del mapa provisional B5 bajo el protocolo declarado.

El ZIP contiene también los 96 resultados por fuente, estadísticas completas y diferencias pareadas. Las nubes completas de celdas se regeneran; las muestras `witness` no deben usarse para recomputar integrales.
