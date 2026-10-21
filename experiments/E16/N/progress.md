# Registro E16-N

- 2026-10-21: base main 63b8589, que integra E16-M. Se crea rama independiente.
- e21d2f6: diseño, grupos, configuración y hashes congelados antes de mediciones.
- e6af3bd: implementación y nota de cota convexa adicional antes de medir
  curvas M/N. Sólo se habían ejecutado controles sintéticos del estimador.
- d5ce5e0: primera corrida conservada íntegra, global INCONCLUSIVE. Nueve
  optimizaciones y 21 comparaciones de curvas. Ocho checks inconclusos;
  todos corresponden a forma o Hausdorff, no a gradiente ni integración.
- Figura derivada de CSV: comparación de Q0 y refinamientos, sin reoptimizar.
- Verificador: congelación, hashes, alcance, controles geométricos y
  reproducción exacta de las 14 salidas científicas; recursos por separado.
- Reproducción completada: 14 salidas científicas idénticas byte por byte;
  segunda corrida 20,41 s, dentro del presupuesto. Controles Hausdorff y
  anidamiento PASS. Primera corrida 21,07 s y 72,81 MiB, preservada sin cambios.
