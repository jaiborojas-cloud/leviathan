# E16-B — Cierre de validación instrumental en red nueva sin entrenamiento

**Identidades: PASS. Rango validado independientemente: INCONCLUSIVE.**
Estado global según protocolo: INCONCLUSIVE. Se conservaron las 81 configuraciones,
sin cambiar umbrales, pesos, puntos ni paneles. Diseño congelado en `d05f31b`
antes del código y la ejecución. El usuario autorizó crear esta red nueva tras
constatar la ausencia de checkpoints independientes. No se reutilizó T1/E15/T2-A.

## Qué se ejecutó

Red Bernoulli 2→2→1 con tanh, nueve parámetros, tres estados explícitos no
entrenados y ocho entradas sintéticas con etiquetas por regla fija. Tres paneles,
tres puntos perspectivales y tres composiciones: suma, producto y cuadrática.
Métrica declarada g=F+0.01 H, H=I en carta inicial y transportada al cambiar carta.
Es un estimando regularizado SPD, no el pseudoinverso ideal de Fisher.

[Resumen oficial](results/run_v1/summary.json): **1615 comprobaciones: 1534 PASS,
0 FAIL, 81 INCONCLUSIVE**. Las 1008 comprobaciones de identidades y las 486 de
diferencias finitas pasaron. Los 81 INCONCLUSIVE son exclusivamente la validación
independiente del rango con el criterio congelado.

| Observable | Resultado |
|---|---|
| Máximo error absoluto B directo vs cadena completa | 2.221e−16 |
| Máximo error absoluto ω directo vs cadena | 1.111e−16 |
| Máximo error absoluto de todas las comprobaciones FD | 5.782e−6 |
| Máximo error absoluto FD de B | 5.286e−7 |
| Máximo error h entre cartas del modelo | 6.662e−15 |
| Máximo residual de admisibilidad de B | 1.372e−16 |
| Condición máxima de g | 43.640 |
| Norma del término mixto, producto | 0.07545 a 0.73468 |
| Norma del término mixto, cuadrática | 0.10667 a 0.46832 |
| Rango autodiff de suma/producto/cuadrática | 2 en 81/81 configuraciones |
| Rangos que cumplen validación FD congelada | 0/81 |

Los términos mixtos son no nulos para producto y cuadrática. Omitirlos produce
errores en B de hasta 0.47161 y 0.27394, respectivamente. Su presencia no implica
cambio de rango: aquí no se observó diferencia respecto de la suma mediante
autodiff. No se confirma una hipótesis empírica de reorganización del rango.
Los paneles dieron el mismo rango autodiff; esto es sensibilidad descriptiva
sobre paneles fijados, no estimación de incertidumbre poblacional.

## Por qué el rango permanece inconcluso

El criterio exigía error FD de B≤τ/10, con τ=1e−8 max(1,s_max(B L)), C=L Lᵀ.
Los errores centrales son O(10⁻7), mayores que ese umbral, aunque cumplen la
tolerancia de derivadas. Al reducir el paso a la mitad, los errores de B caen
por factores 3.9953–4.0026 (mediana 3.99998), compatibles con truncamiento de
segundo orden. No parece un fallo de la regla de cadena ni mal condicionamiento,
pero esta observación no permite cambiar retrospectivamente el criterio.

No hay valores singulares en la banda ambigua congelada, pero la confirmación
FD adicional exigida tampoco pasa. El rango de autodiff se conserva como
descriptor: no se promociona a resultado certificado por el mero gap espectral.
El criterio compara error de B con un umbral de B L como compuerta operacional;
no constituye una cota rigurosa de perturbación espectral transportada por L.

## Geometría verificada

- Cartas invertibles en parámetros y perspectivas: mismo tensor tras transporte;
  no se reinicia H=I en la carta nueva.
- Restricción p=(t,2t): acuerdo entre derivación directa y pullback.
- Agregación π=x+y para S_ag=(x+y)A: tensor básico, dirección vertical nula,
  independencia de representante y descenso a hbar=dθAᵀC dθA.
- π=x para S₁: dirección vertical de norma positiva en las nueve combinaciones
  estado/panel; no existe descenso tensorial de ese h a q=x.
- Admisibilidad puntual respecto al Fisher del mismo panel: residuos pequeños.
  Rango de R de 8 en P0 y 4 en P1/P2; no se certifica rango constante en un abierto.

## Reproducción y límites

[Checks](results/run_v1/checks.csv), [espectros](results/run_v1/spectra.csv),
[paneles](results/run_v1/panel_sensitivity.csv), [kernel](results/run_v1/kernel.csv),
[descriptivos](results/run_v1/descriptive.json), [entorno](results/run_v1/environment.json)
y [recursos](results/run_v1/resources.json). Tiempo del ejecutor ≈1.630 s,
memoria máxima registrada 32184 KiB; cero pasos de entrenamiento.
No se generaron figuras: las tablas bastan para estos controles.

La ejecución valida instrumentación bajo las elecciones declaradas, no aprendizaje,
predicción, emergencia, una métrica canónica ni la utilidad de la composición.
No se descartaron estados ni se hicieron ajustes tras ver resultados. No hubo
excepciones ni correcciones de implementación en esta corrida.

## Siguiente paso concreto, aún no ejecutado

Antes de ampliar redes o entrenar, preparar otro protocolo instrumental para
resolver la precisión de rango: por ejemplo, derivadas numéricas de mayor orden
o una referencia analítica independiente del grafo autodiff, con cotas de error
transportadas por C. Congelar el nuevo método antes de ejecutarlo; usar un
identificador/corrida nuevos, conservar este INCONCLUSIVE y separar diagnóstico
post hoc de cualquier validación futura. No está justificado saltar a un estudio
predictivo mientras esa compuerta instrumental siga sin resolución.

## Incidencia de verificación y corrección

El primer verificador exigía igualdad byte a byte incluso de la duración medida
en la fila `tiempo` de checks.csv. Falló por esa única fila; las otras 1614
coincidieron exactamente en una réplica diagnóstica. Se preservan el código
fallido en el commit `472040d` y [las diferencias observadas](results/verification_v1_diagnostic.json).
Se corrigió sólo el verificador: cinco tablas/reportes se comparan byte a byte,
1614 checks se comparan exactamente y la duración se valida contra el presupuesto,
sin exigir los mismos segundos. No se modificaron salidas ni criterios científicos.
