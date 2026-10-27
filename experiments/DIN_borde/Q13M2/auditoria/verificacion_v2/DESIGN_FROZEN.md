# Verificación independiente de DIN-Q13-M2 v2, antes de congelar

2026-10-27. Objetivo fijo: commit `ac63574f60bcd5bee2aa444dbd57ac88d68e76b7`, analista `512737dd…`, pruebas `6e7b836c…`. Solo archivos nuevos en `Q13M2/auditoria/verificacion_v2/`. No se modifica el diseño ni el analista ajenos ni la auditoría #117. Los snapshots de #117 se incorporan por SHA para que este PR no dependa de que aquel se fusione.

## Lectura y alcance

Leídos AGENTS.md, diseño borrador v2 completo, informe/pruebas/JSON v2, auditoría #117 y diff exacto `66f5de58..ac63574f` del analista. Los nuevos defectos se buscan solo en las líneas cambiadas y sus interacciones. No se ejecuta el main de las pruebas del autor: usa un fixture entrenado de G3/C2. Solo sintéticos generados por la misma receta de #117 y la tabla publicada Q13-DR `ed00364f…` como referencia LS, sin modificar su cierre. No se accede a Wine, T2, C2, Q13 o cohortes M2.

## Casos y criterios fijados antes del código/mediciones

1. Reejecutar los 23 casos de #117 mediante copia byte a byte de su script y soporte adaptado solo a rutas/objetivo v2; semillas 1010100, B39/NB64, trazas NB32, degeneración NB300. Conservar todas las salidas y excepciones esperadas. Comparar exactamente, en casos válidos, primarias, veredictos, β, IC y trazas v1/v2. Las diferencias esperadas son la localización de F01 y la validación explícita de API.
2. Matriz F01 completa: niveles WD3, LP3 y A0 × Y, X, L constantes (9 casos). Y se fija mediante rho250=1; X=-2; L mediante rho10=1. Exclusivo: solo ese manipulador INCONCLUSIVE, el sano idéntico al control y conjunto PARCIAL. A0: inconcluso global. Añadir dos exclusivos fallidos a la vez, múltiples niveles fallidos y cruce con compuerta para revisar precedencias y localización. No cambiar faltantes ni comunes globales.
3. F02: CLI original con tabla sintética, plan/resumen válidos, referencia LS de SHA permitido y marcador previo; exigir ABORTA3 sin traceback y marcador intacto. Directorio como salida final y enlace simbólico colgante deben rechazarse sin sustituirse. Carrera determinista: insertar un marcador después de la comprobación inicial y antes del open exclusivo, usando inyección de fallo en la función LS; exigir conservación y ABORTA3. Tabla/plan/marker/stdout/stderr se archivan fuera de Git con SHA. No se toca ningún resultado real.
4. F03: SHA de archivos v2 frente a informe y JSON; 25 casos y 18 reglas declarados, todos registrados; comprobar la prueba de tolerancia del código. Distinguir vinculación documental de ejecutar la suite ajena. Detectar contradicciones de redacción del diseño sin convertirlas en defecto del algoritmo.
5. F04 y referencia: ejecutar el mismo script de referencia LS de #117 (2000 draws960002), capturando draws/D/c/β; verificar diferencia del literal ≤1e-12 y comparación con salida v1. Primaria M2 sigue usando960001; misma réplica LS para LP/WD. No es un nuevo cierre de Q13-DR.
6. Nuevas rutas LS: error puntual simulado en main y `ls={error:…}` en analizar no deben alterar las primarias ni borrar LP−WD, y deben dejar compatibilidad no definida explícita. Fallos bootstrap LS se preservan completos y suprimen compatibilidad sin contaminar primarias. Tamaños discordantes: ValueError claro, sin broadcasting; tamaños válidos conservan los IC. Distinguir límites API no alcanzables con la CLI fijada de crashes demostrados.
7. Rutas de salida exclusiva: comprobar también una escritura válida sin marcador (tabla sintética pequeña) y JSON estricto. Los fallos de E/S de una ruta nueva se documentan, distinguiendo los heredados si aparecen. No se arregla código auditado.

## Regresiones y Monte Carlo

Comparar AST de las funciones del motor: replica, referencia_ls, q, arreglos, plan, universo y funciones reutilizadas; comprobar que bootstrap, coeficientes, semillas y cuantiles no cambian. Reejecutar trazas compartidas de #117 con c variable, A0 único, copias en bloques originales, recálculo D/c/β, cuantiles .0125/.9875 y misma referencia LS por réplica. La igualdad exacta de los resultados no degenerados debe mantenerse en el mismo entorno; una discrepancia no explicada se conserva y se investiga.

No repetir Monte Carlo si el diff/AST y controles no degenerados confirman la misma ruta estadística. Si no lo confirman, documentar el hallazgo antes de decidir cualquier simulación adicional; no ampliar esta verificación silenciosamente. Las tasas de #117 permanecen evidencia de aquella ejecución, no se renuevan por esta verificación.

## Conservación y entrega

Diseño comprometido antes de código y mediciones. Cada script se compromete antes de ejecutarse. JSON/CSV/logs/manifest por SHA; arrays y fixtures fuera de Git. Escrituras exclusivas. Si hay defecto del instrumento auditor: enmienda congelada antes de código corregido, nueva versión sin sobrescribir. Conclusión por F01–F04 y matriz de regresiones, defectos nuevos con caso mínimo/severidad si existen. PR separado en borrador, no fusionar. No se decide por el responsable ni se congela el confirmatorio.
