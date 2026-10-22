# Ejecutor de producción v12 — VALIDADO y registrado (2026-10-22)

- `visita_produccion_v12.py`: copia de `anexo_implementacion/visita_completa_instrumentada_v11_t4p.py` (congelado, `b7352b23…ceee`). El **único cambio** es que admite `--step` ∈ {25, 50, …, 250}: el modelo del update k se obtiene entrenando k − 5 updates desde `checkpoint_005.pt`. La geometría, la calibración (v1.0 y T4′), los topes T1/T2 y las auditorías no cambian. `diff` frente al congelado: solo docstring, argumentos, el bloque de entrenamiento, el campo `step` del resultado y la opción `--solo-entrenamiento`.
- `validar_ejecutor_v12.py`: validación previa al registro, que no produce visitas de producción.

| prueba | qué exige |
|---|---|
| A | en el update 25, `checkpoint.pt` y `state.npz` idénticos (SHA-256) a los de las 17 visitas del piloto en `piloto_visitas` |
| B | en 3 trayectorias y k = 50…250, el checkpoint directo coincide con reanudar desde k − 25 y entrenar 25 updates (≤ 1e-12, RNG idéntico) |
| C | visita completa de split8_j6_true en el update 25: `comparar_visita.py` PASS frente al piloto |

**Resultado (equipo del responsable, Windows, 2026-10-22 ≈00:05; `VALIDACION_EJECUTOR_v12_2026-10-22.json`): PASA.**
- A: 17/17 bit a bit.
- B: 27/27, con diferencia **exactamente 0** en parámetros y en el estado de Adam, y RNG idéntico.
- C: `comparar_visita` PASS; visita completa en 76 s.

Hashes registrados en `MANIFIESTO_ejecutor_v12_2026-10-22.sha256`, con commit propio. El ejecutor queda vigente para la producción, sujeto al plan de producción.
