# Avances E16-X

- W permanece como dependencia sin merge automático. Se incorpora main
  f158120 y su trabajo T2_A1, conservándolo intacto; base congelada en config.
- Diseño e773c9d e implementación 9acbe96 congelados antes de medir.
- Primera medición preservada en 214d048: doce caminos, 72 ensayos,
  70 válidos, dos inviables, cero inválidos y 627 comprobaciones PASS.
- Cuatro mínimos restringidos negativos resueltos y descenso bilateral
  para sus tres pasos; mínimos UNKNOWN, sin reinterpretación de W.
- Primera corrida 65,357 s / 71,160 MiB, dentro del presupuesto.
- Figura derivada sólo de CSV y revisada visualmente.
- PASS_REPRODUCTION: once salidas científicas idénticas byte por byte;
  segunda corrida 64,954 s, dentro del presupuesto. Espectros, entrelazado,
  comparación con W, pendientes, parejas, signos, costes y alcance verificados.
