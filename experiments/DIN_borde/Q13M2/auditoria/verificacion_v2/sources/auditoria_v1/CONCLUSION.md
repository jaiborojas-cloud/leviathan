# Auditoría independiente DIN-Q13-M2, antes de congelar

**Recomendación: corregir o resolver F01 antes de congelar**, impedir la sobreescritura F02 y actualizar la evidencia F03. La reproducción LS requiere una tolerancia numérica explícita (F04). No se modificaron el diseño ni el analista. Se auditó exclusivamente el commit `66f5de58`, analista `2e69516e…` y pruebas `063c15e4…`; no se aprueba aquí una versión posterior.

El bootstrap principal respeta los mismos remuestreos LP/WD, conserva las copias en el bloque del split original, comparte A0 y recalcula D, c y β. Los cuantiles son exactamente .0125/.9875. La referencia LS usa 2000 remuestreos independientes con semilla 960002, y la misma réplica LS para los dos contrastes. Los fallos de bootstrap se conservan completos y no se sustituyen. Véanse la [matriz de revisión](MATRIZ_REVISION.md) y los [casos de defectos](DEFECTOS.md).

| Hallazgo | Severidad | Resultado |
|---|---|---|
| F01: fallo puntual exclusivo de WD o LP invalida al otro | Alta | SSE_base=0 en WD3 borra LP, aunque sus seis estadísticas son idénticas al control que da MODULA. X/L constantes presentan además una discrepancia de contrato que debe aclararse. |
| F02: resultado anterior sobreescrito | Media, operacional | Una ejecución CLI válida reemplaza `RESULTADO_Q13M2.json` sin rechazar la colisión. |
| F03: evidencia archivada corresponde a otros SHA | Media, trazabilidad | Informe/JSON de pruebas no corresponden al analista y pruebas auditados. |
| F04: igualdad literal de β_LS | Baja, numérica | Diferencia de 3.747×10⁻¹⁶; las dos implementaciones originales coinciden numéricamente. No demuestra un error estadístico. |

La independencia funciona ante una compuerta fallida y ante fallos del bootstrap de un manipulador. El defecto F01 está en las salidas anticipadas del ajuste puntual. Las restricciones globales explícitas de faltantes y de splits comunes en los 11 niveles se respetaron; no se propone cambiar esa población retrospectivamente.

## Tamaño bajo nulos sintéticos

N=320, D poblacional constante .02, β verdadero cero, 400 tablas por escenario; 5000 permutaciones y 2000 réplicas bootstrap por tabla. A0 es único y compartido. Los cálculos independientes se contrastaron con las funciones originales antes del Monte Carlo. Tiempo de Monte Carlo: 922.014 s, dos procesos de un hilo.

| Dependencia ρ del ruido | Falsos MODULA LP | Falsos MODULA WD | Al menos uno: error familiar (Wilson95) | Ambos | A0 PASS |
|---|---|---|---|---|---|
| 0 | 2/400 (0.50 %) | 4/400 (1.00 %) | 6/400: **1.50 % [0.69, 3.23]** | 0/400 | 400/400 |
| .6 | 4/400 (1.00 %) | 6/400 (1.50 %) | 9/400: **2.25 % [1.19, 4.22]** | 1/400 | 399/400 |

Los límites superiores familiares son inferiores al 5 % solicitado: **sin inflación detectada en estos dos modelos**, no un certificado de control universal del bootstrap. Condicionado a A0 PASS, el segundo error familiar es 9/399, 2.256 % [1.191, 4.231] %. La réplica sin señal control se conserva como inconclusa, dentro del denominador global. Tasas individuales, conjuntas, Wilson y denominadores completos en [rates.csv](rates.csv) y [summary.json](results/monte_carlo_v1/summary.json).

Bonferroni con dos IC bilaterales de 97.5 % ofrece cobertura simultánea nominal de 95 % si los IC están calibrados. Aquí solo se decide MODULA por el extremo positivo: la unión direccional nominal es como máximo 2×1.25 %=2.5 %. La simulación no demuestra ese límite más estricto para cualquier distribución.

## Alcance y entrega

23 casos principales, 109 comprobaciones de plan, 27 de dominio, nueve ejecuciones CLI y dos límites adicionales de API. No se ejecutó el `main` de las pruebas del autor, que accede a un fixture entrenado; se leyeron sus fuentes y se usaron controles independientes sintéticos. La única tabla real leída fue la referencia LS autorizada y publicada, SHA `ed00364f…`. No se entrenó ni se leyó la cohorte M2, Wine, C2, Q13, T2 o DIN-C1 como datos.

La referencia LS produce β=0.07692466151365296 frente al literal 0.07692466151365258. El IC95 recalculado con la nueva semilla secundaria 960002 es [0.02672304432290993, 0.1388029414848341]; **no reemplaza el cierre, β ni IC oficiales de Q13-DR**.

[verification.json](verification.json) verifica 826 condiciones de integridad, incluidas las 800 salidas y sus arrays. `PASS_AUDIT_INTEGRITY` significa integridad de esta auditoría, no aprobación del analista. [verification_publicacion.json](verification_publicacion.json), [manifest.csv](manifest.csv) y [manifest.sha256](manifest.sha256) completan la entrega. Los arrays se conservan fuera de Git con SHA y receta reproducible. La decisión de congelar y cualquier cambio del diseño pertenecen al responsable.
