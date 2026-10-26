# DIN-D9g-c: contexto e importación anteriores al diseño

Leído AGENTS.md y el código/diseño de D9g-b. Rama research/din-d9g-c desde main0dbc973.
D9g/D9g-b siguen en PR#91/#92; se copian tablas/documentos por SHA de commits8996c2c
/417b80c dentro de sources/, sin modificar originales. No se abrió C2 ni datos de
Wine/Iris/T2/DIN-C1. Se reutilizarán las 1.500 filas completas de D9g-b, incluido
Y=test250 ya medido, sin generar/evaluar nada nuevo ni restaurar pesos.

Antes del diseño se detectó una ambigüedad de ridge: una función de la base añadida
sin penalizar puede eludir la penalización y mejorar CV aunque no agregue información
al diccionario. Se solicitó elegir entre residualizar c30 (OLS del candidato sobre
los 21 términos, sólo train) o la adición cruda al ridge conjunto. Esa decisión aún
no se congela ni se implementa en este progreso. No se calcularon resultados BR.
