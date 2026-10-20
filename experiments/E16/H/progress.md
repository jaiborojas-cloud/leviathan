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
7. Durante la publicación, G remoto avanzó a `48bedaec` e incorporó E. Se integró
   en `52ae72c` resolviendo sólo los tres índices: se retienen las entradas E/F/G/H.
   `integration.json` fija esa base remota para comprobar el alcance propio de H;
   la base y los archivos del diseño científico congelado no se cambian.
8. Tras esa integración, se verifican integridad y alcance sin repetir mediciones:
   `verify.py --integrity-only`. Fuentes G/F/T2-A coinciden también entre la base
   original y la remota; método, datos, resultados y protocolo H permanecen iguales.
9. Publicación dirigida a main: G se había fusionado en una rama intermedia,
   pero aún no estaba en main. El PR incorpora G sin cambios científicos y H.
   Se comprobó el diff de tres puntos contra main: sólo G/H y los tres índices,
   sin archivos T2-A. No se incorporan ni revierten cambios de otras líneas.
