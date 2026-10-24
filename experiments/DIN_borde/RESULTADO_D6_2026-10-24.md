# DIN-borde D6 — ¿cuándo se decide el destino? Resultado (2026-10-24)

**Naturaleza:** descubrimiento exploratorio, según `PLAN_D6_cuando_se_decide.md` (commit `f11f2b4`, registrado antes de correr). El script es `d6_cuando.py`, con SHA `391dbb65…9703` (coincide con el de la rama). Salidas:
- `d6/PROGRESO_d6.csv`, 3900 filas, SHA `4bd99817…ac9`;
- `d6/RESUMEN_d6.json`, SHA `378fad51…7486`.

**Compuerta de reproducción:** el estado del update 50 coincide byte a byte con el de la fase 2 en las **780 de 780** trayectorias. Errores: 0. Antes se hizo una prueba con 1 trayectoria en otra carpeta.

## Curva de predictibilidad de log ρ_borde(250), dentro del split
Los p son bilaterales, con 5000 permutaciones y descriptivos.

| t | W de log ρ(t) | pares / impares | W de log(1 − p_min,val(t)) | W_adj de esa confianza sobre ρ(t) | W de la precisión en validación (t) | k*(t) = k*(250) | M_kk,max/tr | ρ(t), mediana | mal clasificados en entrenamiento (mediana) |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0.016 (p 0.71) | 0.04 / −0.01 | 0.111 (p 0.006) | 0.113 (p 0.004) | −0.144 | 0.32 | 0.07 | 4.60 | — |
| 10 | 0.040 (p 0.32) | 0.06 / 0.02 | **0.225** | **0.218** (p 2·10⁻⁴) | −0.174 | 0.45 | 0.14 | 1.87 | 3 |
| 20 | 0.374 | 0.42 / 0.33 | 0.416 | 0.119 (p 0.005) | −0.290 | 0.66 | 0.51 | 0.37 | 1 |
| **30** | **0.580** | **0.56 / 0.60** | 0.581 | 0.029 (p 0.48) | −0.387 | 0.79 | 0.74 | 0.23 | 0 |
| 40 | 0.674 | 0.61 / 0.73 | 0.656 | 0.005 | −0.453 | 0.83 | 0.84 | 0.24 | 0 |
| 50 | 0.766 | 0.76 / 0.77 | 0.753 | — | −0.383 | 0.88 | 0.88 | 0.24 | — |

## Lectura
1. **El destino se decide entre los updates 10 y 30.**
   - En el update 10, ρ_borde todavía no predice nada (W = 0.04).
   - En el 20 empieza (0.37) y en el 30 ya predice bien (0.58).
   - Coincide con el colapso de M: la fracción de la traza en un ejemplo pasa de 0.14 a 0.74.
   - Coincide también con la memorización del entrenamiento: la mediana de mal clasificados en entrenamiento pasa de 3 a 0.
2. **Regla registrada:** el primer t en el que W(log ρ(t)) ≥ 0.5, con el mismo signo en las dos mitades, es **t* = 30**.
3. **Señal temprana, antes del colapso.** En el update 10, la **incertidumbre del ejemplo de validación más difícil**, log(1 − p_min), predice el destino con W = 0.225 y **aporta más allá de ρ(10)**: W_adj = 0.218, p ≈ 2·10⁻⁴. Es el único caso en D5 y D6 que pasa |W_adj| > 0.2. En el update 10 todavía no es una tautología respecto de M, porque M no ha colapsado (0.14) y ρ(10) no predice nada por sí solo. Ya en el update 5 hay algo: W_adj = 0.11.
4. **Precisión en validación:** se asocia cada vez más con acercarse al borde. W va de −0.14 en el update 5 a −0.45 en el 40.

## Candidatos para DIN-C1 (los decide el responsable)
- **(A) Regla registrada:** log ρ_borde(30) predice log ρ_borde(250) dentro del split. Es persistencia a partir del momento del colapso: tiene potencia alta y es poco sorprendente.
- **(B) Señal temprana, no tautológica:** log(1 − p_min,val) en el update 10 predice log ρ_borde(250) dentro del split, **ajustado por log ρ_borde(10)**. W_adj descubierto = 0.22. Es la versión precisa de la pregunta original de T2: algo temprano anticipa la degeneración más allá de la geometría del momento.
- **Sesgo a declarar:** B se eligió entre varios candidatos y momentos (6 updates × 3 medidas), así que el efecto descubierto está inflado por la selección. La potencia del confirmatorio debe calcularse con un efecto menor, por ejemplo 0.12–0.15.
