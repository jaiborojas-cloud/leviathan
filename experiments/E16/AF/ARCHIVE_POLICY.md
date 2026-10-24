# Archivo AF antes de etapa2

AGENTS exige arrays diagnósticos fuera de Git. Los cuarenta M/f sintéticos y
los predictores ya están versionados como entradas científicas. Para cada
estado/resolución se guardará la matriz completa de257 radios con p,v,j,j' en
archivos .npy sintéticos fuera del repo, por defecto /workspace/work/e16-af-v1-arrays.
No son .npz ni datos T2. Sus nombres lógicos, formas y SHA256 se versionarán.
Se guardarán además en Git: eventos de TODOS los rayos, fronteras finales,
perfiles de los cuatro rayos axiales y rayos incidentes al primer evento,
bandas/espectros/modos de Morse, controles y escalares completos. No se borran
los arrays. La reproducción usa otro directorio externo y compara sus hashes.
No implica publicar checkpoints o datos de T2; la guarda de acceso continúa.
