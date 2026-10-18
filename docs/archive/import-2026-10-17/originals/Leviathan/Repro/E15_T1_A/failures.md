# Incidencias y estados no resueltos

Recuperación: copia local ZIP A2 y un NPZ local incompletos tras interrupción; restaurados de archivos con SHA verificado, sin regenerar resultados. Dependencias originales restauradas.

Ningún fallo numérico entre estados completados.

## Incidencias resueltas de postprocesamiento

Tres INCONCLUSIVE operativos iniciales (split2/j0/true,split2/j2/true,split5/j2/true) se debieron a lectura de archivos .tmp.npz residuales. Los archivos finales estaban íntegros. Se corrigió la selección de archivos, con cero cambios en JSON/NPZ de tareas y cero reintegraciones; se conservaron result_before_postprocess_correction.json y los bytes temporales. Resultado final:ningún estado científicamente inconcluso o con fallo numérico.
