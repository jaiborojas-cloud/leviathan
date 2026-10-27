# Cierre de la ejecución de auditoría — 2026-10-27

Se preservaron los 23 casos originales, las 109 validaciones de plan, las 27 de dominio, las nueve CLI y dos límites adicionales de API. Las excepciones de IDs inválidos y LS puntual degenerada están archivadas, no descartadas. Los 94/300 fallos bootstrap provocados en WD4/A0 coinciden en todos sus índices con los draws, sin sustitución. Los 23/64 fallos LS sintéticos se conservan y no alteran las primarias M2.

Monte Carlo: completadas las 800 tablas fijadas, sin fallo de ejecución ni sustitución. 922.014 s, 2 procesos y 1 hilo BLAS. Controles independientes contra fuentes originales: p idénticos, máximo error de D 8.88×10⁻¹⁶, de IC 1.64×10⁻¹⁴ y de bootstrap D 1.82×10⁻¹⁴, por debajo de 10⁻¹⁰. Error familiar nulo 6/400 y 9/400 para ρ=0/.6. No se aumentó la muestra ni se cambió la regla después de mirar resultados.

F01: aislamiento incompleto en la primaria puntual; F02: sobreescritura de salida; F03: evidencia de pruebas con SHA previos; F04: literal LS difiere3.747×10⁻¹⁶. El contraste puntual adicional usa únicamente la referencia LS autorizada y confirma igualdad de los vectores D de las dos implementaciones originales; no cambia el cierre oficial.

La verificación de integridad publicó 826 condiciones, incluidas las 800 matrices externas, con PASS. El código de verificación y los casos adicionales se comprometieron antes de ejecutarse. No hubo corrección de código de medición ni reescritura de salidas; no se necesitó una enmienda para corregir una medición. Los límites API de tamaño LS y c constante ya estaban previstos en el diseño.

No se usaron datos nuevos reales ni cohortes restringidas; no se entrenó. No se ejecutó el main de las pruebas del autor. La entrega propone cambios pero no modifica analista/diseño y no aprueba la congelación. Logs en [logs](logs/); inventario externo y manifests en la carpeta de esta auditoría.
