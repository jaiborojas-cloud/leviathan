# Experimentos cerrados

Selección documental mínima, revisada el 18 de octubre de 2026. Los originales permanecen en el archivo histórico; las fichas los enlazan sin duplicarlos. Cierre de ejecución no significa confirmación científica.

| Etapa | Estado del cierre | Lectura |
|---|---|---|
| E10 | CERRADO_EXPLORATORIO | [README](E10/README.md) · [Conclusión](E10/CONCLUSION.md) |
| E11 | CERRADO_EXPLORATORIO | [README](E11/README.md) · [Conclusión](E11/CONCLUSION.md) |
| E12 | CERRADO_EXPLORATORIO | [README](E12/README.md) · [Conclusión](E12/CONCLUSION.md) |
| E13 | INCONCLUSIVE | [README](E13/README.md) · [Conclusión](E13/CONCLUSION.md) |
| E15/B6 | CIERRE_NUMERICO | [README](E15/B6/README.md) · [Conclusión](E15/B6/CONCLUSION.md) |
| E15/B7 | PASS_NUMERICO | [README](E15/B7/README.md) · [Conclusión](E15/B7/CONCLUSION.md) |
| E15/B8 | PASS_NUMERICO | [README](E15/B8/README.md) · [Conclusión](E15/B8/CONCLUSION.md) |
| E15/C1-A | INCONCLUSIVE | [README](E15/C1-A/README.md) · [Conclusión](E15/C1-A/CONCLUSION.md) |
| E15/C1-A2 | GEOMETRIC_NONINJECTIVITY | [README](E15/C1-A2/README.md) · [Conclusión](E15/C1-A2/CONCLUSION.md) |
| T1/A | MAPA_COMPLETO_DESCRIPTIVO | [README](T1/A/README.md) · [Conclusión](T1/A/CONCLUSION.md) |
| T1/B | EXPECTED_GEOMETRIC_CONTROL | [README](T1/B/README.md) · [Conclusión](T1/B/CONCLUSION.md) |

## Límites de cobertura

E1–E8 permanecen en la [revisión estática histórica](../docs/archive/review-before-import/docs/experiment-index.md) y el notebook. E9 y E14 carecen del cierre primario autónomo recuperado: no se inventan fichas de cierre. E15-B1–B5 se consultan como antecedentes históricos en el archivo; sus estimaciones provisionales no sustituyen B6–B8.

T2-A0 es un [prerregistro](../docs/archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md), no un resultado confirmatorio. [T2-A](T2_A/README.md) continúa abierto; el cierre documental de una incidencia no cierra el seguimiento.

## Integridad

[closed_sources.csv](closed_sources.csv) registra ruta, bytes y SHA-256 de cada fuente seleccionada tal como está en este commit. Es un inventario nuevo y no reemplaza los manifests históricos. Verificación documental: `python tools/verify_closed_sources.py`. No requiere checkpoints ni ejecuta geometría.

## Línea independiente analítica

[E16 — Composicionalidad y coarse-graining perspectival](E16/README.md):
EXPECTED_GEOMETRIC_CONTROL; [conclusión](E16/CONCLUSION.md). Diseño congelado,
código y resultados pequeños propios, sin ejecutar ni modificar T2-A.

[E16-B — Instrumentación en red sintética sin entrenamiento](E16/B/README.md):
identidades PASS, validación independiente del rango INCONCLUSIVE; diseño
congelado, 81 configuraciones conservadas y cero pasos de entrenamiento.

[E16-D — Réplica instrumental en configuraciones nuevas](E16/D/README.md):
396/396 rangos PASS_NUMERICAL, 216/216 negativos detectados y ausencia de cambios
de rango entre composiciones en esta muestra sintética sin entrenamiento.

## E16-E — Distancias y anisotropía relativa

[README](E16/E/README.md) · [conclusión](E16/E/CONCLUSION.md) ·
[evidencia](E16/E/results/run_v1/summary.json). Exploratorio sobre datos D:
216 comparaciones SPD con cambios de forma, sin entrenamiento.

## E16-F — Longitudes de caminos prefijados

[README](E16/F/README.md) · [conclusión](E16/F/CONCLUSION.md) ·
[evidencia](E16/F/results/run_v1/summary.json). Estado global INCONCLUSIVE:
239 longitudes validadas y 85 inconclusas; sin entrenamiento ni geodésicas.

## E16-G — Resolución numérica de las limitaciones F

[README](E16/G/README.md) · [conclusión](E16/G/CONCLUSION.md) ·
[evidencia](E16/G/results/run_v1/summary.json). PASS_NUMERICAL diagnóstico:
324/324 longitudes, incluidos los 85 inconclusos F. Sin cambiar F ni T2-A.

## E16-H — Transferencia prospectiva

[README](E16/H/README.md) · [conclusión](E16/H/CONCLUSION.md) ·
[evidencia](E16/H/results/run_v1/summary.json). PASS_NUMERICAL: 324 longitudes
nuevas y 216 pares, sin selección, entrenamiento ni cambios al método G.
