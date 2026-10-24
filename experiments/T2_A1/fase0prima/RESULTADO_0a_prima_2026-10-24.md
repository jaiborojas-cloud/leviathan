# T2-A1 fase 0a′ — instrumento ρ_borde: resultado (2026-10-24)

`rho_borde.py` (`d8ec69f8…416b`) y `pruebas_rho_borde.py` (`cc3c0152…b601`), registrados con commit `d736810` **antes** de correr. Contenedor Linux, Python 3.13, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1; `geometry.py` b4d1e0e4… archivado, sin cambios. Estados: los 80 de desarrollo del diagnóstico. Sin X.

## Compuerta 0a′: **PASA** (6/6)
| control | resultado |
|---|---|
| C1 cambio lineal de carta, f → f·A, en 4 estados de regímenes distintos | diferencia relativa ≤ 7×10⁻¹⁵ (tolerancia 10⁻⁶) |
| C2 traslación del panel, f → f + c | ≤ 4×10⁻¹⁶ (tolerancia 10⁻⁸) |
| C3 escala, M → 4M ⇒ ρ → 2ρ | exacta (0) |
| C4 contraste independiente en mpmath de 50 dígitos, en 4 direcciones (incluida la del mínimo) | ≤ 3.3×10⁻¹⁵ (tolerancia 10⁻⁸) |
| C5 reproducción del diagnóstico (commit `032a1d7`) | 80/80 valores **idénticos bit a bit** |
| C6 cota frente a escapes medidos | T* ≤ ρ_borde en los 8 (j5, j7 y j8 en u25; j5, j7 y j9 en u50; j9 en u150 y u250) |

## Estado
- **El instrumento queda congelado** en `rho_borde.py` v1 (`d8ec69f8…416b`). Es el mismo cálculo que el diagnóstico, con el mismo número de direcciones, orden de cuadratura y refinamiento.
- **Pendiente (no bloquea):** la validación externa E16-AG (otro agente), que mide lo ajustada que es la cota frente a la distancia real al borde con respuesta conocida.
- **Siguiente:** 0c′ (congelar el análisis: estadístico de W, ajuste por ρ_borde(u5), potencia simulada) y, antes de abrir X, ρ_borde(u5) de las 800 trayectorias.
