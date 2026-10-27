# Preparación del productor

El primer intento de adaptar el archivo en memoria falló con SyntaxError antes de escribir fuentes o ejecutar modelos. La causa fue usar offsets AST del texto original después de sustituir una cadena larga; se extrajeron ambas cadenas desde el texto original antes de sustituirlas. No se había publicado ni ejecutado ningún productor DR; no cambian diseño, receta, plan o resultados. Se conserva este incidente operacional. El productor preparado compila y sus dos fuentes embebidas coinciden byte por byte con Q13.
