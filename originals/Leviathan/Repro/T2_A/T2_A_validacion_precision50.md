# T2-A — validación instrumental V2: aceleración con50 dígitos

Resultado: **VALIDATED_FOR_TESTED_LOCAL_SCOPE_ONLY**. Pasa exclusivamente el alcance local probado. La implementación oficial no fue modificada; checkpoint512 intacto,1/8000 visitas completas,3 parciales.

## Diseño congelado antes de ejecutar

Misma ecuación geodésica y campo exacto. Aceleración calculada con50 dígitos en todos los rayos, salida convertida a float64; DOP853 y tolerancias2e-10/2e-12 conservadas. Se cachean M y f a cada precisión, sin alterar datos. No hay selección adaptativa de rayos o umbral ajustado a los nuevos resultados. Plan:precision50_validation_plan.json.

Referencias:80 dígitos en todo el haz y120 dígitos en puntos predefinidos y en las11 integraciones locales. La compuerta operacional compara cada componente en escala2e-12+2e-10|referencia|; no es un cambio de criterio científico.

## Resultados

- 2048/2048 aceleraciones puntuales al snapshot512 coinciden con80 dígitos al redondear a float64.14 puntos de referencia80/120 pasan.
- 11/11 integraciones locales pasan:5 desde el centro y6 en segmentos cercanos al atasco. En las mallas evaluadas, la discrepancia registrada respecto a120 dígitos es cero después del redondeo a float64.
- Un paso del haz completo de2048 rayos pasa.50 y80 dígitos aceptan el mismo tiempo final y coinciden en la salida densa evaluada en513 radios (error escalado=0.0).
- El paso comienza en0.07444033865530993 y termina en0.074440384877681162. El siguiente paso propuesto es4.622237123608208e-7, diez veces el ensayo inicial. Este avance pertenece solo al ensayo: no sustituye el snapshot oficial.

## Coste y límites

El paso completo, incluida su salida densa, necesitó16 evaluaciones de RHS y **113.53s** con50 dígitos; la referencia80 necesitó **118.66s**. Este coste demuestra que la implementación de alta precisión en todos los rayos es cara. Un siguiente paso propuesto más grande no garantiza ahorro global; no se ha medido el tiempo de completar una visita.

No se integró todo el dominio nominal0.02, no se terminó la búsqueda hasta0.09, ni se validaron Jacobi, topología, conjugados o área embebida con esta variante. Las pruebas cercanas al atasco parten del estado float64 almacenado y no eliminan su error acumulado previo. Se necesita replay desde el origen antes de tratar una trayectoria como corregida.

La conclusión es de exactitud local y del mecanismo numérico, no evidencia predictiva ni certificación geométrica. V1 float64 conserva su veredicto NOT_VALIDATED_FOR_PRODUCTION; no se reinterpreta como aprobada.

## Próximo trabajo recomendado

1. Diseñar por escrito una candidata de precisión selectiva o implementación más eficiente, con criterio de activación fijo antes de sus resultados y referencia de alta precisión. No aplicar aún esa selección al estudio.
2. Validarla en los mismos controles y el haz completo; medir coste y exactitud, incluyendo posibles discontinuidades del cambio de precisión.
3. Si pasa, probar de forma aislada replay desde el origen y calibración completa. Después validar Jacobi y topología. Solo entonces decidir si puede incorporarse como implementación equivalente o exige una revisión explícita del protocolo.

La validación terminó sin procesos activos. Hubo un fallo de serialización del booleano final; los dos resultados numéricos ya estaban guardados. Se reconstruyó la comparación desde sus interpolantes persistidos, sin repetir las integraciones. Scripts, plan, resultados e interpolantes permanecen disponibles con SHA-256.
