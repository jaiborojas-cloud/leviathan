# DIN-D9g-c: reproducción sin medir otra vez red o test

Diseñod5e694a → códigodb6687d → controles6d2852d → análisis. Fuentes exactas
copiadas por SHA desde D9g8996c2c y D9g-b417b80c en sources/. La entrada es la
CSV de1.500filas con Y=test250, c30 y las7medidas baratas ya archivadas. No se
requieren checkpoints ni arrays de etapas previas para repetir este análisis.

Entorno: Python3.12.14, NumPy2.3.5, Matplotlib3.10.8. En un clon separado con
salidas nuevas y un hilo BLAS, nunca sobrescribir resultados/fallos:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/D9g_c/scripts/controls_v1.py
python experiments/DIN_borde/D9g_c/scripts/analysis_v1.py
python experiments/DIN_borde/D9g_c/scripts/verify_v1.py
python experiments/DIN_borde/D9g_c/scripts/plot_v1.py
```

Cada script requiere fuentes/código comprometidos y escribe en modo exclusivo.
Ante un defecto: preservar versión/fallo y congelar enmienda antes de corregir.
No generar datos, entrenar, evaluar redes/test o medir geometría. No C2/T2/DIN-C1/
Wine/Iris. La guarda sólo permite D9g_c y su directorio de nuevos arrays.

La selección interna de λ y la compuerta B1/BR se vuelven a ejecutar por pipeline,
con cache de SVD/transformaciones sólo de variables invariantes a c. La selección
observada/primeras2permutaciones se contrasta sin cache en controles. Mu/sigma,
RMS y tamaños/rangos se registran por bloque interno/externo. El candidato se
proyecta nuevamente por OLS y se ajusta gamma para cada permutación; no se fija
la proyección observada. Ver matrices10×1000×33 de scores y10×1000 de λ.

Arrays en /workspace/work/din-d9g-c-v1-arrays/:5controles y4conjuntos reales,
con todos los D/SSE, λ/scores y predicciones completas del candidato en cada
permutación. external_manifest.csv guarda SHA/bytes. Son rutas locales, no hosting.
No se borra ni mueve nada. La salida JSON/CSV conserva las8estimaciones B1/BR y
sus mitades; no se usa un resultado descriptivo para cambiar la primaria.

La figura sólo lee las estimaciones archivadas. La conclusión deja visibles el
margen de adecuación, la definición elegida de candidato y las limitaciones de
una sola realización positiva pequeña. El responsable decide lo siguiente.
