# DIN-D2b · ¿es tautológico el predictor de DIN-C1?

**No es una tautología algebraica universal en el régimen temprano. Parte de
la relación posterior al colapso sí está forzada bajo condiciones Fisher.
El ajuste lineal de Y seguido de Spearman no basta para demostrar información
adicional condicionada a L. La causa del .218 de D6 queda INCONCLUSIVE.**

| Pregunta | Veredicto exploratorio | Alcance |
|---|---|---|
| Q6 escalamiento/construcción | PASS | Identidades condicionadas y contraejemplos a diagonalidad/dominancia universales |
| Q7 fórmula de rho | PASS | Fórmula con factor de red; aproximación coordenada en9 casos sintéticos previstos |
| Q8 redundancia temprana | PASS | Se refuta la redundancia universal; efecto empírico D6 no identificado |
| Q9 sintéticos | PASS | 86/86 redes,9/9 controles primarios; fidelidad nativa83 consistentes y3 geometrías nulas sin log definido |
| Q10 recomendación | PASS_DESCRIPTIVE | Recomendar estimando y controles; el responsable decide DIN-C1 |

Veredictos del [diseño previo](DESIGN_FROZEN.md),
[resumen válido](results/run_v2/summary_v3.json) y
[verificación](verification.json). Ningún estado de otra etapa se modifica.

## Q6 · qué fuerza la construcción y qué depende de la red

En la parametrización reducida REAL de core, r_n=delta_n h_n,
delta_n=1-p(y_n), y K=F+gamma I. Exactamente:

    M_nm=delta_n delta_m h_nᵀK⁻¹h_m,
    M_nn=delta_n²||K⁻¹/²h_n||², tr M=sum_n M_nn.

Los términos cruzados son alineaciones de scores blanqueados. Confianza sola
no fija h ni K; F y ridge varían con las mismas probabilidades. Con Jacobianos
fijos y delta_n=epsilon c_n, F y gamma son de orden epsilon antes del piso
absoluto: M es de orden epsilon y rho de orden sqrt(epsilon), en modos no
anulados. El barrido homogéneo dio pendiente1.00001085 para tr M y .50000543
para rho, sobre epsilon1e-4,1e-6,1e-8. Con gamma fijo por el piso1e-18 y F
despreciable, el orden eventual es M~epsilon²/gamma; no se midió ese régimen.

**Identidad condicional decisiva:** con rango(A)=2N y sin ridge,

    M0=N diag((1-p(y_n))/p(y_n)).

Aquí diagonalidad y coincidencia del máximo con la menor confianza SÍ son
algebraicas. Para ridge despreciable frente al menor autovalor Fisher relevante,
M queda cerca de esa diagonal, con cota espectral explícita. La comprobación
sin ridge fue resoluble en62/86 redes;24 se mantienen fuera de ESA condición,
sin excluirlas del experimento. Un ridge1e-4 lambda_max no es automáticamente
pequeño respecto a lambda_min.

Sin condiciones de rango/condicionamiento no hay diagonalidad universal:
grouped3 produjo fracción de Frobenius fuera de diagonal≈.9428. El caso
lopsided tiene25 ejemplos con p_y=.3 y dos con p_y=.6; su máximo diagonal
está en uno de los dos MÁS confiados. La multiplicidad/alineación reduce el
leverage individual de los25 difíciles. Los tres casos aligned dan M sobre
el modo constante, que anula J. Son contraejemplos construidos, no una
estimación de la frecuencia de esas situaciones en entrenamiento.

La [prueba completa](THEORY.md) y el [lema de contracción](LEMA_CONTRACCION.md)
dan además la desigualdad universal0<=M<=N diag(odds), aun sin rango completo.
Se verifican las62 cotas condicionadas y86 cotas universales como auditoría.

## Q7 · fórmula con factores separados

En el régimen coordenado de D2 y para estos paneles de caras pequeñas,

    rho≈sqrt(Mkk)/n
       =(sqrt(N)/n) sqrt(((1-p_k)/p_k) ell_k), 0<=ell_k<=1.

ell_k es un leverage Fisher regularizado; depende de la red. Si además
ell_k≈1, log rho≈.5log N-log n+.5log(1-p_k)-.5log p_k. La pendiente local
respecto a log(1-p_k) sería1/(2p_k), no una constante universal. Por ello no
se puede interpretar la pendiente publicada .70 como una nueva identidad.

En los9 casos previstos con un difícil y epsilon fácil1e-8, las cotas de
cuerda y de un rayo concreto de extinción encerraron la aproximación dentro
del margen congelado5%; el mayor exceso de la cota superior fue≈.001596
en unidades de sqrt(Mkk)/27. Mkk/[N odds_k]≈.9998994–.9998999 en este grupo.
La inferencia sobre el mínimo usa ambas cotas, no sólo la búsqueda nativa.

Fuera del colapso, la igualdad segura es
log rho=.5log d+log rho(M/d,f). Forma, vector completo de confianzas,
alineaciones, Fisher/ridge y f siguen presentes. La normalización por tr M
quita una escala que SÍ está en el desenlace de DIN-C1. No se afirma distancia
geodésica real ni mínimo global certificado del instrumento.

## Q8 · dos pruebas de no identificación y un control estadístico

Las redes lookup realizan M=d_perp H+d_const ccᵀ, H=I-ccᵀ y c constante.
Como Jᵀc=0, G=d_perp JᵀJ para TODO P. Es una identidad analítica;
la rejilla de nueve puntos sólo comprueba su implementación.

| Control | Resultado en3 semillas |
|---|---|
| Misma confianza .7; a=1 frente a .05 | Delta X=0, rho cambia por factor≈.62768518 |
| Confianzas .7 y .85; d_perp=4 en ambas | Delta X=log2≈.69314718, mismo G y rho |
| Error relativo de G del segundo par | ≤2.87e-13 |
| Concentración espectral máxima del segundo par | .1001104; rango efectivo mínimo24.2905 |
| Embedding de ese par en core.WineMLP | Errores G≤8.87e-14, sin datos Wine |

El par de igual G se fija por una fórmula antes de llamar rho: no selecciona
resultados geométricos. Se mantiene f idéntico. Por tanto ni el campo completo
G identifica X universalmente; menos aún su escalar log rho. Se usa ridge
finito: en esos pares gamma/lambda_min(F)≈10.68 y1.135. No son evidencia contra
la identidad sin ridge ni una afirmación de dispersión condicional en D6.

Sensibilidad: perturbaciones W3 de escala1e-4 cambiaron rho entre≈.07% y8.61%
sin recalibrar. Se conservan los seis casos; no se presenta robustez uniforme
del5% ni se extrapolan las construcciones exactas a redes entrenadas típicas.

**El control del estadístico sí detecta una limitación del borrador:**

    L=(0,.01,.02,.03,1), X=L-2, Y=-L²
    e=residuo MCO de Y~1+L, rangos(e)=(1,2,4,5,3)
    Spearman(X,e)=.7, Pearson(X,e)=0.

X está exactamente contenido en L. Aun así, el W_adj DOCUMENTADO es positivo.
Residualizar X también da residuo cero: correlación NO_IDENTIFICABLE.
No es necesaria una no linealidad entre X y L ni error de medida para este
contraejemplo. Una no linealidad Y(L) más Spearman posterior basta.

| Panel estadístico sintético,64 splits×5 | W del residuo lineal Y |
|---|---:|
| X afín a L, Y=-L² exacta | .700000 |
| Mismo caso, ruido Y de escala.001 | .700000 |
| X función cuadrática de L, Y=X+ruido | .948683 |
| L con error de medida, X mide L latente | .4265625 |
| Control con incremento predictivo independiente | .9296875 |

Estos últimos paneles son descriptivos y usan rangos promedio; en el control
exacto no hay empates y se reproduce la definición C1. Véanse residuos
lineales/cuadráticos, indefinidos y controles en
[statistic_panels.json](results/run_v2/statistic_panels.json).
No se auditó ni ejecutó el script confirmatorio efectivo. La permutación
no resuelve una diferencia entre nulo lineal y nulo condicional general.

**La causa del .218 publicado en D6 es INCONCLUSIVE.** Puede existir predicción
temporal adicional porque la construcción no fija la dinámica10→250; también
puede quedar no linealidad, error de medida o selección exploratoria. No se
leyeron estados empíricos para separarlos. Ausencia de colapso no basta como
prueba de no tautología y este contraejemplo no demuestra artefacto en D6.

## Q9 · ejecución, fidelidad y conservación

86/86 redes con core.make_geom_state y subset_M([0,1,2]) intactos. Máximos
errores relativos normalizados: R2.59e-13, U2.77e-13, M6.17e-11.
83 integrales nativas concuerdan con la integral completa independiente al
ángulo devuelto (máximo error relativo2.73e-8); eso NO certifica el mínimo
angular. Tres casos aligned tienen G=0 analíticamente y log rho indefinido;
el retorno nativo pequeño no se convierte en una distancia positiva fiable.
166 avisos en9 casos se archivan íntegros, sin filtrar ni reparar el instrumento.
No se reinterpreta el FAIL previo de D2 en otras geometrías.

Tiempo válido258.43s; dos procesos, un hilo por librería.
[Entorno y SHA](results/run_v2/environment.json) ·
[tabla completa](results/run_v2/networks_v3.csv) ·
[recursos](results/run_v2/resources.json).
87 arrays válidos, más5 de la versión inválida, se guardan fuera de Git
con SHA; incluyen pesos, R/U, M, f, p, A y espectros. No son estados T2.

Se conserva run_v1 INVALID_PROTOCOL_ORDER: arrancó después del diseño pero
antes del commit de código al fallar una comprobación de CRLF. Fue detenida;
sus cuatro redes y controles NO aportan evidencia primaria.
[Enmienda v2](AMENDMENT_FROZEN_v2.md). La corrida válida fue desde1c7a1bf,
posterior a diseño85fffb4 y código73cb83a.
El postproceso fallido por serialización también se conserva, junto con
[enmienda v3](AMENDMENT_FROZEN_v3.md), resumen v3 y código previo intactos.
No se repitió ninguna medición para corregir el formato.

## Q10 · recomendación, sin decidir DIN-C1

El ajuste lineal seguido de Spearman es insuficiente para una afirmación
condicional general. Conviene fijar el estimando antes de congelar: conservar
una afirmación estrecha sobre ese residuo, o preespecificar un modelo base
flexible, evaluar incremento predictivo fuera de splits de ajuste y validar
controles negativos. Modelar también X|L ayuda a evitar la falsa interpretación,
pero una correlación de residuos tampoco prueba independencia general.

La recomendación desarrolla no linealidad, error de medida, empates, potencia,
covariables y un predictor alternativo en panel separado o dinámica temprana:
[RECOMENDACION_DIN_C1.md](RECOMENDACION_DIN_C1.md).
No se cambia C1, no se entrena una cohorte, no se afirma transferencia a T2.
