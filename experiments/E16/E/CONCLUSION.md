# Conclusión E16-E

Conservar rango no conserva la geometría métrica. En los mismos casos de E16-D,
las dos composiciones no lineales cambian la escala y también la forma respecto
a la suma. Las 216 comparaciones fueron SPD y ninguna quedó sin estimar.

| Observable respecto a la suma | Producto: mediana [mín., máx.] | Cuadrática: mediana [mín., máx.] |
|---|---|---|
| Distancia afín invariante d | 2,9501 [0,5819; 7,5941] | 1,9690 [0,3810; 7,6087] |
| Distancia de forma s | 1,7237 [0,0609; 4,4969] | 1,6793 [0,1745; 5,1145] |
| Anisotropía relativa κ | 11,5006 [1,0900; 578,0334] | 10,7504 [1,2799; 1384,4283] |
| Escala isotrópica de longitud | 0,4236 [0,1024; 1,5588] | 0,7398 [0,1306; 2,5018] |

Son resúmenes marginales; sus extremos no necesariamente corresponden al mismo
caso. κ compara deformaciones **métricas**: la razón entre estiramientos extremos
de longitud es sqrt(κ). No es la condición de H aislada ni un valor absoluto de
anisotropía. La escala de longitud es el promedio geométrico de los dos
estiramientos, no la razón de longitudes en toda dirección.

## Evidencia instrumental

10 176 controles pasaron: acuerdo de 80/120 cifras, identidades de descomposición,
invariancia bajo tres cambios de carta y controles de identidad, escala y forma.
El negativo muestra que la condición ordinaria puede pasar de 4 a 1 al cambiar
coordenadas, mientras la condición generalizada permanece en 4.

La descomposición d²=2μ²+s² permite distinguir contracción/expansión uniforme
de deformación relativa. En todos los casos s>1e-8; no basta un reescalado
isotrópico para explicar las diferencias observadas. Ese umbral sólo expresa
separación numérica. Los resúmenes por panel también están conservados: no se
oculta la variación entre P0/P1/P2 ni se tratan las observaciones como independientes.

## Alcance

Los datos de D se reutilizan para observables nuevos congelados antes de medir.
Estos resultados son exploratorios, específicos de las funciones, puntos,
cométrica regularizada y unidades declaradas. No prueban superioridad predictiva,
una ley universal RIPG ni distancias geodésicas finitas. Alta precisión y
reproducción no constituyen un certificado mediante aritmética de intervalos.
No se ha entrenado ninguna red ni alterado T2-A.

El siguiente diseño puede fijar caminos entre perspectivas y comparar sus
longitudes integradas, comprobando SPD a lo largo del camino y convergencia
de cuadratura. Una longitud de camino tampoco se identificaría con distancia
geodésica sin resolver o acotar el problema de minimización correspondiente.
