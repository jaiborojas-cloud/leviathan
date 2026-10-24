# Aclaración del diagnóstico derivado v1

Se conserva sin sobrescribir derived_diagnostics.json y su generador report.py.
El nombre `max_selected_MP_error` en ese diagnóstico es impreciso: procede de
`numeric_relative_error` de states.csv, que es el máximo entre el estimador
relativo de quad y el contraste MP. Su valor1.24005e-11 es correcto para esa
magnitud combinada, no para el contraste MP por separado.

La verificación independiente distingue ambas magnitudes en verification.json:
`max_selected_combined_quad_MP_error` y `max_MP_relative_error` (testigos y
basales), además del máximo de todos los contrastes MP aceptados. Esta
aclaración corrige la etiqueta documental y conserva el artefacto inicial.
No cambia código de medición, entorno, curvas, longitudes, estados ni reglas;
no requiere otra ejecución geométrica ni modifica los veredictos Q1–Q5.
