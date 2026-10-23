# T2-A1 fase 0a — pruebas de `instrumento_D.py` en el contenedor (2026-10-23)

**No cuentan como P2/P3** (esas se corren en el equipo del responsable). Contenedor Linux, Python 3.13, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1, 2 CPU; `geometry.py` b4d1e0e4… y `audit.py` del archivo importado (`docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/`). **No se ejecutó nada sobre j5, j7 ni j8.**

| prueba | qué | resultado |
|---|---|---|
| U₂ y relectura de U | `u2_desde` sobre la salida v4 guardada de la sintética s8 (resultado.json y rayos.csv) | U releído = U de v4 (diferencia relativa 0.0); U₂ = 1.22736×10⁻⁴ > U = 1.22735×10⁻⁴ |
| Paso 2, asignación (lote ficticio con j6 como estado) | 9 visitas: evaluada INJECTIVE, GEOMETRIC_NONINJECTIVITY e INCONCLUSIVE; pausa con radio nominal; pausa sin radio nominal (→ paso 3); ERROR; ERROR con repetición `u50_r1` evaluada; visita sin archivo terminal; visita no iniciada | D = 0, 1, ?, ?, ?(paso 3), ?, 0 (toma la repetición), ?, ?; Y por trayectoria 1, ?, ?. Razones como en la sección 2 del protocolo |
| **P4** sin escape | paso 3 sobre split8_j6_true/u25 sin forzar | «no se alcanza max\|p\| ≥ 10 antes de t_bound: sin escape en la carta P» → D = ?; 12 s |
| Tope de pared (D0-2) | paso 3 con tope de 3 s (solo prueba) | el proceso hijo y su grupo se terminan; D = ? con «tope de pared … agotado»; sin procesos huérfanos |
| **P1** equivalencia con v4 | `--cota-caso` sobre j6 con t₀ = 0.05 y T⁺ = 0.07883553716312588 forzados (la prueba previa de v4) | U = 0.02980102606 (v4: 0.02980103); κ̂ = 522.277; 115 s. U₂ no se calcula sin T* (forzado) |

La ruta completa de la vía C (escape real con carta de cara) no se puede ejercitar en el contenedor sin j5, j7 o j8: la cubren P2 y los controles por corrida.

## Versión registrada (antes de cualquier corrida sobre j5, j7, j8)
`instrumento_D.py` v1 SHA-256 `d539aaabf4851616899c8e5cc143da1f994e87592ce56501c9e4f6994460a500`.
