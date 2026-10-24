# E16-AG · diseño v1 congelado antes de código o mediciones

Sólo AG/**. No reejecutar AF/AD ni leer estados/tablas T2. Fase0 leyó el
único diagnóstico autorizado en la referencia de config, ausente de main;
no usar sus casos para construir estados. Importar geometry.py intacto con
SHA y reutilizar la guarda AF sin excepciones de lectura T2 en runtime.

## Familia y población, sin selección

40 nuevos, diez semillas/índices × cuatro escalas de longitud a=.01,.03,.1,.3.
Tres grupos de nueve componentes duplicadas: f_j=.04(cosβ_j,sinβ_j),
β_j=2πj/3+iπ/30, j=0,1,2; i=0..9, semillas2026102500..2509 como identificadores
públicos (construcción determinista, sin RNG). D es indicador27×3, E=D/9.
U=[(1,−1,0)/√2,(1,1,−2)/√6]. C=U R(ψ) diag(1,η),
ψ=(i+1)π/17,η=.06+.02i. Q primeras dos columnas=a√27 D C, resto0;
ε=a²*.001, M=QQᵀ/27+εI. Es SPD; su espectro tiene25 autovalores ε y
los otros ε+9a²,ε+9a²η². La imagen a(P)=Ew(P) ocupa un triángulo plano,
con W=EᵀME y K≡0: bordes cercanos por amplitud métrica, no por selección
de escapes. d_borde≤a√(1+.001/9)/√6≤.123. Se incluyen también los40
M/f sintéticos AF archivados, SHA verificado; no se regeneran ni cambian.
Todos80 permanecen en tablas, incluidos fallos/desconocidos.

## Tres magnitudes distintas

ρ es mínimo de longitudes de semirrectas hasta infinito. d_borde es distancia
a la frontera de la completación métrica. d_esc es primer cruce muestreado de
||P||∞=150, **frontera artificial finita**, no necesariamente cota superior de
d_borde. Para la nueva familia d_borde es exacta: mínima distancia métrica
del baricentro a los tres segmentos, con proyecciones limitadas al segmento.
ρ exacta: mínimo de distancias métricas del baricentro a tres vértices y tres
puntos medios; prueba en THEORY. Para AF, d_borde permanece UNKNOWN.
Q1 compara dos números operacionales; un FAIL no refuta ρ≥d_borde.

## ρ: medición anterior a la exponencial de cada estado

Rejillas720/1440 y GL400/800 en s=10x/(1−x), x∈(0,1), las cuatro
combinaciones. Jv por geometry.jac intacto, sin inversión de g cerca del borde.
Añadir los normales exteriores de TODAS las aristas de la envolvente y sus
opuestos (casos de empate de logits): el mínimo puede estar en un conjunto
angular de medida cero, que una rejilla sola no encuentra. Guardar por separado
mínimos de rejilla y ampliados. En las direcciones especiales, imponer los
empates dominantes de la arista a precisión algebraica, verificarlos en MP80.
Refinar con quad epsrel1e-10, epsabs1e-12 max(1,ρ), subdividiendo la cola
según diferencias de logits para no omitir transiciones tardías; búsqueda
acotada en±2π/n alrededor del mínimo y todas las direcciones especiales.
Guardar todos los intentos, incluso fallidos; nunca convertir una integral
que omitió la cola en una cota. Aceptar contraste de resolución≤.5%; control
exacto nuevo y MP con tolerancia relativa2e-5. MP contrasta la dirección
minimizante y sus empates; no equivale a optimización angular certificada.

## Exponencial y refinamiento

2048 rayos, fase0, velocidades de norma g0=1, DOP853 rtol1e-12/atol1e-14,
hasta primer escape,1.5ρ,5000 pasos o presupuesto240s por estado. Fallo
numérico no es escape ni arrastre5000. Total14400s,2 procesos, BLAS/OMP1.

Nuevos estados: carta de cara q=(w0,w1) desde el origen, métrica constante
H=NᵀWN,N=[(1,0),(0,1),(−1,−1)]. IVP transformado a esta carta y DOP853
exactamente para2048 rayos; reconstruir P por log(w0/w2),log(w1/w2).
El umbral se mide SIEMPRE en P original, no en q. Preservar trayectorias y
pasos. Esta carta evita singularidad artificial de la coordenada natural y
no sirve para afirmar ausencia de arrastre en esa coordenada.

AF: DOP853 directo usando jet archivado; no sustituirlo por un control plano.
Guardar t, pasos, nfev, estado nativo, cara, P y tendencia de probabilidades.
Refinar alrededor del primer ángulo con escape en±2π/2048, acotado40iter,
xtol1e-8; cada IVP individual tiene los mismos límites. Si el refinamiento
falla, conservar coarse y etiquetar INCONCLUSIVE para ese contraste, no
sustituir un estado. Fuente: geodésica antes de primer evento de carta, no
mínimo global. Guardar matrices completas de perfiles fuera de Git con SHA.

## Controles y reglas previas

Cualquier control falla→INVALID, Q1–Q5 INCONCLUSIVE. Controles:
1. Softmax3 en triángulo equilátero M=I: d_borde=ρ=1/√6; exponencial
converge al borde conocido, diferencia finita medida por separado.
2. Softmax2 1D M=I, f=(0,.04): ρ=d_borde=1/√2, MP80; NO forzar SPD2D.
3. Invariancia afín P=Aq+b, A=[[2,.3],[−.2,.7]],b=(.6,−.4), mismo P0
físico: ρ invariantes≤2e-5 en un nuevo y primer AF, con aristas mapeadas.
4. AD: leer sólo geometría/IVP archivados E16; K≈0 y longitud continua
conservadas sin reejecutar AD; no atribuirle un borde softmax inexistente.
5. Cada nuevo: contraste ρ exacta y d_esc≤d_borde, con error2e-5;
velocidad métrica unitaria de la carta transformada y correspondencia jet.

Q1: PASS si todos80 tienen escape refinado válido y ρ≥d_esc dentro del error
2e-5; FAIL si alguno válido viola por más del error (investigar sin borrar);
resto INCONCLUSIVE. Dar también denominador de escapes, no sólo supervivientes.
Q2: PASS si80/80 escapes válidos, mediana ρ/d_esc≤1.2 y máximo≤2;
FAIL si mediana o máximo excede de forma numéricamente estable en casos válidos,
incluso con otros UNKNOWN; resto INCONCLUSIVE. Umbrales operacionales exigen
aproximación del20% típica y evitan factores>2; no se eligen tras medir.
Dar además ρ/d_borde exacta y d_esc/d_borde para los40 nuevos.
Q3: Spearman≥.9 global y por grupo, contraste angular/error no cambia veredicto:
PASS con80/80 completos y todos≥.9; FAIL si algún grupo con≥10 completos
estables da<.9; resto INCONCLUSIVE. Escalas emparejadas, sin p-valores de80
independientes, sin imputar censura/fallo. Reportar número de pares.
Q4: descriptiva. Si hubo DRAG_5000 en AF: PASS_DESCRIPTIVE si todos los
cocientes t_stop/ρ están en[.6,1], FAIL_DESCRIPTIVE si alguno estable fuera;
si no hay tales casos, INCONCLUSIVE. Cambio a carta plana no prueba nada
sobre arrastre natural. No llamar arrastre a timeout o fallo SPD.
Q5: descriptiva. Tiempo incluye todas cuadraturas/refinamientos ρ y todos
rayos/refinamientos, excluye controles/generación. PASS_DESCRIPTIVE si mediana
(tρ/texp)<1 en cada grupo, FAIL_DESCRIPTIVE si≥1 con completos, resto
INCONCLUSIVE. No es comparación universal de costes ni mismo objeto geométrico.

Una ejecución v1 y verificación desde archivos, sin reiniciar etapas cerradas.
Defecto→nueva versión documentada y congelada ANTES de corregir código y medir;
conservar salidas y fallos anteriores. No certificado, transferencia T2,
igualdad ρ=d_borde ni conocimiento de d_borde de AF.
