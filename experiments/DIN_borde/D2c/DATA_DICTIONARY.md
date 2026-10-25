# Datos, salidas y reproducción

Sólo dos CSV empíricos autorizados, con SHA en freeze_manifest.csv.
`discovery_table.csv`: unión pública de780 trayectorias; no cohorte nueva.
Los logaritmos calculados y la unión se describen en DESIGN_FROZEN.
`discovery_provenance.json`: cardinalidad, problemas y SHA del array externo.

`comparisons/*.json`: original (proceso aislado) frente a referencia propia,
31 tablas más descubrimiento. `subject/*`: retornos, stdout y stderr nativos.
`A2_comparisons.csv`: resumen sin filtrar casos no identificables.
`cli/*`:17 contratos de input; subdirectorios contienen compuertas SINTÉTICAS,
stdout/stderr y RESULTADO_C1 si el sujeto llegó a escribirlo. Un archivo PASA
de fixture no acredita una reproducción real de redes.
`A3_CLI.csv`: comparación esperada/observada. Los rhos inválidos requieren una
política controlada; el contrato del arnés los marcó INCONCLUSIVE, pero no
se infiere que descartar1 inválido de780 deba siempre impedir PASS.

`monte_carlo.jsonl`:2000 resultados incrementales, todos conservados.
`result.p`:199 permutaciones; `sensitivity.p`:5000 en15 casos prefijados.
Los p incluyen pseudocuenta y holgura1e-15 del sujeto. `realised_r` difiere
del parámetro del generador por ruido finito. Los arrays contienen observaciones,
selección bootstrap y nulos de permutación, fuera de Git con SHA.
`A4_rates.csv` y summary.json contienen Wilson95% y comparación de intervalos.

`external_manifest.csv`: todas las tablas y arrays externos, incluso la tabla
intermedia de duplicados; `manifest.csv`: todos los archivos de la etapa salvo
él mismo y verification.json para evitar ciclos. verification.json es auditoría
de INTEGRIDAD: su PASS no significa que el sujeto C1 sea correcto.
El verificador incluye su SHA; las fuentes del sujeto tienen SHA independientes.
`null=None`/D=None en comparación indica X no identificable; no se imputa.

Para reproducir MEDICIONES en un checkout independiente del commit de código
0f22130, con Python3.12 y requirements (salidas/ruta externa deben estar libres):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python experiments/DIN_borde/D2c/scripts/run_audit_v1.py
```

El postproceso está en09c1b1a y sólo lee sus archivos propios. Los scripts
rechazan sobrescritura; no borrar resultados de esta auditoría para repetirla.
Una versión nueva exige diseño/enmienda y rutas nuevas, según AGENTS.
No ejecutar c1_cohorte.py para reproducir D2c.
