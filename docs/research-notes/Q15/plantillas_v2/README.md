# Plantillas de registro v2

Las cabeceras están vacías de resultados. Sustituyen a las plantillas v1 para la ejecución de v2; las originales se conservan.

- Se mantienen las convenciones de [v1](../plantillas/README.md), con esta ampliación de estados: TRUNCADA_DECLARADA (tope propio), TRUNCADA_ACCESO (límite del servicio), PENDIENTE_FILTRO y NO_CRIBADO_TOPE. Una búsqueda puede tener un tope propio y un fallo de acceso: registrar ambas dimensiones, sin sobrescribir una con la otra.
- `log_busquedas.csv`: anotar N=500, K=200, posiciones, orden garantizado o simplemente recibido, total declarado/filtrado y tipo EXACTO/APROXIMADO/NO_INFORMADO. No contar los 501 registros de un sondeo como 501 cribados si solo se seleccionan 200. No rellenar total desconocido con cero.
- `citas_un_nivel.csv`: registrar el conteo bruto usado para activar el filtro (>500), texto literal, ruta servidor o local, si el tope se aplicó antes del filtro y cuántos quedan pendientes por resumen ausente. Una lista acotada antes de filtrar no es el conjunto de todos los citantes pertinentes.
- `cribado.csv`: conservar las razones originales; añadir FUERA_FILTRO_DIN solo cuando los campos necesarios están disponibles, y PENDIENTE_FILTRO cuando falta información. El filtro se aplica a expansión de citas, no a anclas ni a resultados independientes de consultas temáticas.
- `extraccion.csv`: mismos campos y reglas de lectura v1. No hay bibliografía nueva verificada al preparar v2.
- La síntesis final informa por punto la cobertura efectiva, los topes y el sesgo posible de orden/filtro; «nuevo» se limita a la búsqueda acotada.
