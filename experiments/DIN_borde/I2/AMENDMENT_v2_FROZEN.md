# Enmienda congelada v2 · ejecutor, no instrumento

Posterior al código a105dbe y anterior a cualquier corrección. La ejecución de
controles v1 escribió environment.json y controls.json completos; luego falló
en run_v1.py:132 al imprimir checks con numpy.bool_ sin clean().
TypeError: Object of type bool is not JSON serializable; exit1.
Todos los controles guardados tienen PASS. No se repiten ni sobrescriben.

Corrección autorizada por esta enmienda: crear scripts/run_v2.py como copia
de run_v1.py, cambiando únicamente el json.dumps del resumen para aplicar
clean() (ya usado por el escritor exclusivo). Conservar run_v1.py intacto.
La cohorte seguirá en results/run_v1, que sólo tiene controles; tendrá el
commit del ejecutor v2 registrado aparte. Instrumento, diseño, presupuestos,
semillas y reglas sin cambios. Commit de la enmienda antes del código v2.
