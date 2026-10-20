# Registro E16-K

1. Rama sobre `f172d1e` (J, PR #25), checkout existente. J conserva su estado.
2. Protocolo y configuración congelados en `2a1a9d3` antes de programar y medir.
   Tres casos difíciles conocidos y dos controles explícitos; fase diagnóstica.
3. Primera corrida: cuatro casos PASS_NUMERICAL (dos difíciles y dos controles),
   uno INCONCLUSIVE por refinamiento 8→16. 85/85 reinicios validados, 15/15
   resoluciones válidas individualmente, 2085 controles PASS y uno INCONCLUSIVE.
   36,81 s y 68,60 MiB dentro de 300 s/512 MiB, un hilo.
4. Código y primera evidencia preservados en `49ee934`. No se ajustaron umbrales,
   reinicios o mallas tras medir; no se añadió otro refinamiento para forzar PASS.
5. El desacuerdo entre reinicios J no se atribuye a una causa única: K modifica
   simultáneamente método de integración, familias y reinicios.
6. Reproducción: nueve salidas científicas idénticas byte a byte; 36,41 s dentro
   del presupuesto. Hashes, congelación, fuentes y alcance verificados. El único
   criterio inconcluso se reproduce y conserva; no hubo ajustes posteriores.
7. Sintaxis, enlaces relativos, manifests finales y `git diff --check` comprobados.
   Publicación contra main, incluyendo J (#25 aún pendiente) sin cambios a su
   evidencia; el alcance nuevo propio es K y tres índices. T2-A no se modifica.
