# Proyecto Leviathan / RIPG — estado persistente hasta E15-B1
**Fecha:** 24 de septiembre de 2026

## Estado general
Leviathan estudia la geometría de perspectivas inducida por relevancia (RIPG) sobre redes neuronales. La construcción vigente usa:

\[
P\mapsto S_P\mapsto \omega_P=d_\theta S_P,
\]

con admisibilidad:

\[
\omega_P\in(\ker F_\theta)^\circ,
\qquad
B(P)K_\theta=0,
\]

y métrica regularizada:

\[
G_\rho(P;\theta)
=
B(P)
\left(F+\rho\lambda_{\max}I\right)^{-1}
B(P)^T,
\qquad \rho=10^{-4}.
\]

Desde E14, la curvatura se evalúa sobre el **campo exacto** \(G_\rho(P)\), no mediante jets regionales.

---

# E15-A — atribución mecanística por bloques

## Arquitectura Wine
\[
13\to64\to32\to3
\]

Parametrización identificable con logits reducidos:

- \(L_1=(W_1,b_1)\): 896 parámetros.
- \(L_2=(W_2,b_2)\): 2080 parámetros.
- \(L_3=(W_3,b_3)\) reducido: 66 parámetros.
- Total identificable: 3042.

Se evaluaron los siete subconjuntos no vacíos:

\[
L_1,\ L_2,\ L_3,\ L_1L_2,\ L_1L_3,\ L_2L_3,\ L_1L_2L_3.
\]

## E15-A3 — auditoría final
Se reutilizó la auditoría congelada de E13-A:

\[
128\times64,\ 256\ {\rm RK4}
\quad\text{vs}\quad
256\times128,\ 512\ {\rm RK4},
\]

con:

\[
A_*=0.02,
\qquad
\text{error relativo de área}\le10^{-6},
\qquad
|\Delta C_A|<0.5\%.
\]

Resultado:

\[
7/7
\]

campos aprobaron convergencia.

Valores finales de \(C_{0.02}\):

\[
L_1=391.979,
\quad
L_2=384.333,
\quad
L_3=477.292,
\]

\[
L_1L_2=386.815,
\quad
L_1L_3=391.098,
\quad
L_2L_3=393.859,
\]

\[
C_A({\rm full})=387.907.
\]

Mayor cambio entre mallas:

\[
0.286\%
\]

para \(L_3\).

## Shapley final E15-A

\[
\phi_1=114.724,
\qquad
\phi_2=112.281,
\qquad
\phi_3=160.903.
\]

Participaciones absolutas:

\[
29.58\%,\quad28.95\%,\quad41.48\%.
\]

Concentración:

\[
H_\phi=0.34331,
\]

muy próxima al mínimo uniforme:

\[
1/3=0.33333.
\]

Interpretación vigente del piloto:

\[
\boxed{\text{la organización curvatural es distribuida}}
\]

con peso moderadamente mayor en la salida.

Eficiencia Shapley:

\[
\sum_i\phi_i=C_A({\rm full})
\]

con error aproximadamente:

\[
5.7\times10^{-14}.
\]

Interacciones:

\[
I_{12}\approx-389.50,
\]

\[
I_{13}\approx-478.17,
\]

\[
I_{23}\approx-467.77.
\]

Interpretación: fuerte **no-aditividad/redundancia geométrica**. No se interpreta como causalidad ni inhibición.

Resultado conceptual:

\[
\boxed{
\text{capacidad curvatural aislada}
\neq
\text{contribución marginal dentro de la red}
}
\]

---

# E15-B — comparación mecanística true vs random

## Protocolo Wine recuperado
- 8 particiones: semillas 1000–1007.
- 5 inicializaciones: semillas 2000–2004.
- 40 pares true/random.
- Random labels: semilla \(3000+10s+j\).
- Minibatches emparejados: semilla \(4000+10s+j\).
- Adam, learning rate 0.006.
- Batch 64.
- Máximo 20 000 pasos.
- Checkpoint cada 25 pasos.
- Parada en primer checkpoint con accuracy objetivo \(\ge99\%\).
- True: 25 pasos en 40/40 estados.
- Random: 75–125 pasos.
- Panel geométrico: validación, 27 ejemplos.
- Perspectivas: variables Wine 0 y 1, estandarizadas con entrenamiento.
- \(\rho=10^{-4}\), \(H=I\).

---

# E15-B1 — geometría central exacta por bloques

Se calcularon los siete subconjuntos para los 80 estados y se obtuvo \(K(P_0)\) exacto mediante autodiferenciación.

## Curvatura completa central

Medianas:

\[
|K_0|_{\rm true}=5.89106,
\]

\[
|K_0|_{\rm random}=5.73918\times10^{-4}.
\]

Contraste pareado:

\[
\boxed{
|K_0|_{\rm true}>|K_0|_{\rm random}
\text{ en }40/40\text{ pares}
}
\]

y 8/8 medias de partición en la misma dirección.

Medianas por subconjunto:

### True
\[
L_1=6.05462,
\quad
L_2=5.80319,
\quad
L_3=5.92746,
\]

\[
L_1L_2=6.00665,
\quad
L_1L_3=5.90417,
\quad
L_2L_3=5.75693,
\quad
full=5.89106.
\]

### Random
\[
L_1=5.84\times10^{-4},
\quad
L_2=7.43\times10^{-4},
\quad
L_3=4.07\times10^{-3},
\]

\[
L_1L_2=5.65\times10^{-4},
\quad
L_1L_3=5.79\times10^{-4},
\quad
L_2L_3=8.11\times10^{-4},
\quad
full=5.74\times10^{-4}.
\]

---

# Shapley central E15-B1

Medianas true:

\[
\phi_1=2.27701,
\qquad
\phi_2=1.96185,
\qquad
\phi_3=1.95762.
\]

Medianas random:

\[
\phi_1=-2.74148\times10^{-4},
\]

\[
\phi_2=-2.24277\times10^{-4},
\]

\[
\phi_3=1.37079\times10^{-3}.
\]

Diferencias true-random:

- \(\phi_1>0\) en 40/40 pares.
- \(\phi_2>0\) en 40/40 pares.
- \(\phi_3>0\) en 40/40 pares.
- 8/8 medias de partición positivas en los tres casos.

## Participaciones Shapley

Medianas true:

\[
s_1=0.34556,
\qquad
s_2=0.34079,
\qquad
s_3=0.317441.
\]

Medianas random:

\[
s_1=0.231963,
\qquad
s_2=0.187995,
\qquad
s_3=0.589176.
\]

Por tanto:

\[
\boxed{
\text{true: organización distribuida}
}
\]

mientras:

\[
\boxed{
\text{random: curvatura residual relativamente concentrada en salida}
}
\]

Para \(s_3\):

\[
s_3^{true}<s_3^{random}
\]

en 37/40 pares y 8/8 particiones.

## Concentración Shapley

\[
H_\phi^{true}=0.338206,
\]

\[
H_\phi^{random}=0.434913.
\]

Contraste:

\[
\boxed{
H_\phi^{true}<H_\phi^{random}
}
\]

en 39/40 pares y 8/8 medias de partición.

Como descriptivo exploratorio, 8/8 signos iguales implican una prueba bilateral de signos:

\[
p=0.0078125.
\]

No se considera confirmatoria porque la hipótesis de concentración emergió durante E15.

---

# Control independiente de Shapley

Se normalizaron directamente los singletons:

\[
q_i=
\frac{|K_{L_i}|}
{|K_{L_1}|+|K_{L_2}|+|K_{L_3}|}.
\]

Medianas true:

\[
q_1=0.338001,
\qquad
q_2=0.339260,
\qquad
q_3=0.323676.
\]

Medianas random:

\[
q_1=0.113166,
\qquad
q_2=0.113581,
\qquad
q_3=0.763676.
\]

Concentración:

\[
H_{\rm singleton}^{true}=0.334935,
\]

\[
H_{\rm singleton}^{random}=0.611520.
\]

Contraste:

\[
H_{\rm singleton}^{true}<H_{\rm singleton}^{random}
\]

en 39/40 pares y 8/8 particiones.

Así, la diferencia de distribución **no depende de Shapley**.

---

# Interacciones E15-B1

Medianas true:

\[
I_{12}\approx-5.85117,
\]

\[
I_{13}\approx-5.94503,
\]

\[
I_{23}\approx-5.98895.
\]

Medianas random:

\[
I_{12}\approx-8.03\times10^{-4},
\]

\[
I_{13}\approx-4.07\times10^{-3},
\]

\[
I_{23}\approx-4.01\times10^{-3}.
\]

Los contrastes true-random tienen la misma dirección en 40/40 pares y 8/8 particiones.

Interpretación vigente:

\[
\boxed{
\text{true muestra mucha mayor no-aditividad geométrica entre bloques}
}
\]

sin inferencia causal.

---

# Interpretación científica vigente

Los resultados actuales sugieren la siguiente separación:

\[
\text{random}
:
\quad
\text{mayor participación paramétrica}
+
\text{curvatura muy pequeña}
+
\text{geometría residual concentrada en salida}
\]

frente a:

\[
\text{true}
:
\quad
\text{menor participación global}
+
\text{curvatura mucho mayor}
+
\text{organización distribuida a través de la profundidad}.
\]

En forma compacta:

\[
\boxed{
\text{cantidad de participación}
\neq
\text{cantidad de curvatura}
\neq
\text{arquitectura de la curvatura}
}
\]

y el hallazgo mecanístico candidato es:

\[
\boxed{
\text{el aprendizaje estructurado distribuye la organización geométrica}
}
\]

\[
\boxed{
\text{a través de la profundidad, mientras la memorización deja}
}
\]

\[
\boxed{
\text{una geometría casi plana y relativamente concentrada en la salida.}
}
\]

Esto sigue siendo descriptivo/exploratorio, no causal.

---

# Siguiente etapa: E15-B2

Pregunta:

\[
\boxed{
\text{¿sobrevive la diferencia de distribución true/random}
}
\]

\[
\boxed{
\text{cuando Shapley y concentración se calculan con }
C_{0.02}
\text{ sobre discos geodésicos exactos?}
}
\]

E15-B2 debe usar el campo exacto \(G_\rho(P)\), regiones geodésicas de área 0.02 y el protocolo numérico validado en E15-A3. No se deben reintroducir jets regionales.

Estimandos prioritarios:

\[
C_A(full),
\quad
(\phi_1,\phi_2,\phi_3),
\quad
H_\phi,
\quad
s_3,
\quad
I_{12},I_{13},I_{23}.
\]

El objetivo es falsar o confirmar regionalmente la estructura central observada en E15-B1.
