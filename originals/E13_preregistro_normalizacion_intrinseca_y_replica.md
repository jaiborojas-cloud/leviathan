# E13 — prerregistro de normalización intrínseca y réplica externa

**Estado:** protocolo propuesto, previo a resultados.  
**Punto de partida:** cierre de E12, 23 de septiembre de 2026.

## Pregunta central

¿La mayor magnitud y energía curvatural observada bajo etiquetas reales frente a aleatorias persiste cuando las comparaciones se realizan sobre vecindarios de igual tamaño intrínseco y se replica en una tarea y arquitectura nuevas?

## Hipótesis primaria

Para pares con el mismo reparto, inicialización, panel y protocolo de entrenamiento,

\[
\delta_K=|K_{\rm true}(P_0)|-|K_{\rm random}(P_0)|.
\]

La hipótesis primaria es

\[
\operatorname{median}(\delta_K)>0.
\]

El signo de \(K\) no es hipótesis primaria: E12 mostró que depende de la tarea y de la región.

## Hipótesis secundaria espacial

Sobre una bola geodésica de radio intrínseco fijo \(r\), o una región ajustada a área intrínseca fija \(A_*\), definir

\[
\mathcal E_K(\Omega)=
\frac{1}{\operatorname{Area}_G(\Omega)}
\int_\Omega K(P)^2\,dA_G.
\]

Contrastar de forma pareada

\[
\mathcal E_K^{\rm true}>\mathcal E_K^{\rm random}.
\]

La integral no normalizada se conservará como descriptivo, no como estimando primario, porque mezcla intensidad curvatural y área.

## Coordenadas y regiones intrínsecas

En cada estado, usar en primer orden coordenadas blanqueadas alrededor de \(P_0\),

\[
q=G(P_0;\theta)^{1/2}(P-P_0),
\]

y verificar la región mediante distancias geodésicas numéricas. Las comparaciones principales emplearán el mismo radio intrínseco \(r\); el análisis de sensibilidad usará dos radios adicionales fijados antes del cómputo final. Para holonomía, los lazos se elegirán por igual área intrínseca, no por igual lado coordenado.

## Parámetros congelados

- Familia no lineal de E12-B y rasgos de perspectiva fijados antes de entrenar.
- Referencia tensorial principal \(H=I\) en la carta declarada, con su transporte covariante en controles de carta.
- Regularización principal \(\rho=10^{-4}\); sensibilidad secundaria en \(10^{-5}\) y \(10^{-3}\).
- Mismos paneles Fisher dentro de cada par true/random.
- Mismos repartos e inicializaciones dentro de cada par.
- Criterio de memorización y presupuesto de entrenamiento idénticos entre condiciones.
- Todos los fallos numéricos, exclusiones y singularidades se registrarán antes de agregar resultados.

## E13-A — compuerta metodológica

1. Implementar distancia geodésica local y construcción de bolas intrínsecas.
2. Comprobar invariancia de \(K\), \(dA_G\), \(\mathcal E_K\) y flujo de curvatura bajo una carta no ortogonal.
3. Validar áreas y distancias en plano y esfera.
4. Fijar radios, malla, tolerancias, semillas y criterio de éxito antes de E13-B.

**Criterio de paso:** error de invariancia y de autoensayos por debajo de las tolerancias de E12-C/E, y regiones comparables sin degeneración de \(G\).

## E13-B — reanálisis interno

Reanalizar digits y Wisconsin:

- \(|K(P_0)|\) por los 40 pares ya definidos;
- \(\mathcal E_K\) sobre bolas de igual radio intrínseco;
- fracción de área con \(K>0\), como descriptivo;
- holonomía y flujo de curvatura para lazos de igual área intrínseca;
- relación entre expansión métrica, \(\eta\) y energía curvatural.

El objetivo es decidir si la separación de E12-D sobrevive al eliminar el confusor de escala/área.

## E13-C — nueva tarea y arquitectura

Réplica propuesta, reproducible sin descarga externa:

- conjunto **Wine** de scikit-learn;
- arquitectura MLP \(13\to64\to32\to3\);
- múltiples repartos estratificados y semillas;
- condiciones true/random pareadas;
- entrenamiento hasta el mismo criterio preregistrado;
- panel Fisher independiente del panel usado para construir la perspectiva.

La segunda capa oculta permite atribución por bloques y comprobar si la señal depende de profundidad. Si se adopta más adelante un conjunto mayor, deberá tratarse como réplica adicional, no como sustitución retrospectiva.

## E13-D — decisión de réplica

Resultados principales:

1. signo y tamaño de la mediana pareada de \(\delta_K\);
2. proporción de pares con \(\delta_K>0\);
3. intervalo por bootstrap de pares;
4. contraste pareado por permutación o Wilcoxon, declarado antes de ejecutar;
5. réplica secundaria de \(\mathcal E_K^{\rm true}>\mathcal E_K^{\rm random}\).

**Éxito fuerte:** dirección positiva en los tres conjuntos y evidencia pareada agregada compatible con el umbral preregistrado.  
**Éxito parcial:** réplica agregada con heterogeneidad explícita entre tareas.  
**Fallo informativo:** desaparición o inversión tras normalización intrínseca o en la tarea nueva.

## E13-E — mecanismo por capas, exploratorio

Estimar contribuciones de salida, capa oculta 2 y capa oculta 1 mediante complementos de Schur a escala común. Relacionar:

\[
\eta_{\rm capa},\qquad
\operatorname{Area}_G,\qquad
|K(P_0)|,\qquad
\mathcal E_K.
\]

La pregunta exploratoria es si la mayor participación oculta bajo random coincide con expansión métrica y aplanamiento intrínseco. Una asociación no se interpretará como mecanismo causal.

## Decisiones que no se cambiarán después de ver resultados

- La hipótesis primaria usa \(|K|\), no el signo de \(K\).
- La unidad inferencial es el par reparto–semilla, no cada punto de la malla.
- Las regiones principales tienen igual radio o área intrínseca.
- \(\eta\) y el área son covariables descriptivas, no sustitutos de curvatura.
- La holonomía permanece como control derivado.
- No se afirmará predicción de generalización ni causalidad sin un ejercicio específico posterior.
