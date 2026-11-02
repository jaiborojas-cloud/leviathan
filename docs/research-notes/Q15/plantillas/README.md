# Convenciones de registro

Estos CSV solo tienen cabeceras: no representan búsquedas ni fuentes evaluadas.

- `log_busquedas.csv`: una fila por página/intento. Estados: COMPLETA, PARCIAL, TRUNCADA, BLOQUEADA, ERROR, NO_APLICA. Total: EXACTO, APROXIMADO o NO_INFORMADO; un conteo desconocido queda vacío. Conservar el total por consulta además del conteo por página, sin sumar repetidamente el total declarado.
- `cribado.csv`: conservar las decisiones de título/resumen y texto por separado. Razones: RELEVANTE, FUERA_FECHA, DUPLICADO, HOMONIMO, APLICACION_SIN_RELACION, SECUNDARIA_CONTEXTO, PENDIENTE_ACCESO, PENDIENTE_VERIFICACION. PENDIENTE no es exclusión temática.
- `anclas_verificadas_S0.csv`: cerrar y publicar S0 antes de recorrer sus citas. Registrar por separado candidatos no resueltos.
- `citas_un_nivel.csv`: ATRAS o ADELANTE, nivel 1; conservar identificadores y registros crudos de cada dirección. Un vecino de varias anclas puede repetirse como arista, pero cuenta una sola vez como obra.
- `extraccion.csv`: separar afirmación de la fuente e inferencia propia; enlace primario obligatorio antes de usar como evidencia. `[título]` no confirma los metadatos; `[leído]` necesita RESUMEN, FRAGMENTOS o TEXTO_COMPLETO y ubicación. Los estados de lectura de la primera pasada no se heredan.
- `conclusiones_por_punto.md`: plantilla vacía de resultados. Las etiquetas de novedad se adjudican después de la extracción, no al planificar.

Fechas ISO 8601; UTF-8; campos CSV con comillas cuando sea necesario; enlaces persistentes preferidos; hashes SHA-256 en hexadecimal. Los JSON deben ser válidos y no contener NaN/Infinity. No colocar credenciales ni tokens en URLs guardadas.
