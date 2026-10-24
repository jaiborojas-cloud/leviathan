# E16-AF · réplica sintética de la familia geométrica T2

**Resultado v1:** Q1 PASS · Q2 INCONCLUSIVE · Q3 PASS exploratorio · Q4 FAIL.
35/40 censurados; cinco eventos conjugado+colisión; 20/20 controles PASS.

40 estados nuevos (27 componentes,10 semillas×4 escalas), sin leer estados,
M/f, checkpoints o resultados de T2. Se importa sólo el código autorizado con
SHA verificado y guarda runtime que prohíbe accesos a datos T2 y archivos .npz.
La matriz se calibra en amplitud porque escalar sólo f no cambia K central.

- [Diseño congelado](DESIGN_FROZEN.md), [convenciones y derivación](THEORY.md).
- [Preparación](progress.md), [ejecución](progress_run.md).
- [Predictores y SHA](results/stage1_v1/predictors_sha256.json),
  [etapa1](results/stage1_v1), [etapa2](results/stage2_v1).
- [Diccionario de datos](DATA_DICTIONARY.md), [política de arrays](ARCHIVE_POLICY.md).
- [Conclusión](CONCLUSION.md), [verificación y reproducción](verification.json).

La tabla predictora se comprometió antes del primer código de desenlaces.
Las escalas están emparejadas por semilla y parte de la asociación está inducida
por calibración de unidades: no son40 réplicas independientes ni transferencia
a T2. La validación de Morse conserva el rayoθ0; no lo sustituye por el rayo
que produjo el conjugado mínimo global.

## Entorno y reproducción

Python3.12 con versiones de [requirements.txt](requirements.txt), BLAS/OMP de un
hilo. La etapa2 ejecuta dos procesos numéricos; no se emplearon subagentes.
El runner rechaza sobrescribir directorios de resultados/arrays.

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AF/scripts/stage1_v1.py --out /tmp/af-pred-nuevo
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AF/scripts/stage2_v1.py --out /tmp/af-out-nuevo --arrays /tmp/af-arrays-nuevos
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AF/scripts/verify.py
```

Etapa2 verifica la tabla original cerrada antes de lanzar desenlaces. Las nuevas
versiones científicas requieren nueva congelación; estos comandos sólo repiten
el diseño. No ejecutar main/load de audit.py: acceden a casos archivados y la
guarda AF los bloquea. Los únicos controles con datos E16 leen fuentes sintéticas
H/D/AC para la cuadrática plana, sin modificar ninguna etapa cerrada.
