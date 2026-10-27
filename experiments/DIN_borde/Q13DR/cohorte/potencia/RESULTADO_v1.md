# Potencia previa a DIN-Q13-DR

**N seleccionado:200 splits;6.000 trayectorias(200×5×6).** Primer candidato de la rejilla; no se evalúan N mayores.400 réplicas por escenario,500 bootstrap,1999 permutaciones. Todo D/p/intervalo de esta sección pertenece exclusivamente a simulaciones. La cohorte nueva no existe en este entorno.

| rho | MODULA | Wilson95 | NO_MODULA secundaria | Extremo DESAPARECE/PERSISTE/INDETERMINADO/no evaluado |
|---|---|---|---|---|
| 0.000000 | 395/400 (98.75%) | [0.971076,0.994649] | 0/400 | 250/9/141/0 |
| 0.300000 | 377/400 (94.25%) | [0.915199,0.961382] | 0/400 | 248/10/142/0 |
| 0.600000 | 344/400 (86.00%) | [0.822561,0.890590] | 0/400 | 248/8/143/1 |
| 0.614945 | 343/400 (85.75%) | [0.819837,0.888362] | 0/400 | 249/7/143/1 |

La decisión usa únicamente rho=0: Wilson inferior.971076≥.8. Se conservan5 NO_CONCLUYENTE; no hay control fallido en el escenario decisivo. Conrho=.6 y.614945 hay un control sin señal por escenario, incluido como INCONCLUSIVE_SIN_SENAL_CONTROL en el denominador, sin sustitución. No se exige equivalencia ni extremo para elegirN.

La correlación autorizada A0–LS es.6149450167751661: Pearson de log rho_caras250 centrado intra-split,4.000 pares/800 splits, SHA d360b313…. No se calculó X–Y,D,p ni otra asociación sobre Q13 real. Este rho no identifica ruido condicional ni una matriz de seis dosis.

**Límite observado:** la independencia no fue la sensibilidad de menor potencia en este modelo: las correlaciones positivas redujeron la tasa MODULA. Se conserva esta contradicción de la expectativa de conservadurismo sin cambiar la regla congelada. Los cuatro límites inferiores superan.8; es potencia condicional al modelo gaussiano y al régimen manipulado, no potencia universal.

Tiempo de potencia: 80.979s, dos procesos,un hilo BLAS. Controles: p idénticos; máximo error D≤2.23e−16 y bootstrap≤2.78e−15 frente a funciones congeladas. Fuentes SHA en [config](../config_potencia_v1.json), [salidas completas](results_v1/summary.json), [correlación autorizada](results_v1/sensitivity_Q13_correlation.json), [controles](results_v1/controls.json), [arrays externos](external_manifest.csv).
