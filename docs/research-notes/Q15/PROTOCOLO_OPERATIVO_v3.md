# Q15: protocolo de revisión sistemática de la novedad de DIN

**Estado: OPERATIVA AUTORIZADA. Versión 3, 2026-11-02.**

Esta v3 incorpora la aprobación de Claude de v2 trasladada por el responsable y su único ajuste: año descendente para las actas truncadas; la [v1](PROTOCOLO_BORRADOR_v1.md) y su manifiesto permanecen intactos. Los cambios se enumeran en [CAMBIOS_v1_v2.md](CAMBIOS_v1_v2.md). Este documento fija el procedimiento antes de buscar. No es una revisión ejecutada ni una declaración de novedad. Primero se comprometen este protocolo, las consultas y las plantillas; después de la auditoría se registra la versión autorizada y su commit antes de ejecutar búsquedas. Una modificación se publica como enmienda antes de usarla, sin borrar el procedimiento ni las salidas anteriores. No se ejecutan experimentos ni análisis de cohortes.

## 1. Preguntas y afirmaciones que se comparan

La unidad de comparación es la afirmación científica y sus supuestos, no el nombre DIN ni una coincidencia de palabras. Para cada pregunta se buscarán antecedentes favorables y rivales, incluyendo los que vuelvan esperable el resultado por construcción.

| Punto | Pregunta de revisión | Descomposición obligatoria |
|---|---|---|
| 1 | ¿Qué antecedente tiene D como comparación predictiva? | Definición de R² fuera de muestra respecto de una base, validez incremental, validación por grupos y diferencia entre métrica y aplicación. |
| 2 | ¿Qué se conoce sobre confianza temprana que anticipa confianza, dificultad o geometría final? | Predicción por ejemplo y por corrida; comparación dentro de split entre inicializaciones frente a comparación entre arquitecturas o hiperparámetros; ajuste por información temprana rival y evaluación fuera de muestra. |
| 3 | ¿Qué se conoce de la geometría perspectival de DIN? | 3a: kernel de gradientes blanqueados por Fisher; 3b: pullback por un campo softmax; 3c: longitud mínima de semirrectas al borde y su relación con la distancia geodésica. Se juzgan por separado antes de sintetizar el punto. |
| 4 | ¿Qué antecedente tiene que la concentración o la escala de logits module la señal temporal? | 4a: calibración/sobreconfianza y regularización; 4b: vínculo algebraico o empírico de concentración, confianza y escala; 4c: modulación del incremento predictivo, distinguiendo asociación, intervención y mecanismo identificado. |

La prioridad de lectura es el punto 4 y sus conexiones con 2 y 3. Se cubren temperature scaling, LogitNorm, label smoothing, penalización de logits y weight decay; dinámica temprana de confianza y Fisher; dificultad por ejemplo; kernels de Fisher y geometría de la información en redes. Se añaden explícitamente extrapolación de curvas de aprendizaje, predicción del rendimiento final, sesgo implícito de la entropía cruzada, margen máximo/crecimiento de logits y NTK frente a Fisher empírica y del modelo. La prioridad no elimina ninguna consulta ni permite detener la búsqueda al encontrar una explicación conveniente; sí se aplican los topes predeclarados del §4.

### 1.1 Diccionario matemático para evitar equivalencias falsas

- En DIN, D = 1 − SSE_completo / SSE_base, calculado fuera de muestra. Es una mejora relativa respecto de la base; no es necesariamente la resta de dos R² con denominador SST. La novedad de la fórmula no se reivindica. Se verificará y citará su antecedente primario, además de distinguir el diseño de evaluación de la fórmula.
- El objeto de comparación es M = R(F + γI)⁻¹Rᵀ, donde las filas de R son gradientes de log-probabilidad y F es la Fisher usada por el instrumento. Se buscarán equivalentes bajo cambios de notación, especialmente Fisher kernels, kernels de gradientes y natural gradient. Se anotará si cada fuente usa Fisher del modelo, Fisher empírica, Gauss–Newton u otro objeto.
- El campo perspectival es a(P) = softmax(fP), J = ∂a/∂P y G(P) = J(P)ᵀ M J(P), con M fija para el estado considerado. No se identifica automáticamente con Fisher–Rao del simplex, con la Fisher de parámetros ni con NTK.
- La cantidad ρ_ray = inf_{‖u‖=1} ∫₀^∞ √(uᵀG(su)u) ds restringe las curvas a semirrectas del parámetro natural. En general d_borde ≤ ρ_ray: una longitud de curva concreta da una cota superior, no la distancia geodésica exacta. Se distinguirán rayos a vértices y normales de caras completas. No se buscará solo la frase «distancia al borde».
- c = max_n M_nn / tr M mide concentración diagonal sobre ejemplos. No es tr F, rango efectivo espectral ni el neural collapse de representaciones por clase. La escala de logits es la raíz media cuadrática de logits centrados entre clases; temperatura modifica confianza y las cantidades recalculadas del instrumento.
- Las aproximaciones propias M ≈ N diag((1−p)/p) y ρ ≈ √(N·odds_k)/n tienen condiciones de rango interpolante, ridge despreciable y concentración apropiada. Se comparan con literatura como implicaciones condicionales; no se transforman en identidades universales ni en afirmaciones atribuidas a una fuente que no las demuestra.

## 2. Contexto y cortafuegos documental

Se usan la [síntesis del PR #137](https://github.com/jaiborojas-cloud/leviathan/pull/137), archivada sin editar en [fuentes/research-status_PR137.txt](fuentes/research-status_PR137.txt), y la [primera pasada de Q15](../revision-literatura-Q15.md). La procedencia exacta está en [CONTEXTO.md](CONTEXTO.md). No se modifica ninguna de ellas.

El resultado oficial de Q13-SEP es NO_IDENTIFICABLE en la familia y las manipulaciones estudiadas. El movimiento conjunto de c y escala vuelve central la explicación por sobreconfianza/escala; no demuestra inseparabilidad universal ni identifica causalidad. La revisión no cambiará estados oficiales, reabrirá análisis cerrados ni convertirá los antecedentes en confirmaciones de DIN.

La primera pasada fue dirigida, no sistemática. Sus etiquetas de lectura y sus afirmaciones bibliográficas no se heredan como verificación de esta revisión. Todas sus referencias empiezan aquí como candidatas `[título]`, con metadatos pendientes. Ni siquiera la existencia de una referencia de 2026 se dará por confirmada hasta resolverla en una fuente primaria.

Se registra una discrepancia de terminología sin reescribir aquel documento: allí se llamó a ρ_borde «distancia geodésica al borde». Para el objeto medido por semirrectas, este protocolo usa longitud/cota superior, conforme a la distinción de E16-AG/AH. Asimismo, el parecido entre intervenciones LS y LP descrito en la primera pasada es una hipótesis bibliográfica que se verificará en el original; no se toma como mecanismo independiente ya resuelto.

## 3. Fuentes, fechas e idiomas

**Corte bibliográfico: 2026-11-02, inclusive.** Puntos 1 y 3: 1900-01-01 a 2026-11-02. Puntos 2 y 4: 1990-01-01 a 2026-11-02. Una consulta transversal usa el intervalo más amplio y el filtrado final se hace por afirmación. Se toma la primera disponibilidad pública verificable, conservando por separado fecha de preprint y de publicación. Para preprints se lee y cita una versión disponible al corte. Una versión posterior puede anotarse como posterior, sin introducirla retrospectivamente en el corpus principal. Fechas incompletas o contradictorias quedan pendientes.

| Base | Interfaz prevista y alcance | Condición |
|---|---|---|
| arXiv | API de búsqueda/exportación; título y resumen, metadatos y versiones; dominio oficial [arxiv.org](https://arxiv.org/) | Obligatoria. |
| Semantic Scholar | Graph API de búsqueda de artículos y referencias/citas; interfaz pública si es necesaria; [semanticscholar.org](https://www.semanticscholar.org/) | Obligatoria. Se registran límites de acceso y cobertura. |
| Google Scholar | Interfaz pública [scholar.google.com](https://scholar.google.com/), sin eludir CAPTCHA ni restricciones | Opcional por accesibilidad, como pidió el responsable. Un bloqueo no equivale a cero resultados. |
| NeurIPS | Catálogo y páginas oficiales de [proceedings.neurips.cc](https://proceedings.neurips.cc/), hasta el corte | Obligatoria, conferencias principales; suplementos cuando se vinculen a un artículo incluido. |
| ICML | Volúmenes ICML de [PMLR](https://proceedings.mlr.press/) y archivo oficial histórico cuando corresponda | Obligatoria. No tratar todo PMLR como ICML. |
| ICLR | Actas oficiales y registros aceptados de [OpenReview](https://openreview.net/), hasta el corte | Obligatoria desde la existencia de ICLR. No tratar toda sumisión a OpenReview como artículo aceptado. |

No hay exclusión por idioma. Las consultas iniciales son en inglés, sesgo que se declarará. Una fuente relevante en otro idioma se evalúa con el mismo criterio y se indica cualquier limitación de lectura o traducción. Artículos de otros venues, como EMNLP, entran por Semantic Scholar, arXiv o seguimiento de citas; las tres actas prioritarias no limitan el corpus elegible.

Las herramientas web generales o de recuperación de artículos solo ayudan a resolver metadatos y obtener el original. No sustituyen una búsqueda de las bases fijadas. Un resumen generado por una herramienta no cuenta como lectura del resumen de los autores ni del texto completo.

## 4. Consultas exactas y ejecución reproducible

[consultas_v3.csv](consultas_v3.csv) contiene 43 consultas temáticas y 12 búsquedas de resolución de anclas. Las 44 consultas de v1 se conservan literalmente; se agregan T08–T10, L12–L15 y G11–G14 (11 temáticas). Incluye la expresión lógica, su traducción literal para arXiv, Semantic Scholar y Google Scholar, los filtros de autor cuando corresponden y el intervalo. [plan_busquedas_v3.csv](plan_busquedas_v3.csv) enumera cada combinación a ejecutar: 258 temáticas (43 × 6 bases) y 36 de resolución (12 × 3), 294 en total; 55 de Google Scholar son opcionales y 239 son obligatorias. También fija el orden y N/K por fila. Son unidades planificadas, **no búsquedas ya efectuadas ni resultados**.

Para arXiv se fija la búsqueda de cada término en título O resumen, con grupos OR y conjunción entre grupos, más submittedDate. Para Semantic Scholar se fija la consulta booleana del CSV; la autoría se comprueba sobre metadatos, no suponiendo que el nombre del autor esté en el resumen. En Google Scholar se usan frases entre comillas y OR según el CSV y los filtros de año de su interfaz. Se registra la cadena efectivamente enviada y la versión/interfaz, además de la cadena planificada.

Para actas se recupera el catálogo oficial y se aplica la expresión del CSV a título y resumen disponibles: texto Unicode NFKC, casefold, espacios consecutivos normalizados; coincidencia de cada frase como subcadena literal, OR dentro de cada grupo y AND entre grupos. No hay stemming ni sinónimos implícitos. Se guardan los metadatos originales y sus hashes. Si falta el resumen, se intenta recuperarlo en la página oficial y se registra el campo ausente; buscar solo títulos no se presenta como cobertura completa de título/resumen. Para los años anteriores a la existencia de una conferencia se registra NO_APLICA, no un fallo ni una búsqueda de cero resultados.

### 4.1 Límites fijados antes de buscar: N = 500, K = 200

Se sustituye expresamente el «sin máximo» de v1 por una **revisión sistemática acotada**. Para cada combinación consulta × base, si el total es ≤ 500 se recuperan y criban todos; si es > 500 se criban **los primeros 200 registros en el orden fijado** y se registra **TRUNCADA_DECLARADA**, incluso si los seleccionados contienen pocos artículos relevantes. N = 500 permite completar consultas precisas; K = 200 limita el cribado de las amplias sin seleccionar a mano resultados favorables. Son límites operacionales, no garantías estadísticas de cobertura. No se aplica un tope global retrospectivo.

| Base | Orden predeclarado antes de seleccionar |
|---|---|
| arXiv | relevance descendente (`sortBy=relevance`, `sortOrder=descending`). |
| Semantic Scholar | Relevancia nativa de `paper/search`, conservando exactamente el orden recibido. No cambiar a «más citados» ni «más recientes» según resultados. |
| Google Scholar | Relevancia nativa; orden por fecha desactivado y patentes desactivadas. Se registra región/idioma de interfaz y sesión sin personalización cuando sea posible. |
| Actas NeurIPS, ICML, ICLR | Tras filtrar por consulta, año descendente, título normalizado NFKC/casefold ascendente e identificador oficial ascendente para desempatar. |

Dentro de una respuesta ordenada por el proveedor se mantiene su desempate nativo, se guardan orden, IDs y hash de la exportación. La relevancia del proveedor puede cambiar con el tiempo: la reproducibilidad se refiere al snapshot fechado, no a garantizar idéntico ranking futuro. Si no se puede obtener el orden fijado, se registra el impedimento y se enmienda antes de usar otro.

Si el total comunicado exacto o aproximado es > 500 se activa el tope; el tipo de conteo se informa. Si es desconocido, o un total ≤ 500 no permite asegurar el final, se sondea como máximo hasta la posición 501: final verificado ≤ 500 permite completar; alcanzar 501 activa el tope y solo las posiciones 1–200 van al cribado. El sondeo conserva sus metadatos, pero las posiciones adicionales se marcan NO_CRIBADO_TOPE. Si ni el final ni el umbral se pueden observar por acceso, se declara PARCIAL/TRUNCADA_ACCESO, sin inventar total. Un conteo aproximado no se presenta como exacto.

El cupo se cuenta sobre posiciones de registros de la consulta, antes de deduplicar y de filtros que la base no pueda ejecutar (autoría o fecha precisa, por ejemplo). No se repone un duplicado, exclusión o falta de resumen con la posición 201. Se registran seleccionados, duplicados, no elegibles y pendientes por separado. El total de coincidencias no es el número de obras únicas ni de artículos incluidos. Un tope propio y un bloqueo del servicio pueden coexistir y se registran ambos.

[LIMITES_v3.json](LIMITES_v3.json) fija las constantes y el filtro del §5 en formato legible por máquina. No se ampliará K después de ver una conclusión incómoda. Cambiar límites u orden requiere enmienda previa; tampoco se declara exhaustividad por haber agotado el cupo.

No se alteran términos para mejorar una conclusión. Si una interfaz no soporta la sintaxis fijada, se registra el intento y se prepara una enmienda de traducción, con la nueva cadena literal y su motivo, antes de ejecutarla. Las reformulaciones, consultas adicionales y hallazgos incidentales conservan su procedencia diferenciada. Un error de acceso puede reintentarse sin cambiar la consulta, registrando ambos intentos y respetando los límites del servicio.

## 5. Anclas y seguimiento de citas: un nivel

[anclas_heredadas_v1.csv](anclas_heredadas_v1.csv) preserva los 16 enlaces de la primera pasada como candidatos, no como referencias verificadas. La página secundaria de R² no se convierte en el artículo primario. Las 12 búsquedas A01–A12 resuelven autores/títulos de los trabajos clave y amplían a calibración de Guo, natural gradient de Amari, Fisher kernel de Jaakkola–Haussler y el antecedente primario de Campbell–Thompson. Son objetivos de búsqueda, no citas ya comprobadas.

Antes de recorrer el grafo se publica la lista S0 de identificadores canónicos verificados: los 15 candidatos a artículos de la primera pasada que puedan resolverse, más los cuatro antecedentes primarios recién indicados, deduplicados. Un candidato inexistente, discordante o de fecha posterior se documenta como tal y no se reemplaza silenciosamente. Las consultas de autor ayudan a resolver anclas ya previstas; no crean una selección según el resultado DIN.

Se mantiene **un solo nivel**, con metadatos de la fuente primaria y el grafo de Semantic Scholar; los «citado por» de Scholar son complemento si accesibles. Para referencias hacia atrás no hay filtro DIN: se recuperan todas hasta 500 y, si superan 500, las primeras 200 en el orden de la bibliografía/grafo guardado, con TRUNCADA_DECLARADA. No se promete recuperar todos los vecinos sin límite.

### 5.1 Citantes de anclas muy citadas

Si un ancla tiene **más de 500 citas**, se criban solo citantes cuyo **título o resumen** contenga al menos un término del filtro DIN predeclarado siguiente. Con exactamente 500 citas no se activa el filtro. Si el conteo es desconocido se activa por factibilidad y se declara CONTEO_DESCONOCIDO; nunca se interpreta como cero. El conteo bruto disponible al identificar S0, incluso si incluye citas posteriores al corte, decide esta rama y se guarda con fecha; los artículos posteriores siguen fuera del corpus.

**Filtro DIN, OR de frases:** `early`, `Fisher`, `training dynamics`, `confidence`, `calibration`, `overconfidence`, `logit`, `logits`, `LogitNorm`, `softmax`, `implicit bias`, `max margin`, `maximum margin`, `neural tangent`, `learning curve`, `learning curves`, `forgetting`, `difficulty`, `information geometry`.

Este filtro incluye los cuatro términos sugeridos en la auditoría y términos de las tres coberturas nuevas para no eliminarlas por diseño. La coincidencia se evalúa sobre título y resumen por separado: Unicode NFKC + casefold, guiones ASCII/Unicode convertidos a espacio, espacios colapsados y frase literal delimitada por límites de palabra Unicode. No se buscan automáticamente raíces o sinónimos. Un título que coincide basta; sin coincidencia en título y sin resumen, el estado es PENDIENTE_FILTRO, no «irrelevante». No se lee el texto completo de miles de citantes para decidir este filtro.

1. **Si la interfaz permite filtrar dentro de citantes:** se guarda la cadena literal enviada (OR de los términos, agrupada), el identificador del ancla y el resultado. El límite de §4.1 se aplica al total filtrado, con el orden de citantes recibido del proveedor, sin reordenación manual. Si su sintaxis no equivale al filtro fijado, no se presenta como búsqueda exacta: se usa la ruta 2 y se documenta.
2. **Si la interfaz no permite el filtro del lado del servidor:** no se descarga el grafo entero de un ancla con miles de citas. Se toman solo las primeras 200 posiciones de la lista nativa de citantes de esa ancla y se aplica el filtro localmente. Esta es **TRUNCADA_DECLARADA antes del filtro**, aunque solo sobrevivan unas pocas. No se buscan más posiciones para llenar 200 coincidencias. Orden nativo significa orden recibido, sin presumir ranking por relevancia, antigüedad o citas que la API no garantice. Se guardan IDs y respuestas fechadas; no se mezcla con la ruta 1 como si fueran equivalentes. Si se desconoce el conteo, esta ruta también se limita a 200 y conserva esa incertidumbre.

Para anclas con conteo conocido ≤ 500 se criban todos los citantes, sin filtro DIN, hasta ese número. Se registra por ancla y dirección: conteo bruto, rama, ruta, filtro, total filtrado si se conoce, número recuperado, número con resumen ausente, seleccionados y límite efectivo. Una referencia central conocida de antemano sigue en S0 aunque no pase el filtro; el filtro restringe la expansión, no borra anclas ni hallazgos de consultas independientes. La ausencia de grafo es falta de acceso, no ausencia de antecedentes.

Los vecinos se criban y, si son relevantes, se leen; no se recorren sus propios vecinos (sería nivel 2). Un artículo relevante descubierto incidentalmente se conserva como INCIDENTAL, sin fingir que estaba en S0. Ampliar el grafo o las consultas exige una enmienda previa. No se excluye una refutación o un equivalente cercano por su ruta incidental.

## 6. Elegibilidad, deduplicación y cribado

**Incluir:** investigación primaria teórica o empírica que defina, demuestre o pruebe un objeto o afirmación de 1–4; trabajos metodológicos de evaluación incremental; fundamentos de información geométrica/kernels pertinentes; dinámica temprana, dificultad por ejemplo y calibración/regularización que puedan explicar el resultado. Se admiten artículos revisados, preprints y capítulos/libros de fundamento, con tipo y estado editorial separados. La revisión por pares no se presume a partir de arXiv.

**Excluir con razón registrada:** fuera de fecha; duplicado de la misma obra; homónimo no pertinente; aplicación sin contenido relevante para las preguntas; material sin fuente identificable tras los intentos documentados. Revisiones, tutoriales y notas secundarias sirven de contexto o ruta a originales, no de prioridad intelectual primaria. Un paywall, un abstract no disponible o un enlace roto no justifican «no pertinente»: quedan PENDIENTE_ACCESO o PENDIENTE_VERIFICACIÓN.

Dos pasos: (i) título/resumen para pertinencia y (ii) texto para verificar la afirmación. Se conserva decisión, razón, fecha, revisor y conflictos. Los desacuerdos con la auditoría se registran; no se simula cribado doble independiente si solo hubo un lector. Se agrupan DOI, familia arXiv y publicación de la misma obra, preservando versiones y diferencias relevantes; no se cuentan como estudios independientes. Los artículos distintos de un mismo grupo no se fusionan por compartir autores.

No se excluye un antecedente porque use otro dataset, año de entrenamiento, arquitectura, número de clases o acrónimo si contiene la misma afirmación. Tampoco se equipara «aprendizaje temprano importa» a haber mostrado exactamente el incremento DIN. El corpus incluido se ordena por cercanía conceptual y las fuentes más cercanas se leen completas antes de adjudicar novedad.

## 7. Extracción y niveles de lectura

Se usa [plantillas_v2/extraccion.csv](plantillas_v2/extraccion.csv), una fila por obra y versión evaluada. Campos obligatorios: referencia y enlace primario verificable, fecha/versión, estado editorial, qué afirma la fuente, método, objetos matemáticos, unidad de comparación, predictor/desenlace/tiempos, base rival, intervención, relación con cada punto, secciones o páginas comprobadas, limitaciones, y qué es inferencia del revisor.

Toda referencia presentada lleva enlace y etiqueta:

- `[título]`: no se ha leído contenido primario suficiente. Se separa metadato verificado de candidato todavía no verificado. La etiqueta nunca implica existencia confirmada por sí sola.
- `[leído]`: además se declara alcance **RESUMEN**, **FRAGMENTOS** o **TEXTO_COMPLETO**, fecha y ubicación. Leer una página de resumen no autoriza afirmar que se leyó el PDF completo.

Una relación se codifica EQUIVALENTE_DIRECTO, ANTECEDENTE_PARCIAL, IMPLICACIÓN_CONDICIONAL, RELACIONADO o NO_PERTINENTE, con justificación. Se compara fórmula/hipótesis, no solo título. Para una implicación se distingue lo demostrado por la fuente de la deducción propia. Ausencia de una fórmula en el resumen no prueba que falte en el artículo.

Se comprobarán especialmente: Fisher del modelo frente a empírica; inversión/ridge; qué espacio recibe la métrica; M fija o variable; curvas admisibles y borde; normalización; si la predicción es realmente temprana; si se ajusta por confianza previa; validación por split; medidas de confianza calibrada frente a escala sin calibrar. Un efecto de temperature scaling sobre confianza no constituye por sí solo evidencia de modulación de D. Neural collapse no equivale automáticamente a concentración diagonal de M.

## 8. Síntesis y regla de adjudicación

La entrega posterior tendrá una conclusión por punto y subpunto, con citas y alcance de lectura. Se usará:

| Etiqueta | Regla |
|---|---|
| **ya conocido** | Un antecedente verificado establece la misma definición/afirmación bajo condiciones comparables, o se demuestra su equivalencia por cambio de notación con supuestos explícitos. No se necesita coincidencia del nombre DIN. |
| **parcialmente cubierto** | Hay antecedentes de componentes sustantivos o una explicación condicional conocida, pero queda una combinación, prueba empírica o condición específica no establecida por esas fuentes. Se enumera exactamente qué queda y qué no. |
| **nuevo** | No se encontró un antecedente equivalente tras completar el procedimiento aplicable y leer los originales más cercanos. Significa «no encontrado en el alcance y corte declarados», no «primero en la historia». Se explicita la contribución residual, sin basarla solo en nombres, constantes o datasets. |

Los filtros y topes autorizados son límites de alcance, no búsquedas incumplidas: completar el procedimiento acotado permite adjudicar solo dentro de ese alcance, siempre mostrando por punto cuántas búsquedas y expansiones se truncaron. Un punto etiquetado «nuevo» dirá «sin antecedente equivalente encontrado en la búsqueda acotada», nunca «búsqueda exhaustiva»; se señala el riesgo de omisión por ranking y filtro. Si una fuente cercana conocida o un hueco crítico no puede evaluarse, no se compensa con esa fórmula de alcance. Si falta acceso crítico, búsqueda obligatoria dentro de sus límites, resolución de una ancla central o lectura de una fuente cercana, el punto queda **PENDIENTE, sin adjudicar** hasta resolverlo; no se fuerza una de las tres etiquetas. Un bloqueo opcional de Scholar se declara y limita el alcance, sin equivaler a una revisión mundial exhaustiva. Los antecedentes secundarios no bastan para atribuir la prioridad de un resultado original.

Se publican tanto los solapamientos como los posibles residuos nuevos. Se distinguirá: idea amplia conocida; objeto matemático conocido o nuevo; aplicación particular; evidencia propia; generalidad; mecanismo. No se concluirá que c causa la señal, que escala la explica por completo, ni que M/ρ añaden información independiente de confianza sin comprobar los supuestos. La conclusión de novedad no modifica los resultados oficiales de DIN.

No habrá metaanálisis de tamaños de efecto incompatibles ni puntuación numérica de novedad. Se entrega una matriz fuente × afirmación con citas directas breves, páginas/ecuaciones y lectura, más la conclusión razonada por punto. Se muestra el embudo de registros obtenidos, deduplicados, cribados, pendientes e incluidos, sin llamar a esta revisión PRISMA completa si no se han cumplido y documentado sus requisitos.

## 9. Registro, integridad y cierre de la fase

Las plantillas de [plantillas_v2/](plantillas_v2/) fijan log de búsquedas, cribado, citas, extracción y conclusiones. Cada búsqueda registra fecha/hora UTC y America/Mexico_City, base/interfaz, cadena exacta, filtros, orden, paginación, total declarado y tipo de conteo, N/K, orden y posiciones seleccionadas, filtro y si se aplicó antes o después del tope, registros recuperados/cribados/no cribados, fallos y hash del artefacto crudo. El informe separará completo dentro de límites, truncamiento declarado y truncamiento por acceso. Los registros bloqueados dejan conteos desconocidos vacíos, no cero. Se almacenan metadatos/exportaciones permitidas, no copias públicas de PDFs restringidos.

Se guardan versiones, hashes y fallos; correcciones mediante archivos nuevos/enmiendas. Se prohíbe borrar un resultado negativo de búsqueda o cambiar una referencia discordante sin rastro. El [MANIFEST_OPERATIVA_v3.sha256](MANIFEST_OPERATIVA_v3.sha256) fija los archivos operativos y el manifiesto v2 sin modificarlo; [VERIFICACION_OPERATIVA_v3.json](VERIFICACION_OPERATIVA_v3.json) verifica estructura y procedencia documental, no resultados científicos ni búsqueda ya ejecutada.

**Criterio operativo:** aprobación recibida; se registra y compromete esta versión y su SHA antes de la primera consulta. Las consultas pasan a ejecución con las plantillas v2. La extracción y las conclusiones se publican por versiones, sin modificar este protocolo. Esta autorización de búsqueda no es una conclusión de novedad.


## 10. Acta de fijación de la versión operativa

El responsable comunicó el 2026-11-02 la aprobación de Claude del PR #138 v2 y autorizó iniciar la búsqueda después de un único cambio: ordenar las actas truncadas por año descendente, con título e ID ascendentes para desempatar. Se aplica ese orden también a las listas no truncadas, sin cambiar su conjunto. No cambian preguntas, cadenas, corte, anclas, N=500/K=200, filtro DIN ni reglas de adjudicación.

Esta versión operativa v3 se guarda en archivos nuevos; los borradores y sus manifiestos permanecen intactos. `REGISTRO_OPERATIVA_v3.json` registra SHA-256 del protocolo, consultas, plan y límites. El commit de fijación se cita en cada log de búsqueda posterior. La aprobación no convierte fuentes heredadas en verificadas ni permite sustituir bases inaccesibles por resultados web sin declararlo.
