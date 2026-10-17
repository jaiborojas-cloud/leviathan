# E11-O — réplica Schur en datos naturales

## Objetivo

E11-O aplica sin reentrenar la atribución de E11-N a dos conjuntos naturales y dos arquitecturas ya existentes:

1. `digits`: red 64→128→10, cuatro repartos, cinco semillas, 900 imágenes independientes por reparto;
2. Wisconsin Breast Cancer: red 30→96→2, cuatro repartos, cinco semillas, 285 casos independientes por reparto.

Se conservaron relevancia de etiqueta verdadera, \(H=I\), \(\rho=10^{-4}\) y escala común por estado

\[
\alpha=\rho\lambda_{\max}(F_{completa},H).
\]

Para ambas redes, de una sola capa oculta, se calculó

\[
G_{completa}=G_{salida}+\Delta G_{oculta\mid salida},
\qquad \Delta G_{oculta\mid salida}\succeq0.
\]

## Resultados con panel completo

### Digits

| Componente | \(D_{real}\) | \(D_{aleatoria}\) | Contraste | Pares positivos | Repartos positivos |
|---|---:|---:|---:|---:|---:|
| Salida | 3.613 | 2.074 | **−1.539** | 0/20 | 0/4 |
| Corrección oculta | 3.227 | 5.192 | **+1.965** | 20/20 | 4/4 |
| Red completa | 3.487 | 3.734 | +0.247 | 13/20 | 2/4 |

La salida y la corrección oculta reproducen exactamente el patrón de E11-N en los veinte pares. En la red completa ambos efectos se compensan: el contraste residual es pequeño y cambia de signo entre repartos. La prueba bilateral de signos sobre cuatro medias de reparto da \(p=0.125\) para salida y corrección, y \(p=0.5\) para la red completa.

### Wisconsin

| Componente | \(D_{real}\) | \(D_{aleatoria}\) | Contraste | Pares positivos | Repartos positivos |
|---|---:|---:|---:|---:|---:|
| Salida | 4.026 | 2.585 | **−1.440** | 6/20 | 0/4 |
| Corrección oculta | 5.195 | 5.561 | +0.366 | 12/20 | 3/4 |
| Red completa | 4.296 | 4.359 | +0.063 | 13/20 | 3/4 |

La salida conserva media negativa y los cuatro repartos negativos. La corrección oculta no ofrece una réplica direccional estable: sus medias de reparto fueron +1.022, +2.614, **−4.362** y +2.189. La red completa queda esencialmente en cero. Las pruebas sobre medias de reparto dan \(p=0.125\), \(0.875\) y \(1.0\), respectivamente.

Por tanto, la hipótesis fuerte «la trayectoria Schur oculta es siempre mayor al memorizar aleatorio» se reproduce en `digits`, pero queda **no confirmada en Wisconsin**.

## Control de subpanel

Se usó un subpanel emparejado de 700 imágenes en `digits` y 240 casos en Wisconsin.

| Datos | Componente | Contraste del subpanel | Sesgo | RMSE | Coincidencia de signo |
|---|---|---:|---:|---:|---:|
| Digits | Salida | −1.278 | +0.261 | 0.433 | 100 % |
| Digits | Corrección oculta | +2.033 | +0.068 | 0.543 | 100 % |
| Digits | Red completa | +0.519 | +0.272 | 0.496 | 75 % |
| Wisconsin | Salida | −1.942 | −0.502 | 0.885 | 100 % |
| Wisconsin | Corrección oculta | −0.805 | −1.171 | 2.119 | 85 % |
| Wisconsin | Red completa | −0.530 | −0.593 | 1.266 | 75 % |

La inestabilidad de Wisconsin se agrava al reducir el panel. Esto confirma que su contraste medio oculto de +0.366 no debe interpretarse como evidencia robusta.

## Una magnitud más estable: participación oculta invariante

La distancia temporal de \(\Delta G\) puede cambiar de dirección entre tareas. E11-O identificó una señal más consistente: la proporción relativa de la métrica completa explicada por la corrección oculta. Se define mediante los autovalores generalizados de \((\Delta G,G_{completa})\):

\[
\boxed{
\eta
=\frac{1}{2}\operatorname{tr}
\left(G_{completa}^{-1}\Delta G_{oculta\mid salida}\right)
}
\]

Como \(0\preceq\Delta G\preceq G_{completa}\), se tiene \(0\leq\eta\leq1\). Además, \(\eta\) es invariante bajo cambios invertibles de coordenadas en el espacio bidimensional de perspectivas, porque es la media de autovalores generalizados.

Medianas con panel completo:

| Datos | Inicial | Final real | Final aleatorio | Pares con \(\eta_{aleatoria}>\eta_{real}\) |
|---|---:|---:|---:|---:|
| Digits | 0.289 | 0.349 | **0.786** | **20/20** |
| Wisconsin | 0.360 | 0.480 | **0.860** | **20/20** |

La diferencia aleatoria menos real de \(\eta\) fue positiva en los **40/40 pares naturales**. También fue positiva en 40/40 al usar los subpaneles: medianas real/aleatoria de 0.320/0.803 en `digits` y 0.219/0.857 en Wisconsin. La menor diferencia individual fue +0.363 en `digits` y +0.145 en Wisconsin con panel completo.

Esto sostiene una afirmación más precisa que el contraste de distancias:

> Después de memorizar etiquetas aleatorias, una proporción mucho mayor de la geometría regularizada total reside en la corrección Schur de la capa oculta que después de aprender etiquetas verdaderas.

La afirmación se refiere a participación métrica en el estado final, no a la longitud de la trayectoria de esa corrección.

## Positividad y controles numéricos

El menor autovalor de todas las métricas y correcciones fue \(4.46\times10^{-4}\); no se realizaron recortes espectrales. Residuos máximos del solucionador:

- `digits`: \(1.00\times10^{-6}\);
- Wisconsin: \(9.98\times10^{-7}\).

Error máximo de carta:

- `digits`: \(2.55\times10^{-7}\) para la corrección oculta y \(7.54\times10^{-8}\) para la red completa;
- Wisconsin: \(2.93\times10^{-7}\) y \(9.67\times10^{-8}\), respectivamente.

Todos permanecen por debajo de la tolerancia iterativa declarada.

## Estado de RIPG

E11-O separa dos afirmaciones que antes podían confundirse:

1. **Trayectoria:** el signo de \(D_{aleatoria}-D_{real}\) para la corrección oculta depende de la tarea; es sólido en `digits` y sintético, pero no en Wisconsin.
2. **Composición del estado final:** la participación invariante \(\eta\) del bloque oculto es mayor bajo memorización aleatoria en los 40 pares naturales, además de los 12 pares sintéticos de E11-N.

La segunda señal es actualmente el resultado empírico más consistente de E11. Sigue condicionada al funcional de relevancia, \(H\), \(\rho\), arquitectura y partición salida/oculta. El número 40 no representa 40 conjuntos de datos independientes: son semillas y repartos dentro de dos tareas.

## Siguiente paso natural

E11-P debe tratar \(\eta_{aleatoria}>\eta_{real}\) como hipótesis principal y comprobar su estabilidad frente a:

- una familia preregistrada de \(\rho\);
- referencias transportables \(H\) alternativas;
- otros pares de parámetros perspectivales;
- particiones ocultas más finas cuando la red tenga varias capas.

Si la desigualdad sobrevive esas variaciones, debe registrarse antes de una nueva réplica en un tercer conjunto natural. Si falla, E11-P identificará exactamente qué elección sostiene la señal.

## Reproducción

Ejecutar los estados de E11-I/K y después `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11o_natural_schur_replication.py`, `python3 e11o_invariant_share.py` y `python3 e11o_plot_results.py`. El paquete incluye código, estados, métricas, contrastes, participaciones invariantes, controles y figura.
