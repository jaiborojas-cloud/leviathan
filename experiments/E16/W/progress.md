# Avances E16-W

- Base a00cbf6, V integrado en main. S/T/U/V y T2_A/T2_A1 intactos.
- Diseño dfa1a66 e implementación 0619132 congelados antes de medir.
- Primera medición preservada en b0b66d3: 144 ensayos, 140 válidos,
  cuatro inviables y cero inválidos; 1.144 comprobaciones PASS.
- Ocho rutas PROJECTED y cuatro SMALL_GRADIENT. Curvatura proyectada
  cuadrática positiva y aumento en ambos signos de todos sus pasos.
- Primera corrida 135,170 s / 62,898 MiB, dentro del presupuesto.
- Figura generada sólo de CSV y revisada visualmente.
- PASS_REPRODUCTION: nueve salidas científicas idénticas byte por byte;
  segunda corrida 129,791 s, dentro del presupuesto. Proyección, pendientes,
  parejas, signos, geometría, costes, fuentes y alcance verificados.
