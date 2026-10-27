# DIN-Q13-M2: potencia preparatoria N=320

**N=320 cumple la regla individual en rho=0:** LP398/400(99.50%),Wilson95[.981955,.998628]; WD393/400(98.25%),Wilson95[.964323,.991498]. La conjunta,contada directamente,es391/400(97.75%),Wilson95[.957797,.988118]; solo se reporta,no se exige.

|rho|LP MODULA|WD MODULA|Ambos MODULA|
|---|---:|---:|---:|
|0|99.50 %|98.25 %|97.75 %|
|.3|95.75 %|95.50 %|93.25 %|
|.6|87.50 %|89.75 %|86.00 %|
|.615|87.00 %|89.75 %|85.50 %|

400 réplicas por escenario,11 niveles con A0 único compartido,bootstrap500,IC97.5 y1999 permutaciones. No se buscó otroN,ni se generaron plan o cohorte. Una futura cohorte Windows no se ejecutó ni preparó en esta tarea.

- [Informe completo con Wilson95,generadora y limitaciones](RESULTADO_v1.md).
- [Potencias CSV](potencia.csv), [conteos y todos los marcos](results_v1/summary.json), [controles contra analista2e69516e](results_v1/controls.json).
- [Verificación de todas las salidas y MCO independiente](verification.json), [contraste adicional de respuestas simuladas con covariables piloto](results_v1/crosscheck_pilot_simulated.json).
- [SHA/AST del analista](analyst_equivalence.json), [diff exacto](ANALISTA_DIFF_NMAX.diff), [equivalencia de código de potencia](power_equivalence.json).
- [Procedimiento previo](PROCEDIMIENTO_v1_CONGELADO.md), [implementación por SHA](IMPLEMENTACION_v1.sha256), [fuentes](sources/provenance.json).
- [N200 intacto](preservation_N200.json), [resultado N200](../RESULTADO_v1.md).
- [Manifiesto](manifest.csv), [SHA](manifest.sha256), [arrays externos](external_manifest.csv).

Analista comprobado:2e69516e62b59d90d8abd9d91e1468e538c07b50dc059a6814cd7a20197030fa,en66f5de58 del PR#114. Solo cambia el docstring y N_MAX218→320 respecto del anterior; el estimando es idéntico. No se encontró analista congelado M2 en main al iniciar. Si cambia al congelar,se verifica o repite,como en la preparación anterior.

Generadora,piloto y constantes estadísticos idénticos a N200. Se conserva la fórmula de semillas[412000,2,N,marco] y[413000,2,N,marco],con N320; bootstrap960001. Eso no significa reutilizar literalmente el flujo N200. No se ajustaron semillas o efectos a los resultados. Los objetivos LP5/WD5 siguen truncados; los D muestrales negativos se conservan. Es potencia condicional al modelo y soporte piloto,no garantía sobre la cohorte futura.
