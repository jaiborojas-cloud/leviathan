# Conclusión E16-AC

**INCONCLUSIVE** conforme a la regla congelada. V2 es VALID_EXPLORATORY:
8/8 controles PASS,12/12 shooting convergentes y12 índices numéricos0 estables.
V1 permanece INVALID por el contraste RK4 del control hiperbólico largo.
No se sobrescribieron sus resultados; corrección documentada y congelada antes
 del código v2. No se reejecutaron etapas S–AB.

| Fuente AB | Malla | Shooting | L continua | Conjugados | Negativos normales discretos |
|---|---:|---|---:|---:|---|
| Q0/reference/132 | 264 | True | 0.506971938975 | 0 | UNKNOWN |
| Q0/reference/264 | 528 | True | 0.506971938975 | 0 | UNKNOWN |
| Q0/scaled/132 | 264 | True | 0.506971938975 | 0 | UNKNOWN |
| Q0/scaled/264 | 528 | True | 0.506971938975 | 0 | UNKNOWN |
| Q1/reference/132 | 264 | True | 0.506971938975 | 0 | UNKNOWN |
| Q1/reference/264 | 528 | True | 0.506971938975 | 0 | UNKNOWN |
| Q1/scaled/132 | 264 | True | 0.506971938975 | 0 | UNKNOWN |
| Q1/scaled/264 | 528 | True | 0.506971938975 | 0 | UNKNOWN |
| C0/reference/132 | 264 | True | 1.09776582287 | 0 | UNKNOWN |
| C0/reference/264 | 528 | True | 1.09776582287 | 0 | UNKNOWN |
| C0/scaled/132 | 264 | True | 1.09776582287 | 0 | UNKNOWN |
| C0/scaled/264 | 528 | True | 1.09776582287 | 0 | UNKNOWN |

Los bloques normales de Z/AB no están archivados y sus testigos no tienen
fracción tangencial medida. T no los sustituye: usa otras curvas, de S, y un
marco euclidiano en coordenadas z. Ni la cercanía Hausdorff ni igualdad del
identificador de procedencia hacen idénticos los puntos finales.

El índice cero de estas ramas no proporciona evidencia de H1; es compatible
con la componente continua de H2, pero no satisface su condición sobre modos
discretos. La teoría de la inmersión cónica explica planitud local de esta
métrica regular; no identifica causa única de las negativas discretas.
La asociación polígono/geodésica usa Hausdorff muestreado, no certificado.
El contraste MP de Jacobi está condicionado a la trayectoria float; no es una
solución MP independiente del problema de contorno. Sin intervalos, sin prueba
de mínimo global, sin identificación de todo el locus de corte.

## Controles y salidas

C0 K=0 e índice0 en las cuatro fuentes. Esfera unidad:0 conjugados en0.75π
y1 en1.5π, con cero enπ. Hiperbólico K=−1:índice0 para L1 y10.
La mayor resolución MP v2 conserva el umbral y resuelve el error de truncamiento
del control; su error queda explícito, además del error DOP853.

Se conservan intentos de shooting (incluidas perturbaciones del Jacobiano),
estados nativos, eventos, perfiles de curva/Jacobi, contrastes K MP50/80,
Hausdorff dirigido, deriva de velocidad, tiempos, entorno y hashes por versión.
Las diferencias L continua−L_AB son descriptores de ramas aproximadas, sin
promoverlas a mínimos globales. No se archivan matrices Hessianas ni testigos
vectoriales nuevos; no se midieron bloques discretos ausentes.

## Siguiente paso propuesto

Con H2 establecido: E16-AD en el cociente por reparametrización, con velocidad
constante. Con H1 establecido: E16-AD shooting multiángulo y locus de corte.
Dado este INCONCLUSIVE, primero un protocolo prospectivo que mida bloques
normales y descomposición tangencial en discretizaciones nuevas de las
geodésicas AC, preservando AB cerrado. No tratar H2 como ya confirmado.

## Integridad y tiempos

V1:40.276710s/78.785156MiB, INVALID conservada. V2:42.866823s/78.949219MiB.
Reproducción v2:40.939331s/78.894531MiB; diez salidas científicas idénticas byte
a byte, excluyendo recursos/tiempos. [Verificación](verification.json).
Integridad aprobada no cambia el veredicto INCONCLUSIVE.
