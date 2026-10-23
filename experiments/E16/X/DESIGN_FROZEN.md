# E16-X — Mínima curvatura restringida a g⊥

Exploratorio prospectivo. Doce caminos originales de S, ambos métodos/mallas
y C0 completo. Sin selección por outcomes, optimización ni entrenamiento.
W es dependencia aún no fusionada; main incorporado sin cambios de T2_A/T2_A1.
S/T/U/V/W intactos. H de L por AD, g de columnas MP finales de S.

## Restricción y controles

Si ‖g‖>1e-25, n=g/‖g‖ float64; s=+1 si n0≥0, −1 si no;
u=(n+s e0)/‖n+s e0‖. Q=I−2uuᵀ, B=Q[:,1:]. Hc=Bᵀ(H+Hᵀ)B/2,
simetrizado para diagonalizar. Comprobar BᵀB=I y nᵀB=0 a ≤1e-12.
Si ‖g‖≤1e-25, SMALL_GRADIENT: B=I, espacio completo. No quitar una
dirección arbitraria ni afirmar gradiente cero exacto.

Guardar todos los autovalores de H y Hc, no matrices ni vectores densos.
Umbral propio τ=1e-8 max(1,max|λ|): NEGATIVE/NEAR_ZERO/POSITIVE.
Simetría, residuo de autovector reducido y entrelazado de Cauchy
λi(H)≤λi(Hc)≤λi+1(H), error/max(1,‖H‖2)≤1e-10.
SMALL_GRADIENT: igualdad de espectros. Controles analíticos:
H=diag(−2,3,5), g=e0 da mínimo3; g=(1,1,0)/√2 da mínimo0,5;
H=2I, g=(1,2,3) da mínimo2. No ajustar tolerancias.

## Dirección y contraste MP

Levantar v=By del autovector mínimo reducido y canonizar por componente
máxima positiva. En MP80/120 limpiar sólo error float de restricción con
v−g(gᵀv)/(gᵀg), normalizar y canonizar. Gradiente pequeño: sólo normalizar.
Norma previa≤1e-8: DEGENERATE sin fallback, ensayos UNKNOWN.
Norma unitaria y |gᵀv|/max(1,‖g‖)≤1e-35; acuerdo vector80/120≤1e-35.
Rayleigh AD tras limpieza frente a mínimo reducido y residuo de autovector
proyectado: error/max(1,‖H‖2)≤1e-10.

Pendiente/curvatura centrales MP: pasos1e-10/1e-12, precisiones80/120.
Pendiente contra gᵀv≤1e-6, pasos≤1e-16; curvatura contra AD≤1e-6,
pasos≤1e-8. Errores normalizados por max(1,|a|,|b|). Precisiones≤1e-35.
Pendiente del paso menor/max(1,|L|)≤1e-18. Fallos INCONCLUSIVE preservados.
Negativo resuelto requiere μmín<−τ y Rayleigh MP120<−τ con auditorías válidas.
No es certificado riguroso del espectro completo. Comparar μmín≤qW archivado
(projected MP120 de W), tolerancia normalizada1e-8; no reinterpretar W.

## Ensayos finitos

Una dirección por camino: h=1e-5/1e-4/1e-3, signos±, siempre desde la base.
72 ensayos/36 parejas. Puntos y dirección MP para L, sin conversión float.
L base contra S≤1e-35, MP80/120≤1e-35. Cajas MP sin clipping, aristas no
nulas, primitiva válida, positividad métrica numérica Bernstein h00/det MP120
por arista. Conservar inviables/invalidaciones, sin paso ni dirección alternativa.
Δ± normalizado por max(1,|L0|), E/O, signos banda±1e-20, ambos/sólo uno/ningún
descenso; predicciones lineal/cuadrática auditadas y residuos sin reajuste.

Geometría U: inferior simétrica por vértices/medios a todos los segmentos,
superior por correspondencia, colchón1e-12 y proyección float≤1e-15.
CHANGED si inferior>1e-8, WITHIN_TOLERANCE si superior≤1e-8; si no UNRESOLVED.
No intervalos rigurosos ni distancia intrínseca.

## Alcance y reproducción

Mínimo numérico en espacio de gradiente aproximado; no certificar mínimo,
silla exacta, geodésica o convergencia continua. Mismos datos exploratorios,
sin confirmación independiente ni causa única. Diagnóstico PASS/INCONCLUSIVE,
mínimos UNKNOWN y ruta SMALL_GRADIENT separados. Preservar todos los estados.
900 s/512 MiB por corrida; exceso conserva parcial INCONCLUSIVE. Repetir una
vez once salidas científicas: nueve CSV (checks,spectra,directions,audits,
trials,pairs,paths,costs,comparisons) y summary/provenance JSON. Recursos fuera
de igualdad; matrices/vectores internos fuera de Git.
