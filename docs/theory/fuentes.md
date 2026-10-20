# Fuentes, precedencia y faltantes

Compendio preparado desde el checkout de `main` en el commit
`d2164422e8a556cb7bcf029eaf93004bf7bc6c0b`. Es una reorganización documental:
no se reejecutó el notebook ni experimentos, no se verificaron hipótesis nuevas
y no se modificaron archivos de `experiments/T2_A/claude` ni de otras etapas.
Los hashes de fuentes locales consultadas están en `source_manifest.csv`.

## Fuentes de las formulaciones

| Fuente | Tipo y uso en este compendio |
|---|---|
| [RIPG_contexto_vigente_axioma](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md) | Síntesis técnica histórica: definición, axioma tras E9-G, cociente, regularización y límites |
| [E11-J](../archive/import-2026-10-17/originals/E11J_regularizacion_explicita_y_estado_RIPG.md) | Informe de etapa: estimando regularizado, referencia transportada y covariancia |
| [E11-N](../archive/import-2026-10-17/originals/E11N_atribucion_schur_y_estado_RIPG.md) | Informe de etapa: atribución de métricas mediante Schur con escala común |
| [E12-B](../archive/import-2026-10-17/originals/E12B_campo_no_lineal_admisible_y_estado_RIPG.md) | Familia exponencial, scores, admisibilidad y construcción del campo |
| [E12-C](../archive/import-2026-10-17/originals/E12C_conexion_curvatura_y_estado_RIPG.md) | Derivadas, conexión y convención de Riemann y curvatura |
| [E12-E](../archive/import-2026-10-17/originals/E12E_holonomia_control_derivado_y_cierre_E12.md) | Transporte paralelo, holonomía y cierre con alcance delimitado |
| [E13, cierre](../archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md) | Estimando regional y cierre externo INCONCLUSIVE; prevalece sobre su plan |
| [E15-B1, estado](../archive/import-2026-10-17/originals/Leviathan_RIPG_estado_E15-B1_2026-09-24.md) | Síntesis de atribución por capas, Shapley y preguntas de profundidad |
| [E15-B8, cierre](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-B8_cierre_y_E15-C_inicio.md) | Reporte de magnitud, localización y alcance poblacional acotado |
| [T1, diseño](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1_diseno_topologia_local.md) | Distingue conjugados, corte, Maxwell, inyectividad y frontera |
| [T2-A0, prerregistro](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md) | Fuente histórica de Jacobi, Dexp, concentración y formulación temporal; no resultado de seguimiento |
| [Mapa de rutas, DOCX](../archive/import-2026-10-17/originals/RIPG_mapa_rutas_investigacion.docx) y [transcripción derivada](../archive/import-2026-10-17/RUTAS_INVESTIGACION_texto_extraido.md) | Propuestas exploratorias de dimensión mayor, composición y aplicaciones; la transcripción no es una fuente independiente |
| [E16, especificación](../../experiments/E16/mathematical_spec.md) y [errata](../../experiments/E16/ERRATA_v2.md) | Formalización reciente de mapas, descenso y cadena; incorporar corrección manual sin borrar su historial |
| [E16-B, cierre](../../experiments/E16/B/CONCLUSION.md) | Control instrumental de red nueva sin entrenamiento; rango conserva INCONCLUSIVE |
| [E16-C, especificación en commit externo a esta base](https://github.com/jaiborojas-cloud/leviathan/blob/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C/mathematical_spec.md) | Procedencia adicional del error transportado; no se incorpora código ni se importa esa rama |

Las expresiones del gradiente métrico, distancia SPD, longitud, conexión,
curvatura seccional, Jacobi, ecuación de Gauss, Shapley y perturbación de valores
singulares se explicitan como herramientas matemáticas estándar bajo sus
hipótesis. Esta exposición no las presenta como descubrimientos de RIPG ni como
pruebas experimentales de generalización. Las consecuencias algebraicas se
separan de los hallazgos reportados en los informes.

## Precedencia entre documentos

Los informes de ejecución y cierres de una etapa prevalecen sobre sus planes.
El [documento de transferencia de septiembre en docs](../Leviathan_RIPG_estado_investigacion_2026-09-23.md)
es histórico y termina con el plan E13-C/D: no debe tomarse como cierre actual.
El [estado de septiembre archivado](../archive/import-2026-10-17/originals/Leviathan_RIPG_estado_investigacion_2026-09-23.md)
contiene material posterior de cierre. Comparten nombre pero no bytes ni alcance;
no se sustituyen entre sí. El nombre 2026-09-23 tampoco borra las fechas internas
que puedan indicar otro corte.

La [revisión previa al import](../archive/review-before-import/docs/foundations/mathematical-framework.md)
decía que faltaban axioma y formulación regularizada; esos faltantes se recuperaron
luego. Se conserva como fotografía histórica, no como descripción vigente.
El [estado científico](../research-status.md) es otra síntesis con corte explícito,
no una lectura en tiempo real del seguimiento ni de ramas de trabajo.

## Faltantes y límites explícitos

1. Definición histórica de `relevance_covariant_derivative`, procedencia de
   salidas E6 y cierres autónomos E9/E14 siguen en el [inventario existente](../handoff/missing-sources.md).
2. E15-B1 reporta $s_\ell$ y $H_\phi$ pero las fuentes seleccionadas no fijan
   todas sus normalizaciones con Shapley negativos y caso vacío. No se reconstruyen
   desde medianas o nombres. La fórmula estándar de Shapley no reemplaza ese contrato.
3. No se presupone acceso a conversaciones, pesos externos o bibliotecas privadas.
   Las referencias archivadas a archivos voluminosos no son equivalentes a un dataset público.
4. La suavidad de redes, validez de dominios, rango constante del cociente y
   canonicidad de la referencia son hipótesis de construcción, no garantías universales.

## Integridad de esta entrega

`review.json` registra la revisión documental, el commit base y el identificador
del árbol Git protegido. Se verifican enlaces locales, delimitadores matemáticos,
hashes de fuentes y alcance del diff. Los verificadores de archivos históricos
sólo cotejan bytes; no entrenan ni recalculan geometría. No se introducen scripts
experimentales, cachés, entornos, checkpoints ni copias de fuentes voluminosas.
