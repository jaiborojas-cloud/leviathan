# Enmienda congelada v2 · orden de ejecución

Se conserva diseño85fffb4 y código v1 de73cb83a sin editar. Se inició run_v1
antes del commit de código porque diff --check rechazó CRLF del manifest,
y el orquestador lanzó la siguiente llamada sin condicionar al éxito anterior.
Se detuvieron los tres procesos. Los JSON, arrays externos y execution_v1.log
se preservan. **run_v1=INVALID_PROTOCOL_ORDER**, no aporta evidencia primaria.
Su environment.json registra el commit de diseño, sin ocultar la incidencia.

No se cambia ninguna semilla, estado sintético, métrica, tolerancia, presupuesto
o regla de decisión por sus salidas. Hasta detener se vieron el resumen
estadístico y los primeros retornos de redes; no se seleccionan ni sustituyen.
Se ejecutarán TODOS los mismos86 casos y controles desde el código intacto,
en results/run_v2 y /workspace/work/din-d2b-v2-arrays. Sin sobrescritura de v1.

Antes de corregir la orquestación se compromete esta enmienda. Después se
añadirá un launcher v2 que exige un árbol sin cambios científicos y código
v1 comprometido, y dirige las salidas a v2. El launcher se comprometerá y se
comprobará el éxito del commit ANTES de arrancar. No corrige ni parchea core,
geometry o rho; tampoco altera el algoritmo científico v1.
