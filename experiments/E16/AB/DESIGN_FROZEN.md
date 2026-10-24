# E16-AB · región de confianza para estacionariedad estricta

Protocolo prospectivo congelado antes de implementar o medir AB. Base main
`56a6f75ef6c3ed7979481b4ebc78761b82c8275c`, que integra AA. No modificar ni reclasificar etapas cerradas.

## Pregunta e intervención

¿Resolver el gradiente con región de confianza y escalado de columnas permite
alcanzar KKT físico≤1e-7 desde los doce puntos finales de AA, dentro de un
presupuesto fijo? Conservar Q0/Q1/C0, ambas procedencias y ambas mallas264/528,
sin filtrar inconclusos. Los nombres132/264 son las fuentes originales S.
No cambiar pesos de red, datos, caja, malla o masa. No hay entrenamiento.

Resolver mínimos cuadrados F(x)=∇L_AD(x)/c, con c=max(1,|L_AD(x_inicial)|)
fijo por fuente, Jacobiano H_AD/c, método scipy.optimize.least_squares TRF,
tr_solver exact (SVD densa), x_scale jac (escalas adaptativas por normas de
columnas del Jacobiano), loss linear. ftol y gtol desactivados; xtol1e-14,
max_nfev60. Una sola llamada por caso; sin reinicios, búsqueda de parámetros,
selección del mejor estado anterior ni expansión de presupuesto.

La función objetivo del solver es ||F||²/2, no L. No exigir descenso de L:
archivar su diferencia con AA de cualquier signo. Esto no busca mínimos ni
resuelve directamente el KKT proyectado en bordes. La caja física continúa
siendo t∈[0,1],s∈[-.25,.25], extremos fijos(0,0),(1,0).

## Parada y controles

Auditoría inicial MP80 completa, fuera de la racha. Sólo C0 verificado ya
estacionario puede terminar INITIAL_CONTROL sin invocar SciPy; campos nativos
vacíos y coste cero. No inventar éxito nativo. En otros casos, callback registra
cada **punto aceptado distinto** del anterior, con contador propio; callbacks
que repiten x no cuentan como observaciones nuevas. Guardar también número
de callbacks y costes nativos de evaluaciones, sin llamarlos iteraciones aceptadas.

En cada nuevo punto: KKT físico AD=||x−clip(x−g,C)||∞/max(1,|L_AD(x)|).
AD>2e-7 reinicia racha como SCREENED_NONSTATIONARY, sin MP. En otro caso
gradiente completo MP80 local FD1e-18/1e-22; acuerdo AD≤1e-8, pasos≤1e-20,
normalizados por max(1,|L_MP|). Tres aceptados consecutivos verificados con
KKT_MP≤1e-7 solicitan StopIteration en ese punto, conservando status−2 y
successFalse propios de least_squares. Inicial no cuenta ni se repite el mismo
punto para completar racha. Éxito nativo por xtol sólo se acepta con validación
final independiente. Agotar max_nfev sin racha queda INCONCLUSIVE aunque el
último descriptor aislado cumpla. Cualquier monitor UNVERIFIED impide PASS.

Controles sintéticos previos: regla de rachas S; root diagonal mal escalada
con solución conocida (residuo≤1e-9, posición≤1e-7); callback interrumpido en
segundo punto distinto, status−2, successFalse y mismo punto devuelto. No usar
estos controles para adaptar parámetros de casos científicos.

Si SciPy aborta por arista nula, primitiva inválida o fallo algebraico, guardar
SOLVER_ERROR, texto de excepción, nativos vacíos y último punto aceptado
(no el mejor); no penalizar artificialmente ni arreglar la primitiva. Analizar
ese punto si evaluable, sin convertir el fallo en éxito. Contabilizar llamadas
reales, incluso las que aborten. Preservar cualquier fallo de validación final.

## Validación final y espectro

Mismos umbrales de AA salvo eliminar la exigencia de no empeorar L. Gradiente
MP final separado, KKT≤1e-7, longitud MP80/120 relativa1e-35, cajas/extremos,
aristas no nulas y primitiva válida, positividad numérica Bernstein por arista.
C0: longitud recta1e-8 y desvío normal1e-6. No son certificados de intervalos.

Masa consistente P1 fija de Y/Z/AA: pesos del arco euclidiano normalizado de
la fuente S divididos en dos por subdivisión; no recalcular sobre AA o AB.
Todos los puntos devueltos evaluables, incluidos inconclusos: mínimo vᵀHv
sujeto a vᵀMv=1,g_MPᵀv=0, Householder (espacio completo si ||g||≤1e-25).
Cholesky M; base1e-12, simetría/residuo/interlacing1e-9. Clasificación float
relativa1e-8. Dirección mínima auditada MP80/120, pasos1e-10/1e-12; restricción
1e-35, pendiente1e-18, pasos pendiente1e-16, Rayleigh1e-5, pasos Rayleigh1e-7,
precisión1e-35. Testigo MP negativo: q<−1e-8 max(1,|mu|) y espectro verificado.
No confundir C0 casi nulo float con testigo negativo MP.

Elegible sólo primer orden PASS, espectro PASS e interior con margen>1e-8.
Prueba bilateral pequeña aparte. No se resuelve el cono crítico de caja.
Comparar por fuente KKT, norma de gradiente, L y mínimo de masa AA/AB;
conservar todos los estados en tablas y denominadores. No interpretar
curvatura de un punto no elegible como estabilidad estacionaria estricta.

## Presupuesto, integridad y alcance

1800s/512MiB por corrida, max_nfev60 por fuente. Comprobar recursos en cada
residual/Jacobiano y auditoría; si excede, guardar parcial INCONCLUSIVE y
restantes UNKNOWN, no ampliar. Una corrida y una reproducción exacta de
once salidas científicas: nueve CSV y summary/provenance JSON; resources.json
con tiempos queda excluido. Congelar implementación antes de medir.

Versionar gradientes y vértices finales, tablas escalares, estados, costes,
hashes, manifests, documentación y figura posterior. No matrices densas,
autovectores ni checkpoints. Alcance AB y tres índices; T2_A/T2_A1 intactos.
Si algún caso no cumple, resultado global INCONCLUSIVE, sin excluirlo.

Exploratorio y determinista, mismas fuentes, sin confirmación independiente.
AB cambia método e inicio; no aísla causalmente sólo el precondicionamiento.
Una raíz de gradiente puede ser mínimo, máximo o silla: no certificar mínimos,
sillas exactas, geodésicas, convergencia ni éxito futuro desde éxito numérico.
