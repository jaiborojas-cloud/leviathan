# Cómo reconstruir el testigo de un quiebre

`rho1` en las tablas significa **hatρ1**, mínimo de candidatos validados de
esta búsqueda finita. No significa el mínimo global sobre todos Q,u. El
candidato elegido y el basal se conservan con componentes segmento, cola
hasta U y cota del resto. `quad_error` es un estimador, no un intervalo riguroso.

La curva física empieza en P0=0. `Q1_P,Q2_P` son las coordenadas del quiebre,
y `u1_P,u2_P` representan la dirección final. `q1,q2` son las coordenadas
acotadas BQ, no las respuestas a las preguntas Q1/Q2. Los índices originales
del soporte asintótico y sus probabilidades límite están en la misma fila.

## Direcciones exactas de arista

Un empate exacto y uno casi exacto tienen extremos distintos. Para una rama
de arista, el testigo se define por su **arista algebraica**, no por interpretar
los decimales de u como si fueran coordenadas exactas independientes.
Del soporte original elíjanse dos índices con rasgos distintos f_i,f_j.
Sea Δ=f_j−f_i. La dirección exacta es proporcional a(Δ2,−Δ1), con signo
hacia el soporte dominante. Las entradas f son los floats archivados promovidos
exactamente; esa fórmula define el empate. La normalización positiva sólo
reparametriza la misma semirrecta. El cálculo MP80 aplica esta construcción;
los decimales de u son su representación aproximada para inspección.
En triángulos hay nueve duplicados por vértice: no escoger dos filas iguales.

Para una rama genérica, u es el vector físico almacenado y el máximo de fu
es único. La cola incluye su transición tardía hacia ese vértice. Los sectores
explorados excluyen márgenes angulares fijados; esa restricción sólo limita
la búsqueda, nunca convierte su mínimo en uno global.

## Extremo, cola y agrupación

Para Q fijo, b=fQ y S=argmax(fu), el límite es exp(b_i)/Σ_Sexp(b_j) en S,
y0 fuera. Nunca se usa el umbral de carta150 como llegada al borde. La suma
de longitud integrada hasta U y cota analítica del resto aproxima desde arriba
la longitud completa, dentro de los errores numéricos documentados.

La agrupación de rasgos idénticos es algebraica: si E reparte la probabilidad
de cada grupo entre sus componentes, M_grupo=EᵀME. Los offsets log(n_grupo)
conservan las multiplicidades. MP agrega la M original a80 dígitos; no utiliza
sólo una factorización float aproximada. Se contrasta además la velocidad con
J de geometry.py original intacto. Ninguna agrupación selecciona estados.

## Archivos

`results/run_v1/candidates.csv`: candidato, origen grid/optimizer/base, q,θ,
soporte de grupos, longitud quad, error, avisos, cortes, límite y contraste MP.
`optimizers.csv`: todos los estados nativos, incluidos límites y no convergentes.
`arrays.csv`: nombres, formas y SHA de .npy externos. `fast_evaluations` tiene
columnas[rama,q1,q2,θ,L_rápida]; no es una tabla de longitudes validadas.
`winner_profile` contiene[tipo,parámetro,P1,P2,velocidad_métrica,a1..a27],
tipo0=segmento,1=cola hasta U. La llegada al infinito es el extremo separado,
no la última muestra finita. Los cuatro arrays de ρ0 conservan la rejilla basal.

Las respuestas reales de AG sólo se usan para evaluar los40 triángulos.
AF mantiene d_borde UNKNOWN. El coste total incluye la búsqueda contemporánea
de ρ0, la búsqueda de quiebres, validaciones quad/MP y archivo del testigo;
se conserva el coste incremental. Las escalas son emparejadas: no hay p-valores
de80 réplicas independientes. No se ejecutan geodésicas en AH ni datos T2.
