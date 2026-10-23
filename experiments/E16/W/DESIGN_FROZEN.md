# E16-W — Proyección con variación de primer orden nula

Exploratorio prospectivo. Doce caminos originales de S, incluidos todos C0;
dirección full_min de T/U. No seleccionar por outcomes ni tocar S/T/U/V o T2-A.
Sin optimización, entrenamiento, nuevos candidatos oficiales o búsqueda de
una dirección alternativa después de medir.

## Proyección congelada

Recuperar v con Hessiano original, eigensolver y signo canónico de T; comprobar
hash. Usar g del gradiente MP final de S (mp_fd_2, orden t/s archivado).
En MP80 y MP120 por separado calcular q=v−g(gᵀv)/(gᵀg), w=q/‖q‖, signo
canónico por mayor componente. Proyección euclídea física en (t,s), no Fisher.
Si ‖g‖≤1e-25: ruta SMALL_GRADIENT, normalizar v sin dividir por g; no afirmar
nulidad exacta. Si ‖q‖≤1e-8: DEGENERATE, conservar todos sus ensayos UNKNOWN,
sin fallback. Si no, ruta PROJECTED.

Registrar norma g, pendiente original, norma q, ángulo/componente retenida,
pendiente gᵀw, hashes de representaciones MP de vectores y Rayleigh AD.
Norma unitaria y |gᵀw|/max(1,‖g‖)≤1e-35. Acordar w80/w120 a ≤1e-35.
No convertir w a float para medir longitud; float sólo para diagnóstico AD
Rayleigh y geometría. Proyectar una dirección no minimiza H sobre g⊥.

## Auditoría direccional separada

Para ambas familias original/projected, medir derivada central y curvatura
central de L con pasos 1e-10/1e-12, MP80/MP120. Contrastar pendiente MP con
gᵀdirección a ≤1e-6, acuerdo entre pasos ≤1e-16; curvatura con Rayleigh AD
≤1e-6, pasos ≤1e-8. Normalización max(1,|a|,|b|).
Precisión de pendiente y curvatura ≤1e-35. Para projected exigir además
|pendiente MP del paso menor|/max(1,|L|)≤1e-18; si incumple, mantener diagnóstico
INCONCLUSIVE y todos los resultados, sin cambiar pasos o proyección.
No es una nueva auditoría de todo el gradiente de S ni un certificado riguroso.

## Ensayos finitos

Dos familias, mismos tres pasos 1e-5/1e-4/1e-3 y signos ±, desde cada original;
144 ensayos/72 parejas. Construir puntos MP como en U. Conservar original
contra U (longitud, delta, estado) a ≤1e-35. L base contra S ≤1e-35.
Precisión MP80/120 ≤1e-35. Cajas MP sin clipping, aristas no nulas, primitiva
válida y positividad métrica numérica Bernstein h00/det MP120 por arista.
INFEASIBLE/INVALID/DEGENERATE se conservan, sin sustituciones.

Δ±=(L±−L0)/max(1,|L0|); E=(Δ++Δ−)/2, O=(Δ+−Δ−)/2; banda ±1e-20.
Registrar clasificación de ambos signos, ambos descensos/sólo uno/ninguno,
E/O, predicciones con la pendiente y curvatura direccionales MP auditadas y
residuos sin umbral retrospectivo. Primer orden nulo no elimina términos
impares cúbicos ni garantiza descenso a paso finito.

Geometría: cotas numéricas de U contra la base, muestras simétricas de vértices
y medios a todos los segmentos y superior por correspondencia; colchón1e-12,
proyección float≤1e-15. CHANGED si inferior>1e-8, WITHIN_TOLERANCE si
superior≤1e-8, en otro caso UNRESOLVED. No intervalos rigurosos.

## Estados, límites y reproducción

Diagnóstico PASS/INCONCLUSIVE, estado exploratorio y mínimos UNKNOWN separados.
Si la curvatura cambia al proyectar, no significa que todo g⊥ sea positivo;
si permanece negativa, tampoco certifica silla exacta o mínimo. Mismos datos,
sin confirmación independiente. Ninguna inferencia causal única sobre nodos.
Guardar escalares, hashes y todos los estados; no matrices o vectores densos.
900 s/512 MiB por corrida; exceso preserva parcial INCONCLUSIVE. Repetir una
vez nueve salidas científicas (checks,directions,audits,trials,pairs,paths,costs
CSV y summary/provenance JSON), excluyendo resources.json.
