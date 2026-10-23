# Resultado E16-AB

**INCONCLUSIVE global**, con progreso parcial: cinco de ocho curvas cuadráticas
alcanzan KKT físico≤1e-7 con racha y validación final; tres agotan60 evaluaciones.
Los cuatro controles C0 pasan INITIAL_CONTROL sin llamar a SciPy. No se amplió
el presupuesto, no se eligieron mejores puntos anteriores ni se excluyeron fallos.

Los doce diagnósticos espectrales pasan. Hay cuatro testigos MP negativos,
todos en curvas de528 segmentos que cumplen el criterio estricto y son
interiores: curvatura negativa numérica compatible con estacionariedad aproximada
más estricta. No es confirmación independiente ni certificado de silla exacta.
La Q1/scaled/132 (malla actual264) también cumple primer orden y tiene mínimo
restringido positivo numéricamente, sin certificado de mínimo.

## Universo completo

| Fuente S | Segmentos AB | Aceptados | nfev | KKT final | Mínimo masa | Primer orden | Testigo MP negativo |
|---|---:|---:|---:|---:|---:|---|---|
| Q0/reference/132 | 264 | 42 | 60 | 1.272388e-07 | 9.1733667e-05 | INCONCLUSIVE | No |
| Q0/reference/264 | 528 | 6 | 11 | 4.915622e-08 | -0.020670288 | PASS | Sí |
| Q0/scaled/132 | 264 | 42 | 60 | 1.47963e-07 | 5.4011967e-05 | INCONCLUSIVE | No |
| Q0/scaled/264 | 528 | 18 | 26 | 8.776794e-08 | -0.016377354 | PASS | Sí |
| Q1/reference/132 | 264 | 43 | 60 | 1.082793e-07 | 7.6431153e-05 | INCONCLUSIVE | No |
| Q1/reference/264 | 528 | 40 | 54 | 9.44921e-08 | -0.0092324062 | PASS | Sí |
| Q1/scaled/132 | 264 | 16 | 20 | 9.612074e-08 | 5.5626604e-05 | PASS | No |
| Q1/scaled/264 | 528 | 15 | 21 | 9.013005e-08 | -0.014273067 | PASS | Sí |
| C0/reference/132 | 264 | 0 | 0 | 2.942449e-36 | -3.1879707e-07 | PASS | No |
| C0/reference/264 | 528 | 0 | 0 | 1.176979e-35 | -2.5389269e-06 | PASS | No |
| C0/scaled/132 | 264 | 0 | 0 | 2.942449e-36 | -3.1879707e-07 | PASS | No |
| C0/scaled/264 | 528 | 0 | 0 | 1.176979e-35 | -2.5389269e-06 | PASS | No |

Los tres casos inconclusos son Q0/reference/132, Q0/scaled/132 y
Q1/reference/132. Sus residuos finales son1.27e-7,1.48e-7 y1.08e-7,
respectivamente. Se conserva successFalse/status0 por límite de evaluaciones.
Los cinco éxitos cuadráticos terminan por PHYSICAL_SUSTAINED, con
successFalse/status−2 nativo de least_squares conservado. Los controles tienen
campos nativos vacíos y coste de solver cero: no representan éxitos de SciPy.

9/12 comparaciones son elegibles: cinco cuadráticas y cuatro C0. Las tres
restantes mantienen su espectro como diagnóstico del punto devuelto, sin
promoverse a estacionarias. Todos los puntos son interiores y las pruebas
bilaterales pequeñas son factibles. No se resolvió un cono crítico de borde.

## Controles y recursos

759 comprobaciones:756 PASS y3 INCONCLUSIVE, exactamente los tres KKT finales
insuficientes.234 monitores:40 descartes AD SCREENED_NONSTATIONARY y194
auditorías MP completas. Los descartes AD no se presentan como auditorías MP.
No hay monitores UNVERIFIED ni errores del solver. Cada punto aceptado distinto
cuenta una vez; los gradientes finales se auditan aparte de la racha.
Se archivan9480 componentes de gradiente,4764 vértices,9472 autovalores y24
auditorías direccionales MP; no Hessianas, autovectores ni checkpoints.

Primera corrida: 1629.610065s / 295.710938MiB, dentro de1800s/512MiB.

La tabla de costes separa evaluaciones residuales, Jacobianos/Hessianas y
monitores MP. El caso Q1/reference/264 requiere40 puntos aceptados; el número
de evaluaciones no equivale al coste de gradientes de AA/L-BFGS-B.
Las ocho curvas cuadráticas reducen KKT y norma del gradiente respecto de AA.
Dos aumentan su longitud y seis la reducen: no se usó descenso de L para
filtrar aceptación. Los controles conservan exactamente sus coordenadas; las
diferencias de longitud del orden1e-81 son precisión MP80/120, no movimiento.
Los valores y diferencias por fuente se conservan en comparisons.csv.

## Alcance de la inferencia

El método permite alcanzar el umbral estricto en cinco fuentes donde AA no lo
alcanzó, partiendo de sus puntos finales. No es un ensayo que aísle sólo el
escalado: cambian método, inicio y presupuesto de evaluaciones. No demuestra
superioridad temporal, resolución general del mal condicionamiento o convergencia.
Las curvas, datos y pesos de red son los mismos; no hay evidencia independiente.
C0 conserva curvatura MP casi nula, aunque el mínimo float sea ligeramente negativo.

Los cuatro testigos negativos elegibles persisten en las mallas528 dentro de
este protocolo. Los tres casos inconclusos impiden una conclusión uniforme sobre
todas las fuentes. No certificar mínimos, sillas exactas o geodésicas.

El siguiente problema es distinguir qué direcciones limitan el residuo en los
tres inconclusos y qué relación guardan con el gradiente y el espectro, bajo
otro protocolo prospectivo. No extender o relajar AB retrospectivamente.

[Formulación](THEORY.md) · [Tablas](results/run_v1) · [Figura](figures/trust_region_comparison.svg)
