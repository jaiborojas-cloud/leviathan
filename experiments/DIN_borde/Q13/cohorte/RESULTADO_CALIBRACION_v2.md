# DIN-Q13 v2 — calibración completa

900/900 ejecuciones válidas, cero errores y faltantes. Datos, pesos iniciales y
lotes idénticos en las nueve condiciones pareadas. Sólo c250, q250 y precisión.

| Brazo | Dosis | Mediana c250 | Mediana q250 | Mediana acc_panel250 | Elegible |
|---|---:|---:|---:|---:|---|
| A0 | 0 | .838653 | .000124754 | .925926 | Referencia |
| LS | .001 | .737400 | .000138557 | .925926 | No |
| LS | .002 | .701850 | .000172569 | .925926 | No |
| LS | .005 | .609784 | .000224343 | .925926 | Sí, menor elegible |
| LS | .01 | .540762 | .000262098 | .925926 | No |
| WD | .2 | .675014 | .000179453 | .925926 | Sí, menor elegible |
| WD | .5 | .655868 | .000200535 | .925926 | Sí |
| WD | 1 | .597474 | .000281142 | .925926 | Sí |
| WD | 2 | .542048 | .000415522 | .925926 | No |

**Dosis elegidas: LS ε=.005 y WD λ=.2.** Se aplica el rango cerrado [.55,.70]
y la diferencia absoluta de medianas de precisión <.05. No se redondeó .701850
para admitir LS .002. A0 es referencia de precisión, sin compuerta en este piloto.

Receta copiada byte por byte de v1; código/config publicados en f865be3 antes de
medir. Tiempo total 104.312 s, dos procesos con un hilo BLAS. Calibración v1 y
diseños íntegros. No se calcularon X, rho ni asociaciones; C2 no se leyó.

Sigue únicamente la potencia simulada del diseño. Aún no hay N, plan ni cohorte.
[Tabla](calibracion_v2/calibracion.csv) · [resumen](calibracion_v2/summary.json) ·
[verificación](calibracion_v2/verification.json) · [SHA](calibracion_v2/PUBLICACION.sha256).
