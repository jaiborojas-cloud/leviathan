# E16-Q — Energía, parametrización y condicionamiento

Diagnóstico exploratorio sobre los mismos datos sintéticos. Se conservan Q0,
Q1 y C0; no se promueve ningún superviviente a confirmación independiente.

## Identidad continua y límite discreto

L=integral sqrt(q(u)) du y E=1/2 integral q(u) du, intervalo u de longitud 1.
Cauchy–Schwarz da E≥L²/2, con igualdad sólo para velocidad métrica constante.
Para el mismo polígono, permitir parametrizar por arco métrico da E_arc=L²/2.
Su gradiente es L·grad L y su Hessiano L·H_L+grad L·grad L^T: en un punto
estacionario no elimina los modos nulos por simple cambio escalar del objetivo.

En cada segmento afín de un polígono, con duración fija 1/m y q_i(v)=c+bv+av²,
A_i=c+b/2+a/3. E_aff=m/2 sum A_i. Es el objetivo energía que se optimiza en Q.
Aun optimizando sólo las duraciones, min E_aff=1/2(sum sqrt(A_i))²≥L²/2.
No se afirma equivalencia de mínimos discretos de L y E_aff. Registrar las
tres magnitudes E_aff, E_durations y E_arc, sus brechas y desigualdades.

## Contraste prospectivo

Fuentes: P/free/132 de Q0, Q1 y C0, conservando también sus INCONCLUSIVE.
Cada variante parte independientemente de esa fuente, sin reejecutar P.
Variantes en orden length y energy: minimizar L o E_aff con ambas coordenadas
t/s libres, extremos y rectángulo de P. Mismos ajustes L-BFGS-B de config.json,
4800 iteraciones por optimización, sin reinicios ni fallback. La variante
length es una continuación de referencia con el mismo presupuesto nuevo,
no una corrección ni repetición del resultado histórico P.

Optimizar 132 y luego 264, subdividiendo TODOS los segmentos del candidato
anterior de cada variante. La longitud del polígono debe conservarse antes de
optimizar. La energía E_aff también se conserva al subdividir cada segmento y
su duración por mitades; verificar ambas identidades. No iniciar una variante
con el resultado de la otra. Aristas exactamente nulas se rechazan como en P,
sin suelo de métrica, regularización o separación mínima positiva. Conservar
conteos de ensayos rechazados, candidatos devueltos y fallos. Continuar sólo
operaciones evaluables; no descartar un linaje por un fallo.

Presupuesto: 900 s y 512 MiB por corrida, congelado antes de medir.

## Verificación y éxito

Heredar validación de longitud por precisión 80/120, cuadraturas 16/32/64,
reparametrización, primitivas y SPD Bernstein. Verificar también E_aff con
integral polinómica en multiprecisión y cuadratura GL16 (polinomio de grado 2).
Desigualdades E_aff≥E_durations≥E_arc con error normalizado permitido 1e-40.
La conversión de t exacto binario y s decimal se mantiene como P.

Validar gradientes AD y FD local de 80 cifras de AMBOS objetivos para cada
candidato, en ambas coordenadas, con pasos 1e-18/1e-22 y tolerancias de P.
Residual KKT proyectado normalizado por max(1,objetivo). La variante length
requiere KKT_L≤1e-5; energy requiere KKT_E≤1e-5 Y KKT_L≤1e-5, pues se busca
estacionariedad también de longitud, no sólo del problema discreto diferente.
Además exigir éxito del optimizador y no empeoramiento de SU objetivo.

Comparar 132/264 mediante longitud normalizada≤1e-3 y Hausdorff superior≤1e-3,
brecha≤1e-5; refinamiento válido sólo si ambos caminos pasan. No exigir
refinamiento de energía como sustituto de la geometría. Comparaciones entre
variantes y Q0/Q1 son descriptivas; no se exige que coincidan para pasar.
No usar sup|delta s(t)|, pues las curvas pueden retroceder.

C0, métrica constante: longitud recta y s≈0 en ambas variantes (errores
normalizados de longitud≤1e-8 y max|s|≤1e-6). Para energy, además brecha
E_aff−L_recta²/2≤1e-8 y max|t_i−i/m|≤1e-4. No exigir uniformidad de t a length,
pues redistribuir nodos colineales no cambia L. Controles de equivalencia,
verticalidad, inversión, subdivisión, arco y Hausdorff se conservan.

## Condicionamiento, alcance y controles

Sólo en 132: fuente y ambos resultados, para cada linaje, sin elegir por éxito.
Hessianos AD de L, E_aff y E_arc. Verificar la identidad H_arc anterior con
error relativo≤1e-8. Para C0, H_E=m·kron(T,G_frame), con T tridiagonal (2,-1,-1),
es identidad analítica comprobable aun con distribución no uniforme.
Verificar que un desplazamiento tangencial de un nodo interior de la recta
no cambia L pero modifica E_aff; no atribuir a este control un diagnóstico
universal sobre Q0/Q1.

Reportar espectro completo sólo como escalares resumidos (no matrices):
mínimo/máximo, negativos, casi nulos y razón del espectro positivo con umbral
1e-10·max(1,max|lambda|). Usar bloque de variables no activas a tolerancia 1e-6;
informar dimensión y umbral. Si hay negativos o casi nulos, no llamarlo número
de condición SPD. En puntos no estacionarios no certificar un mínimo.

Dos direcciones deterministas: campo de tangentes por secantes centradas entre
vecinos y su rotación normal, proyectadas al bloque no activo y normalizadas.
Comparar Rayleigh AD con segunda diferencia de L/E en MP80, pasos 1e-16/1e-18;
acuerdo entre pasos≤1e-20 y AD/MP≤1e-5. No convertir perturbaciones a float.
Caso de campo nulo: conservar diagnóstico desconocido, no inventar un cociente.
Brechas de energía o espectros desfavorables son descriptores, no fallos por
sí mismos; fallos de comprobación numérica sí son inconclusos.

PASS_NUMERICAL requiere todos los controles, candidatos, KKT correspondientes
y refinamientos. Fallos de identidades son FAIL; limitaciones numéricas o de
optimización pendientes son INCONCLUSIVE. Conservar la primera corrida y
reproducir salidas científicas byte por byte; recursos aparte. No se certifican
mínimos globales, geodésicas, unicidad ni convergencia de una curva límite.
