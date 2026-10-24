# T2-A1 fase 0c′ — análisis confirmatorio, BORRADOR v0 (2026-10-24)

**Estado:** borrador para el responsable y para revisión adversarial. **No congelado.** Concreta las secciones 3 y 4 del diseño v3 (`../DISENO_T2A1_BORRADOR_v3.md`, decisiones del 2026-10-24 10:11). Instrumento congelado: `rho_borde.py` (`d8ec69f8…416b`; `RESULTADO_0a_prima_2026-10-24.md`). X sigue cerrado.

## 1. Datos
- **Unidad:** trayectoria. Muestra confirmatoria: splits 12–167 (156 splits × 5 = 780). Los splits 8–11 (desarrollo) **no** entran.
- **Predictor:** X sellado (T2-A0). Se abre solo después de congelar este documento y de publicar por hash la tabla de ρ_borde(u5).
- **Desenlace primario:** Y_c = min(ρ_borde(u50), ρ_borde(u150), ρ_borde(u250)), en escala log. Si una visita falla numéricamente, el mínimo se toma sobre las disponibles y se reporta. Si fallan las tres, Y_c = ? y la trayectoria se excluye **del primario** (se reporta en las cotas).
- **Covariable:** L5 = log ρ_borde(u5), calculado con `rho_borde_u5.py` desde los `checkpoint_005`.

## 2. Estadístico W (dentro del split)
- **Por split s** (con ≥ 3 trayectorias con Y_c): r_s = correlación de Spearman entre X y −log Y_c.
- **Estadístico:** W = media de r_s sobre los splits válidos, cada uno con peso 1.
- **Empates en X:** se rompen por índice de inicialización, regla fijada antes de abrir X. Los empates en Y_c se tratan con rangos promedio.
- **Splits sin variación** (todos los Y_c iguales o todas las X iguales): r_s no está definido y el split sale del promedio. Se reporta el número de splits válidos.
- **p-valor (unilateral, H1: W > 0):** permutación de Y_c **dentro de cada split**, con 20 000 permutaciones y semilla 220021. p = (1 + #{W_perm ≥ W_obs}) / (1 + 20 000).

## 3. Condición de ajuste por ρ_borde(u5)
- **Modelo:** log Y_c = α_s + β · L5 + ε, con una ordenada por split y una pendiente común, por mínimos cuadrados sobre las 780 (o las disponibles). e = residuos.
- **W_adj:** el mismo estadístico de la sección 2 aplicado a (X, −e).
- **p-valor:** permutación de los residuos dentro del split (Freedman–Lane, sin reestimar β), 20 000 permutaciones, semilla 220022.
- **Éxito confirmatorio (diseño v3, sección 3):** p(W) < 0.05 **y** p(W_adj) < 0.05, ambos unilaterales. No hay corrección por multiplicidad: es una regla conjunta, más estricta que cada prueba por separado.
- **Veredictos:** PASS si se cumplen ambas; NOT_MET si los datos son válidos y no se cumplen; INCONCLUSIVE si hay menos de 120 splits válidos o más del 5 % de trayectorias con Y_c = ? **[DECISIÓN: umbrales]**.

## 4. Secundarios y complementarios (no deciden)
- Δ = log Y_c − L5, con W sobre (X, −Δ).
- G global: correlación de Spearman de X con −log Y_c en las 780, con IC por bootstrap de splits completos (20 000, semilla 220020, la del prerregistro).
- Y_b = 1 si alguna visita tiene ρ_borde < r*: precision@top10 % de X y lift.
- Comparadores geométricos sellados (C_A, Λ_0.1 %, R_eff) y no geométricos (pérdida, precisión y norma de pesos en el update 5): W de cada uno y W de X ajustado por cada uno.
- Fracción de visitas con fallo numérico.

## 5. Potencia (antes de abrir X)
Se simula con datos que no contienen X:
- la varianza dentro del split de log Y_c y su relación con L5, tomadas de la tabla de ρ_borde(u5) de las 800 y del desarrollo (splits 8–11, updates 25–250);
- X sintético con una correlación de Spearman dentro del split ρ_X ∈ {0.1, 0.2, 0.3} con el **residuo** (la parte de Y_c no explicada por L5).

Se reporta la potencia de la regla conjunta al 5 % con 156 splits. **Si la potencia para ρ_X = 0.2 es menor del 80 %, se informa antes de abrir X y el responsable decide si sigue** (diseño v2, sección 4). Script: `potencia_0c_prima.py` (por escribir).

## 6. Orden de operaciones
1. Correr `rho_borde_u5.py` y publicar por hash `rho_borde_u5.csv`. No necesita X ni visitas futuras.
2. Simular la potencia (sección 5).
3. Revisión adversarial de este documento; congelarlo con los umbrales **[DECISIÓN]** resueltos.
4. Abrir X: publicar tabla, rangos y hash.
5. Fase 2: 2340 visitas confirmatorias (entrenar hasta k y calcular ρ_borde), con informes operacionales sin desenlaces.
6. Análisis único según este documento.

## 7. Decisiones pendientes
- **Umbrales INCONCLUSIVE:** mínimo de splits válidos (propuesta: 120 de 156) y máximo de Y_c = ? (propuesta: 5 %).
- **Si la potencia sale baja:** seguir, ampliar visitas (más updates por trayectoria) o parar. Se decide con el resultado de la sección 5, antes de abrir X.
