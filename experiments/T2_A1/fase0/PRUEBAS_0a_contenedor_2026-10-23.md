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

## v2 (2026-10-23 ≈10:50), tras el primer intento de P2
- **Defecto de implementación (v1):** en Windows, el `ProcessPoolExecutor` de `un_caso` crea sus procesos con *spawn* y serializa `_mp_init` y `_k_mp_lote` por el nombre del módulo `certificar_t5`. v1 cargaba ese módulo desde su ruta sin registrarlo, así que los procesos hijos no podían importarlo: `PicklingError: Can't pickle <function _mp_init>: import of module 'certificar_t5' failed`. En el contenedor (Linux, *fork*) no aparecía.
- **Intento afectado:** P2 de j5 en el equipo del responsable (2026-10-23 ≈10:40), que falló a los 104 s, antes de calcular la cota. j7 se lanzó a continuación con la misma versión. No se calculó U de ningún caso con v1. Las salidas de ese intento se conservan en `D:\RIPG_DATA\T2_A1\fase0a\P2_2026-10-23\`.
- **Corrección (único cambio):** `cargar_t5` registra el módulo en `sys.modules` y añade su carpeta a `sys.path`. No cambia ningún cálculo; `certificar_t5.py` sigue siendo v4 sin cambios.
- **Pruebas:** reproducción del fallo con *spawn* forzado en Linux (v1 falla igual que en Windows; v2 evalúa K en mpmath en los procesos hijos); regresión del lote ficticio (mismas D) y de j6 forzado (U = 0.02980103).
- Es la **versión 2 de 3** permitidas por D0-3.
- SHA-256 v2: `254ebd83f11e3459f48bc94a2a54fe4019cddfab3341a4db7aaeac54d7789663`.
