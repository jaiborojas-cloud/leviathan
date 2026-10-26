# DIN-D9g-b: reproducción y conservación

Diseño9c598bc → códigob6e614a → controles062a1ae → covariables99ca5a1 → análisis.
No se ejecuta ninguna etapa previa ni se cambia un archivo original. D9g se conserva
por commit8996c2c y SHA en sources/D9g/, porque PR#91 aún no está en main. La pérdida
test250 y c30/base barata provienen exactamente de esa tabla; no se genera test.

Requisitos: Python3.12, NumPy2.3.5, SciPy1.17.0, Torch2.9.1+cpu, Matplotlib3.10.8,
y los 1.800 archivos G3 de input_manifest.csv disponibles en sus rutas originales.
En un clon separado con salidas nuevas, usar un hilo y no sobrescribir versiones:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/D9g_b/scripts/controls_v1.py
python experiments/DIN_borde/D9g_b/scripts/features_v1.py
python experiments/DIN_borde/D9g_b/scripts/analysis_v1.py
python experiments/DIN_borde/D9g_b/scripts/verify_v1.py
python experiments/DIN_borde/D9g_b/scripts/report_v1.py
```

Todos los scripts requieren código y fuentes comprometidos, y escriben en modo
exclusivo. Guardar cada salida antes del paso siguiente. Si aparece un defecto,
conservar el fallo y congelar una enmienda antes de corregir. No volver a entrenar,
generar test, reevaluar test o medir geometría. C2, Wine/Iris y T2/DIN-C1 están bloqueados.

features_v1 restaura pesos u30, hace forward sólo en panel y conserva logits,
márgenes y entropías por ejemplo. La norma incluye las seis matrices/sesgos de
parámetros, excluyendo Adam. Los pesos/datos originales quedan por referencia/SHA.
Las 1.500 filas y detalles de reproducción se publican; cualquier fallo se conserva.

Mu/sigma, escalas de términos, rango y condición por bloque constan en cada JSON
de análisis y analysis.json. Todos los 2.001 D/SSE por celda y los controles completos
se conservan como arrays en /workspace/work/din-d9g-b-v1-arrays/, fuera de Git.
external_manifest.csv identifica por SHA/bytes los 3.324 archivos usados, originales
y nuevos. Las rutas son locales, no un alojamiento externo descargable. Nada se borra.

report_v1 sólo presenta las 16 celdas ya archivadas y no añade pruebas ni bases.
La conclusión distingue la regla operacional de robustez de una explicación causal.
Se deja explícita la menor predicción de las bases flexibles solas y la falta de
potencia conocida de controles grandes para D pequeño. El responsable decide lo siguiente.
