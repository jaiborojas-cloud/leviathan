# DIN-borde D4 — resultado exploratorio (2026-10-24)

**Naturaleza:** exploratorio, según `PLAN_D4_exploratorio.md` (commit `7244cfb`, registrado antes de correr). `d4_confianza.py` se corrió en el equipo del responsable. Salidas:
- `d4/d4_estados.csv`, 3120 estados, SHA `223b4aba…a258`;
- `d4/d4_resumen.json`, SHA `f15abd50…205e`.

Los datos ya se usaron en T2-A1, así que **no confirma nada**.

## Hallazgos
1. **k* es el ejemplo de validación con menor confianza.** La fracción de estados con k* = argmin p(y) es 97.6 % en el update 5 y 100 %, 99.9 % y 100 % en los updates 50, 150 y 250. El rango de k* es 1 en todos los cuartiles.
2. **Desde el update 50, ρ_borde es casi una función monótona de la confianza en ese ejemplo:**
   - Spearman global entre log ρ_borde y log(1 − p(y_k*)): 0.996 en el 50, 0.998 en el 150 y 0.998 en el 250;
   - dentro del split: 0.79–0.80;
   - en el update 5, antes del colapso, la relación no existe (0.04).
   No es una ley lineal en log-log: una recta ajustada sobre los updates 50–250 da pendiente 0.70 y R² 0.82.
3. **El resto del panel ya está aprendido.** La mediana de p(y) en el panel es 0.99999 o más desde el update 50. k* es el único ejemplo que queda: su p(y) mediano es 0.45–0.60, y está mal clasificado en ≈ 48 % de los estados.
4. **Cuándo se llega al borde (updates 50–250):**
   - con k* bien clasificado, ρ_borde tiene mediana 0.051 y 55 % de los estados queda por debajo de r*;
   - con k* mal clasificado, la mediana es 1.01 y ningún estado queda por debajo de r*.

## Lectura
En esta familia, la distancia perspectival al borde **mide cuánta incertidumbre le queda al modelo en su ejemplo de validación más difícil**. Cuando el entrenamiento resuelve también ese ejemplo, la geometría toca el borde. Eso explica a la vez cuatro cosas:
- **el colapso a rango 1:** solo un gradiente sigue vivo;
- **el piso 1/n:** M ≈ e_k e_kᵀ;
- **el dominio del split:** los datos fijan cuál es el ejemplo difícil y si se puede aprender;
- **por qué X del update 5 no lo anticipaba:** el ejemplo dominante cambia después del update 5 y su resolución depende del entrenamiento posterior.

**Límites:** una sola familia (WineMLP, panel de 27 ejemplos de validación). M depende de cómo se construye a partir de R y F; con un panel más grande o con otra regularización, el mecanismo podría verse distinto. Es una hipótesis mecánica para un prerregistro futuro con cohorte nueva, no un resultado confirmatorio.
