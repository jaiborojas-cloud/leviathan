# Proyecto Leviathan / RIPG — cierre formal de E13

**Fecha de cierre:** 24 de septiembre de 2026  
**Estado:** E13 cerrado; réplica externa inconclusa.  
**Siguiente etapa:** E14 — reconstrucción métrica positiva y nueva confirmación.

## 1. Pregunta de E13

E13 preguntó si la mayor magnitud curvatural observada bajo aprendizaje
verdadero frente a memorización aleatoria sobrevivía al comparar regiones con
la misma área intrínseca.

El estimando primario prerregistrado fue:

\[
C_A=\left(\frac1A\int_{D_A}K^2\,dA\right)^{1/2},
\qquad
\Delta C_A=C_A^{true}-C_A^{random},
\]

con \(A_*=0.02\) y áreas secundarias \(0.01\) y \(0.04\). La hipótesis no
presuponía un signo universal de \(K\); buscaba mayor energía o magnitud
curvatural en `true`.

## 2. E13-A — prerregistro

Se congelaron antes de abrir resultados las áreas, centro, mallas, semillas,
particiones, emparejamiento, criterios de faltantes, refinamiento, prueba
exacta de signos, intervalo BCa y condición conjunta de éxito. Se mantuvieron
la familia RIPG, \(H=I\) y \(\rho=10^{-4}\).

Los controles sintéticos de plano, esfera y cambio de carta aprobaron en las
tres áreas antes de comenzar E13-B.

## 3. E13-B — reanálisis interno

El jet analítico de segundo orden se aplicó a Digits y Wisconsin:

- 36/37 pares incluidos mostraron \(\Delta C_{0.02}>0\);
- las 8/8 medias partición–tarea fueron positivas;
- la dirección persistió en \(A=0.01,0.02,0.04\);
- Digits conservó 20/20 pares;
- Wisconsin conservó 17/20, con tres exclusiones `true` por pérdida de
  positividad del jet;
- con cuatro particiones por tarea, el mínimo valor exacto unilateral posible
  fue \(p=0.0625\).

Conclusión: la expansión métrica de `random` no explica por sí sola la
diferencia interna de curvatura. El resultado depende de una aproximación
métrica local y no constituye confirmación externa.

## 4. E13-C — tarea y arquitectura nuevas

Se construyó la réplica Wine:

- 178 observaciones y 13 variables;
- arquitectura \(13\to64\to32\to3\), ReLU y softmax;
- ocho particiones y cinco inicializaciones: 40 pares, 80 estados;
- todas las ramas alcanzaron al menos 99% de accuracy sobre su objetivo;
- mediana de prueba: 0.96296 en `true` y 0.29630 en `random` contra etiquetas
  verdaderas;
- 40/40 hashes iniciales emparejados;
- rango dos y métrica exacta positiva en 3920 evaluaciones;
- ninguna exclusión antes de calcular curvatura.

E13-C validó capacidad, emparejamiento y admisibilidad sin abrir el contraste
primario.

## 5. E13-D — resultado confirmatorio

La construcción regional mediante un único jet métrico cuadrático tuvo:

- 3/40 pares incluidos;
- 37/40 pares excluidos;
- pérdida de 92.5%, frente al máximo permitido de 10%;
- 0/8 particiones con al menos cuatro pares, frente al mínimo exigido de 6/8.

La regla de faltantes se activó antes del análisis direccional. No se produjo
un valor \(p\) ni un intervalo BCa confirmatorio. E13-D no confirma ni refuta
\(\Delta C_{0.02}>0\).

La causa fue diferencial: el jet perdió positividad al intentar construir el
área inicial en 37 estados `true`, mientras los 40 estados `random` pudieron
integrarse. E13-C había mostrado que el campo exacto permanecía positivo en su
malla; el fallo pertenece a la extrapolación cuadrática, no a la definición
RIPG exacta.

## 6. Evidencia descriptiva no confirmatoria

En los tres pares supervivientes:

\[
\operatorname{median}(C_{0.02}^{true})=5.29388,
\quad
\operatorname{median}(C_{0.02}^{random})=0.00107556,
\]

\[
\operatorname{median}(\Delta C_{0.02})=5.29281.
\]

La auditoría analítica exacta de frontera conservó
\(|K_{true}|>|K_{random}|\) en 24/24 direcciones pareadas. Pero los tres pares
son un subconjunto seleccionado por estabilidad numérica y no admiten
inferencia confirmatoria.

El refinamiento convergió dentro del surrogate, pero la auditoría contra el
campo exacto alcanzó 24.2% de error métrico relativo y 1.75 de error escalado de
curvatura. Convergencia de cuadratura no equivale a exactitud del campo
aproximado.

## 7. Conclusión científica

\[
\boxed{
\text{E13 queda cerrado como inconcluso en su réplica externa.}
}
\]

Lo aprendido es:

1. la señal interna sobrevive a normalizar por área intrínseca;
2. el signo de \(K\) no es universal;
3. `random` puede expandir la métrica y permanecer casi plano;
4. los campos profundos `true` son demasiado variables para un único jet
   cuadrático local;
5. el fallo del surrogate no refuta la hipótesis, pero impide confirmarla;
6. E13-E no debe ejecutarse sobre los tres supervivientes porque heredaría el
   sesgo de selección.

## 8. Estado vigente de RIPG

Permanece respaldado dentro del protocolo que una perspectiva operacional
\(P\mapsto S_P\mapsto\omega_P\) induce una geometría medible, que la
admisibilidad \(\omega_P\in(\ker F)^\circ\) y \(BK=0\) elimina direcciones no
identificables y que aprendizaje verdadero y memorización producen
organizaciones geométricas distintas en los experimentos internos.

\(|K_{true}|>|K_{random}|\) sigue siendo una señal candidata, no una ley
universal ni un resultado externamente confirmado. Tampoco se han demostrado
causalidad, independencia respecto de \(H\), \(\rho\), panel o perspectiva, ni
predicción universal de generalización.

## 9. Punto de partida para E14

E14 no será una reparación retroactiva de E13-D. Debe comenzar con un nuevo
prerregistro.

### E14-A — reconstrucción métrica positiva

Comparar, sin usar el signo del contraste para escoger método:

1. evaluación del campo métrico exacto;
2. atlas fijo log-euclídeo, \(G(P)=\exp L(P)\);
3. atlas Cholesky, \(G(P)=L(P)L(P)^T\);
4. opcionalmente, atlas de jets locales con regla de recambio congelada.

Criterios previos: positividad por construcción, cobertura 40/40 en Wine,
error métrico/de conexión/de curvatura contra evaluaciones exactas, invariancia
de carta, convergencia de área y malla, presupuesto declarado y tolerancias
fijadas antes de reagrupar `true/random`.

### E14-B — recuperación metodológica en Wine

Aplicar el método cerrado a los mismos estados. El resultado será exploratorio
o de recuperación, no una confirmación independiente, porque E13-D ya abrió
parte de los resultados.

### E14-C — nueva réplica confirmatoria

Usar una tarea, particiones y estados no abiertos. Sólo esta fase podrá volver a
probar confirmatoriamente \(\Delta C_{0.02}>0\).

## 10. Memoria compacta para continuar en otro chat

> E13 está cerrado. E13-B mostró que la mayor energía curvatural de `true`
> sobrevive internamente a igualar área intrínseca: 36/37 pares incluidos y
> 8/8 medias partición–tarea positivas. E13-C produjo 40 pares Wine profundos,
> emparejados y geométricamente admisibles. E13-D quedó inconcluso porque el jet
> cuadrático local perdió positividad en 37 estados `true`: sólo 3/40 pares
> sobrevivieron, con 92.5% de pérdida y 0/8 splits suficientes. Los
> supervivientes favorecieron descriptivamente a `true` y la frontera exacta
> lo hizo en 24/24 direcciones, pero no cuentan como confirmación. El fallo es
> del surrogate regional, no una refutación del campo RIPG ni de la hipótesis.
> E13-E no se ejecuta. E14 debe empezar con reconstrucción métrica positiva,
> validar cobertura/error sin abrir contrastes, tratar Wine como recuperación
> exploratoria y reservar una tarea nueva para confirmación externa.

---

**Fin de E13 — Proyecto Leviathan / RIPG**
