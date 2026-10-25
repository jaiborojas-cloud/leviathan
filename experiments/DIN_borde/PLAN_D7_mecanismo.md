# DIN-borde D7 — ¿por qué predice la señal temprana? (plan exploratorio, 2026-10-25)

**Naturaleza:** **exploratorio**. Se registra antes de calcular. Usa solo tablas ya publicadas de los datos de descubrimiento: d1, d3, d4 y d6, es decir, los splits 12–167 de T2-A1. **No usa la cohorte de DIN-C1** (splits 168–323), que queda reservada. No confirma nada.

## Motivación
DIN-C1 confirmó que X(10) = log(1 − p_min,val) en el update 10 predice log ρ_borde(250) más allá de una base cúbica de log ρ_borde(10), con pendiente positiva. D4 mostró que ρ(250) sigue la incertidumbre del ejemplo dominante, k*: si k* está mal clasificado, ρ queda lejos del borde. G1 mostró que en Iris el ejemplo difícil casi nunca se resuelve y que la señal temprana no aparece.

**Hipótesis de mecanismo:** X(10) predice el borde final porque anticipa **si el ejemplo difícil quedará resuelto** en el update 250.

## Variables (por trayectoria)
- **X:** log(1 − p_min,val) en el update 10 (d6).
- **L10:** log ρ_borde(10) (d6).
- **Y:** log ρ_borde(250) (d1).
- **R:** log(1 − p(y_k*)) en el update 250 (d4), la incertidumbre final del dominante.
- **Mal:** 1 si k* está mal clasificado en el 250 (d4).
- **Mismo:** 1 si k_min(10) (d6) es igual a k*(250) (d3).

## Descriptivos
1. **Identidad del ejemplo:** la fracción con Mismo = 1, global y por update de origen (5, 10, 20, 30, 40, 50) si existe en d6.
2. **X anticipa la resolución:** W intra-split (media de Spearman) de X con R y con Mal; y lo mismo **ajustado por L10** (residuo de R sobre la base cúbica de L10).
3. **Mediación descriptiva del estimando de C1:**
   - **D_X** = incremento fuera de muestra de X sobre la base cúbica de L10 (definición de C1, 10 bloques, semilla 260010);
   - **D_X|R** = el mismo incremento con R añadido a la base.
   - Si D_X|R es cercano a 0, la información de X sobre Y pasa por R. Se reporta además la fracción 1 − D_X|R / D_X.
4. **Heterogeneidad:** D_X por separado en las trayectorias con Mismo = 1 y con Mismo = 0, y según Mal.
5. **Permutaciones:** dentro del split, 2000, semilla 300001. Los p son descriptivos, sin corrección por multiplicidad.

Sin umbrales ni veredictos. Salida: `d7/d7_resumen.json` y una nota de resultados.
