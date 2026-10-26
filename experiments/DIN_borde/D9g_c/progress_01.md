# DIN-D9g-c: controles antes del análisis de las tablas reales

Diseñod5e694a → códigodb6687d → controles.
Negativos c=q0² y c=q1q2: D_BR=0, alias10/10bloques, como establece el estimando
residual fuera del diccionario. Positivo grande D_BR=.147151,p=.001; pequeño
(D_oráculo=.02) D_BR=.029237,p=.001; ambos detectados con signo positivo estable.
Una realización pequeña detectada no estima potencia ni garantiza ausencia real.

Pipeline vectorizado vs directo: todos los1.000D, error máximo7.77e-16, p idéntica.
Validación sin caché de mu/sigma/score/selecciónλ en observado y primeras2permutaciones
por bloque: PASS. Guarda impide C2/T2/DIN-C1 antes de lectura. No se midieron nuevos
resultados BR en G3 todavía. Este commit conserva controles antes del análisis.
