# DIN-Q13-M2 — potencia preparatoria N=320

**Preparación, no congelación del confirmatorio.** Se simulan 400 réplicas por rho, con 11 niveles y un A0 único compartido; 500 bootstrap y 1999 permutaciones. Las potencias incluyen inconclusas en el denominador.

| rho | MODULA LP: éxitos/400; potencia [Wilson95] | MODULA WD: éxitos/400; potencia [Wilson95] | Ambos MODULA: éxitos/400; potencia [Wilson95] |
|---|---|---|---|
| 0 | 398/400; 99.50% [0.981955,0.998628] | 393/400; 98.25% [0.964323,0.991498] | 391/400; 97.75% [0.957797,0.988118] |
| 0.3 | 383/400; 95.75% [0.932998,0.973298] | 382/400; 95.50% [0.929995,0.971349] | 373/400; 93.25% [0.903573,0.953199] |
| 0.6 | 350/400; 87.50% [0.838981,0.903885] | 359/400; 89.75% [0.863897,0.923541] | 344/400; 86.00% [0.822561,0.890590] |
| 0.615 | 348/400; 87.00% [0.833492,0.899469] | 359/400; 89.75% [0.863897,0.923541] | 342/400; 85.50% [0.817117,0.886130] |

**Regla de preparación:** rho0 decide. Wilson inferior≥.8 por manipulador; la conjunta solo se reporta. Ambos cumplen.

Tiempo total: 195.120s; dos procesos de un hilo. Son estimaciones condicionales al modelo y soporte piloto, no una garantía de potencia en la cohorte futura ni certificado de error finito.

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

**Referencia provisional:** PR#114,commit66f5de58,analista SHA`2e69516e62b59d90d8abd9d91e1468e538c07b50dc059a6814cd7a20197030fa`. Sigue siendo borrador. Al congelar hay que cotejar el SHA y demostrar equivalencia del estimando o repetir la potencia. Esta preparación no autoriza plan o cohorte.

[Potencias CSV](potencia.csv) · [Resumen y conteos completos](results_v1/summary.json) · [Controles](results_v1/controls.json) · [Verificación](verification.json) · [Arrays por SHA](external_manifest.csv) · [Procedimiento previo](PROCEDIMIENTO_v1_CONGELADO.md) · [Decisión de truncamiento](DECISION_TRUNCAMIENTO.md).
