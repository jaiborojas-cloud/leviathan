# Registro E16-P

- 2026-10-21: base main 73b6351, que integra el PR de O. Rama independiente en
  el checkout existente; T2-A intacto.
- 4f9e8e6: diseño, configuración, grupos y hashes congelados antes de medir.
  Dos variantes independientes, 132/264, con presupuesto de 600 s/512 MiB.
- 5a8d52f: implementación congelada. Gradientes AD/FD en ambas coordenadas
  para free; fuente con t binario exacto/s decimal como en O.
- 0ba0912: primera corrida preservada íntegra. Global INCONCLUSIVE; doce
  optimizaciones, cuatro alcanzan 4800 iteraciones. Ocho caminos pasan el
  protocolo completo; los doce pasan integración, SPD y concordancia AD/MP.
- Primera corrida: 98,51 s y 85,04 MiB. Seis checks inconclusos de
  estacionariedad/terminación; cero FAIL y cero ensayos rechazados.
- Figura derivada de CSV. Se distinguen el acuerdo de longitudes, la
  diferencia Hausdorff entre familias y los criterios de terminación.
- Reproducción completada: trece salidas científicas idénticas byte por byte;
  segunda corrida 98,52 s dentro del presupuesto. Fuente, congelación,
  familias, coordenadas, gradientes, controles y alcance verificados.
- Enlaces relativos, manifests y whitespace revisados; resultados y código
  científico de la primera corrida conservados sin modificaciones.
