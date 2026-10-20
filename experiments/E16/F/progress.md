# Registro E16-F

1. Base main `24807241f56859aba2445c6e7766963b19956072`, checkout existente,
   rama `research/e16-f-longitudes-caminos`. No incorpora la rama E aún no fusionada;
   usa directamente las fuentes D ya integradas, con hashes fijados.
2. Diseño y configuración congelados en `7717db2`, antes del programa y cálculo.
3. Primera corrida: 21,50 s, 38,40 MiB, un hilo; presupuesto cumplido.
   324 longitudes: 239 PASS_NUMERICAL, 85 INCONCLUSIVE, cero FAIL.
   12 426 controles: 12 202 PASS, 224 INCONCLUSIVE, cero FAIL.
4. Código, resultados y verificador inicial preservados en `3a0f6a3` antes de
   interpretar los límites. No se retocaron tolerancias, caminos ni refinamientos.
5. La clasificación de causas de la conclusión se obtiene de `positive_global`
   y los controles de cada caso; es diagnóstico posterior, no hipótesis previa.
   No se efectuó una corrida con ajustes para resolver los inconclusos.

La reproducción se registra por separado de la validez científica. Una salida
idéntica puede reproducir precisamente un resultado inconcluso.
6. Reproducción: cinco salidas científicas idénticas byte a byte; 25,71 s dentro
   del presupuesto. Hashes, diseño congelado, alcance y T2-A comprobados.
   `git diff --check` sin errores. El estado científico sigue INCONCLUSIVE.
