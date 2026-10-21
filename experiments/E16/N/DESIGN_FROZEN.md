# E16-N — Protocolo previo a mediciones

Diagnóstico exploratorio del caso h00/0/quadratic y control h00/0/sum.
No confirma una hipótesis nueva con datos independientes. Se conservan Q0, Q1,
C0 de M, sin seleccionar por resultado ni añadir reinicios.

## Intervención y comparaciones

Se fijan nodos t_i=1-(1-i/m)^2, m=32,64,128, anidados y concentrados en t=1.
Mismo dominio, extremos, normal global, corredor |s|≤0,25, longitud y optimizador
que M. Cada linaje parte del camino M32, interpolado a la nueva malla, y se
optimiza en 32/64/128. La interpolación inicial cambia el polígono: se informa
su cambio de longitud y forma; no se exige identidad con M32. Las elevaciones
32→64→128 sí preservan el polígono y deben pasar identidad 1e-12.
No se atribuye causalidad exclusiva a los nodos: cambian también los grados
de libertad físicos y la trayectoria de inicialización del optimizador.

Se comparan: (a) M32/64/128 archivados sin optimizarlos, (b) N32/64/128,
(c) M y N al mismo número de segmentos. Se informa sup|delta s(t)| usando
la unión de nodos: es distancia al mismo parámetro longitudinal.

Además se estima Hausdorff euclídea simétrica entre polígonos en coordenadas
normalizadas (t,s). Esta carta es una isometría de la carta de perspectivas
tras dividir por la longitud de la cuerda; no es distancia intrínseca de h.
No se confunde máximo entre vértices con Hausdorff entre curvas.
Para cada dirección, distancias exactas en float64 de extremos y puntos medios
a TODOS los segmentos destino dan una cota inferior. Cada intervalo fuente
queda acotado superiormente por distancia en su punto medio + media longitud
 del intervalo (propiedad 1-Lipschitz). Se divide el intervalo con mayor cota
hasta brecha ≤1e-5; máximo 200000 divisiones por dirección. Simetrizar por
máximos. Son cotas geométricas numéricas, sin aritmética dirigida ni certificado
riguroso. Preservar inconcluso al agotar presupuesto o solapar el umbral.
Controles: curva idéntica con distinta subdivisión; segmentos paralelos separados
0,02; segmento fuente horizontal frente a V con mismos extremos, cuyo máximo
de distancia es interior y positivo aunque sus vértices coinciden.

## Reglas de evaluación

Se heredan de M precisión 80/120, cuadraturas 16/32/64, SPD Bernstein,
primitiva estable, gradiente AD frente a FD multiprecisión local con pasos
1e-18/1e-22, KKT, límites, presupuestos y tolerancias de config.json.
La referencia archivada usa su intervalo de redondeo de 40 cifras.
Comparaciones M son diagnósticas y no cambian su resultado histórico.
Cada transición N debe pasar longitud ≤1e-3, forma ≤1e-3 y cota superior
Hausdorff ≤1e-3, además de validación de cada camino. Hausdorff con inferior
>1e-3 incumple; intervalo solapado es desconocido. La comparación M/N es
 descriptiva, no condiciona éxito. Global inconcluso si algún linaje o control
no pasa. No se certifican geodésicas, unicidad ni mínimos globales.

Versionar los resultados de la primera corrida incluso si fallan. Reproducir
las tablas científicas byte por byte; tiempos y memoria se informan aparte.
