# Enmienda congelada r3 · coherencia de brackets flotantes

Congelada antes de corregir. r2 conservada en results/run_r2, con302 salidas:
296 numéricas y6 FAILED (coordenado interior0 y null_lambda0.9 mass_face,
las tres semillas). I2/I3/I4 r2 son INCONCLUSIVE, no PASS.

Defecto reproducible: el signo vectorizado de una derivada casi nula difiere
del escalar por orden de redondeo. turning_points usa el primero para autorizar
brentq con el segundo, que levanta 'f(a) and f(b) must have different signs'.
No se deduce una raíz de signos incompatibles.

Corrección fijada: preservar archivo público r2 bit a bit en versions/r2/;
reevaluar cada bracket candidato con LA MISMA función escalar que recibe
brentq. Si mantiene signos opuestos, ejecutar brentq; si un extremo vale0,
conservarlo como candidato; si no, registrar explícitamente el bracket como
rechazado por redondeo (extremos, valores escalares y vectorizados). No se
relajan tolerancias ni se ignoran excepciones de brentq. Devolver ese diagnóstico.

Crear ejecutor r3 y resultados/run_r3, arrays externos din-i2-r3-arrays.
Repetir controles, TODOS los302 estados,24 sensibilidades y4 contrastes MP.
Comparadores v1 se reutilizan intactos de run_v1. Mantener r1/r2 y resúmenes.
Mismos presupuestos, topología, estadísticos y reglas de veredicto.
