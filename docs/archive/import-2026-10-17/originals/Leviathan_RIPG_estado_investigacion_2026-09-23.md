# Proyecto Leviathan — RIPG
## Estado de la investigación y contexto para análisis externo

**Fecha de corte:** 24 de septiembre de 2026  
**Estado:** E13 cerrado; E14 es la siguiente etapa  
**Propósito:** documento técnico de transferencia para un investigador o una IA que necesite comprender, auditar y continuar el proyecto.

---

## 1. Objetivo general

Leviathan estudia si puede construirse una **geometría intrínseca del espacio de perspectivas** sobre una red neuronal y si esa geometría contiene información reproducible sobre la estructura del aprendizaje.

La investigación parte de una distinción básica:

- Fisher describe la geometría estadística del espacio del modelo.
- Una perspectiva determina qué es relevante respecto de un funcional concreto.
- RIPG estudia la geometría inducida por la variación de esas relevancias.

La pregunta actual no es simplemente si una red cambia durante el entrenamiento, sino:

> ¿El aprendizaje estructurado y la memorización producen organizaciones geométricas intrínsecamente distintas en el espacio de perspectivas?

---

## 2. Definición operacional de perspectiva

Sea \(M\) la variedad de modelos y \(\mathcal P\) el espacio de perspectivas.

Una perspectiva \(P\in\mathcal P\) define un funcional suave:

\[
S_P:M\rightarrow\mathbb R.
\]

Su relevancia respecto de los parámetros del modelo es el covector:

\[
\boxed{\omega_P=d_\theta S_P\in T_\theta^*M}
\]

y se define:

\[
\Phi_\theta(P)=\omega_P.
\]

La cadena conceptual central es:

\[
\boxed{
P\longmapsto S_P\longmapsto\omega_P=d_\theta S_P
}
\]

Cambiar de perspectiva no es cambiar de coordenadas. Una carta sólo cambia la representación; cambiar \(P\) modifica operacionalmente el observable, ponderación, criterio o funcional de relevancia.

---

## 3. Fisher y el axioma de admisibilidad

Sea \(F_\theta\) el tensor de Fisher y:

\[
K_\theta=\ker F_\theta.
\]

RIPG exige que una perspectiva admisible no asigne relevancia a direcciones que Fisher identifica como nulas:

\[
\boxed{
\omega_P\in K_\theta^\circ
}
\]

equivalentemente:

\[
d_\theta S_P(k)=0
\qquad
\forall k\in\ker F_\theta.
\]

Para estudiar cómo cambia la relevancia con la perspectiva:

\[
B=d_P\omega=d_Pd_\theta S.
\]

También debe cumplirse:

\[
\boxed{BK_\theta=0.}
\]

Así, la geometría vive en el cociente identificable:

\[
Q_\theta=T_\theta M/K_\theta,
\qquad
Q_\theta^*\simeq K_\theta^\circ.
\]

La formulación intrínseca vigente es:

\[
\boxed{
h^{(\theta)}
=
\Phi_\theta^*(\bar g_{F,\theta}^{-1})
}
\]

y, en coordenadas compatibles:

\[
\boxed{
h=BF^+B^T.
}
\]

Para una familia

\[
S(\theta,p)=\sum_i c_i(p)o_i(\theta),
\qquad
v_i=d_\theta o_i,
\]

se recupera:

\[
\boxed{
h=J_c^TV^TF^+VJ_c.
}
\]

RIPG **no reemplaza Fisher**. Fisher proporciona la geometría base; la relevancia selecciona y organiza direcciones dentro de ella.

---

## 4. Hipótesis refinada

La formulación inicial —“el aprendizaje crea una geometría de perspectivas”— fue demasiado fuerte.

Los controles mostraron que una red sin entrenar puede poseer ya una geometría perspectival no trivial.

La formulación vigente es:

\[
\boxed{
\text{arquitectura + entrada + perspectiva}
\rightarrow
\text{geometría perspectival inicial}
}
\]

y:

\[
\boxed{
\text{entrenamiento}
\rightarrow
\text{deformación de esa geometría}.
}
\]

Una distinción experimental central es:

\[
\boxed{
\text{magnitud de deformación}
\neq
\text{organización de deformación}.
}
\]

Una red puede moverse mucho geométricamente sin adquirir una estructura funcional coherente.

---

# 5. Evolución experimental

## E7 — Definición de perspectiva

Se abandonó la identificación implícita entre Fisher y la geometría que se quería investigar.

Se introdujeron explícitamente:

\[
P\mapsto S_P\mapsto\omega_P.
\]

Resultado conceptual: dos perspectivas pueden compartir la misma Fisher y tener covectores de relevancia diferentes:

\[
F_A=F_B,
\qquad
\omega_A\neq\omega_B.
\]

---

## E8 — Transporte y variación covariante

Para \(\omega=dS\) se estudió:

\[
\nabla_a\omega_i
=
\partial_a\omega_i
-
\Gamma^k{}_{ai}\omega_k.
\]

Se confirmó que puede cumplirse:

\[
d\omega=0
\]

mientras:

\[
\nabla\omega\neq0.
\]

La variación covariante local reprodujo el cambio observado tras transporte paralelo, y la circulación de una forma exacta permaneció nula dentro del error numérico.

Conclusión: variación geométrica de relevancia no implica falta de integrabilidad.

---

## E9 — Geometría del espacio de perspectivas

Se construyó una métrica inducida sobre \(\mathcal P\) y se validó matemáticamente.

### Controles

- invariancia bajo reparametrización;
- longitud intrínseca de curvas;
- benchmark esférico con:
  \[
  K=1;
  \]
- error de curvatura esférica:
  \[
  6.66\times10^{-16};
  \]
- longitud de un benchmark:
  \[
  L=1.943410004095.
  \]

Posteriormente, los covectores sintéticos se reemplazaron por cantidades derivadas de redes:

\[
\boxed{v_i=d_\theta o_i.}
\]

Las redes mostraron geometrías:

- anisotrópicas;
- dependientes de la entrada;
- dependientes del entrenamiento.

En un resultado representativo:

\[
\langle\|\Delta G\|\rangle_{true}\approx0.904
\]

frente a:

\[
\langle\|\Delta G\|\rangle_{random}\approx1.406.
\]

La memorización podía deformar más la métrica en magnitud, pero con menor organización funcional.

### E9-G

El análisis del kernel de Fisher llevó al axioma vigente:

\[
\omega_P\in(\ker F)^\circ,
\qquad
BK=0.
\]

Toda continuación de Leviathan debe respetar estas condiciones o justificar explícitamente una alternativa.

---

## E10 — Geometría y generalización temprana

E10 examinó:

- cambios métricos tempranos;
- distancias entre checkpoints;
- trayectorias;
- comparación true/random;
- optimizadores;
- poder predictivo condicional.

El resultado fue negativo en un sentido importante: **no se obtuvo evidencia suficiente para declarar una distancia o señal geométrica temprana como predictor universal de generalización**.

Se detectaron problemas de:

- densidad temporal insuficiente;
- sensibilidad al estimador;
- ruido Fisher;
- dependencia del protocolo.

Esto motivó E11.

---

## E11 — Auditoría del estimador

E11 separó cambio geométrico real de variación numérica.

### Regularización explícita

El corte espectral discreto de \(F^+\) mostró sensibilidad al umbral. Se reemplazó por:

\[
\boxed{
G_\rho
=
B
\left(
F+
\rho\lambda_{\max}(F,H)H
\right)^{-1}
B^T.
}
\]

Configuración principal:

\[
H=I,
\qquad
\rho=10^{-4}.
\]

La familia es covariante si \(H\) se transporta tensorialmente, pero sigue siendo **condicionada a \(H\) y \(ho\)**. No es una construcción canónica absoluta.

### Descriptor de participación \(\eta\)

Se definió:

\[
\boxed{
\eta=
\frac12
\operatorname{tr}
\left(
G_{completa}^{-1}
\Delta G_{oculta\mid salida}
\right).
}
\]

Resultado principal:

\[
\boxed{
\eta_{random}>\eta_{true}
}
\]

en:

\[
40/40
\]

pares principales.

Medianas:

**Digits**

\[
\eta_{true}\approx0.349,
\qquad
\eta_{random}\approx0.786.
\]

**Wisconsin**

\[
\eta_{true}\approx0.480,
\qquad
\eta_{random}\approx0.860.
\]

Conclusión de E11:

- una distancia global \(D_G\) no es universal;
- la regularización debe declararse;
- \(\eta\) es útil pero protocolaria;
- la holonomía no debía tratarse aún como hipótesis independiente;
- la curvatura quedó como la pregunta natural siguiente.

---

# 6. E12 — Campo métrico, conexión y curvatura

E12 completa la cadena:

\[
\boxed{
P
\to
S_P
\to
\omega_P
\to
B(P)
\to
G(P;\theta)
\to
\Gamma
\to
R,K
\to
\mathrm{Hol}.
}
\]

---

## E12-A — Robustez condicionada de \(\eta\)

La dirección:

\[
\eta_{random}>\eta_{true}
\]

se mantuvo en:

\[
40/40
\]

pares para:

\[
\rho\in[10^{-6},10^{-3}],
\]

además de controles con referencias \(H\), observables y particiones alternativas.

En:

\[
\rho=10^{-2}
\]

se conservó en:

\[
38/40.
\]

Conclusión:

\[
\boxed{
\eta \text{ es robusta dentro del protocolo, no canónica en valor absoluto.}
}
\]

---

## E12-B — Familia no lineal admisible

Se definió:

\[
S_P(\theta)
=
\sum_n
a_n(P)
\log p_\theta(y_n\mid x_n)
\]

con:

\[
a_n(P)
=
\frac{e^{P^Tf_n}}
{\sum_m e^{P^Tf_m}}.
\]

Entonces:

\[
\omega_P=\sum_n a_nr_n,
\]

y:

\[
B_i(P)
=
\sum_n
a_n(f_{ni}-\mu_i(P))r_n.
\]

Si \(k\in\ker F\), los jacobianos por muestra anulan \(k\), por lo que:

\[
\omega_P(k)=0,
\qquad
B(P)k=0.
\]

### Validación

Se evaluaron:

- 80 estados finales;
- 49 puntos por estado;
- 3920 evaluaciones.

Resultados:

\[
\lambda_{\min}(BB^T)=2.47\times10^{-4},
\]

condición máxima:

\[
10.96,
\]

residuos de simetría:

\[
<9.1\times10^{-17},
\]

error máximo de \(B=d_P\omega\) por diferencias finitas:

\[
1.83\times10^{-10}.
\]

El campo:

\[
G_\rho(P;\theta)
=
B(P)
(F+\rho\lambda_{\max}I)^{-1}
B(P)^T
\]

fue definido positivo y no constante en el vecindario.

---

## E12-C — Conexión y curvatura

Se calcularon:

- derivadas de \(G\);
- símbolos de Christoffel;
- tensor de Riemann;
- curvatura gaussiana \(K\).

### Controles

Plano:

\[
K=0.
\]

Esfera:

\[
K=1.
\]

La convergencia numérica fue de segundo orden.

Bajo una carta no ortogonal:

- error absoluto máximo en \(K\):
  \[
  2.19\times10^{-8};
  \]

- error relativo máximo en la transformación de \(\Gamma\):
  \[
  1.41\times10^{-7}.
  \]

### Atlas representativos

**Digits / true**

\[
K<0
\]

en 25/25 puntos, mediana:

\[
-1.271.
\]

**Digits / random**

mediana:

\[
-0.005744.
\]

**Wisconsin / true**

18 puntos positivos y 7 negativos, mediana:

\[
+0.003755.
\]

**Wisconsin / random**

25/25 negativos, mediana:

\[
-0.003747.
\]

Conclusión:

\[
\boxed{
\text{el signo de }K\text{ no es universal.}
}
\]

---

## E12-D — Curvatura durante aprendizaje

Se analizaron:

\[
40
\]

pares y:

\[
120
\]

estados.

### Digits

\[
K_0\approx-0.0950
\]

\[
K_{true}\approx-1.6046
\]

\[
K_{random}\approx-0.00717.
\]

Además:

\[
\Delta K_{true}<0
\]

en 20/20 pares, mientras:

\[
\Delta K_{random}>0
\]

en 20/20.

### Wisconsin

\[
K_0\approx-0.2777,
\]

\[
K_{true}\approx+0.04597,
\]

\[
K_{random}\approx-0.00591.
\]

El signo fue menos estable.

### Resultado transversal prioritario

La señal más consistente fue:

\[
\boxed{
|K_{true}|>|K_{random}|
}
\]

en:

- 20/20 pares de digits;
- 16/20 de Wisconsin;
- 36/40 en total.

Éste es actualmente el resultado empírico más importante que requiere réplica.

No debe interpretarse todavía como ley universal.

---

## E12-E — Holonomía

Se comprobó localmente:

\[
\boxed{
\operatorname{Hol}(\gamma)
\approx
\int_{\Sigma_\gamma}K\,dA.
}
\]

En el lazo menor, errores relativos:

- digits-true: 0.0152%;
- digits-random: 0.0037%;
- Wisconsin-true, región positiva: 0.0337%;
- Wisconsin, región negativa: 0.0081%.

El error decreció al contraer los lazos.

Conclusión:

\[
\boxed{
\text{la holonomía es un control derivado de la curvatura, no una hipótesis independiente.}
}
\]

---

# 7. Interpretación actual

Los resultados obligan a distinguir:

\[
\eta
\quad\text{(participación por bloques)}
\]

de:

\[
\operatorname{Area}_G
\quad\text{(escala o expansión métrica)}
\]

y de:

\[
K
\quad\text{(organización geométrica intrínseca).}
\]

Las redes random podían expandir mucho el área métrica y permanecer casi planas:

\[
K\approx0.
\]

Por tanto:

\[
\boxed{
\text{métrica grande}
\not\Rightarrow
\text{curvatura grande}.
}
\]

y:

\[
\boxed{
\text{deformación grande}
\not\Rightarrow
\text{organización intrínseca}.
}
\]

---

# 8. Qué está demostrado y qué no

## Establecido dentro del marco

- \(P\mapsto S_P\mapsto\omega_P\) es una definición operacional utilizable.
- La condición de admisibilidad evita componentes no identificables.
- Puede inducirse una métrica sobre \(\mathcal P\).
- La construcción pasa controles de coordenadas y benchmarks analíticos.
- Puede construirse conexión, curvatura y holonomía.
- La geometría cambia durante el entrenamiento.
- True y random muestran diferencias sistemáticas bajo los protocolos actuales.

## No establecido

- No existe una ley universal sobre el signo de \(K\).
- No existe aún un predictor geométrico universal de generalización.
- \(\eta\) no es un escalar canónico absoluto.
- La señal 36/40 no ha sido validada externamente.
- No se ha demostrado causalidad.
- No se ha demostrado comportamiento equivalente en redes profundas modernas.

---

# 9. E13 — Diseño original y cierre

Las subsecciones siguientes conservan el diseño que guio E13. El cierre
autoritativo aparece al final de esta sección y prevalece sobre el lenguaje
prospectivo del plan original.

E13 tiene como objetivo comprobar si la señal de curvatura sobrevive cuando se elimina un confusor importante: comparar regiones de diferente tamaño intrínseco.

## Hipótesis primaria

Para cada par:

\[
\delta_K
=
|K_{true}(P_0)|
-
|K_{random}(P_0)|.
\]

Hipótesis preregistrada:

\[
\boxed{
\operatorname{median}(\delta_K)>0.
}
\]

El signo de \(K\) no es hipótesis primaria.

---

## Energía curvatural

Sobre una región \(\Omega\):

\[
\boxed{
\mathcal E_K(\Omega)
=
\frac{1}{\operatorname{Area}_G(\Omega)}
\int_\Omega K(P)^2\,dA_G.
}
\]

Contraste secundario:

\[
\boxed{
\mathcal E_K^{true}
>
\mathcal E_K^{random}.
}
\]

La integral no normalizada se mantiene sólo como descriptivo, porque mezcla intensidad de curvatura y área.

---

## Regiones intrínsecas

Coordenadas locales iniciales:

\[
q
=
G(P_0;\theta)^{1/2}(P-P_0).
\]

Las comparaciones principales usarán:

- igual radio geodésico;
- o igual área intrínseca.

La holonomía se comparará sobre lazos de igual área intrínseca, no de igual lado coordenado.

---

## E13-A — Prerregistro

Quedan congelados:

- familia de perspectivas;
- \(ho=10^{-4}\);
- \(H=I\) en la carta declarada, transportado tensorialmente;
- sensibilidad secundaria en \(10^{-5}\) y \(10^{-3}\);
- paneles Fisher;
- particiones;
- semillas;
- mallas;
- criterios de inclusión/exclusión;
- tolerancias numéricas;
- criterio de éxito.

Umbrales:

\[
\text{error relativo entre cartas}
\le5\times10^{-4},
\]

\[
\text{error frente a solución analítica}
\le10^{-3}.
\]

Si falla un control, sólo puede corregirse la implementación **antes** de abrir resultados de redes.

---

## E13-B — Reanálisis interno

Tareas:

- digits;
- Wisconsin.

Diseño:

- 4 particiones;
- 5 semillas;
- 20 pares por tarea;
- 40 pares totales.

Se reanalizarán:

\[
|K(P_0)|,
\]

\[
\mathcal E_K,
\]

fracción de área con \(K>0\),

holonomía a igual área,

y las relaciones entre:

\[
\eta,
\operatorname{Area}_G,
\mathcal E_K.
\]

---

## E13-C/D — Réplica externa

Tarea congelada:

```text
sklearn.datasets.load_wine
```

Arquitectura:

\[
13\to64\to32\to3.
\]

- ReLU;
- softmax;
- partición 70/15/15 estratificada;
- estandarización ajustada sólo en entrenamiento;
- semillas de partición 1000–1007;
- inicializaciones 2000–2004;
- condiciones true/random emparejadas;
- no se sustituyen corridas fallidas.

---

## E13-E — Mecanismo por capas (no ejecutado)

La arquitectura 64–32 permitirá explorar por bloque:

- participación geométrica;
- expansión;
- energía curvatural.

Este análisis habría sido exploratorio y no causal. No se ejecutó porque E13-D
activó la regla de faltantes; atribuir por capas sobre sólo tres pares
supervivientes habría introducido sesgo de selección.

---

## Cierre autoritativo de E13

E13-A congeló como estimando primario

\[
C_A=\left(A^{-1}\int_{D_A}K^2\,dA\right)^{1/2},
\qquad
\Delta C_A=C_A^{true}-C_A^{random},
\]

con \(A_*=0.02\), áreas secundarias 0.01 y 0.04, discos geodésicos de igual
área y refinamiento duplicado. Los controles sintéticos de plano, esfera e
invariancia de carta aprobaron antes de abrir resultados.

E13-B conservó \(C_{0.02}^{true}>C_{0.02}^{random}\) en 36/37 pares internos
incluidos y en 8/8 medias partición–tarea. La dirección persistió en las tres
áreas. Esto descarta que la expansión métrica de `random` explique por sí sola
la diferencia interna, pero sigue condicionado al jet local de segundo orden.

E13-C produjo 40 pares Wine, 80 estados, con arquitectura
\(13\to64\to32\to3\). Todas las ramas alcanzaron al menos 99% sobre su objetivo,
los 40/40 pares compartieron inicialización y el campo métrico exacto conservó
rango dos y positividad en 3920 evaluaciones, sin exclusiones previas.

E13-D incluyó sólo 3/40 pares. La pérdida de 92.5% excedió el máximo
prerregistrado de 10% y 0/8 particiones conservaron al menos cuatro pares. La
regla de faltantes se aplicó antes del contraste: no hubo valor \(p\) ni
intervalo BCa confirmatorio.

La causa fue el surrogate cuadrático: 37 estados `true` perdieron positividad
al intentar encerrar el área inicial, mientras los 40 `random` pudieron
integrarse. Esto no contradice la positividad del campo exacto verificada en
E13-C. Los tres pares supervivientes favorecieron descriptivamente a `true` y
la frontera exacta lo hizo en 24/24 direcciones, pero el subconjunto está
seleccionado por estabilidad numérica y no admite inferencia confirmatoria.

\[
\boxed{
\text{E13 queda cerrado como inconcluso en su réplica externa.}
}
\]

No se confirma ni se refuta \(\Delta C_{0.02}>0\). E13-E queda cancelado en
esta etapa. La siguiente fase deberá validar una reconstrucción regional que
preserve positividad antes de retomar una atribución por capas o una nueva
confirmación.

---

# 10. Estado del proyecto

## Cerrado

- E7 — definición de perspectiva.
- E8 — variación covariante.
- E9 — métrica y admisibilidad.
- E10 — generalización temprana.
- E11 — auditoría, regularización y atribución.
- E12 — campo métrico, conexión, curvatura y holonomía.
- E13 — normalización intrínseca y réplica externa; cierre inconcluso por
  cobertura insuficiente del jet local.

## Siguiente etapa

\[
\boxed{
E14
=
\text{reconstrucción métrica positiva + nueva confirmación externa}.
}
\]

Secuencia recomendada:

\[
E14A\to E14B\to E14C.
\]

- E14-A: comparar campo exacto, atlas log-euclídeo/Cholesky y, si procede,
  atlas de jets; congelar cobertura y error antes de contrastar regímenes.
- E14-B: recuperación metodológica en Wine, exploratoria porque los resultados
  ya fueron parcialmente abiertos.
- E14-C: réplica confirmatoria en una tarea y estados nuevos.

---

# 11. Resultado provisional central

La lectura más compacta del proyecto es:

\[
\boxed{
\text{la arquitectura y la perspectiva inducen una geometría inicial;}
}
\]

\[
\boxed{
\text{el entrenamiento deforma esa geometría;}
}
\]

y los experimentos actuales sugieren:

\[
\boxed{
\text{aprendizaje estructurado y memorización producen}
}
\]

\[
\boxed{
\text{organizaciones geométricas cualitativamente diferentes.}
}
\]

La señal prioritaria es:

\[
\boxed{
|K_{true}|>|K_{random}|
}
\]

observada en:

\[
36/40
\]

pares en E12.

E13 mostró que la diferencia interna sobrevive a igualar área, pero no logró
confirmarla externamente: el surrogate local produjo pérdida diferencial de
cobertura. La señal continúa plausible, no confirmada como reproducible.

---

# 12. Pregunta científica actual

La pregunta de Leviathan ya no es simplemente:

> ¿Puede construirse una geometría del espacio de perspectivas?

Operacionalmente, sí.

La pregunta relevante ahora es:

\[
\boxed{
\text{¿contiene esa geometría información reproducible sobre}
}
\]

\[
\boxed{
\text{la estructura del aprendizaje que no se reduzca a Fisher,}
}
\]

\[
\boxed{
\text{escala métrica o artefactos del estimador?}
}
\]

---

# 13. Qué falsaría la hipótesis actual

La interpretación fuerte debería debilitarse si:

1. \(|K_{true}|>|K_{random}|\) desaparece al igualar radio o área intrínseca.
2. La réplica Wine no muestra separación consistente.
3. Perspectivas razonables invierten arbitrariamente el resultado.
4. Una estadística mucho más simple explica completamente la misma señal.
5. La diferencia depende principalmente de \(ho\), \(H\) o ruido Fisher.
6. El efecto desaparece en una arquitectura distinta.
7. La señal no sobrevive a réplicas independientes.

---

# 14. Preguntas recomendadas para análisis externo

## Matemática

- ¿Es \(P\mapsto S_P\mapsto d_\theta S_P\) suficientemente general?
- ¿Puede derivarse la admisibilidad desde un principio más fundamental?
- ¿Existe una construcción que elimine o naturalice \(H\)?
- ¿Qué información adicional aportan los invariantes de curvatura?

## Estadística

- ¿Cuál es la unidad de análisis correcta: corrida, semilla o partición?
- ¿Conviene un modelo jerárquico?
- ¿Cómo cuantificar el efecto 36/40 sin selección posterior?
- ¿Qué controles adicionales previenen sobreajuste experimental?

## Deep learning

- ¿La señal se mantiene con mayor profundidad y anchura?
- ¿Se replica en CNN, ResNet o Transformers?
- ¿Cómo se relaciona con margen, representación, sharpness o compresión?
- ¿Qué ocurre durante grokking o memorization-to-generalization transitions?

## Interpretación

- ¿La curvatura perspectival aporta información distinta de Fisher?
- ¿Qué significa funcionalmente \(K>0\), \(K<0\) o \(K\approx0\)?
- ¿La energía curvatural puede relacionarse con organización de representaciones?
- ¿Cuál sería un mecanismo causal comprobable?

---

# 15. Reglas para continuar Leviathan

Cualquier análisis posterior debe preservar:

1. **Perspectiva ≠ coordenada.**
2. **Fisher ≠ RIPG.**
3. Usar:
   \[
   \omega_P=d_\theta S_P.
   \]
4. Respetar:
   \[
   \omega_P\in(\ker F)^\circ,
   \qquad
   BK=0.
   \]
5. No tratar \(ho\) ni \(H\) como canónicos.
6. No presentar \(\eta\) como universal.
7. No presentar el signo de \(K\) como universal.
8. Tratar holonomía como derivada de curvatura.
9. Mantener separados:
   - definición;
   - invariancia;
   - medición;
   - predicción;
   - causalidad.
10. Separar estrictamente la recuperación metodológica en Wine de una nueva
    confirmación sobre datos no abiertos.

---

# 16. Resumen ejecutivo para otra IA

Leviathan/RIPG define una perspectiva \(P\) mediante un funcional \(S_P\). Su relevancia es el covector \(d_\theta S_P\). La variación de estos covectores, medida respecto de la geometría Fisher identificable, induce una métrica sobre el espacio de perspectivas.

La cadena completa actualmente construida es:

\[
\boxed{
P
\to
S_P
\to
\omega_P
\to
B
\to
G
\to
\Gamma
\to
R,K
\to
\mathrm{Hol}.
}
\]

El marco ha superado pruebas de invariancia, plano, esfera, transformación de coordenadas y consistencia curvatura-holonomía.

En redes pequeñas, aprendizaje verdadero y memorización aleatoria producen geometrías distintas. La memorización puede generar mayor deformación o expansión, pero el aprendizaje estructurado ha mostrado mayor organización curvatural.

La señal más fuerte hasta E12 es:

\[
|K_{true}|>|K_{random}|
\]

en 36/40 pares.

Esto **no está establecido como ley universal**.

E13 examinó si la señal sobrevivía a:

- normalización por radio/área intrínseca;
- réplica interna;
- nueva tarea;
- nueva arquitectura;
- análisis por capas.

El reanálisis interno fue favorable a igual área, pero la réplica externa quedó
inconclusa por pérdida de positividad del jet cuadrático en 37/40 estados
`true`. Esto no refuta la hipótesis y tampoco la confirma. El siguiente problema
es construir una representación regional que preserve positividad y validar su
error contra el campo exacto antes de abrir una nueva réplica.

---

## Estado en una línea

\[
\boxed{
\text{Leviathan ha construido la geometría perspectival y ahora debe}
}
\]

\[
\boxed{
\text{separar señal reproducible de error de reconstrucción regional.}
}
\]

---

**Fin del documento de transferencia — Proyecto Leviathan / RIPG**
