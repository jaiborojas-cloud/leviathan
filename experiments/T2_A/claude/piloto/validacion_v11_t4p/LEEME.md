# Salidas de validación de v1.1 (T1, T2, T4′) — equipo del responsable, 2026-10-20/21

Solo los JSON pequeños de cada corrida (no los checkpoints). Todo es validación y prueba de sensibilidad, **no son visitas del piloto ni asignan Y**.

| Directorio | Qué es |
|---|---|
| `validacion_t4p_j6_forzada` | j6 con T4′ forzada: `VISIT_EVALUATED`, `INJECTIVE_AT_NOMINAL_RADIUS`; `comparar_visita` contra v11: PASS global |
| `validacion_t4p_j6_cap22` | j6 con `--attempt-cap 22` (v1.0 pausada, T4′ recupera): mismo resultado, PASS global |
| `validacion_t4p_j17_forzada` | j17 con T4′ forzada. `REVISION_PENDIENTE.json` conserva la pausa `PAUSED_TIME_CAP` (driver sin T1); `VISITA_COMPLETA.json` es la corrida final (`VISIT_EVALUATED`, `GEOMETRIC_NONINJECTIVITY`, radio …136) |
| `sensibilidad_j17_m5e16` | prueba de sensibilidad, radio …086 (T4′ − 5×10⁻¹⁶): completa |
| `sensibilidad_j17_p5e15` | radio T4′ + 5×10⁻¹⁵: `PAUSED_TIME_CAP` por hibernación del equipo (tiempo de pared); omitida por decisión D6 |
| `validacion_v11_j17` | referencia v11 (calibración v1.0, radio …186) |

Lectura e interpretación: `E1/ANEXO_OPERATIVO_E1_v1.1_CONGELADO.md`, secciones 2.4 y 2.5.
