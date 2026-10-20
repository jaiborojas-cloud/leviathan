# E16-F — Longitudes de caminos prefijados

**INCONCLUSIVE global.** De 324 longitudes, 239 cumplen el protocolo numérico y
85 quedan inconclusas; no hay fallos de identidad. No se cambiaron los caminos,
el refinamiento ni las tolerancias después de observar los resultados.

- [Diseño previo](DESIGN_FROZEN.md), commit `7717db2`.
- [Conclusión, diagnóstico y límites](CONCLUSION.md).
- [Longitudes y estado de cada caso](results/run_v1/lengths.csv).
- [216 razones, incluidas las no validadas](results/run_v1/paired_ratios.csv).
- [Resumen y denominadores](results/run_v1/summary.json), [controles](results/run_v1/checks.csv).
- [Procedencia](results/run_v1/provenance.json), [recursos](results/run_v1/resources.json),
  [registro](progress.md), [manifest](manifest.csv).

Se reutilizan los 12 estados y tres paneles de [D](../D/README.md), sin entrenar
ni seleccionar supervivientes. Se recorren los tres segmentos entre sus puntos.
Se calcula ∫sqrt(γ̇ᵀh(γ)γ̇)dt para suma, producto y cuadrática. La positividad
durante el recorrido se estudia mediante cotas polinómicas de Bernstein con
precisión múltiple. Son controles numéricos globales, no certificados intervalares.

Estas son longitudes de los mismos caminos bajo métricas distintas. No se busca
el camino mínimo ni se anuncian distancias geodésicas o curvatura.

## Reproducción

Python 3.12 y [dependencias fijadas](requirements.txt). Desde la raíz del repo:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/F/scripts/verify.py
```

El verificador comprueba hashes, diseño previo, alcance y ausencia de cambios
propios en T2-A, y reproduce cinco salidas científicas byte a byte en un directorio
temporal. **PASS_REPRODUCTION no convierte INCONCLUSIVE en PASS_NUMERICAL.**
Tiempos y memoria se comprueban respecto al presupuesto, no byte a byte.
Se requiere el historial Git de la congelación. Para una corrida nueva:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/F/scripts/run.py --out /tmp/e16-f-nueva-corrida
```

No sobrescribir `results/run_v1`. El programa devuelve error ante FAIL o exceso
de presupuesto; puede finalizar normalmente con INCONCLUSIVE, que debe leerse
en summary.json. El código analítico de D se importa con hash verificado, sin
ejecutar su corrida ni escribir en su directorio. T2-A y evidencia A–E intactas.
