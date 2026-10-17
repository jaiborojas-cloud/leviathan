# E11-J — regularización explícita de la geometría RIPG

## Objetivo

E11-I mostró que una pseudoinversa obtenida mediante corte espectral discreto cambia materialmente al mover el umbral. E11-J reemplaza ese corte por una familia regularizada que forma parte explícita de la magnitud reportada:

\[
\boxed{
G_\rho
=B\bigl(F+\rho\,\lambda_{\max}(F,H)H\bigr)^{-1}B^T
}
\]

Aquí \(H\) es una referencia positiva definida declarada, \(\lambda_{\max}(F,H)\) es el mayor autovalor generalizado de \(Fv=\lambda Hv\), y \(\rho>0\) es adimensional. Se fijó \(H=I\) en la carta original y se transportó como tensor al cambiar de coordenadas. La comparación principal se declaró antes del cálculo con \(\rho=10^{-4}\) y relevancia de etiqueta verdadera. Se evaluó además \(\rho\in\{10^{-2},\ldots,10^{-8}\}\) y la relevancia uniforme.

## Covariancia de la familia

Para \(\theta=T\phi\),

\[
F_\phi=T^TF_\theta T,\qquad
B_\phi=B_\theta T,\qquad
H_\phi=T^TH_\theta T.
\]

Los autovalores generalizados de \((F,H)\), incluido \(\lambda_{\max}\), no cambian. Por tanto,

\[
B_\phi(F_\phi+\rho\lambda_{\max}H_\phi)^{-1}B_\phi^T
=B_\theta(F_\theta+\rho\lambda_{\max}H_\theta)^{-1}B_\theta^T.
\]

Esta igualdad hace covariante **la familia condicionada a \(H\) y \(\rho\)**. No convierte a \(H\) ni a \(\rho\) en elecciones canónicas de Fisher.

## Diseño

Se reutilizó sin cambios la cuadrícula de E11-I: cuatro repartos estratificados de 897 imágenes de entrenamiento y 900 de evaluación; cinco semillas comunes; 20 pares de redes entrenadas con etiquetas verdaderas o aleatorias; estados iniciales y primeros estados con al menos 99 % de precisión sobre el objetivo. Los observables de relevancia, rasgos perspectivales, subpaneles de 40 y 70 imágenes por clase y emparejamiento permanecieron idénticos. Así, la diferencia entre E11-I y E11-J procede de la regla de inversión de Fisher.

La regularización usa todos los modos de manera continua. En lugar de retener o descartar un modo, su inverso cambia de \(1/\lambda\) a

\[
\frac{1}{\lambda+\rho\lambda_{\max}}.
\]

Con \(\rho=10^{-4}\), el número de condición regularizado es aproximadamente 10 001 en todos los estados examinados.

## Resultado principal: \(\rho=10^{-4}\)

Con las 900 imágenes de evaluación por reparto:

| Magnitud | Resultado |
|---|---:|
| Distancia media, etiquetas verdaderas | 3.588 |
| Distancia media, etiquetas aleatorias | 2.706 |
| Contraste medio \(D_{aleatoria}-D_{real}\) | **−0.881** |
| Pares con contraste positivo | 3/20 |
| Repartos con contraste medio positivo | 0/4 |
| Prueba bilateral de signos sobre cuatro medias de reparto | \(p=0.125\) |

Las medias por reparto fueron −1.075, −0.365, −1.215 y −0.871. El tamaño de cuatro repartos y su solapamiento de imágenes impiden interpretar \(p=0.125\) como confirmación poblacional. El resultado sí demuestra estabilidad descriptiva del signo entre los cuatro repartos examinados bajo el estimando fijado.

## Sensibilidad a \(\rho\)

| \(\rho\) | Contraste verdadero | Pares positivos | Repartos positivos | Contraste uniforme |
|---:|---:|---:|---:|---:|
| \(10^{-8}\) | −0.676 | 5/20 | 0/4 | −6.381 |
| \(10^{-7}\) | −0.774 | 4/20 | 0/4 | −6.158 |
| \(10^{-6}\) | −0.878 | 4/20 | 0/4 | −5.450 |
| \(10^{-5}\) | −0.968 | 3/20 | 0/4 | −4.326 |
| \(10^{-4}\) | −0.881 | 3/20 | 0/4 | −3.162 |
| \(10^{-3}\) | −0.663 | 3/20 | 0/4 | −2.402 |
| \(10^{-2}\) | −0.351 | 5/20 | 1/4 | −2.092 |

La dirección media es negativa en toda la familia examinada para ambos funcionales. Esto contrasta con la inversión producida por el corte duro de E11-I cerca de \(10^{-12}\). La magnitud sigue dependiendo de \(\rho\): entre \(10^{-5}\) y \(10^{-2}\), el contraste verdadero cambia de −0.968 a −0.351. La regularización genera una familia estable en signo dentro de este intervalo experimental, no un único valor intrínseco.

## Convergencia del panel

Para el criterio principal, cada subpanel se compara con las 900 imágenes del mismo reparto, semilla y régimen:

| Imágenes por clase | Contraste medio estimado | Sesgo del contraste | RMSE del contraste | Coincidencia de signo | Error relativo mediano de D | Percentil 90 |
|---:|---:|---:|---:|---:|---:|---:|
| 40 | +0.014 | +0.896 | 1.286 | 47.5 % | 28.5 % | 45.3 % |
| 70 | −0.551 | +0.330 | 0.429 | 92.5 % | 7.7 % | 11.8 % |

Frente al corte duro principal de E11-I, el error mediano/percentil 90 baja de 37.3 %/75.0 % a 28.5 %/45.3 % con 40 por clase, y de 8.4 %/17.7 % a 7.7 %/11.8 % con 70. La mejora es real en esta comparación emparejada. Sin embargo, 40 por clase vuelve a invertir el promedio; la regularización no sustituye un panel suficientemente grande.

## Control de carta

Se aplicó al reparto 0 y semilla 0 el mismo cambio no ortogonal de E11-H, con escalas coordinadas entre 0.01 y 100, transportando \(H\). El error máximo entre métricas del mismo modelo fue:

- \(6.14\times10^{-15}\) para el criterio principal \(\rho=10^{-4}\).
- \(2.34\times10^{-11}\) como máximo sobre los siete valores de \(\rho\), ambos funcionales y los tres estados examinados.

La regularización transportada supera aquí el control numérico de covariancia y evita la inestabilidad del corte extremo observada en E11-H.

## Estado de E11

E11-J resuelve un problema operacional concreto: reemplaza el rango discontinuo por una familia suave, bien condicionada y covariante cuando \(H\) se transporta. Para la familia evaluada, el contraste real/aleatorio conserva dirección negativa y la convergencia del panel mejora.

El resultado sigue condicionado a cuatro elementos declarados: funcional \(S_P\), referencia \(H\), intensidad \(\rho\) y distribución del panel. La regularización asigna geometría mediante \(H\), incluso donde Fisher es degenerada; por ello \(G_\rho\) es un **estimando regularizado de RIPG**, no la métrica canónica del cociente Fisher. En el límite \(\rho\to0\), recuperar la pseudoinversa solo es estable si el soporte admisible de \(B\) y el espectro efectivo están controlados.

El paso natural E11-K es una réplica externa previamente especificada: fijar `true`, \(H=I\), \(\rho=10^{-4}\), tamaños de panel y contraste antes de usar otro conjunto de datos y otra arquitectura. La predicción registrada sería \(D_{aleatoria}<D_{real}\) en promedio, junto con convergencia del error al crecer el panel. Una réplica fallida limitaría la afirmación al benchmark `digits`; una réplica exitosa permitiría empezar a estudiar generalidad.

## Reproducción

Ejecutar `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 e11j_explicit_regularization.py` y `python3 e11j_plot_results.py` después de E11-H/I. El paquete adjunto incluye scripts, tablas, figura y los archivos de E11-I necesarios para localizar los estados ya entrenados.
