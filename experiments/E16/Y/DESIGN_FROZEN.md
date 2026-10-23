# E16-Y — Refinamiento con norma consistente de desplazamientos

Exploratorio prospectivo. Doce fuentes de S, sin filtrar por resultados de X.
Dos niveles por fuente: coarse original132/264 y fine por punto medio264/528.
No optimizar ni entrenar. No alterar S/T/U/V/W/X ni T2-A. W/X dependencias
sin merge automático; main incorporado antes de congelar. No ensayos finitos
nuevos: Y compara espectros y audita direcciones con MP.

## Misma imagen, norma y gradientes

Construir base coarse MP con convención heredada t binario/s decimal repr;
fine inserta puntos medios EXACTOS en MP. AD usa su proyección float64.
L coarse frente a S y L fine frente a coarse: error≤1e-35 en MP80/120.
No llamar optimizado al nuevo fino ni compararlo con otro candidato de S.

Norma común de desplazamiento: P1 consistente sobre longitud de arco euclídea
NORMALIZADA de la poligonal coarse (t,s). Peso de cada arista δ=‖Δz‖/Σ‖Δz‖.
M local por componente =δ/6[[2,1],[1,2]], extremos fijos. Fine usa cada δ/2.
No es métrica Fisher ni arclength intrínseco. Transporte lineal S por puntos
medios; comprobar SᵀMf S=Mc≤1e-12. Comparar autovalores generalizados, no
los Euclídeos de X. Las diferentes fuentes conservan sus parámetros propios.

Coarse g de gradientes MP finales archivados de S; no repetir auditoría cerrada.
Fine g NUEVO: diferencias finitas locales MP80 en cada t/s, pasos1e-18/1e-22,
cuatro referencias locales por variable. Guardar ambos escalares por componente.
AD contra MP≤1e-6 y pasos≤1e-20, normalizados por max(1,|L|).
H coarse/fine por AD. Comprobar gradiente pullback Sᵀgf=gc≤1e-6 y
H pullback SᵀHf S=Hc relativo≤1e-8. Son controles de aditividad, no datos nuevos.

## Problema espectral

Para cada nivel resolver min vᵀHv con vᵀMv=1 y gᵀv=0. Base Householder de X
para gradiente no pequeño; ‖g‖≤1e-25 usa espacio completo SMALL_GRADIENT.
Diagonalizar (BᵀHB,BᵀMB) por eigh generalizado. Comprobar M SPD por Cholesky,
B ortonormal y Bᵀg unitario≤1e-12, residuos generalizados≤1e-9 normalizados
por max(1,‖H‖∞,|μ|‖M‖∞). Guardar todos los autovalores restringidos escalares.
Entrelazado con espectro generalizado completo, error relativo≤1e-9.

Control analítico: tres nodos uniformes, pesos.5/.5, dos variables interiores;
M=I/3, H=diag(−2,3); g=e0 deja mínimo9 y espacio completo mínimo−6.
Comprobar fórmula de masa y solución a ≤1e-12. No ajustar umbrales.

## Dirección MP y clasificaciones

Levantar mínimo, limpiar residuo de restricción en MP como X, canonizar signo.
Para auditoría escalar por máximo desplazamiento euclídeo nodal=1, sin cambiar
su dirección. Registrar masa de ese vector y convertir curvatura FD a cociente
vᵀHv/(vᵀMv); no confundir amplitud nodal con norma de masa.
Norma previa de limpieza≤1e-8: DEGENERATE, sin fallback.
Ortogonalidad MP≤1e-35; misma dirección80/120≤1e-35.
MP80/120, pasos1e-10/1e-12: pendiente central normalizada≤1e-18; pasos≤1e-16.
Cociente de curvatura contra μ≤1e-5 y entre pasos≤1e-7, relativos max(1,|a|,|b|).
Precisión de pendiente/cociente≤1e-35. Preservar inconclusos y fallos.

Umbral espectral τspec=1e-8 max(1,max|μ|) por nivel: NEGATIVE/NEAR_ZERO/POSITIVE.
La norma y el espectro alto pueden ensanchar esa banda. Informar POR SEPARADO
NEGATIVE_MP_WITNESS si cociente MP120<−1e-8 max(1,|μmin|) y auditorías válidas.
Ese testigo direccional no certifica error de todo el espectro ni reetiqueta
modos casi nulos. Pequeños negativos C0 se conservan sin inferir inestabilidad.

## Comparación y límites

Registrar mínimo coarse/fine, diferencia, normas g, estados y testigos, sin
criterio retrospectivo de estabilización. Comprobar μfine≤μcoarse con margen
1e-5 max(1,|ambos|), motivado por espacios anidados y pullbacks anteriores.
No suponer que estén cerca; nueva malla permite nuevas direcciones. Una sola
subdivisión no demuestra convergencia, mínimo, silla exacta ni geodésica.
Mismos datos exploratorios, gradientes aproximados, aritmética no intervalar.

24 problemas, todos los estados conservados. Diagnóstico PASS/INCONCLUSIVE
separado de mínimos UNKNOWN.900s/512MiB por corrida; exceso conserva parcial.
Repetir una vez NUEVE salidas científicas: checks,gradients,spectra,paths,
comparisons,audits,costs CSV y summary/provenance JSON; recursos excluidos.
Matrices/vectores densos y polígonos intermedios no versionados.
