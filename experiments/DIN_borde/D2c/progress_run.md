# Progreso posterior al diseño

- Diseño congeladoa6ad5d0 después de lectura; código0f22130 antes de correr.
- Sujeto fijado6b17d25, copias byte por byte; no se modificó rama de C1.
- Corrida v1 completa153.7437467s:32 comparaciones,17 CLI originales,
  2000 simulaciones,15 sensibilidades a5000. Cero errores propios.
- A2 todas PASS; D/p reproducidos. A1/A3 defectos de input/decisión probados,
  no un desacuerdo entre dos implementaciones del estadístico.
- Los4 errores de proceso del original se preservan con stdout/stderr;
  no hay sustitución de casos ni reejecución después de mirar resultados.
- Campo source_lines del control de cuerda impreciso: ERRATAS_METADATA.md
  identifica50–55 por AST sin alterar archivo ni resultado numérico.
- Postproceso/verificador comprometidos09c1b1a; resumen desde las mismas
  salidas. No se abrió ningún dato adicional de T2.
- Recomendación entregada sin editar C1 ni decidir la congelación.
