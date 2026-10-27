# Decisión recibida antes de simular

El responsable confirmó: «Sí, usa max(0,D(c)) y déjalo explícito». La generadora nominal es max(0,−.038434071244996953+.077c). Se preserva el escenario pendiente previo como historial, no como estado vigente. La preparación se autoriza, no se congela el diseño confirmatorio ni se autoriza plan/cohorte.

LP5,c=.40: recta−.0076340712449969525→0; WD5,c=.438:−.0047080712449969545→0. LP4/WD4,c=.50: .00006592875500304601, positivo,sin truncar,casi cero. La curva es lineal a tramos,no lineal en todo el rango.

La pendiente MCO determinista después del truncamiento es LP=.06495278262015627 y WD=.0699508052937943. Ambas son menores que.077. WD cubre un rango menor(.426 frente a.464),pero eso no significa que su pendiente sea menor: es mayor en estos seis puntos. El contraste beta_efectiva×rango es .0297990431 en WD y .0301380911 en LP. No se prejuzga cuál tendrá menor potencia ni se afirma conservadurismo universal; se reporta la sensibilidad empírica del modelo.

La truncación hace no negativos los objetivos de varianza explicada de este generador. No se afirma que todo D predictivo estimado por un algoritmo tenga que ser no negativo; los D muestrales de las simulaciones se conservan, incluidos negativos. No se truncará el estadístico D de ninguna réplica: solo el objetivo generador.
