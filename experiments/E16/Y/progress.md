# Avances E16-Y

- Dependencias W/X conservadas; se incorpora main461bfda y sus reglas
  .gitattributes sin cambios. Toda etapa previa y T2_A/T2_A1 intacta.
- Diseño c826975 e implementación f60a896 congelados antes de medir.
- Primera medición preservada en 2332ba6: 24 problemas, 559 comprobaciones
  PASS, 9.480 componentes nuevas y 14.192 autovalores restringidos.
- Doce testigos MP negativos: cuatro coarse y ocho fine cuadráticos;
  el nuevo gradiente fino impide interpretar esto como mínimos estacionarios.
- Primera corrida 139,893 s / 192,156 MiB, dentro del presupuesto.
- Figura sólo de CSV revisada visualmente. Convención de campos coarse
  marcados con cero explicitada en README, sin atribuirles FD nueva.
- PASS_REPRODUCTION: nueve salidas científicas idénticas byte por byte;
  segunda corrida 142,609 s, dentro del presupuesto. Dos niveles, gradientes,
  masa, espectros, testigos, costes y alcance reconstruidos/verificados.
