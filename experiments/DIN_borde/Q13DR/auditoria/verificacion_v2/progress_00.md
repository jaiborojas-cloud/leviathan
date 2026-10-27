# Prelectura de la revisión245d735f

Diseño v2, analista, pruebas e informe solicitados leídos. Pruebas y analista
coinciden con los SHA dados. Se conserva referencia a F01–F06 y ambigüedades de
#104. La suite original no se ejecuta por su fixture C2; todo será sintético.

Por inspección: c puntual ahora usa comunes; el bootstrap atrapa fallos; planes
y dominio se validan; equivalencia es secundaria y hay rangos medios. Quedan
por ejecutar casos de constancia decimal, rango de c común no ordenada y errores
de lectura/conversión en la nueva validación. No son hallazgos confirmados aún.

Congelar antes del código y las mediciones. V1 se importa por SHA sólo como
código/documentación y baseline sintético, sin alterar sus resultados.
