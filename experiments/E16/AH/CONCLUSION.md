# E16-AH · conclusión exploratoria v1

**Q1 PASS · Q2 FAIL · Q3 PASS · Q4 PASS_DESCRIPTIVE · Q5 PASS_DESCRIPTIVE.** Corrida VALID_EXPLORATORY; 80/80 estados con
curva testigo validada,13/13 controles previos PASS y
80/80 controles de quiebre nulo PASS. No se
sustituyeron estados ni se adaptó el presupuesto después de observar resultados.

## Resultado y comparación por grupo

Se estudiaron exactamente los 40 triángulos AG y 40 AF. En triangle el cociente
es hatρ1/d_borde y la correlación es Spearman(hatρ1,d_borde). En AF son
hatρ1/ρ0 y Spearman(hatρ1,ρ0); **d_borde AF sigue UNKNOWN**.

| Grupo | Estados válidos | Mediana cociente | Máximo cociente | Spearman | tρ0 mediano(s) | t1 total mediano(s) | Mediana t1/tρ0 |
|---|---:|---:|---:|---:|---:|---:|---:|
| triangle | 40/40 | 1.307235087 | 2.171752708 | 0.979362101 | 3.096131 | 3.514596 | 1.141252 |
| AF | 40/40 | 0.964992667 | 1.000000000 | 0.998499062 | 6.136833 | 30.608143 | 5.153239 |

Las medianas de tiempos y la mediana de sus cocientes son estadísticas
separadas. Los tiempos incluyen la búsqueda basal contemporánea; no son
comparaciones con un tiempo histórico en otra máquina.

**Q1 PASS:** los 40 triángulos conservan hatρ1≥d_borde dentro del
error fijado. Cada valor seleccionado corresponde a un segmento y una
semirrecta al infinito, con soporte, extremo, parámetros, integral y resto de
cola archivados. También se conserva hatρ1≤ρ0 validada por inclusión del
camino Q=0, sin recortar resultados al valor verdadero.

**Q2 FAIL:** la mediana baja de≈1.998884 en AG a
1.307235087, y el máximo de≈4.266419 a
2.171752708. Los umbrales congelados son mediana≤1.2 y máximo≤1.5.
Hay mejora respecto a la semirrecta desde 0, pero la búsqueda ejecutada no
cumple ambos requisitos. Esto **no prueba** que el ínfimo matemático de todos
los caminos con un quiebre incumpla esos umbrales: no se certifica un mínimo
global ni se explora Q fuera de la caja fijada. No se añade retrospectivamente
la sensibilidad opcional de dos quiebres.

**Q3 PASS:** Spearman frente a la distancia exacta es
0.979362101, frente a≈.939212 de AG; el umbral previo era≥.95.
Las cuatro escalas de cada semilla están emparejadas; no hay p-valores de 40
réplicas independientes ni evidencia de transferencia.

**Q4 PASS_DESCRIPTIVE:** el criterio descriptivo previo aceptaba un sobrecoste
mediano total de hasta 10× la búsqueda de ρ0 en ambos grupos. Los factores
medidos son 1.141252 en triángulos y
5.153239 en AF. El criterio evalúa ese presupuesto, **no que el método sea más rápido** que ρ0. El total
incluye optimización, quad, MP y archivo del perfil, además de la base; no es
un benchmark aislado repetido ni una predicción universal de coste.

**Q5 PASS_DESCRIPTIVE, descriptivo AF:** cociente mediano
0.964992667, máximo 1.000000000;
Spearman frente a ρ0=0.998499062. Cambian de orden
6 de 780 pares. Los estados sin
mejora conservan el basal. Esa asociación no mide orden frente a d_borde real.

## Qué curva se valida

El instrumento reporta **hatρ1**, mínimo de sus candidatos validados, no el
mínimo global ρ1. La familia tiene un quiebre, caja q=BQ∈[−12,12]²,
inicializaciones de rejilla y base, ramas de arista y sectores abiertos.
Se conserva el camino sin quiebre. Cada cola usa su offset fQ: su extremo en
una arista cambia con Q y no es el de una semirrecta desde 0.

Las aristas se definen algebraicamente por los rasgos, no interpretando una
normal decimal casi empatada como un empate exacto. Véanse las
[convenciones de reconstrucción](WITNESS_CONVENTIONS.md). La integral llega
al borde infinito con una cota explícita del resto desde U, no al umbral 150.
Las longitudes de los candidatos se validan con quad y las tres menores más
la base con MP80 (nodos/pesos MP, dos órdenes, integral completa y cola).

Se registraron 784 optimizadores, de los cuales
675 declararon convergencia nativa. Los límites y
salidas no convergentes permanecen en optimizers.csv: una curva factible con
longitud validada no se convierte por eso en un punto estacionario. Hubo
261 contrastes MP PASS y 0 inconclusos;
el error relativo máximo de los testigos seleccionados fue
1.24e-11. No hubo selección de estados ni sustitución
de candidatos inválidos por valores inventados.

En 16/80 testigos el quiebre alcanza el límite de la caja
(0 triángulos y 16 AF). Es una limitación material de esta búsqueda;
no se deduce que ampliar la caja o el presupuesto no pueda mejorar la cota.

## Controles, archivo y límites

13/13 controles previos PASS: triángulo trivial en baricentro, quiebre nulo
analítico y MP; origen afín; curvas de arista/genéricas en primeros
triángulo/AF con cambio de carta; velocidades frente a J original; K plano AD
y lectura de longitud continua AC archivada. No se reejecutaron AD/AC.
Los 80 basales nulos contrastan quad/MP y los valores cerrados de AG.

Tiempo de corrida 720.466036s, dos procesos y BLAS/OMP1.
480 arrays originales fuera de Git con SHA; todas las longitudes,
candidatos, estados nativos y recursos se conservan. Los testigos MP y las
versiones originales no se sobrescriben. [Resultados](results/run_v1),
[recursos](results/run_v1/resources.json), [diagnósticos derivados](results/run_v1/derived_diagnostics.json).

Historia: diseño d62326a → código dad765e → mediciones. Se verificó el SHA
de geometry.py antes de importarlo, sin modificar su fuente; la guarda AF
permanece activa sin excepciones de acceso T2. No se leyó ningún dato T2 ni
se modificaron estados o resultados de otras etapas.

No se afirma certificado riguroso (quad/MP no son intervalos), mínimo global,
igualdad ρ1=d_borde ni transferencia a T2. El ajuste que falta puede motivar
un protocolo nuevo de dos quiebres o búsqueda más amplia, declarado como
sensibilidad exploratoria o con estados independientes para confirmar. La corrida conserva sus reglas y resultados, incluidos los fallos de ajuste.

Verificación de archivos PASS:480 arrays,80 testigos y80 basales nulos;
los veredictos coinciden usando las longitudes MP archivadas. El máximo
contraste MP de testigos seleccionados y basales es2.75e-15, mientras
1.24e-11 es el máximo combinado con el estimador quad. Se conserva y aclara
la etiqueta imprecisa del diagnóstico v1 en [DERIVED_LABEL_ERRATA.md](DERIVED_LABEL_ERRATA.md).
[Registro de verificación](verification.json). No se reintegraron curvas.
