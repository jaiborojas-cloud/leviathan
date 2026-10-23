# E16-AA · sensibilidad a una estacionariedad más estricta

Diseño prospectivo, congelado antes de implementar o medir AA. Fuentes cerradas
Z, S, X e Y son sólo entradas; no se reabren ni reclasifican. Base: `2db0bedb8841d32dca3524ff13044c0aa95ccd30`.

## Pregunta y universo

¿Persiste la curvatura negativa restringida al continuar las doce curvas finales
de Z hacia KKT físico ≤1e-7? Se incluyen Q0/Q1/C0, ambas procedencias y ambas
mallas (264/528 segmentos), sin seleccionar resultados. Identificadores conservan
el número de segmentos de la fuente S (132/264), no el de la curva actual.
No se subdivide de nuevo. C0 es control; las procedencias no son tratamientos.

## Intervención y parada

Cada inicio es el vector final float64 archivado de Z, con igualdad de hash y
longitud inicial frente a Z (tolerancia relativa 1e-12). Una sola continuación
L-BFGS-B física, sin escalado, reinicios, selección del mejor punto ni ajustes
posteriores: maxiter4800, maxfun80000, maxls40, ftol0, gtol1e-11.
Se desactiva la salida por reducción relativa de función para permitir buscar
el residuo menor. Esto y el nuevo inicio impiden atribuir causalmente cualquier
cambio sólo al umbral. No se prueba una familia de tolerancias ni convergencia.

Caja t∈[0,1], s∈[-.25,.25], extremos(0,0),(1,0). Residuo
r=||x−clip(x−g,C)||∞/max(1,|L|). Monitor cada200 iteraciones aceptadas:
AD>2e-7 implica SCREENED_NONSTATIONARY y reinicia racha, sin auditoría MP.
Si no, gradiente completo MP80, FD locales1e-18/1e-22; acuerdo AD≤1e-8,
acuerdo pasos≤1e-20 (normalización max(1,|L|)). Tres muestras consecutivas
verificadas r≤1e-7 solicitan StopIteration en ese punto. Inicial no cuenta.
Estado nativo99/successFalse se conserva. Éxito nativo puede aprobar sólo con
validación final independiente; agotar iteraciones sin racha es INCONCLUSIVE.
Cualquier monitor UNVERIFIED impide aprobar. No se fuerza a alcanzar el umbral.

## Validación final y segundo orden

Mismo procedimiento final de Z: gradiente MP separado, KKT≤1e-7, longitud
MP80/120 (1e-35), no empeorar(1e-12), cajas/extremos, aristas no nulas,
primitiva definida y positividad numérica Bernstein por arista. C0 además
longitud recta1e-8 y desvío normal1e-6. Masa P1 **fija de Y/Z**, calculada desde
arcos euclidianos normalizados de la fuente S y pesos de aristas divididos en dos;
no se recalcula desde el inicio o final AA.

Para todos los puntos devueltos evaluables, incluso inconclusos, minimizar
vᵀHv sujeto a vᵀMv=1 y gᵀv=0, H AD y g MP final. Base Householder; si
||g||≤1e-25 usar espacio completo. Cholesky de M, ortogonalidad1e-12,
interlacing/residuo/simetría1e-9. Clasificación espectral relativa1e-8.
Dirección mínima contrastada MP80/120 con pasos1e-10/1e-12 y corrección MP
ortogonal a g: restricción1e-35, pendiente1e-18, acuerdo pasos pendiente1e-16,
Rayleigh1e-5, acuerdo pasos1e-7, precisión1e-35. Testigo negativo MP requiere
q<−1e-8 max(1,|mu|) y validación espectral completa. C0 casi nulo float no
se interpreta como negatividad real. No se archivan Hessianas ni autovectores.

Elegible: primer orden PASS, espectro PASS e interior con margen>1e-8;
prueba bilateral pequeña aparte. No se resuelve cono crítico en bordes.
Comparar Z/AA dentro de cada fuente: residuo KKT, longitud, mínimo de masa y
norma de gradiente. Toda comparación y denominador conserva inconclusos.
Negatividad en un punto no elegible es sólo diagnóstico de ese punto.
El éxito del protocolo exige los doce casos y todos los controles aprobados;
fallos e incógnitas se conservan, no se amplía el presupuesto.

## Presupuesto, archivos y límites

1800s y512MiB por corrida; 4800 iteraciones por fuente, sin ampliar. Si excede,
conservar tablas parciales y restantes UNKNOWN. Una corrida y una reproducción
exacta de once salidas científicas (nueve CSV y summary/provenance JSON),
excluyendo resources.json por contener tiempos. Congelar implementación antes
de primera corrida. Registrar hashes, costes, estados nativos, gradientes finales
y vértices; figura posterior sólo a partir de tablas. Alcance AA y tres índices.
No modificar T2_A, T2_A1 ni etapas previas. Sin entrenamiento.

Es exploración determinista de los mismos datos, no confirmación independiente,
certificado de mínimo, silla exacta, geodésica ni convergencia. Si no se alcanza
1e-7, la sensibilidad estacionaria a ese umbral queda sin resolver, aunque
el diagnóstico espectral del punto devuelto sea evaluable.
