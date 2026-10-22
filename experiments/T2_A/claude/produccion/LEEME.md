# Ejecutor de producción (candidato v12, no vigente hasta validarlo y registrar su hash)

- `visita_produccion_v12.py`: copia de `anexo_implementacion/visita_completa_instrumentada_v11_t4p.py` (congelado, `b7352b23…ceee`). El **único cambio** es que admite `--step` ∈ {25, 50, …, 250}: el modelo del update k se obtiene entrenando k − 5 updates desde `checkpoint_005.pt`. La geometría, la calibración (v1.0 y T4′), los topes T1/T2 y las auditorías no cambian. `diff` frente al congelado: solo docstring, argumentos, el bloque de entrenamiento, el campo `step` del resultado y la opción `--solo-entrenamiento`.
- `validar_ejecutor_v12.py`: validación previa al registro, que no produce visitas de producción.

| prueba | qué exige |
|---|---|
| A | en el update 25, `checkpoint.pt` y `state.npz` idénticos (SHA-256) a los de las 17 visitas del piloto en `piloto_visitas` |
| B | en 3 trayectorias y k = 50…250, el checkpoint directo coincide con reanudar desde k − 25 y entrenar 25 updates (≤ 1e-12, RNG idéntico) |
| C | visita completa de split8_j6_true en el update 25: `comparar_visita.py` PASS frente al piloto |

Si pasa: registrar los hashes (ejecutor, salida de la validación) en un manifiesto, con commit propio, antes del lote 0.
