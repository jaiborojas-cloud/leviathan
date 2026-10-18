# Organización documental e integridad

La remesa se conserva como unidad en `docs/archive/import-2026-10-17/`, con sus rutas internas, manifiesto y verificador originales. Los resúmenes previos se preservan en `docs/archive/review-before-import/`; describen la evidencia disponible antes de la importación y no el estado actual. No se ejecutaron experimentos.

Se restauraron los saltos CRLF de 71 CSV: cada candidato se aceptó sólo tras coincidir con el SHA-256 original, sin regenerar ni alterar hashes esperados. `.gitattributes` desactiva normalización de texto en el archivo histórico. El notebook original permanece en su ruta para conservar referencias por celda.

La biblioteca común `src/ripg/` no se crea artificialmente: extraer código científico será una tarea independiente con pruebas de equivalencia. Los scripts archivados son fuentes históricas, no una API estable.

Archivos reparados:

- `SOURCE_CATALOG.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/before/cohort_manifest.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/before/manifest.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/before/outcomes.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/before/task_log.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/before/visits.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/cohort_manifest.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/incident_register.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/outcomes.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/predictors_locked.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/task_log.csv`
- `extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/visits.csv`
- `extracted/Leviathan_T2A_diagnostico_paso139/diagnostic139/all_rays.csv`
- `originals/Leviathan/Repro/E15_B7_estadisticas.csv`
- `originals/Leviathan/Repro/E15_B7_fuentes.csv`
- `originals/Leviathan/Repro/E15_B8_diferencias_pareadas.csv`
- `originals/Leviathan/Repro/E15_B8_estadisticas.csv`
- `originals/Leviathan/Repro/E15_B8_fuentes.csv`
- `originals/Leviathan/Repro/E15_B8_poblacion_mesh_independent.csv`
- `originals/Leviathan/Repro/E15_B8_resumen_poblacional.csv`
- `originals/Leviathan/Repro/E15_T1_A/correlations.csv`
- `originals/Leviathan/Repro/E15_T1_A/hierarchical_correlations.csv`
- `originals/Leviathan/Repro/E15_T1_A/inherited_results_states.csv`
- `originals/Leviathan/Repro/E15_T1_A/linked_geometry.csv`
- `originals/Leviathan/Repro/E15_T1_A/manifest.csv`
- `originals/Leviathan/Repro/E15_T1_A/split_summary.csv`
- `originals/Leviathan/Repro/E15_T1_A/state_results.csv`
- `originals/Leviathan/Repro/E15_T1_A/task_log.csv`
- `originals/Leviathan/Repro/E15_T1_B/T1A_linked_geometry.csv`
- `originals/Leviathan/Repro/E15_T1_B/T1A_state_results.csv`
- `originals/Leviathan/Repro/E15_T1_B/area_effect.csv`
- `originals/Leviathan/Repro/E15_T1_B/common_radius_results.csv`
- `originals/Leviathan/Repro/E15_T1_B/correlations.csv`
- `originals/Leviathan/Repro/E15_T1_B/dimensionless_candidates.csv`
- `originals/Leviathan/Repro/E15_T1_B/large_residuals.csv`
- `originals/Leviathan/Repro/E15_T1_B/manifest.csv`
- `originals/Leviathan/Repro/E15_T1_B/positive_cases.csv`
- `originals/Leviathan/Repro/E15_T1_B/residual_feature_correlations.csv`
- `originals/Leviathan/Repro/E15_T1_B/residuals.csv`
- `originals/Leviathan/Repro/E15_T1_B/stability.csv`
- `originals/Leviathan/Repro/E15_T1_B/task_log.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_A2_area_diagnostics.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_A2_comparison.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_A2_intersections.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_A2_jacobi_summary.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_A2_resolution_phase_matrix.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_estados.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_fuentes.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_pares.csv`
- `originals/Leviathan/Repro/Leviathan_E15_C1_particiones.csv`
- `originals/Leviathan/Repro/T2_A/cohort_manifest.csv`
- `originals/Leviathan/Repro/T2_A/incident_register.csv`
- `originals/Leviathan/Repro/T2_A/manifest.csv`
- `originals/Leviathan/Repro/T2_A/original_zip_manifest.csv`
- `originals/Leviathan/Repro/T2_A/outcomes.csv`
- `originals/Leviathan/Repro/T2_A/predictors_locked.csv`
- `originals/Leviathan/Repro/T2_A/restoration_b743_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/restoration_b751_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/restoration_b759_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/restoration_b763_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/restoration_b783_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/restoration_b800_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/restoration_f001_original_manifest.csv`
- `originals/Leviathan/Repro/T2_A/task_log.csv`
- `originals/Leviathan/Repro/T2_A/visits.csv`
- `originals/Leviathan/Repro/T2_A0/cohort_seeds.csv`
- `originals/Leviathan/Repro/T2_A0/event_sensitivity.csv`
- `originals/Leviathan/Repro/T2_A0/interval_width_examples.csv`
- `originals/Leviathan/Repro/T2_A0/manifest.csv`
- `originals/Leviathan/Repro/T2_A0/optimistic_power_benchmark.csv`
- `originals/Leviathan/Repro/T2_A0/sample_size_sensitivity.csv`
