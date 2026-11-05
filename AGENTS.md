# Instrucciones documentales y científicas

- Trabajar en el checkout existente; no crear worktrees salvo petición explícita.
- Una solicitud documental no autoriza experimentos, entrenamientos ni auditorías geométricas.
- No modificar implementaciones científicas ni resultados originales en tareas documentales.
- No reiniciar auditorías cerradas salvo fallo de integridad documentado.
- No alterar protocolos, semillas, radios, métricas, tolerancias, umbrales ni reglas congeladas.
- No reemplazar estados fallidos ni excluirlos retrospectivamente.
- No convertir supervivientes en evidencia confirmatoria ni usar los mismos datos para descubrir y confirmar una hipótesis.
- Preservar outcomes desconocidos como desconocidos.
- Separar análisis exploratorio de resultados oficiales y estimaciones numéricas de certificados rigurosos.
- Guardar avances documentales incrementalmente; registrar correcciones y contradicciones explícitamente.
- Escribir en español, conservar identificadores técnicos y usar enlaces relativos.
- Versionar código, protocolos, manifests, hashes, reportes y documentación. Mantener ZIP, checkpoints y arrays diagnósticos fuera de Git.
- No borrar ni mover datos existentes innecesariamente; no publicar ni hacer push automáticamente.
- No inventar fuentes, resultados, fechas, hashes ni acceso a conversaciones o bibliotecas externas.

# Roles y flujo de trabajo

Esta sección se añadió el 2026-11-05. No cambia ninguna de las reglas anteriores; las aplica a cada agente.

## Quién hace qué
- **Responsable (humano):** ejecuta en su PC, aprueba diseños y decisiones, y fusiona los PR. Es el único que decide exclusiones, cambios de alcance y borrados.
- **Codex:** diseña y audita. Desde el 2026-11-05 ya no participa en Q15.
- **Claude:** implementa y audita. Abre los PR. Al revisar PR de otro agente, lee el código sin correr sus pruebas.
- **Argon:** hace el cribado y la extracción de Q15 por decisión del responsable del 2026-11-05. Fuera de Q15 sigue en periodo de prueba (ver abajo).

Ningún agente fusiona PR ni hace push a `main`.

## Reglas comunes a todos los agentes
- Los diseños se congelan antes de ver datos, y se hace un solo análisis confirmatorio por diseño.
- Cada afirmación lleva su respaldo: archivo y línea, commit o comando. Si algo no se encuentra, se dice explícitamente; no se deduce.
- Si dos documentos se contradicen, se reporta la contradicción en lugar de elegir uno en silencio.
- Los procesos largos los ejecuta el responsable en PowerShell, en sesiones de alrededor de una hora. El agente entrega el script y el comando exacto, con ruta completa y `python -I`; no los lanza en segundo plano.
- Los datos pesados viven fuera de Git, en `D:\RIPG_DATA\`. Un agente no escribe ahí salvo instrucción explícita del responsable.
- Borrar algo, en el repo o en `D:\RIPG_DATA\`, requiere aprobación previa del responsable.
- Dos agentes no escriben a la vez en la misma carpeta ni en la misma rama.

## Argon: periodo de prueba
Argon trabaja por niveles. Cada nivel lo califica Claude contra respuestas conocidas, y el responsable aprueba el paso al siguiente.

| Nivel | Qué hace | Permisos | Estado |
|---|---|---|---|
| 0 | Lectura con respuestas conocidas y una trampa | Solo lectura | Aprobado (2026-11-05) |
| 1 | Auditoría a ciegas de un entregable ya auditado | Solo lectura | Aprobado (2026-11-05). Halló hallazgos que la auditoría previa no vio, sin inventar datos; tuvo errores de conteo, así que sus cifras se recalculan siempre. |
| 2 | Tarea con verificador mecánico (por ejemplo, un lema en `lean/`) | Rama propia, sin fusionar | Pendiente |
| 3 | Tareas de la ruta crítica | Según lo apruebe el responsable | Pendiente |

**Excepción, Q15:** el responsable asignó a Argon el cribado y la extracción de Q15 el 2026-11-05, sin pasar los niveles 2 y 3. En esa tarea Argon trabaja en su propia carpeta, por lotes fijados antes de leer, y Claude audita cada lote recalculando los conteos antes de seguir.

Fuera de Q15, mientras no apruebe el nivel 3, Argon:
- no escribe en `D:\RIPG_DATA\` ni en carpetas donde trabaje otro agente;
- no toca rutas críticas abiertas (por ejemplo, el cribado de Q15);
- trabaja solo en ramas `argon/…`, y sus resultados los revisa Claude antes de que el responsable los considere.
