# DIN-borde D4 — ¿k* es el ejemplo difícil? (plan exploratorio, 2026-10-24)

**Naturaleza:** **exploratorio**. Se registra antes de calcular. Mismos estados que D1 y D3. No confirma nada.

## Medidas
Para cada trayectoria de los splits 12–167 y cada update (5, 50, 150 y 250), se carga el checkpoint correspondiente y se calcula p(y_n) en los 27 ejemplos de validación (el panel). Se registran:
- k_min, el ejemplo con menor p(y);
- min p(y) y la mediana de p(y);
- el número de ejemplos mal clasificados;
- p(y) del ejemplo k* de D3, y el rango de ese ejemplo entre los 27 (1 = el de menor confianza).

## Descriptivos
1. Por update, fracción de estados con k* = k_min, y distribución del rango de k*.
2. Fracción de estados en que k* está mal clasificado.
3. Spearman, global y dentro del split, entre log ρ_borde y log(1 − p(y_k*)), y entre log ρ_borde y log(1 − min p(y)).
