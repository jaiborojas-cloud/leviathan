# DIN-D2 · el piso normalizado cuando M colapsa

[Diseño congelado](DESIGN_FROZEN.md) · [Demostraciones](THEORY.md) · [Fase0](progress.md).

Sólo paneles sintéticos; instrumento congelado importado sin cambios.
Se distingue prueba matemática, contraste numérico y compatibilidad con los
escalares publicados de D1. No se afirma transferencia a T2.

**Resultado:** Q1/Q2/Q3 PASS · Q4 PASS_DESCRIPTIVE · Q5 FAIL.
Los PASS resuelven preguntas con condiciones: rango1 no implica un piso1/n.
El instrumento congelado tiene173 casos consistentes,33 fallidos y4
inconclusos entre210 sintéticos, con8/8 controles de referencia PASS.

- [Conclusión por pregunta](CONCLUSION.md), [datos y estados](DATA_DICTIONARY.md).
- [Detalles de referencias](REFERENCE_DETAILS.md), [lo que no identifica el piso](IDENTIFIABILITY.md).
- [Resultados](results/run_v1), [por forma](results/run_v1/by_form.csv),
  [fallos preservados](results/run_v1/failures.csv), [escalares teóricos/D1](results/run_v1/theoretical_scalars.json).
- [Registro de ejecución](progress_run.md), [stdout/stderr original](execution.log).

El contexto D1 se leyó en la referencia fija del PR68 registrada en progress.md,
porque aún no estaba en main al preparar D2. Sólo se usaron escalares
publicados descriptivamente; ningún estado, checkpoint ni tabla T2 prohibida.

Desde la raíz, Python3.12 con requirements.txt:

```sh
python -m pip install -r experiments/DIN_borde/D2/requirements.txt
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/DIN_borde/D2/scripts/run_v1.py --out /tmp/d2-salidas-nuevas --arrays /tmp/d2-arrays-nuevos
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/DIN_borde/D2/scripts/verify.py
```

El runner rechaza sobrescrituras y conserva todos los casos. La guarda sólo
permite los dos fuentes autorizados de T2/archivo; no se llama al main del
instrumento, que cargaría estados. El verificador necesita los arrays externos
originales para comprobar sus hashes y no ejecuta geometría nueva.

[Verificación de archivos y álgebra](verification.json):360 arrays,153 valores
globales conocidos y210 controles espectrales; no reintegra ni repite el instrumento.
