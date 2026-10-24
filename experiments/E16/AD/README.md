# E16-AD · Bloques discretos y carta normal

[Diseño congelado](DESIGN_FROZEN.md) antes de código y mediciones; [formulación](THEORY.md).
Parte A: suma/producto/cuadrática, prueba simbólica y malla con MP80/120.
Parte B: nuevas discretizaciones de la geodésica AC, sin reabrir S–AC.

- [Resultados A](results/part_a_v1), [resultados B](results/part_b_v1).
- [Conclusión](CONCLUSION.md), [preparación congelada](progress.md), [ejecución](progress_run.md).
- Cada caso conserva ambos KKT (admisible y completo), espectros, bandas,
  gradientes y vértices finales, testigos MP y componentes de modos negativos.

COCIENTE permite sólo desplazamientos normales iniciales. Su KKT restringido
no se presenta como estacionariedad de todas las coordenadas libres. Los
mínimos físicos, métricos y admisibles se etiquetan por separado. Las fracciones
son de modos resueltos bajo el umbral congelado; UNKNOWN no equivale a cero.

Desde la raíz, Python3.12 con [dependencias](requirements.txt):

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AD/scripts/part_a_v1.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AD/scripts/part_b_v1.py --out /tmp/e16-ad-b-nuevo
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python experiments/E16/AD/scripts/verify.py
```

Los runners rechazan sobrescribir resultados. A debe estar disponible antes de B.
El verificador reconstruye bandas/modos y ejecuta una repetición exacta de B;
los tiempos se excluyen. No reejecuta auditorías cerradas. El archivo suplementario
de modos esféricos se deriva de las bandas preservadas, sin nueva Hessiana AD.

**Estado final:** INCONCLUSIVE; producto también plano, controles12/12 PASS.
Los tres LIBRE cuadráticos conservan INCONCLUSIVE.
[Reproducción exacta de A y B](verification.json).
