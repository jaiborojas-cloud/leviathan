# RIPG — contexto vigente y axioma de admisibilidad

**Fecha:** 23 de septiembre de 2026. Esta nota integra el documento histórico E9 compartido por el usuario con el axioma E9-G y el cierre formal de E10–E12. Es el contexto vigente para abrir E13; no reemplaza los datos, informes ni protocolos originales.

## Definición operativa

La variedad de modelos es \(M\), la de perspectivas admisibles es \(\mathcal P\), y una perspectiva \(P\) determina un funcional suave \(S_P:M\to\mathbb R\). Su relevancia es el covector

\[
\omega_P=d_\theta S_P\in T_\theta^*M,\qquad
\Phi_\theta(P)=\omega_P.
\]

Fisher \(F_\theta\) es la geometría estadística base; no elige por sí solo qué observables o costos son relevantes. Cambiar cartas de coordenadas del modelo o de \(\mathcal P\) no es lo mismo que cambiar una perspectiva operativa (observable, medida de evaluación o costo).

## Axioma de admisibilidad perspectival tras E9-G

Sea \(K_\theta=\ker F_\theta\). Se exige

\[
\boxed{\omega_P=d_\theta S_P\in K_\theta^\circ}
\quad\Longleftrightarrow\quad
d_\theta S_P(k)=0\quad\forall k\in K_\theta.
\]

Para la geometría entre perspectivas, con \(B=d_Pd_\theta S\), también

\[
\boxed{B K_\theta=0}
\quad\Longleftrightarrow\quad
d_Pd_\theta S_P(k)=0\quad\forall k\in K_\theta.
\]

Estas condiciones hacen que la relevancia y sus variaciones perspectivales desciendan al dual del cociente identificable

\[
Q_\theta=T_\theta M/K_\theta,\qquad Q_\theta^*\simeq K_\theta^\circ.
\]

La formulación intrínseca vigente es

\[
\boxed{h^{(\theta)}=\Phi_\theta^*(\bar g_{F,\theta}^{-1})},
\]

donde \(\bar g_F\) es la métrica Fisher no degenerada sobre el cociente. En coordenadas compatibles,

\[
\boxed{h=B F^+B^T.}
\]

Para una familia \(S(\theta,p)=\sum_i c_i(p)o_i(\theta)\), con \(v_i=d_\theta o_i\), se recupera la ecuación central histórica

\[
\boxed{h=J_c^T V^T F^+V J_c}
\]

**si** los covectores y sus combinaciones cumplen el axioma y el pseudoinverso implementa correctamente la geometría del cociente. La versión E9 \(h=J_c^TV^Tg^{-1}VJ_c\) sigue siendo válida cuando la métrica base \(g\) es no degenerada; no identifica automáticamente una regularización euclídea con el cociente Fisher.

## Qué conservamos de E9

E9-A–D verificó en benchmarks controlados la métrica inducida, su transformación de coordenadas y una esfera de curvatura \(K=1\). Con covectores derivados de redes reales, E9 observó anisotropía, dependencia de entrada \(x\) y estado \(\theta\), y una diferencia entre **magnitud** y **coherencia por clase** de la deformación. En el control de tres semillas con memorización casi completa, la coherencia media reportada fue \(S_\Delta\approx0.471\) en true y \(0.092\) en random, mientras la deformación media fue mayor en random (\(1.406\) frente a \(0.904\)). Son hallazgos de ese protocolo, no leyes universales.

La geometría puede estar presente antes del entrenamiento por la arquitectura y los datos; aprender cambia esa geometría. Una dirección nula de \(h\) corresponde a una variación de perspectiva cuya relevancia no cambia, condicionada a que la métrica del cociente sea positiva en la imagen de \(d\Phi\).

## Lo aprendido después

E10 encontró cambios geométricos y controles negativos: la separación geométrica no precedió a la de accuracy en su prueba, no apareció una ley monótona de corrupción ni una ganancia predictiva condicional robusta. E11 mostró que el tamaño del panel Fisher, el espacio tangente, las direcciones débiles y la elección de \(S_P\) alteran los contrastes true/random. Por tanto una distancia escalar \(D_G\) no tiene aquí un sentido universal de «más generalización».

E11-E probó una exigencia directamente relacionada con el axioma: la misma red y el mismo \(S_P\), expresados en otras coordenadas, deben producir el mismo \(h\). El corte de autovalores **de la matriz cruda** de Fisher falló bajo reescalas no ortogonales; un control con autovalores generalizados y una métrica de referencia **transportada** recuperó invariancia en los casos evaluados. Elegir esa referencia requiere justificación adicional. En particular, \(F+\lambda I\) sólo es una construcción covariante si el término regularizador se especifica y transforma como tensor; fijar una identidad nueva en cada carta no basta.

Además, \(\omega_P=dS_P\) es exacto como 1-forma en \(M\): \(d\omega_P=0\) y sus integrales sobre lazos cerrados se anulan cuando se cumplen las condiciones globales pertinentes. Esto no implica \(\nabla\omega_P=0\) ni holonomía trivial de la conexión. Deben distinguirse exactitud, variación covariante y transporte.

## Cierre de E11

E11 queda cerrado. El estimando operativo regularizado es

\[
G_{\rho,\mathcal U}
=B_{\mathcal U}
\left(F_{\mathcal U}+\rho\,\lambda_{\max}(F_{\mathcal U},H_{\mathcal U})H_{\mathcal U}\right)^{-1}
B_{\mathcal U}^{T},
\]

con (S_P), la referencia tensorial (H), la escala (ho), el panel y el alcance tangente \(\mathcal U\) declarados. Es covariante cuando (H) se transporta; no es canónico sin justificar esas elecciones. El corte espectral crudo no se conserva bajo cambios de carta no ortogonales y queda descartado como construcción intrínseca.

La atribución por bloques queda definida mediante el complemento de Schur a escala común:

\[
G_{E\cup U}=G_E+\Delta G_{U\mid E},\qquad \Delta G_{U\mid E}\succeq0.
\]

Los barridos de E11-A–I mostraron que la variación debida al panel, el observable, el espectro, la carta, la referencia y el alcance tangente puede exceder la deriva temporal. E11-J estabilizó los saltos de rango mediante regularización suave. E11-K replicó externamente un contraste escalar, pero con dispersión por semilla. E11-L–M mostró que el signo true/random cambia al pasar de salida a capas ocultas. E11-N–O confirmó que ni la distancia temporal ni su contraste son universales: en datos naturales, el bloque oculto fue informativo, pero con heterogeneidad entre tareas y particiones.

El candidato empírico más estable para continuar es la participación oculta normalizada

\[
\boxed{\eta=\frac12\operatorname{tr}\!\left(G_{\mathrm{full}}^{-1}\Delta G_{\mathrm{hidden}\mid\mathrm{output}}\right)}\in[0,1],
\]

invariante bajo congruencias en las coordenadas de perspectiva. En los dos conjuntos naturales evaluados, random superó a true en 40/40 comparaciones agregadas; esto es evidencia exploratoria en dos tareas, no una ley general ni cuarenta conjuntos independientes.

### Conclusiones negativas que no deben reabrirse sin nueva evidencia

- (D_G) no es un escalar universal de generalización.
- No existe, en estos ensayos, un signo universal del contraste de trayectoria true/random.
- No se obtuvo un predictor temprano robusto, una firma universal del optimizador ni una relación causal.
- La geometría existe antes del aprendizaje; el entrenamiento la deforma.
- Magnitud geométrica y organización o coherencia son propiedades distintas.

### Estado de curvatura y holonomía

La curvatura **no** queda descartada. La exactitud \(\omega_P=dS_P\) implica \(d\omega_P=0\), pero no implica \(\nabla\omega_P=0\), curvatura nula ni holonomía trivial. La holonomía tampoco es imposible; deja de ser una hipótesis independiente y se reserva como control derivado de la curvatura mediante la aproximación de lazo pequeño. El antiguo acuerdo numérico de E6 entre ángulo de holonomía e integral de curvatura precede al axioma, al cociente y a la regularización finales, por lo que valida maquinaria histórica, no la RIPG vigente.

## Cierre de E12 — campo métrico y geometría intrínseca

E12 completa la cadena operativa

\[
P\longmapsto S_P\longmapsto \omega_P\longmapsto B(P)
\longmapsto G(P;\theta)\longmapsto \Gamma\longmapsto (R,K)
\longmapsto \operatorname{Hol}.
\]

### E12-A — canonicidad condicionada de \(\eta\)

La dirección del contraste \(\eta_{\rm random}>\eta_{\rm true}\) fue estable en las configuraciones principales: 40/40 pares para \(\rho\in[10^{-6},10^{-3}]\), referencias alternativas \(H\), observables alternativos y cuatro particiones ocultas complementarias. En \(\rho=10^{-2}\) se conservó en 38/40 pares, con dos fallos en Wisconsin. Por tanto, \(\eta\) es un descriptor robusto **condicionado al protocolo**, pero no un escalar absoluto canónico: su magnitud depende de \(\rho\) y de la referencia tensorial \(H\).

### E12-B — familia no lineal admisible

Se fijó la familia exponencial normalizada

\[
S_P(\theta)=\sum_n a_n(P)\log p_\theta(y_n\mid x_n),
\qquad
a_n(P)=\frac{e^{P^Tf_n}}{\sum_m e^{P^Tf_m}},
\]

con

\[
\omega_P=\sum_n a_nr_n,
\qquad
B_i(P)=\sum_n a_n(f_{ni}-\mu_i(P))r_n.
\]

Si \(k\in\ker F\), entonces los Jacobianos por muestra anulan \(k\), de modo que \(\omega_P(k)=0\) y \(B(P)k=0\) para todo \(P\). La verificación cubrió 80 estados finales y 49 puntos por estado (3920 evaluaciones): rango dos de \(B\) en todo el vecindario, \(\lambda_{\min}(BB^T)=2.47\times10^{-4}\), condición máxima 10.96, residuos de simetría menores que \(9.1\times10^{-17}\) y error máximo de \(B=d_P\omega\) por diferencias finitas de \(1.83\times10^{-10}\). El campo

\[
G_\rho(P;\theta)=B(P)\bigl(F+\rho\lambda_{\max}I\bigr)^{-1}B(P)^T,
\qquad \rho=10^{-4},
\]

resultó definido positivo y no constante en el vecindario estudiado.

### E12-C — conexión y curvatura

Se calcularon analíticamente las derivadas del campo, los símbolos de Christoffel, el tensor de Riemann y la curvatura gaussiana. En los atlas representativos, la curvatura no tuvo signo universal: digits-true fue negativa en 25/25 puntos (mediana \(-1.271\)); digits-random fue negativa y cercana a cero (mediana \(-0.005744\)); Wisconsin-true mezcló signos (18 positivos y 7 negativos; mediana \(+0.003755\)); Wisconsin-random fue negativa en 25/25 puntos (mediana \(-0.003747\)).

Los controles recuperaron \(K=0\) en el plano y \(K=1\) en la esfera. La convergencia por diferencias finitas fue de segundo orden y el cambio a una carta no ortogonal preservó \(K\) con error absoluto máximo \(2.19\times10^{-8}\); la ley de transformación de \(\Gamma\) tuvo error relativo máximo \(1.41\times10^{-7}\).

### E12-D — curvatura durante el aprendizaje

En 40 pares y 120 estados, digits mostró una separación fuerte: la mediana de \(K_0\) fue \(-0.0950\), la de \(K_t\) true \(-1.6046\) y la random \(-0.00717\); \(\Delta K\) fue negativa en 20/20 true y positiva en 20/20 random. Wisconsin fue heterogéneo: \(K_0\) mediano \(-0.2777\), \(K_t\) true \(+0.04597\), random \(-0.00591\), con contrastes de signo menos estables.

El resultado transversal más consistente fue de **magnitud final**: \(|K_{\rm true}|>|K_{\rm random}|\) en 20/20 pares de digits y 16/20 de Wisconsin (36/40 en total). En los mapas representativos, random expandió fuertemente el área métrica pero dejó una curvatura intrínseca casi nula; true concentró mucha más energía curvatural, especialmente en digits. Así, \(\eta\), el área de \(G\) y \(K\) miden aspectos distintos: participación de bloques, escala métrica y organización intrínseca, respectivamente.

### E12-E — holonomía como control derivado

Para cuatro regiones y lazos cuadrados decrecientes de lado 0.20, 0.10 y 0.05, se verificó

\[
\operatorname{Hol}(\gamma)\approx\int_{\Sigma_\gamma}K\,dA.
\]

En el lazo menor, el error relativo fue 0.0152% en digits-true, 0.0037% en digits-random, 0.0337% en una región positiva de Wisconsin-true y 0.0081% en una negativa. El error decreció monótonamente en las cuatro regiones. Esto valida la holonomía como consecuencia derivada de la conexión y la curvatura, no como hipótesis independiente. Un mismo lazo coordenado no encierra la misma área intrínseca entre estados; por eso una región casi plana pero métricamente expandida puede acumular holonomía comparable.

### Alcance y límites de E12

- Los resultados de población cubren dos tareas naturales y no autorizan una ley universal.
- Los mapas espaciales detallados son representativos, no réplicas exhaustivas de cada par.
- No se ha demostrado utilidad predictiva fuera de muestra ni causalidad.
- La señal que merece réplica es \(|K_{\rm true}|>|K_{\rm random}|\), no un signo universal de \(K\).
- La comparación debe normalizarse por radio o área intrínseca para separar curvatura de expansión métrica.

## Apertura natural de E13

**E13 — normalización intrínseca y réplica externa de la relación curvatura–generalización.** Antes de añadir otro invariante local, se debe comprobar si la señal de magnitud curvatural sobrevive a regiones de igual tamaño intrínseco y a una tarea y arquitectura nuevas.

1. **E13-A — prerregistro y normalización intrínseca:** fijar hipótesis, estimandos, semillas y regiones geodésicas de igual radio o área antes de mirar resultados.
2. **E13-B — reanálisis interno:** repetir las comparaciones E12 en bolas intrínsecas, incluyendo holonomía a igual área intrínseca.
3. **E13-C — nueva tarea y mayor profundidad:** añadir un tercer conjunto natural y una red con dos capas ocultas para habilitar atribución por capa.
4. **E13-D — réplica externa:** contrastar como hipótesis primaria la diferencia pareada de magnitudes \(|K_{\rm true}|-|K_{\rm random}|\).
5. **E13-E — mecanismo por capas:** relacionar exploratoriamente \(\eta\), expansión de área y energía curvatural por bloque, sin lenguaje causal.

## Regla de interpretación actual

Mantener separados: **(1)** definición y admisibilidad de la perspectiva, **(2)** invariancia geométrica del estimador, **(3)** cambios medidos durante aprendizaje, **(4)** utilidad predictiva y **(5)** explicación causal. E12 consolida (1), una versión condicionada de (2), la construcción diferencial local y evidencia protocolaria para (3). E13 debe probar generalidad y normalización intrínseca; (4) y (5) siguen abiertas.
