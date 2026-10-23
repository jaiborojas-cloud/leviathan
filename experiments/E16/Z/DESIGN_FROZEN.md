# E16-Z — Reestacionarización de mallas subdivididas

Prospectivo exploratorio. Doce fuentes de S, todos Q0/Q1/C0 y etiquetas de
procedencia reference/scaled. Subdividir cada arista con P/kernel.subdivide
float64: 132→264,264→528. Es proyección numérica de la subdivisión MP de Y:
comprobar desviación por coordenada≤1e-15 y longitud inicial contra S≤1e-12.
Ningún candidato optimizado previo se cambia. No entrenar red ni tocar T2-A.

## Optimizador y regla de parada

Único método en Z: L-BFGS-B físico t/s, misma L/cajas/extremos; procedencias
reference/scaled no son dos algoritmos de Z. Maxiter4800,maxfun80000,maxls40,
ftol1e-14,gtol1e-9. Sin reinicios, fallback o escalas nuevas. Cada fuente se
optimiza independientemente desde su propia subdivisión, sin warm start cruzado.

Auditoría MP completa inicial, excluida de racha. Cada200 iteraciones aceptadas
calcular KKT proyectado AD físico, normalizado max(1,|L|). Si >2e-5:
SCREENED_NONSTATIONARY, sin FD MP, reiniciar racha. No llamar independiente a
ese filtro negativo. Si ≤2e-5: FD locales MP80 de cada t/s con1e-18/1e-22;
AD/MP≤1e-6, pasos≤1e-20. Sólo auditorías MP válidas con KKT≤1e-5 cuentan.
Tres consecutivas programadas solicitan StopIteration en ese punto, no el mejor
previo. Verificar hash de estado y nit/callbacks; conservar success=False/status99.

UNVERIFIED (fallo de evaluación/acuerdo) se conserva, reinicia racha y hace el
camino INCONCLUSIVE aunque después pase. STATIONARY/NONSTATIONARY MP y filtro
AD negativo son observaciones diferentes. Auditoría final MP siempre separada.
NATIVE_VERIFIED: terminación natural success=True más validación física final;
C0 puede parar sin iteraciones NATIVE_CONTROL. Límite4800 sin racha o sin éxito
natural es INCONCLUSIVE, aunque algún descriptor final pase.

## Validación física final

MP80 gradiente completo, ambos pasos; KKT≤1e-5, acuerdo AD/MP y pasos igual
que monitor. L MP80/120≤1e-35, no empeorar inicial a >1e-12 normalizado.
Cajas y extremos originales, aristas no nulas, primitiva definida; positividad
métrica numérica Bernstein h00/det MP120 por arista. C0 longitud recta≤1e-8
y max|s|≤1e-6. Datos finales y todos los fallos se guardan sin reclasificar S/Y.

## Espectro final, incluso si no pasa la parada

Masa P1 FIJA de Y: longitud de arco euclídea normalizada de la poligonal fuente,
pesos partidos por mitad. No recalcular masa al cambiar la curva optimizada.
Con H final por AD y g MP final, resolver mínimo generalizado en g⊥ usando
Householder X; ‖g‖≤1e-25 conserva espacio completo SMALL_GRADIENT.
M SPD, B ortonormal/ortogonal≤1e-12; residuos generalizados y entrelazado≤1e-9.
Guardar todos los autovalores restringidos escalares, τspec1e-8 max(1,max|μ|).

Dirección mínima levantada, limpiar residuo MP de restricción, escalar a máximo
nodal1. Restricción MP≤1e-35. Curvatura/pendiente MP80/120, pasos1e-10/1e-12;
Rayleigh dividido por vᵀMv contra mínimo≤1e-5, pasos≤1e-7; pendiente≤1e-18,
pasos≤1e-16. Precisiones≤1e-35. Testigo MP negativo si qMP<−1e-8 max(1,|μ|)
con diagnóstico válido; no reetiquetar bandas espectrales ni certificar mínimos.

Todos los puntos devueltos se analizan, incluso INCONCLUSIVE de parada, si son
evaluables. Si no, conservar UNKNOWN y motivo sin sustitución. Comparación
estacionaria admisible sólo si parada/validación PASS, diagnóstico espectral PASS
y todas las variables interiores a margen>1e-8. Si hay bordes activos, g⊥ no es
el cono crítico de caja: registrarlo sin resolverlo ni interpretar negativo como
testigo admisible bilateral. No excluir esos casos del denominador.

## Comparación y presupuesto

Comparar todos los finales con sus Y/fine (mínimo, gradiente y longitud fuente),
indicando elegibilidad anterior. Sin prueba de convergencia ni selección de
supervivientes confirmatorios. Primer orden aproximado no certifica mínimo.

Presupuesto NUEVO Z1800s/512MiB por corrida, incluidas auditorías y espectros;
no ampliar. Exceso conserva parcial INCONCLUSIVE y restantes UNKNOWN. Registrar
costes reales, filtro AD y MP separados, tiempos fuera de igualdad científica.
Repetir una vez once salidas: checks,paths,vertices,gradients,monitor,spectra,
audits,comparisons,costs CSV más summary/provenance JSON. No matrices, vectores
de monitor ni checkpoints internos; sólo estado final escalar/gradiente/vértices.
Controles: regla SustainedRule de S y callback SciPy de cuadrática 5D detenido
en segunda iteración; verificar status99 y punto devuelto exacto.
