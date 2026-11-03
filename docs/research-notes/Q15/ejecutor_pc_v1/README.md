# Ejecutor Q15 v3 para PC — borrador para auditoría

**Productor v1.1 en BORRADOR. No ejecutar búsquedas reales antes de la auditoría de Claude.**

El archivo único [ejecutar_q15_v3.py](ejecutar_q15_v3.py) produce metadatos y archivos de recuperación; no entrena, calcula geometría, adjudica novedad ni decide qué fuentes se han leído. Lee `consultas_v2.csv`, `plan_busquedas_v3.csv`, `LIMITES_v3.json`, el protocolo operativo y S0, verificando sus SHA. Los originales permanecen intactos.

Código y suite vigente en el commit `7056e0dd05cb8ed2b280c2c877d5f6cd7b75487c`:

| Archivo | SHA-256 |
|---|---|
| Productor | `d561cb0bdccdd40fb91e5d0553ac85dbc58adc13e7487c7f1a1c226b2af1ee41` |
| [Suite vigente v1.1](pruebas_ejecutar_q15_v3_v1_1.py) | `f9fd933d0d3f6417874fca7cb855d9951380baa4a6c3eb2629781f9ed2916671` |

## Antes de ejecutar: decisión de compatibilidad pendiente

La v3 fija cadenas booleanas de Semantic Scholar y orden por relevancia de `/paper/search`. La [documentación oficial](https://api.semanticscholar.org/api-docs/graphs) especifica texto sin sintaxis especial para ese endpoint; la búsqueda booleana está en `/paper/search/bulk`. No se puede garantizar simultáneamente la sintaxis y el orden actuales usando esos endpoints como si fueran equivalentes.

**El productor no cambia el protocolo ni simula cumplimiento:** construye las URL previstas, pero deja esas 55 consultas como `PENDIENTE_ENMIENDA_S2`, sin enviarlas. Sí implementa y ejecuta, cuando se autorice, las consultas arXiv, los catálogos y la resolución/recuperación de referencias y citas de S0. La [nota de compatibilidad](COMPATIBILIDAD_Y_AUDITORIA.md) expone la decisión necesaria antes de la ejecución real completa.

## Fases y cobertura

| Fase | Qué hace |
|---|---|
| `preparar` (predeterminada) | Valida los insumos y publica 294 entradas de plan y URL, sin red. |
| `consultas` | arXiv por API export, relevancia descendente; S2 con el bloqueo de compatibilidad descrito. |
| `catalogos` | Descubre y recupera NeurIPS y los volúmenes ICML de PMLR; OpenReview v1 hasta 2023 y v2 desde 2024, con `venueid` aceptado exacto. Aplica las consultas locales después de recuperar metadatos. |
| `citas` | Resuelve solamente las 19 anclas, publica S0 resuelta y recorre un nivel hacia atrás/adelante. No expande vecinos. |
| `todo` | Todas las fases de recuperación y sus estados, preservando lo ya escrito. |

Google Scholar queda siempre `OMITIDA_OPCIONAL`: no se envían solicitudes, no hay automatización de CAPTCHA. `--bases` permite ejecutar fases por base; lo no seleccionado se marca `NO_EJECUTADA_EN_ESTA_FASE`, nunca cero resultados. Después, `--fase todo` puede agregar los trabajos ya recuperados desde caché sin repetirlos.

No se ocultan años ausentes: los formatos históricos de OpenReview que no permitan contrastar aceptados quedan pendientes; PMLR no cubre el histórico ICML anterior a su serie; un año no listado —incluido el año de corte— requiere comprobación humana, no se trata automáticamente como inexistente. Estas limitaciones impiden declarar completa una búsqueda de actas que no lo esté. El programa no inventa una fecha pública a partir del año 2026 ni convierte una página «Loading» en catálogo vacío.

## Reglas implementadas

- Consultas: ≤500, todas; >500, primeras 200; total desconocido, sondeo hasta 501 como máximo. Cupo antes de deduplicar y postfiltrar autor/fecha; no se repone por exclusión. Paginación inconsistente, total cambiante o acceso parcial quedan registrados.
- Actas: AND de grupos/OR de frases literales sobre título o resumen, Unicode NFKC/casefold/espacios según v3. Orden por año descendente, título e ID ascendentes antes del tope. No se trunca el catálogo a 200 documentos antes de buscar: eso cambiaría la revisión.
- Citantes: conteo >500 o desconocido activa la ruta local autorizada: primeras 200 posiciones nativas y después filtro DIN. No se completa el cupo con coincidencias posteriores. ≤500, se recuperan todos sin ese filtro. Referencias hacia atrás no usan filtro DIN. La falta de resumen deja `PENDIENTE_FILTRO` cuando el título no basta.
- Fechas parciales: se comparan intervalos posibles; si cruzan el corte, quedan pendientes. Título coincidente no permite inventar un día. La fecha de una consulta se registra en UTC y America/Mexico_City.

## Conservación, reanudación y pausas

La salida tiene que estar **fuera del clon Git**. `IDENTIDAD.json` vincula script, insumos y modo; se rechaza reutilizarla con otro código o mezclar simulación con red. Un bloqueo de archivo impide dos productores simultáneos sobre la misma salida; se libera al terminar el proceso. Los cuerpos, metadatos y resultados se publican con escritura temporal exclusiva y promoción sin reemplazo (`os.rename` exclusivo en Windows, enlace exclusivo en POSIX). Los temporales de una interrupción se conservan; no se reutiliza su nombre ni se sobreescribe un destino.

Una respuesta exitosa se reutiliza solo tras verificar SHA y cuerpo. Se conservan también 429, 403, errores de transporte y todas las versiones de resultados. La reanudación normal salta trabajos terminados y conserva fallos; `--reintentar-fallos` permite intentos/versiones nuevas, sin borrar las anteriores. Si hay una modificación del script, se usa otra carpeta de salida; no se adopta un conjunto previo como si perteneciera al código nuevo.

Semantic Scholar espera al menos 1,1 s entre solicitudes, también antes de la primera tras arrancar; `--pausa-s2` no permite valores <1 s. arXiv espera al menos 3 s. Los demás hosts, 1 s. Hay hasta 5 reintentos adicionales ante 429/errores transitorios, con backoff y respeto de `Retry-After` (segundos o fecha). Cada intento deja su cuerpo, metadatos y SHA. La clave opcional `S2_API_KEY` se toma del entorno; no se guarda ni se pasa por URL. S2 no sigue redirecciones fuera del limitador; los demás redireccionamientos conservan su trazabilidad y no reenvían credenciales entre hosts.

Se imprime progreso por consulta, por volumen y cada 50 solicitudes. La recuperación completa de resúmenes puede ser larga: el programa no reduce años ni limita el catálogo para acelerar el matching. No se ha medido un tiempo real con internet normal; los tiempos de fixtures no son una estimación de coste real.

## Salidas

```text
IDENTIDAD.json
raw/<sha_url>/attempt_000001.body
raw/<sha_url>/attempt_000001.json
jobs/<identificador>/result_000001.json
S0/resolved_000001.json
runs/run_000001.json
runs/run_000001/busquedas.csv
runs/run_000001/registros.csv
runs/run_000001/citas.csv
```

Los JSON de respuesta incluyen URL solicitada/final, redirecciones, HTTP, UTC/México, SHA del cuerpo y del script, tamaño y errores. Los resultados de trabajos tienen SHA y no sustituyen versiones anteriores. Los CSV son índices derivados, UTF-8 con BOM para Excel; el registro completo de vecinos y pendientes sigue en JSON. Los fallos no se convierten en filas vacías exitosas.

Código de salida: **0**, fase preparada o recuperación seleccionada sin pendientes registrados; **2**, hay búsquedas, catálogos o grafos pendientes (no es un cierre); **1**, error de integridad, entradas, uso o sistema. Una búsqueda `COMPLETA` significa recuperación conforme dentro del alcance, no texto completo leído ni revisión terminada. Con la incompatibilidad S2 presente no se debe esperar cierre completo de `todo`.

## Prueba y procedimiento

La [suite vigente](pruebas_ejecutar_q15_v3_v1_1.py) pasó **66/66** con transporte simulado, reloj simulado y red bloqueada por las pruebas; incluye un recorrido de las 55 consultas arXiv y su reanudación. El [informe](PRUEBAS_SIMULADAS.md) y [run_04](pruebas_simuladas/run_04.json) fijan los SHA efectivamente probados. La prueba de la rama Windows simula sus primitivas; **todavía no es una ejecución en Windows ni validación de servicios vivos**.

Python 3.12 o posterior; biblioteca estándar y [tzdata fijada para Windows](requirements.txt). No necesita torch, numpy, scipy ni sklearn. Los comandos reproducibles están en [PROCEDIMIENTO_WINDOWS.md](PROCEDIMIENTO_WINDOWS.md). Antes de usar red, Claude debe auditar este borrador y resolverse la incompatibilidad del protocolo.
