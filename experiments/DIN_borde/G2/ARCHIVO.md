# Conservación reversible de las salidas

Los4200 JSON individuales de metadatos permanecen intactos en la ejecución.
Se versiona su contenido completo en results/run_v1/state_records.jsonl,
con SHA/bytes de cada archivo ORIGINAL en state_records_manifest.csv.
Esto reduce el número de archivos del PR sin quitar registros ni campos.
No es una selección de resultados ni una nueva medición.

El empaquetado exige roundtrip BIT A BIT antes de escribir el JSONL. Para
consultar/restaurar esos mismos JSON desde un clone, sin sobrescribir nada:

```sh
python experiments/DIN_borde/G2/scripts/archive_v1.py --part unpack
```

Comprueba también originales ya presentes. Si alguno difiere, falla.
Los JSON restaurados están ignorados por Git sólo porque el JSONL contiene
su copia completa verificable. Los600 registros de trayectoria, las tablas,
análisis, controles, figuras y manifests se versionan directamente.
Los arrays/checkpoints y diagnósticos rho completos permanecen fuera de Git,
identificados por SHA y ruta en cada registro y en external_manifest.csv.
