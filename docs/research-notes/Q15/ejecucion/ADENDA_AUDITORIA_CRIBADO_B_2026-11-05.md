# Adenda a la auditoría del cribado B

**2026-11-05, hora de México.** Completa y corrige la [auditoría del cribado B](AUDITORIA_CRIBADO_B_2026-11-05.md). No reemplaza ese documento.

Origen: Argon hizo una auditoría a ciegas del mismo paquete (SHA-256 `86f8660d…961d`), como prueba de nivel 1, leyendo el repo en `4a95e721`. Claude verificó cada hallazgo nuevo contra el paquete, con `python3 -I`. Aquí solo se registra lo verificado.

## Corrección a H4
H4 decía que ninguna de las 410 exclusiones parecía errónea. Esa revisión buscó términos de aprendizaje automático y no detectó exclusiones con **razón de plantilla que no corresponde al título**. Ejemplos verificados:
- W03336 ("Knowledge Proficiency Tracing Model…"), W03384 ("AI-based academic performance prediction using ML…") y W03322 ("Theory-guided data-driven based on the learning curve for fracturing performance prediction") quedaron excluidas con la plantilla de "procedimientos clínicos, adquisición de habilidades humanas, aprendizaje industrial…".
- W03336 y W03384 tienen resumen disponible que no se leyó. W03322 no tiene resumen, y su título no es una exclusión inequívoca.

La decisión de fondo puede ser correcta (aplicaciones sin contenido relevante), pero la razón registrada no lo dice, y para W03322 no se cumple la regla de exclusión por título. **Se requiere:** revisar con razón propia por obra las 112 exclusiones de esa plantilla y las 126 de la plantilla "physical, clinical, biological, social or human-learning", leyendo el resumen donde exista. Las que no tengan resumen y no sean inequívocas pasan a PENDIENTE_ACCESO.

## Hallazgos nuevos

### N1. Pérdida de identificadores en `cribado.csv`
`q15_package.py` toma `doi`, `arxiv`, `url`, `autores` y `fecha_publica` solo del primer miembro elegible de cada obra (`m = eligible[0]`). Además, no extrae el identificador de arXiv de la URL.
- Hay 1 011 filas con URL o `version_id` de arxiv.org y la columna `arxiv` vacía.
- En los pares confirmados por DOI (W00684/W00911, W01272/W01520, W03436/W03458, W03439/W03459 y W03472/W03571), **`doi` y `arxiv` están vacíos en ambos miembros**, aunque `identity_adjudication.csv` sí los tiene.

**Se requiere:** reunir los identificadores de todos los miembros elegibles y extraer el ID de arXiv de la URL. Sin esto, la deduplicación y la extracción pierden la referencia primaria verificable que exige la sección 7 del protocolo.

### N2. `q15_refine.py` no reproduce el estado final
La lista `ambiguous` asigna VERIFY a 48 índices, pero el estado final tiene 43. Los índices 902, 1392, 1986, 2078 y 4459 se cambiaron después tras leer su resumen (3 a RETAIN y 2 a EXCLUDE), y ese paso no está en ningún script entregado.

### N3. Grupos de identidad que salen del universo cribado
9 de los 135 grupos de `identity_adjudication.csv` tienen miembros fuera de las 4 481 obras: TG043, TG081, TG127, TG128, TG129 y TG133 tienen un miembro dentro, y TG076, TG077 y TG080 ninguno. El reporte debe aclarar que los grupos se calcularon sobre las obras seleccionadas, no solo sobre las elegibles.

### N4. Grupos con decisiones divergentes
15 grupos de título duplicado tienen un miembro en PENDIENTE_ACCESO y otro en INCLUIR_PARA_TEXTO o CONTEXTO: TG006, TG025, TG032, TG033, TG034, TG036, TG038, TG058, TG062, TG088, TG091, TG107, TG108, TG110 y TG126. No se pueden fusionar sin verificar identidad, pero conviene priorizar su resolución.

### N5. Vocabulario de decisiones
`cribado.csv` usa códigos de decisión (INCLUIR_PARA_TEXTO, EXCLUIR_FUERA_TEMA…) distintos de las razones que enumeran `plantillas/README.md` y `plantillas_v2/README.md` (RELEVANTE, HOMONIMO, APLICACION_SIN_RELACION…). Es coherente internamente, pero falta una tabla de equivalencias.

## Efecto en la entrega C
- La entrega C conservó las 410 exclusiones de B apoyándose en H4. La corrección de H4 aplica también a C.
- N1 a N5 deben atenderse en la consolidación final de C, no lote por lote, salvo que el responsable decida otra cosa.
