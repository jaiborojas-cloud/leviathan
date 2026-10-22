# Registro E16-R

- 2026-10-22: base main f3523c7, que conserva Q e integra trabajo ajeno de
  T2-A. Se crea rama independiente en el checkout existente; T2-A intacto.
- 49029d8: protocolo, configuración, grupos y hashes congelados antes de medir.
  Escalado diádico, criterio KKT físico y costes separados; 900 s/512 MiB.
- 243e8c6: implementación congelada. Identidades de objetivo/cotas/coordenadas,
  regla de la cadena y validación MP del gradiente físico.
- 0966d44: primera corrida conservada íntegra. Global INCONCLUSIVE; cuatro
  caminos C0 pasan y ocho cuadráticos agotan iteraciones. KKT físico pasa
  en 4/4 escalados y 2/4 referencias cuadráticas.
- Primera corrida: 142,70 s y 94,21 MiB. Diez checks inconclusos de
  terminación/KKT, cero FAIL. No se rechazó ningún ensayo.
- Se conserva el diagnóstico espectral desfavorable del control tras escalar:
  no se altera el umbral ni se interpreta como curvatura negativa real.
- Figura derivada de CSV. Documentación separa KKT físico, residuo del solver,
  terminación, preparación del método y coste de evaluaciones.
- Reproducción completada: quince salidas científicas idénticas byte por byte;
  segunda corrida 143,76 s dentro del presupuesto. Escalas, KKT físico,
  coordenadas, costes, fuentes y congelación verificados.
- Recuperación de una desconexión del entorno durante el cierre documental,
  sin pérdida ni modificación de resultados. Enlaces, manifests y whitespace
  revisados. Q y todo T2-A conservan exactamente su contenido de la base.
