# Formalización en Lean de DIN (piloto)

Lean v4.35.0 con Mathlib v4.35.0 (commit `56a005855ea17e0b0958f73ec801ae140b0a1679`). Se compila en GitHub Actions (`.github/workflows/lean.yml`) con la caché oficial de Mathlib. La compilación falla si alguna prueba queda incompleta (`sorry`).

**Alcance:** son enunciados sobre ℝ que respaldan la lógica del código. **No certifican resultados numéricos** (D, p, ρ), que se calculan en punto flotante. Ver la [propuesta](../docs/research-notes/lean-formalizacion.md).

| id | archivo | teorema(s) | qué respalda |
|---|---|---|---|
| L1 | `DIN/Confianza.lean` | `margen_nonpos`, `Xpanel_nonpos`, `R_le_X` | X ≤ 0 y R ≤ X (dominios del analista de F1) |
| L2 | `DIN/Borde.lean` | `rho_caras_le_rho_vert`, `min_superconjunto_le` | ρ_caras ≤ ρ_vert por construcción de `rho_borde_v2` |
| L3a | `DIN/Concentracion.lean` | `concentracion_mem` | c ∈ (0, 1] si la diagonal es no negativa y la traza positiva |
| L4 | `DIN/Softmax.lean` | `softmax_add_const`, `softmax_reducida_eq`, `logitsReducidos_desplazamiento` | La cabeza reducida da el mismo softmax y es invariante al desplazamiento común |
| L7 | `DIN/Recorte.lean` | `recortar_eq_self`, `recortar_mem`, `base_recortada_eq` | La base recortada de la primaria robusta coincide con la de C1 dentro del rango |

**Estado:** primera compilación limpia el 2026-11-02 (commit `fe6aa934`).

**Pendientes:**
- L3 completo: M es semidefinida positiva, y por lo tanto su diagonal es ≥ 0.
- L5: la identidad de Woodbury.
- L6: invariancia afín de la base.
- L8: validez del p de permutación.
