# Precisión de metadatos de procedencia

El JSON original `results/run_v1/chord_face26.json` guarda
`source_lines=[46,53]`, un rango impreciso escrito en el arnés. Se conserva
sin reescribir. La función realmente ejecutada por extracción AST se llama
`cuerda` y está en las líneas **50–55** de sources/c1_cohorte.py.
La línea46 pertenece a init_index. El SHA de la fuente y la extracción por
nombre identifican sin ambigüedad el código ejecutado. La revisión A1 y
conclusión usan50–55; la verificación contrasta ese rango mediante AST.
No cambian código, matrices, resultados, reglas ni veredictos.
