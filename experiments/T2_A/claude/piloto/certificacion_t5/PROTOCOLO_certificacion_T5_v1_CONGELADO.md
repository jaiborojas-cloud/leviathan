# Protocolo de certificación de T5 para split8_j5_true y split8_j7_true — v1 (CONGELADO)

**Estado:** congelado el 2026-10-21 ≈14:24 America/Mexico_City por decisión del responsable (Jaibo Rojas), que adoptó todas las propuestas del borrador («me iré con tus propuestas»). El contenido técnico es el del borrador v0 (SHA-256 `fe25d3012b8785b15e06973ec8f2378016497dbf09cb5aaf421fe2869ee99b7c`, que se conserva sin cambios). Solo cambian este encabezado, la sección 8 (decisiones) y la nueva sección 9 (procedimiento del código). No se ha calculado nada con este protocolo antes de congelarlo. Los puntos marcados **[DECISIÓN]** en el texto quedan resueltos con el valor propuesto (sección 8).

**Naturaleza:** diagnóstico adicional de T5 según el anexo E1 v1.1 congelado (2.2, D3). **No reclasifica** j5 ni j7: siguen `PAUSED_PENDING_REVIEW` hasta que E2 resuelva el tratamiento de T5. No asigna Y, no cambia la compuerta del piloto, no modifica A = 0.02, rayos, tolerancias ni el solver de producción. Una certificación fallida **no** es `INCONCLUSIVE` ni `NUMERICAL_FAILURE` de la visita: es «T5 no certificado» y la visita sigue igual.

## 1. Qué se quiere demostrar
Para cada caso, que **el disco construido con la exponencial (todos los rayos) deja de existir antes de alcanzar área 0.02**:

> existe un radio t*_min en el que al menos una geodésica de la exponencial sale del dominio original (familia softmax con P finito), y A(t*_min) < 0.02.

Por los tres requisitos de 2.2:
- **(i)** salida real del dominio (no una singularidad removible de la carta P);
- **(ii)** área medida con convergencia entre rejillas;
- **(iii)** una cota **superior** del área en t*_min, sin extrapolación, con margen respecto a 0.02.

**Advertencia de alcance (del anexo):** T5 se define sobre el procedimiento de E1 (exponencial con todos los rayos), no sobre la bola métrica.

## 2. Idea de la cota (iii)
**Observable.** En marco ortonormal en el origen y ángulo θ uniforme (lo que ya usan `geometry.rays` y `audit.jacsolve`), el campo de Jacobi transversal j(s,θ) cumple j″ + K(γ_θ(s)) j = 0, con j(0) = 0 y j′(0) = 1. El área de la imagen de la exponencial contada con multiplicidad es

  A(t) = ∫₀^{2π} ∫₀^t |j(s,θ)| ds dθ.

`geometry.area7` (suma de áreas absolutas de triángulos, cuadratura de grado 5 con √det G) es la discretización de esta cantidad. A(t) es **no decreciente** en t (el integrando es ≥ 0), aunque haya plegados. Así queda resuelta la objeción de 2.1 sobre la monotonía del área poligonal: se acota A y la diferencia con el área poligonal se mide (sección 4.2).

**Cadena de desigualdades.** Sean:
- t₀ < t*_min, un radio donde todo se mide en la carta P;
- T⁺ ≥ t*_min, una cota superior del radio de escape. Basta el escape de **un** rayo concreto, porque t*_min ≤ t*(ese rayo); no hace falta cubrir el continuo angular.
- κ ≥ sup |K| sobre la franja barrida por los rayos en [t₀, t*_min].

Para cada rayo y s ∈ [t₀, t*_min], por Grönwall aplicado al par (|j|, |j′|):

  |j(s)| ≤ |j(t₀)| cosh(√κ (s−t₀)) + |j′(t₀)| sinh(√κ (s−t₀))/√κ.

Con Δ = T⁺ − t₀:

  A(t*_min) ≤ A(t₀) + Δ · L⁺,   con L⁺ = ∫ [ |j(t₀,θ)| cosh(√κ Δ) + |j′(t₀,θ)| sinh(√κ Δ)/√κ ] dθ.

La desigualdad exige una cota de |K| por los dos lados (no basta K ≥ −κ).

**Factibilidad estimada con datos ya publicados** (`../diagnostico_escape/`; orientativa, no forma parte de la certificación):

| caso | t₀ (\|p\| ≥ 10) | A(t₀) | Δ hasta T⁺ ref. | L⁺ máximo admisible | dA/dt actual | κ máximo admisible |
|---|---|---|---|---|---|---|
| j5 | 0.0710028 | 0.016880 | 3.47×10⁻³ (T⁺ ref. 0.0744744, otro estado) | 0.899 | 0.516 | ≈ 1.1×10⁵ |
| j7 | 0.0715096 | 0.017139 | 3.15×10⁻³ (T⁺ ref. 0.074662, ajuste de polo) | 0.908 | 0.512 | ≈ 1.4×10⁵ |

El κ admisible es antes de aplicar el factor de seguridad F_K de 4.3 y sin contar el término en j′. Si |K| en la franja resulta del orden de 10³ o menos, la cota pasa con holgura. Si es del orden de 10⁵ o más, no pasa.

## 3. Entradas (fijas)
- **Estados:** los regenerados de update 25 que usaron la calibración del piloto y el diagnóstico de escape.
  - `state_025_regen_split8_j5_true.npz` — SHA-256 `845c22519a20be8ceef4e35210157d97bd5bc223fc9f05e1769b91d998aa4776`
  - `state_025_regen_split8_j7_true.npz` — SHA-256 `59990ae56e64499d9bc46bfa056a8c91bcbffd9b188e4fc081933fdb413625c2`
  - Control: `state_025_regen_split8_j8_true.npz` — SHA-256 `f70d88b3c300286e31b8ca55860cc99f7d2a38c9e5f0c21242d566703928132b`

  Fuente de los hashes: `../estados_u25/regeneracion_u25.csv`. El script aborta si un hash no coincide.
- **Geometría:** `geometry.py` SHA-256 `b4d1e0e4…bdf3` (misma `jet`, `eval`, `area7`, `triangles`) y `audit.jacsolve` sin cambios.
- **No se usan** los M/f del replay 139 del agente original (otro entorno, SHA-256 6713246b…). Su análisis de frontera (`docs/archive/import-2026-10-17/extracted/Leviathan_T2A_frontera_paso139/`) sirve como **método y referencia**; todo se recalcula con los estados de arriba.
- **Integración de rayos:** nt = 2048, fase 0, DOP853 rtol 2×10⁻¹⁰ y atol 2×10⁻¹², `t_bound` 0.09, como `bg.calibrate`. Sin topes de producción, porque es un diagnóstico de solo lectura. Se para cuando se cumple 4.1.

## 4. Procedimiento
### 4.1 Integración y elección de t₀ (regla fija)
1. Integrar los 2048 rayos registrando por paso aceptado t, max|p| y argmax.
2. **t₀** = t del **primer paso aceptado con max|p| ≥ 10**. Es la misma regla de umbral del diagnóstico ya publicado y garantiza que en t₀ todos los rayos están en la zona de la carta P donde `jet` en float64 es fiable.
   - Valores esperados: j5 ≈ 0.0710027616 (paso 37) y j7 ≈ 0.0715096487 (paso 37).
   - Como **sensibilidad** se reportan también los cruces de |p| ≥ 5 y ≥ 20; **no** entran en la decisión.
3. **Rayo designado** = argmax|p| en t₀. Esperado: en el sector 1771–1782 (j5) y 1822–1833 (j7). Se registra si difiere de 1776/1828.
4. Continuar la integración más allá de t₀ hasta que cada rayo llegue a T⁺ (4.4) o al umbral de cambio de carta (4.3), guardando la salida densa para muestrear K.

### 4.2 Área en t₀ — requisito (ii)
- **A₀** = `area7` con la regla del instrumento: 33 anillos (`np.linspace(0, t₀, 33)`) × 2048 rayos.
- **Variantes:** 65 anillos × 2048; 33 × 1024 (rayos pares); 129 × 2048.
- **δ_disc** = máx |A_variante − A₀|.
- **Identidad de área (validación V3):** A_J(t₀) = ∫∫|j| con j de `audit.jacsolve` (trapecio en θ, 513 radios con Simpson). Se exige |A_J − A₀|/A₀ ≤ 10⁻⁵ **[DECISIÓN: tolerancia]**. Comprueba que `area7` y el observable de la sección 2 son la misma cantidad en estos estados.

### 4.3 j, j′ en t₀ y κ
- j(t₀,θ) y j′(t₀,θ) para los 2048 rayos con `audit.jacsolve(g, angles, t₀)`: es la ecuación del instrumento, con K por la ecuación de Gauss.
- Se registra si algún j cambia de signo en [0, t₀]. Es descriptivo: un conjugado antes de t₀ no impide T5, pero se reporta.
- **κ̂** = máx |K| muestreado sobre la franja [t₀, min(T⁺, salida del rayo)], para **todos** los rayos, en la salida densa (513 puntos por rayo en esa franja; repetido con 1025: debe dar el mismo máximo a 10⁻³ relativo).
  - Con |p| ≤ 10: K con `geometry.eval` en float64.
  - Con |p| > 10: K con las mismas fórmulas (ecuación de Gauss, M, f) en mpmath de 50 dígitos.
  - **Solapamiento:** en los puntos con |p| ∈ [8, 12], float64 y mpmath deben coincidir a 10⁻⁶ relativo.
  - Cuando un rayo pasa |p| = 150 (donde la carta P deja de ser útil), K se evalúa en la carta de cara (4.4) hasta su salida. El agente original encontró que K → 0 en el borde: aquí se **mide**, no se supone.
- **κ** = F_K · κ̂ con **F_K = 4** (×2 en √κ) **[DECISIÓN]**. El muestreo puede perder un pico entre muestras; F_K lo cubre de forma declarada, no rigurosa.

### 4.4 Escape y T⁺ — requisito (i)
Para el rayo designado (y para cualquier rayo que pase |p| = 150 antes de T⁺):
1. **Cara.** Identificar la arista de la envolvente convexa de los vectores f_k hacia la que se dirige el rayo: los dos componentes que sobreviven y el primer componente transversal suprimido. En j5, según el agente original, son 6/13 y 20, a confirmar con este estado; en j7 no se ha analizado.
2. **Carta de cara**, como en `FRONTERA_CONFIRMACION.md`: a = log(w_i/w_j), b = w_k/w_j, P = A⁻¹(a, log b). Exigencias:
   - (C1) det A ≠ 0 y β_l > 0 para todos los demás componentes, calculados con 100 dígitos;
   - (C2) identidad de jacobianos con la carta P en el solapamiento, a 10⁻¹².
3. Integrar con b como variable independiente hasta b = 0⁺ (solo b ≥ 0, sin continuar a b < 0), con DOP853 2×10⁻¹⁰/2×10⁻¹² y una repetición con tolerancias 100 veces más estrictas. Arranque en el primer paso aceptado con |p| ≥ 40 de 4.1.
4. **Criterios de (i):**
   - (C3) |db/dr| en el límite ≥ 1, es decir, encuentro transversal y no asintótico **[DECISIÓN: umbral]**;
   - (C4) la métrica límite en la carta de cara es definida positiva (mín. autovalor > 0 en mpmath con margen de 10³ sobre la diferencia float64/mpmath);
   - (C5) longitud finita (T* finito) y rapidez intrínseca en el límite = 1 a 10⁻⁶;
   - (C6) los pesos fuera de la cara → 0. Es estructural: w_k = 0 no se alcanza con P finito, así que el punto límite no pertenece a la familia original.
   - Esto distingue una salida del dominio de una singularidad removible de la carta P. float64 y mpmath **no** cuentan como verificaciones independientes (2.2 del anexo).
5. **T⁺** = T*(rayo designado) + F_T · δ_T, donde δ_T = |T*(tol) − T*(tol/100)| y **F_T = 10** **[DECISIÓN]**.

### 4.5 Cota y decisión — requisito (iii)
- U = A₀ + F_disc · δ_disc + Δ · L⁺ · (1 + 10·ε_θ), con:
  - Δ = T⁺ − t₀ y L⁺ por la fórmula de la sección 2 con κ = F_K · κ̂;
  - **F_disc = 10** **[DECISIÓN]**;
  - ε_θ = |L⁺(2048) − L⁺(1024)| / L⁺(2048), el error de la cuadratura angular.
- **T5 certificado** si se cumplen todas estas condiciones:
  - (i) C1–C6;
  - (ii) δ_disc ≤ 10⁻⁵;
  - V1–V4 válidas (sección 5);
  - **U ≤ 0.0195** **[DECISIÓN: margen; propuesta 2.5 % bajo 0.02]**.
- Si falla alguna, el resultado es **T5 no certificado**, con la razón (i), (ii), (iii) o V. **No se reajustan** t₀, factores ni margen después de ver resultados. Se reporta U/0.02 en todos los casos.

## 5. Validaciones (deben pasar para que el resultado cuente)
- **V1 — la cota acota (prueba de falsación).** Para j5, j7 y j8: aplicar la misma fórmula de t₀ a t₁ = primer paso con max|p| ≥ 40, donde el área se mide directamente. Se exige U(t₀→t₁) ≥ A₀(t₁) en los tres. Si falla en uno, la maquinaria es inválida y nada se certifica.
- **V2 — control negativo j8.** En j8, el disco nominal existe antes del escape: A medida = 0.0239 en t = 0.0861 < t* ≈ 0.0875. Aplicando la cota completa hasta T⁺ de j8, debe salir **U ≥ 0.0239** y T5 **no** certificado. Si j8 «se certificara», el procedimiento es inválido.
- **V3 — identidad de área** (4.2).
- **V4 — solapamientos** (C2 y float64/mpmath en 4.3).

## 6. Qué es riguroso y qué no
- **Riguroso** (dado lo que se mide): la cadena de la sección 2, que incluye la monotonía de A, la comparación de Jacobi, t*_min ≤ t*(rayo) y la estructura de la cara (C1, C6).
- **No riguroso, cubierto con factores declarados:**
  - el máximo muestreado de |K| (F_K);
  - el error global de DOP853, estimado por sensibilidad a tolerancias (F_T);
  - la discretización del área (F_disc);
  - la cuadratura angular (ε_θ).
- **No es aritmética de intervalos.** **[DECISIÓN D-T5-1]:** si «cota superior verificable» en 2.2 admite esta forma (desigualdades explícitas, cálculo reproducible y factores de seguridad declarados), o si exige intervalos. En este segundo caso, este protocolo solo daría «evidencia fuerte, no certificación» y habría que diseñar otra cosa.
- Las validaciones V1–V2 prueban que la cota no subestima en tres estados, no en general.

## 7. Ejecución y salidas
- **Dónde:** en el equipo del responsable, porque los estados están en `D:`. Solo lectura sobre los estados; carpeta de salida nueva `D:\RIPG_DATA\T2_A\expediente\certificacion_t5_<fecha>\`, con un JSON por caso, tablas CSV pequeñas y log. No se escribe en las carpetas del piloto.
- **Duración estimada:** unos 2 min de rayos por caso más la evaluación de K en mpmath para los ≈ 100 rayos del sector (minutos) más la carta de cara (segundos). Se entrega el comando exacto (ruta completa, `python -I`).
- **Informe:** `RESULTADO_certificacion_T5_<fecha>.md` en `piloto/certificacion_t5/`, con, por caso:
  - el estado (certificado o no certificado, con razón);
  - U, U/0.02, A₀, δ_disc, κ̂, T⁺, Δ, L⁺, C1–C6 y V1–V4;
  - la sensibilidad a t₀.

## 8. Decisiones adoptadas (2026-10-21 ≈14:24)
1. **D-T5-1:** para este diagnóstico, una cota numérica con desigualdades explícitas, cálculo reproducible y factores de seguridad declarados cuenta como «cota superior verificable» (2.2 del anexo). Queda declarado que **no es aritmética de intervalos** (sección 6). La revisión estadística de E2 puede exigir más; en ese caso, el resultado se reporta como evidencia fuerte y no como certificación.
2. **Factores:** F_K = 4 (sobre κ̂), F_T = 10, F_disc = 10. **Margen:** U ≤ 0.0195.
3. **Tolerancias:** V3 ≤ 10⁻⁵ relativo; C3: |db/dr| ≥ 1 en el límite.
4. **j8 se incluye** como control (V1 y V2). No cambia su estado ni su reevaluación D4.
5. **Orden:** se corre ya, con este protocolo congelado, y el protocolo y el resultado se presentan **juntos** a la revisión estadística de E2. La congelación previa al cálculo es lo que protege contra elegir el análisis después de ver los datos.

## 9. Código (procedimiento añadido al congelar, no altera el método)
- Los scripts se escriben **después** de esta congelación. Antes de correrlos se registran sus SHA-256 en `MANIFIESTO_scripts_certificacion_T5.sha256` (commit propio).
- **Pruebas previas solo en casos que no entran en la decisión:** split8_j6_true (sin escape: rayos, área, Jacobi, V3, solapamiento float64/mpmath) y geometrías sintéticas (para la carta de cara). **No se ejecuta nada sobre j5, j7 ni j8 antes de registrar los hashes.** Si un script cambia después de registrarlo, se registra la nueva versión y se explica el motivo; ninguna corrida con una versión anterior se descarta en silencio.
