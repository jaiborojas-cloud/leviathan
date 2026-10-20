# Registro E16-H

1. Rama sobre `89e1e55` (G, PR #21), checkout existente. Main incorporó F durante
   la secuencia; H conserva como base la rama G sin fusionar otras líneas.
2. Diseño, configuración y nuevos sorteos congelados en `3c96c95`, antes del
   adaptador, programa H y mediciones. No hubo filtrado ni reintentos de sorteos.
3. Se verificó identidad por AST de las 14 funciones compartidas G/H. Adaptación
   limitada a datos, procedencia y eliminación de comparación por caso con F.
4. Primera corrida: 324/324 longitudes PASS_NUMERICAL, 216/216 pares validados,
   13 102 controles PASS, cero FAIL/INCONCLUSIVE. 19,01 s y 39,61 MiB; un hilo.
5. Código y primera corrida preservados en `07107e9`, sin cambios a protocolo,
   método, tolerancias ni muestra después de medir.
6. Verificación: sorteos regenerados sin selección; sin coincidencias exactas
   con D; 14 funciones compartidas idénticas por AST y adaptación reconstruida.
   Cinco salidas científicas idénticas byte a byte; repetición de 19,86 s.
   La repetición no cuenta como muestra nueva. Fuentes previas intactas.
