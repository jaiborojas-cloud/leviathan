# E16-AH · cota superior por caminos de un quiebre

[Diseño congelado](DESIGN_FROZEN.md) · [Teoría](THEORY.md) · [Preparación](progress.md).

80 estados sintéticos de AG/AF, sin datos T2. Longitudes de curvas concretas
al borde infinito; no confundirlas con un umbral finito de carta.

**Resultado v1:** Q1 PASS · Q2 FAIL · Q3 PASS · Q4 PASS_DESCRIPTIVE ·
Q5 PASS_DESCRIPTIVE. Ochenta estados con testigo y controles nulos válidos;
13/13 controles previos PASS. La mediana de hatρ1/d_borde en triángulos es
1.307235 y el máximo2.171753: mejora respecto de AG, sin alcanzar los umbrales.

- [Conclusión y límites](CONCLUSION.md), [convenciones del testigo](WITNESS_CONVENTIONS.md).
- [Resultados](results/run_v1), [tabla por grupo](results/run_v1/groups.csv),
  [diagnósticos derivados](results/run_v1/derived_diagnostics.json).
- [Ejecución](progress_run.md), [stdout/stderr original](execution.log).

Los estados nativos no convergentes quedan archivados. Una longitud validada
es una cota de una curva concreta, no un certificado de que la búsqueda haya
resuelto el mínimo global. Los datos AF sólo tienen interpretación descriptiva:
su distancia real continúa UNKNOWN. Se incluye siempre el camino sin quiebre.

Desde la raíz, Python3.12 y dependencias de requirements.txt:

```sh
python -m pip install -r experiments/E16/AH/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AH/scripts/run_v1.py --out /tmp/ah-resultados-nuevos --arrays /tmp/ah-arrays-nuevos
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AH/scripts/verify.py
```

El runner rechaza sobrescribir directorios. Los480 arrays originales permanecen
fuera de Git, en resources.json, con su manifiesto de SHA. La verificación
requiere esa copia y no reintegra curvas. Se reutilizan funciones puras de AG
para una base contemporánea, sin ejecutar ni escribir sus etapas cerradas.

[Verificación desde archivos](verification.json) ·
[Aclaración de etiqueta del diagnóstico v1](DERIVED_LABEL_ERRATA.md).
