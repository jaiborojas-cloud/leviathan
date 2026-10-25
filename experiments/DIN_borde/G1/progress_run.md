# Ejecución G1 y procedencia

- Base maina532c3c. Diseño bb7fedf antes del primer código28c6395.
- Sólo Iris cargado. Guardas bloquean otros datasets, T2 y DIN-C1; se usan
  core.make_geom_state/subset_M originales y Geometry/rho sin parches.
- 200 entrenamientos físicos completos,300 trayectorias por familia en total,2100
  estados.2846.614779s con dos procesos, un hilo por librería.
- Todos los estados tienen M/rho básicos válidos.120 auditorías completas;
  R2739/40, P6037/40, W2740/40. P60 no alcanza95% y no se cambia su regla.
- Análisis de H1–H5 por código b96b277 comprometido antes de ejecutarlo.
  H1R27=79% frente a80% exigido se conserva INDETERMINADO. No se recortó
  cohorte ni se sustituyeron semillas, tiempos o resultados.
- Una discrepancia angular motivó suplemento SEPARADO, posterior explícito:
  diseño6512ffb antes del código0ace87b. Se ejecutó después de la corrida
  principal, sin más de dos procesos numéricos. No cambia H1–H5.
- Un testigo axial en P60 confirma una limitación del retorno nativo como
  mínimo numérico. Los tres centinelas no prueban ausencia de otros errores.
- Resúmenes de p del dominante y escala desde logits/M ya archivados:
  código00e3af1, sin nuevos entrenamientos ni geometría.
- Figura inspeccionada visualmente; medianas/IQR y límites claros.
  No hay p-valores confirmatorios ni acceso a estados o tablas de Wine/C1.
