# Registro E16-O

- 2026-10-21: base main 6d23a12, con N integrado. Rama independiente en el
  checkout existente; T2-A intacto.
- 6a6c21e: protocolo, configuración, grupos y hashes congelados antes de medir.
- 681a804: implementación congelada antes de ejecutar; controles sintéticos
  de marcado y conservación de polígonos pasan.
- ae0b3bc: primera corrida completa conservada, global INCONCLUSIVE. Once
  caminos válidos, ocho optimizaciones, 1428 probes válidos. Cuatro bisecciones
  por candidato, 128→132 segmentos; ocho checks de forma inconclusos.
- Primera corrida: 53,10 s y 81,38 MiB, dentro del presupuesto. El máximo de
  pendiente crece junto al nodo heredado t=0,984375, no en t=1.
- La primera verificación se detuvo leyendo el formato np.float64 de NumPy;
  se corrigió sólo el lector y se conserva la nota SERIALIZATION_NOTE.md.
- Figura derivada exclusivamente de CSV. Documentación separa acuerdo de
  Hausdorff, forma al mismo t e indicador terminal; no declara convergencia.
- Reproducción completada: 17 salidas científicas idénticas byte por byte;
  segunda corrida 52,81 s, dentro del presupuesto. Marcado, anidamiento,
  fuente N128, congelación y alcance verificados. Enlaces y whitespace revisados.
