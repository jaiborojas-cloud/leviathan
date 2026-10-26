# Archivo reversible y arrays externos

Los JSON originales de cada visita permanecen intactos localmente. Se
versionan todos sus campos en results/run_v1/state_records/part_*.jsonl,
con hasta1000 registros por shard. state_records_manifest.csv conserva
SHA/bytes del original y ubicación shard/línea.

El empaquetado verifica roundtrip BIT A BIT; no borra ni sobrescribe.
Para comprobar/restaurar esos mismos metadatos desde el repo:

```sh
python experiments/DIN_borde/G3/scripts/archive_v1.py --part unpack
```

Si ya existen, sólo comprueba igualdad; si difieren, falla. La exclusión
Git de los originales individuales evita duplicarlos: el JSONL completo
reversible conserva toda su información. Las tablas, registros de trayectoria,
controles, potencia, fuentes y reportes se versionan directamente.

Arrays/checkpoints y diagnósticos rho completos permanecen fuera de Git,
con ruta/SHA/tamaño en cada registro y external_manifest.csv; también los
draws/estadísticos nulos de potencia. No se sustituyen por supervivientes
ni se convierten desconocidos en conocidos.
