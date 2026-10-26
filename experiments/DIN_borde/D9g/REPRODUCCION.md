# DIN-D9g: reproducción y archivo

Diseño0896fe4 precede al código43b1202, controles9a99718 y medicionesf961929.
No modificar G3 ni C2. Se requieren los archivos G3 del input_manifest.csv en sus
rutas locales, con SHA idéntico, y los paquetes de requirements.txt. No hay datos
Wine/Iris/T2/DIN-C1. C2 está prohibida. Sólo se permite código C1 sin ejecutar CLI.

En un clon separado y con salidas nuevas (las escrituras son exclusivas), exportar:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/D9g/scripts/measure_v1.py --part prepare
python experiments/DIN_borde/D9g/scripts/controls_v1.py
python experiments/DIN_borde/D9g/scripts/measure_v1.py --part evaluate
python experiments/DIN_borde/D9g/scripts/archive_v1.py --part pack
python experiments/DIN_borde/D9g/scripts/archive_v1.py --part unpack
python experiments/DIN_borde/D9g/scripts/analysis_v1.py
python experiments/DIN_borde/D9g/scripts/verify_v1.py
python experiments/DIN_borde/D9g/scripts/report_v1.py
```

Guardar cada salida antes de la siguiente. No repetir para reemplazar un fallo.
Si se descubre un defecto, conservarlo y congelar enmienda antes de código nuevo.
Los controles artificiales se ejecutan antes de evaluar redes en test y comparar
asociaciones. La extracción y el análisis ya publicados no necesitan repetirse
para consultar sus resultados.

El inventario source G3 tiene 7.500 checkpoints y 300 matrices de datos con scaler
train. El nuevo test usa seeds711000..711099, 100 ruidos compartidos entre niveles
y 300 test estandarizados. Todas las pérdidas/logits por ejemplo de 1.500 test250
quedan en /workspace/work/din-d9g-v1-arrays/. Los arrays de permutación/SSE completos
y controles están en el mismo directorio. Son rutas locales, no enlaces de descarga.
[Manifiesto externo](external_manifest.csv) conserva SHA/bytes de los 9.748 archivos
usados (originales G3 y nuevos). Nada se borra ni se mueve.

Los 1.500 JSON de evaluación se conservan localmente en results/run_v1/records/
(ignorados por Git). Los tres shards JSONL en results/run_v1/record_shards/ los
restauran bit por bit; record_manifest.csv identifica cada línea por SHA. Pack y
unpack preservan originales y no sobrescriben datos distintos. Todos los fallos,
si los hubiera, aparecen en measurement_failures.json y no se reemplazan.

La visualización y conclusión consumen únicamente estimates.csv y analysis.json;
no calculan nuevos contrastes. Entorno y tiempos están archivados. Los estados y
conclusiones de otras etapas permanecen intactos.
