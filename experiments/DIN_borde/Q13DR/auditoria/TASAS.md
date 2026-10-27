# Tamaño y potencia sintéticos — parámetros nominales completos

**No se observa inflación global sobre5% de falsos MODULA en los nulos
independientes auditados. Sí se observa potencia de equivalencia muy baja.**
Se completaron1.400 réplicas, semillas prefijadas, **5.000 permutaciones y2.000
bootstrap en cada réplica**. Dos procesos, un hilo BLAS; tiempo906.65 s para las
celdas, más los controles. No se entrenó ni se usó un piloto/cohorte real.

## Nulo principal: D poblacional constante .02 en los seis niveles

Ruido normal independiente entre niveles; X/L compartidos por split. c por nivel
fijada en [.86,.70,.61,.54,.42,.36], con compuerta válida. Los valores d_l son
efectos poblacionales condicionales del generador, no D_CV finitos idénticos:
precisamente se deja fluctuar D_l con el ruido. Las seis Y no son copias.

| N splits ×5 | Réplicas | L0 PASS | Falsos MODULA globales | IC95 Wilson | NO_MODULA global | IC95 Wilson |
|---:|---:|---:|---:|---:|---:|---:|
|200|400|385|8/400 =2.00%|[1.02%,3.90%]|0/400 =0%|[0%,.95%]|
|400|400|400|10/400 =2.50%|[1.36%,4.54%]|0/400 =0%|[0%,.95%]|

Condicionado a L0 PASS: falsos MODULA8/385=2.08%, IC95[1.06%,4.05%] en N200;
10/400=2.50% en N400. NO_MODULA sigue siendo0/385 y0/400; sus límites superiores
son .99% y .95%. No confundir los denominadores globales y condicionados.
Los demás resultados son NO_CONCLUYENTE377/400 y390/400; en N200 hay15/400
INCONCLUSIVE_SIN_SENAL_CONTROL. Los conteos suman exactamente cada celda.

El criterio MODULA usa límite inferior de IC95 >0: bajo nulo regular simétrico
es idealmente una cola de2.5%, no5%. Las tasas observadas son compatibles con eso.
No es una certificación para toda distribución, faltantes o dependencia.

**NO_MODULA bajo β=0 no es falso positivo: es potencia de equivalencia.** Aquí
es0%, muy lejos de .8 requerido por el diseño. Sólo se auditaron200 y400, no se
afirma un teorema para todos los tamaños intermedios. Copiar seis veces el mismo
resultado como prueba lógica no reproduce este nulo con ruido independiente.
La potencia del protocolo debe declarar/justificar la dependencia entre niveles
y explorar su sensibilidad; un resultado bajo ruido compartido no es universal.

## Alternativas y nulo sin señal de control

| Escenario, N400 | Réplicas | L0 PASS | MODULA global | NO_MODULA global | Lectura |
|---|---:|---:|---:|---:|---|
|β=0, d=0|200|6|0/200|4/200|194/200 paran por ausencia de señal en L0|
|β=+.03, d central=.02|200|200|74/200 =37%|0/200|Potencia MODULA IC95[30.61%,43.88%]|
|β=−.03, d central=.02|200|199|0/200|0/200|199 NO_CONCLUYENTE;1 sin señal de control|

En las alternativas ±.03, fuera de la banda [−.02,.02], NO_MODULA sí sería una
equivalencia falsa: **0/200 en ambas**, límite superior Wilson95=1.88% global.
Para β negativo, MODULA también sería un error de dirección: no se observó.
La alternativa+.03 es un escenario de auditoría, no la curva más intensa del
escenario(a) del diseño; no se sustituye su cálculo de potencia preentrenamiento.

En el nulo d=0, sólo seis controles pasan: entre ellos NO_MODULA4/6 y MODULA0/6.
El IC95 de MODULA condicionado a esos seis llega a39.03%: **no hay precisión
para sostener una cota condicional de5% allí**, aunque la tasa global0/200 tenga
límite superior1.88%. Seleccionar por control PASS cambia el denominador.

## PERSISTE/DESAPARECE: conteos globales, conservando la compuerta

| Escenario | PERSISTE | DESAPARECE | INDETERMINADO | No evaluado por L0 |
|---|---:|---:|---:|---:|
|null_N200|378/400|0/400|7/400|15/400|
|null_N400|400/400|0/400|0/400|0/400|
|zero_N400|0/200|5/200|1/200|194/200|
|positive_N400|199/200|1/200|0/200|0/200|
|negative_N400|199/200|0/200|0/200|1/200|

El orden de las reglas del extremo coincide con el diseño: PASS implica PERSISTE
antes de mirar el límite .006. DESAPARECE es una clasificación estadística bajo
esa tolerancia, no prueba de D exactamente0. En la alternativa positiva el d de
L5=.01335 y aparece1/200 DESAPARECE: un error finito posible, no por sí solo un
bug. Tasas e intervalos globales/condicionados completos en los CSV enlazados.

## Motor independiente y límites prácticos

Se usa FWL para permutaciones y OLS ponderado por multiplicidades para el
bootstrap. Respeta folds originales y centrado por copia. Se contrasta con
primaria C1 y D_punto Q13: máximo error D4.45e-16, bootstrap3.11e-15; p idéntica.
Un control lleva5.000 permutaciones y los otros199; el Monte Carlo completo usa
las5.000 nominales en todas sus réplicas. β y sus decisiones usan las funciones
auditadas. En las celdas c es constante por nivel, por lo que su mediana de
bootstrap es exactamente esa constante; la traza con c variable comprueba el
recálculo real del código. No se simplificaron los intervalos a errores estándar.

No se evalúan aquí todas las correlaciones entre niveles, heterocedasticidades,
faltantes o relaciones no gaussianas. Los defectos de casos mínimos tampoco
están presentes en estas tablas completas regulares. No trasladar las tasas a
esos casos ni a Wine/C2/Q13 reales. Se preservan todas las réplicas, incluidos
resultados no concluyentes; no hubo fallos del motor ni se descartó ninguna.

[Configuración y semillas](config.json) · [protocolo previo](DESIGN_FROZEN.md) ·
[resumen nominal](results/monte_carlo_v1/summary.json) · [controles](results/monte_carlo_v1/controls.json) ·
[tasas con Wilson](results/rates.csv) · [extremos con Wilson](results/endpoint_rates.csv).
