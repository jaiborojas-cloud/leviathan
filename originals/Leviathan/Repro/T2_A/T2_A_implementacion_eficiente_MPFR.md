# T2-A — implementación eficiente MPFR de precisión fija

Estado: **VALIDATED_FOR_TESTED_LOCAL_SCOPE_ONLY**. Validación instrumental local; no cambio de la implementación científica oficial ni nueva visita cerrada.

## Implementación

Se mantienen las ecuaciones y los datos M, f, P y v. Se evalúa la aceleración −solve(G, Jᵀ M H[v,v]) con MPFR a **169 bits**, la precisión binaria correspondiente a mpmath con 50 dígitos decimales. Se usan redondeo al más cercano, todos los rayos y conversión a float64 únicamente al entregar la aceleración al integrador. Se reutiliza Jᵀ M y se resuelve el sistema 2×2 mediante eliminación con pivoteo. No se supone simetría exacta de M. No hay precisión selectiva, nuevo umbral, cambio de dominio ni reducción de resolución.

DOP853 conserva rtol=2e−10 y atol=2e−12. El diseño y su código quedaron guardados antes de ejecutar las pruebas en fast_mpfr_plan.json. Dependencias: {"python": "3.12.14", "gmpy2": "2.3.2", "mpfr": "MPFR 4.2.2", "mpmath": "1.3.0"}. La referencia mpmath se ejecutó con su backend Python original.

## Exactitud medida

- 2048/2048 aceleraciones del snapshot 512: error escalado máximo 0 frente a las referencias MP80 guardadas.
- 11/11 integraciones locales evaluadas en 513 radios: error escalado máximo 0 frente a MP120. Se usaron los mismos cinco rayos desde el centro y los seis segmentos cercanos al atasco del diseño anterior.
- Tres repeticiones de un paso del haz completo de 2048 rayos: error escalado máximo 0; mismo tiempo aceptado que MP80 en las tres.
- Compuerta de exactitud: máximo por componente |candidato−referencia|/(2e−12+2e−10|referencia|) ≤ 1 en todas las pruebas; superada: True.

## Rendimiento

El paso completo, incluida la salida densa, tardó 14.299, 14.793, 15.020 segundos. Mediana: **14.793 s**, frente a **113.531 s** de la ejecución MP50 anterior: **7.67×** de aceleración medida respecto a esa referencia histórica. Es una comparación no simultánea en el mismo entorno de trabajo; no es un benchmark controlado entre máquinas ni una estimación del coste de una visita completa. Las tres repeticiones usan el mismo estado inicial para medir ejecución, no constituyen evidencia científica independiente.

Evaluar las 2048 aceleraciones puntuales necesitó 0.886 s. El tiempo de persistencia y el de la referencia MP120 se excluyen del coste del candidato y se conservan por separado en los resultados. Se conservan evaluaciones de RHS, pasos y tiempos por ensayo. No se ha demostrado aceleración de la calibración completa.

## Estado científico y siguiente compuerta

La trayectoria oficial sigue en el paso **512**: **1/8000 visitas completas**, tres parciales, ningún horizonte completo. No se abrieron nuevos checkpoints futuros ni se calcularon nuevos outcomes. Snapshot oficial verificado por SHA-256: a418ed98d65be0b14c784e4c2e1446282f3b0c4e272e2eef00d33434e505eda8.

La variante pasa únicamente el alcance local probado. Los segmentos cercanos al atasco parten del estado float64 anterior; no eliminan sus errores acumulados. El siguiente ensayo debe ser una integración aislada desde el origen y calibración completa, con persistencia incremental, seguida por validación de Jacobi y topología antes de adoptar el cambio. No debe declararse una visita terminada ni un estado geométrico a partir de estos ensayos.

La variante float64 anterior conserva su veredicto NOT_VALIDATED_FOR_PRODUCTION. Esta mejora no modifica los criterios científicos ni constituye evidencia confirmatoria prospectiva.
