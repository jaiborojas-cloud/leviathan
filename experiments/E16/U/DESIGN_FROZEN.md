# E16-U — Descenso finito y cambio geométrico

Protocolo exploratorio congelado antes de implementar o medir. Doce caminos
finales de S, incluyendo todos los controles C0, con las cinco direcciones
unitarias canónicas de T, sin seleccionar supervivientes. No optimizar, entrenar,
corregir S/T, cambiar umbrales ni elegir pasos después de ver resultados.

## Reconstrucción y perturbaciones

Reconstruir exactamente los marcos, Hessianos y autovectores de T únicamente
para recuperar sus direcciones no archivadas; comprobar cada hash contra T.
No es una nueva auditoría ni reinterpretación de T. Misma normalización y signo
canónico. Cinco direcciones: full_min, tangent_min, normal_min, tangent_sine,
normal_sine. Pasos absolutos h=1e-5,1e-4,1e-3 y ambos signos; máximo 360 ensayos.
Cada perturbación parte del mismo original, nunca de otra perturbación.

Puntos interiores MP: pⱼ±h(vⱼ,t(b−a)+vⱼ,s R(b−a)), extremos fijos.
Factibilidad de cajas en MP, sin clipping ni paso alternativo. Guardar ensayos
inviables como INFEASIBLE y excluirlos sólo de evaluaciones no definidas, no
del denominador. Arista nula o primitiva inválida: INVALID, nunca fallback.

L original y perturbada con primitiva MP80/MP120 heredada. Acuerdo relativo
≤1e-35; longitud central de S ≤1e-35. En MP120 comprobar positividad métrica
por Bernstein numérico heredado de G en todas las aristas (h00 y det); fallo
conservar INCONCLUSIVE. No confundir con aritmética de intervalos.

## Separar descenso y curvatura

Δ±=L(x±hv)−L(x), normalizado por max(1,|L(x)|). Signo con banda ±1e-20:
DESCENT, INCREASE, WITHIN_TOLERANCE; si invalidez, UNKNOWN.
Para cada pareja completa registrar E=(Δ++Δ−)/2 y O=(Δ+−Δ−)/2,
predicciones lineal ±h∇L·v y cuadrática h²vᵀHv/2, y residuos sin reajuste.
Usar gradiente MP final archivado de S y Rayleigh MP120 archivado de T.
E<−1e-20 indica cambio par negativo observado; descenso unilateral puede
proceder del gradiente residual. No atribuir causalidad a H sin esta distinción.
No seleccionar un mejor punto ni proponerlo como nuevo óptimo oficial.

## Cambio de imagen geométrica

En coordenadas normalizadas (t,s), comparar las dos poligonales completas.
Cota inferior numérica de Hausdorff: máximo simétrico de distancias a todos
los segmentos destino desde todos los vértices y puntos medios origen.
Cota superior: máximo desplazamiento entre vértices correspondientes, por
interpolación afín sobre cada arista. No confundir correspondencia con distancia
intrínseca ni la inferior muestreada con Hausdorff exacto.

Geometría en float64 sobre las proyecciones de los puntos MP: comprobar error
máximo por coordenada ≤1e-15; restar/sumar colchón fijo 1e-12 a las cotas
inferior/superior. No son cotas rigurosas de redondeo. Clasificar CHANGED si
inferior ajustada>1e-8, WITHIN_TOLERANCE si superior ajustada≤1e-8; en otro
caso UNRESOLVED. No refinar selectivamente ni llamar reparametrización exacta
a un cambio no detectado. Controles geométricos: identidad, redistribución en
segmento recto y traslación perpendicular de segmento recto.

## Estados, coste y reproducibilidad

Registrar todos los ensayos, parejas, direcciones/hash, signos, estados,
comprobaciones y costes; matrices y vectores densos fuera de Git. Sin imágenes
ni archivos de vértices perturbados: reconstruibles con código y hashes.
Validez diagnóstica PASS/INCONCLUSIVE separada de conclusiones sobre mínimos,
que permanecen UNKNOWN. Ensayo inviable es observación, no fallo de integridad.
C0 no se usa para ajustar tolerancias ni se descarta.

Presupuesto 900 s/512 MiB por corrida; si se excede, preservar resultados
parciales y terminar INCONCLUSIVE. Repetir una vez para igualdad exacta de
salidas científicas, excluyendo recursos. Ninguna inferencia confirmatoria:
se usan los mismos datos sintéticos, candidatos y direcciones exploratorios.
