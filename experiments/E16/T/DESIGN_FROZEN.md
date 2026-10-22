# E16-T — Segundo orden y redistribución de nodos

Protocolo prospectivo exploratorio. No optimizar, entrenar, seleccionar nuevos
candidatos ni modificar S o sus criterios. Incluir los doce caminos finales
de S: Q0/Q1/C0, reference/scaled, 132/264. Misma L, dominio y métrica.
Las etiquetas de los métodos identifican la procedencia, no escalas del Hessiano:
todo se calcula en coordenadas físicas normalizadas (t,s).

## Pregunta y alcance

¿Aparece curvatura negativa resuelta numéricamente? ¿Cómo se distribuyen los
modos débiles entre desplazamientos tangenciales y normales del polígono?
Es diagnóstico sobre candidatos aproximadamente estacionarios. No representa
confirmación independiente, condiciones suficientes de mínimo, cociente exacto
por reparametrizaciones ni certificado de geodésica.

## Cálculo congelado

Hessiano AD completo de L en las 2(m−1) variables interiores. Conservar bruto
para comprobar simetría relativa ≤1e-10; simetrizar sólo para eigensolver.
No almacenar matrices densas ni autovectores. Registrar espectro completo
escalar del Hessiano y sus bloques tangencial TᵀHT y normal NᵀHN.
T/N son marcos euclídeos ortonormales por nodo, obtenidos del acorde entre
vecinos. Acorde ≤1e-14: no inventar marco; caso INCONCLUSIVE.
T y N separan desplazamientos locales, no espacios invariantes del Hessiano.
Registrar norma de acoplamiento, participación tangencial del autovector mínimo
y umbral τ=1e-8 max(1,max|λ|) propio de cada bloque, sin reajustarlo al medir.
No extrapolar modos negativos o casi nulos de un bloque al espectro completo.

Registrar margen a las cajas. Si alguna variable está a ≤1e-8 del borde,
no interpretar espectro irrestricto como condición necesaria en el cono crítico.
No resolver ese cono en T; conservar diagnóstico y limitación.

## Validación independiente

Cinco direcciones unitarias por camino, sin selección posterior: autovector
mínimo completo, mínimo tangencial, mínimo normal, seno de índices interiores
orientado tangencialmente y el mismo seno orientado normalmente. Orientar el
signo haciendo positiva la componente de mayor módulo. Para degeneración no
se afirma unicidad de los autovectores. Registrar hash de cada vector.
Evaluar curvatura central de L en MP80 y MP120 con pasos 1e-10/1e-12,
perturbando puntos MP sin convertirlos otra vez a float. Contrastar AD/MP
≤1e-6, ambos pasos ≤1e-8 y precisiones ≤1e-35, con error normalizado por
max(1,|a|,|b|). Comprobar factibilidad bilateral de ambos pasos. La comparación
MP valida cinco Rayleigh, no cada entrada ni el espectro completo.
Longitud MP central debe coincidir con S a ≤1e-35; reconstruir KKT de las
columnas MP finales archivadas, sin repetir auditoría de primer orden cerrada.

Control C0: construir Hessiano analítico de longitud recta en métrica constante,
con pesos inversos a Δt de cada arista y extremos fijos; comparar con AD a
≤1e-10 relativo. Sus m−1 direcciones tangenciales son nulas exactamente en
aritmética real mientras se conserva el orden. No convertir pequeños negativos
de redondeo en inestabilidad real. Q0/Q1 no heredan esa nulidad exacta.

## Estados y presupuesto

Clasificar cada bloque: NEGATIVE_AT_THRESHOLD, NEAR_SINGULAR o
POSITIVE_AT_THRESHOLD. Curvatura negativa numéricamente resuelta requiere
λmín<−τ, Rayleigh MP concordante y también <−τ; si no, mantenerla no resuelta.
Sólo la dirección negativa bilateralmente factible es testigo factible.
Ningún resultado declara mínimo: primer orden es aproximado, el umbral es
numérico, y T no demuestra control de errores ni positividad exacta en todos
los modos. Estado científico global INCONCLUSIVE sobre mínimos, separado de
PASS/INCONCLUSIVE de las comprobaciones diagnósticas.

Registrar todos los casos, espectros escalares, Rayleigh, contadores, errores,
fallos y resultados inconclusos. No descartes ni fallbacks ni nuevos umbrales.
900 s/512 MiB por corrida, incluidos MP; si se excede, preservar parcial y
terminar INCONCLUSIVE. Repetir una vez para igualdad exacta de salidas
científicas, excluyendo recursos. No versionar matrices o vectores internos.
