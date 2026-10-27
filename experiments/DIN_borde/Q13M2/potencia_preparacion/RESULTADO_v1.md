# DIN-Q13-M2 — potencia preparatoria N=200

**Preparación, no congelación del confirmatorio.** Se simulan 400 réplicas por rho, con 11 niveles y un A0 único compartido; 500 bootstrap y 1999 permutaciones. Las potencias incluyen inconclusas en el denominador.

| rho | MODULA LP: éxitos/400; potencia [Wilson95] | MODULA WD: éxitos/400; potencia [Wilson95] | Ambos MODULA: éxitos/400; potencia [Wilson95] |
|---|---|---|---|
| 0 | 310/400; 77.50% [0.731573,0.813195] | 301/400; 75.25% [0.707939,0.792257] | 274/400; 68.50% [0.637901,0.728579] |
| 0.3 | 297/400; 74.25% [0.697485,0.782902] | 299/400; 74.75% [0.702708,0.787583] | 276/400; 69.00% [0.643049,0.733336] |
| 0.6 | 267/400; 66.75% [0.619931,0.711882] | 275/400; 68.75% [0.640474,0.730958] | 252/400; 63.00% [0.581659,0.675868] |
| 0.615 | 267/400; 66.75% [0.619931,0.711882] | 274/400; 68.50% [0.637901,0.728579] | 252/400; 63.00% [0.581659,0.675868] |

**Regla de preparación:** rho0 decide. Wilson inferior≥.8 por manipulador; la conjunta solo se reporta. No cumplen ambos: reportar al responsable sin cambiar N ni generar plan.

Tiempo total: 166.694s; dos procesos de un hilo. Son estimaciones condicionales al modelo y soporte piloto, no una garantía de potencia en la cohorte futura ni certificado de error finito.

## Generadora y efecto que queda tras truncar

`D_recta(c)=−0.038434071244996953+0.077c`; objetivo `d(c)=max(0,D_recta(c))`, autorizado antes de simular. Se recortan objetivos de varianza explicada, nunca los estadísticos D de las réplicas. La curva es lineal a tramos, no lineal en todo el rango.

| Nivel | c esperada | Recta sin truncar | Objetivo generador | Truncado |
|---|---:|---:|---:|---|
| A0 | 0.864 | 0.028093928755 | 0.028093928755 | no |
| LP1 | 0.688 | 0.014541928755 | 0.014541928755 | no |
| LP2 | 0.610 | 0.008535928755 | 0.008535928755 | no |
| LP3 | 0.560 | 0.004685928755 | 0.004685928755 | no |
| LP4 | 0.500 | 0.000065928755 | 0.000065928755 | no |
| LP5 | 0.400 | -0.007634071245 | 0.000000000000 | sí |
| WD1 | 0.690 | 0.014695928755 | 0.014695928755 | no |
| WD2 | 0.610 | 0.008535928755 | 0.008535928755 | no |
| WD3 | 0.560 | 0.004685928755 | 0.004685928755 | no |
| WD4 | 0.500 | 0.000065928755 | 0.000065928755 | no |
| WD5 | 0.438 | -0.004708071245 | 0.000000000000 | sí |

LP4 y WD4,c=.50: .000065928755>0,no se truncan,pero quedan prácticamente en cero. LP5(.40) y WD5(.438) sí se truncan.

| Manipulador | beta nominal | Pendiente MCO efectiva de seis objetivos | Rango c | beta efectiva×rango |
|---|---:|---:|---:|---:|
| LP | .077 | 0.064952782620 | 0.464 | 0.030138091136 |
| WD | .077 | 0.069950805294 | 0.426 | 0.029799043055 |

Ambas pendientes efectivas son menores que.077. WD tiene menor rango,pero su pendiente post-truncamiento es mayor que LP; su contraste ajustado a lo largo del rango es ligeramente menor. No se atribuye de antemano una menor potencia de WD solo a su rango. La potencia observada resuelve esa comparación en este modelo.

El truncamiento reduce la pendiente nominal respecto de la recta sin recortar. No se toma esto como una garantía matemática de conservadurismo para toda distribución o ajuste. La curvatura por tramos,los errores de muestra y la dependencia se preservan en las simulaciones.

## Método y alcance

Piloto G3s=.8 por SHA1364e8e7…:100 splits×5,se remuestrean splits completos en cuatro marcos de100 réplicas gaussianas. Solo se usan sus covariables y varianza residual de Y respecto de base cúbica de L. No se calcula D de ninguna cohorte real. Los seis D/c de LS se leen del resultado oficial ya publicado(SHA0f74669d…),no se recalculan desde su tabla.

Ruido con factor común y11 específicos:rho0/.3/.6/.615. Un solo A0 se genera y evalúa por réplica y se reutiliza en ambas pendientes. El bootstrap de500 draws(seed960001) comparte splits en los11 niveles y mantiene copias en su bloque original. La conjunta se cuenta como intersección,no producto de marginales.

La compuerta operacional se supone válida con c fijos y precisión/q apropiadas; la señal del control sí se evalúa con C1 exacto. Los fallos de control permanecen como inconclusos. d es objetivo nominal del generador gaussiano, no el valor esperado exacto del D estimado por CV en una muestra finita. No se vuelven a calibrar efectos para alcanzar una potencia deseada.

Los motores agrupados se contrastaron con el analista M2 completo solo en dos tablas sintéticas,N20/N40: D,p,réplicas,IC97.5 y etiquetas individuales/conjuntas. p idénticos; errores numéricos<1e−10. Se verificaron todas las16 salidas y sus pendientes mediante una MCO independiente.

**Referencia provisional:** PR#114,commit525c7455,analista SHA`15ca7b428110f0b7bff1520d93587c7438e8ea0959394f98c91ac37653d95332`. Sigue siendo borrador. Al congelar hay que cotejar el SHA y demostrar equivalencia del estimando o repetir la potencia. Esta preparación no autoriza plan o cohorte.

[Potencias CSV](potencia.csv) · [Resumen y conteos completos](results_v1/summary.json) · [Controles](results_v1/controls.json) · [Verificación](verification.json) · [Arrays por SHA](external_manifest.csv) · [Procedimiento previo](PROCEDIMIENTO_v1_CONGELADO.md) · [Decisión de truncamiento](DECISION_TRUNCAMIENTO.md).
