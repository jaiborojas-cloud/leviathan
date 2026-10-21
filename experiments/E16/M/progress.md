# Registro E16-M

1. Base main `84d08a9` con L integrado; mismo checkout, rama independiente M.
2. Diseño, agrupamiento y configuración congelados en `eacfa4d` antes de programar.
   Dos representantes cuadráticos y un control; no se escoge por menor longitud.
3. Primera corrida v1 preservada en `1486ef1`: cuatro controles de forma inconclusos
   y uno artificial del lector de referencia redondeada. Se conservan salidas y
   copia exacta de su código. Ninguna salida fue borrada o reetiquetada.
4. Errata congelada en `456aa57`: comparar sólo la referencia archivada con su
   intervalo de redondeo, manteniendo tolerancias, solver, mallas y grupos.
   Implementación corregida registrada en `4dfbcdc` antes de ejecutar v2.
5. V2 preservada en `6eeaf8f`: global INCONCLUSIVE por cuatro diferencias de forma;
   nueve recorridos validados, seis optimizaciones. Q0/Q1 coinciden a 64 y 128;
   el pico cerca del extremo no cumple concentración de masa en la cola fijada.
   18,72 s y 72,70 MiB dentro de 300 s/512 MiB.
6. Siete tablas de geometría, gradientes y comparaciones idénticas entre v1/v2.
   Figura derivada de tablas guardadas; no ejecuta otra optimización.
7. Reproducción v2: trece salidas científicas idénticas byte a byte; 18,45 s.
   V1 conservada, siete tablas numéricas idénticas entre versiones, agrupamiento,
   congelación y fuentes verificados. No se cuenta como muestra nueva.
8. Figura inspeccionada; sintaxis, enlaces, XML SVG, manifests finales y
   `git diff --check` comprobados. Alcance propio M y tres índices;
   evidencia anterior y T2-A intactos. Sin fusión automática.
