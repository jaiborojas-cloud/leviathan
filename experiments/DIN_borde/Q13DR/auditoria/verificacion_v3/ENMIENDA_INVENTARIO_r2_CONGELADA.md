# Enmienda de inventario r2, antes de corregirlo

La comprobación posterior al push del commit `51ada0ad14c06e949871d83e3c8a92e1cc293ee6` encontró dos ficheros locales `__pycache__/*.pyc` incluidos por el inventario recursivo, pero ignorados por Git. Los subprocesos usan `python -I`, que ignora PYTHONDONTWRITEBYTECODE; por eso se generaron esas cachés aunque el proceso padre lo fijó. No es un defecto del analista ni cambia resultados.

La comprobación local de los112 hashes pasó, pero ese manifiesto no era verificable íntegramente solo con el checkout publicado. Se conserva `manifest.csv`, `manifest.sha256` y `verification.json` como registro r1 del commit anterior; no se sobrescriben. Sus referencias corresponden a aquel commit y al entorno local, no al HEAD corregido.

Se añadirá un generador de inventario r2, comprometido antes de ejecutarlo. Excluirá únicamente cachés y sus propios manifiestos; archivará las dos cachés fuera de Git por SHA y publicará su mapa. El resultado vigente será `verification_r2.json`, `manifest_v2.csv`, `manifest_v2.sha256` y `external_manifest_r2.csv`. Se actualizarán enlaces documentales, sin editar mediciones, snapshots ni verificadores científicos. No se repetirá ningún caso o simulación. Se verificará que todo miembro del manifiesto vigente esté versionado y conserve su SHA.
