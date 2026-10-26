# DIN-D9g-b: cierre exploratorio de la ejecución

Veredicto por regla: ARTEFACTO_DE_BASE_LINEAL_EXPLORATORIO. B1 reproduce D9g; en s=.8 los D adicionales
B2/B3/B4 son −.016018/−.007763/−.008598. Signo de β permanece negativo en mitades,
pero no añade predicción fuera de muestra. Las bases solas empeoran respecto a B1:
D_base .075126→.063988→.019266→.011801. Se evita atribuir la caída exclusivamente
a absorción de no linealidad: puede intervenir sobreajuste/variabilidad.

16 celdas, 2.000 permutaciones cada una; análisis 10.743386s. Positivo con
señal grande pasa todas; negativos de proyección D≈0 artificiales y reales. B1 con
p idéntica y errorD≤3.34e-16. Verificación PASS, 3324 archivos
externos SHA, 1.500 pérdidas test250 y medidas originales copiadas exactamente.
No test nuevo, reentrenamiento ni acceso a C2. B5 no se incluyó retrospectivamente.

Se conserva un fallo de sintaxis de borrador de presentación (no ejecutado), con
fuente/SHA y enmienda2d8a805 antes de corregir. Sin fallos ni cambios de medición o
análisis; no se volvió a calcular ningún contraste para corregir el reporte.

Se recomienda posponer el confirmatorio basado sólo en D9g; el responsable decide.
Una posible tarea futura con regularización/CV anidada debe registrarse antes de
sus resultados y mantener C2 reservada. Este cierre no ejecuta esa tarea.
