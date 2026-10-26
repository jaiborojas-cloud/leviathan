# DIN-C2: cohorte completa antes de publicar la tabla

1.000/1.000 trayectorias terminadas; 4.000/4.000 estados. Cero errores de trayectoria
y cero estados inválidos en el log. Tiempo de entrenamiento/medición:
1427.855433 segundos. Todas las trayectorias y estados se conservan.

Los 4.000 JSON por estado quedaron archivados en cuatro shards JSONL reversibles
bit por bit; pack y unpack PASS, sin borrar ni sobrescribir originales. Los arrays,
pesos y diagnósticos completos se conservan fuera de Git con SHA. Se conserva el
log completo. No se ejecutó analisis_C2.py ni se calcularon asociaciones o c/q agregados.

ESTE commit conserva el paso 5 completo antes del paso 6 de publicación. El próximo
paso copiará los valores individuales a la tabla, sin análisis estadístico.
