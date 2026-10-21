# Registro E16-L

1. Rama sobre `b818eab` (K, PR #26), checkout existente; T2-A sin cambios propios.
2. Diseño y configuración congelados en `0212bcf` antes de programar/medir.
   Mallas 16/32/64, umbral de longitud 0,001 y criterios nuevos de forma previos.
3. Primera corrida: longitud del caso pendiente cumple el umbral, pero forma
   entre mallas y estabilidad de reinicios M32 no. Global INCONCLUSIVE:
   un caso inconcluso y un control PASS; 36/36 reinicios validados.
   2712 controles PASS y cuatro INCONCLUSIVE, cero FAIL.
   19,39 s y 70,32 MiB dentro de 300 s/512 MiB, un hilo.
4. Código y primera evidencia preservados en `48d09f7` antes de interpretar causas.
   No se relajaron umbrales ni se añadió otra malla o reinicio después de medir.
5. Figura derivada de los parámetros ya guardados; no ejecuta optimizaciones.
   El contraste local/completo del gradiente y las funciones K de hash fijo
   permiten comprobar la implementación sin recalcular fases anteriores.
6. Reproducción: diez salidas científicas idénticas byte a byte; 20,28 s dentro
   del presupuesto. Se reproducen los cuatro criterios inconclusos. Fuentes,
   congelación y alcance verificados; K no se reetiqueta.
7. Figura inspeccionada; sintaxis, enlaces relativos, manifests y `git diff --check`
   comprobados. Publicación contra main con J/K ya presentes, sin cambios T2-A.
