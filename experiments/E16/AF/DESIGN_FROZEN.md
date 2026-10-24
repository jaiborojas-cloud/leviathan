# E16-AF · diseño congelado antes de código y mediciones

Lectura previa geometry.py y audit.py: [convenciones](THEORY.md). Sólo esos dos
archivos de T2 son autorizados; SHA verificado antes de importar/ejecutar código.
No llamar a funciones que cargan casos. Prohibir en runtime aperturas bajo
experiments/T2_A*, cualquier Repro/T2_A y todo .npz. No leer otros datos T2.
Fuentes E16 sintéticas de control sí autorizadas. Sólo cambios AF/**.

## Estados y escalas, sin selección

40 estados:27 componentes, semillas2026102400..2026102409, PCG64,10×4.
Regla exacta de f,Q,M y calibración α en THEORY/config. Q radial prefijada3,
ruido.1 y ε_base.1; si la norma radial es≤1e-12 usar columna0, registrar fallo,
no regenerar semilla. Mantener signos y casos casi planos. T=[1,10,1000,10000],
s=.0004√T; justificación únicamente transformación de K central, no geodésicas.
El cambio conjunto de M es necesario: f solo es cambio de carta. Modelo sintético
deliberado, no M/f recuperadas de T2 ni los pesos de una red entrenada.

## Etapa1: predictores, única información antes de desenlaces

Generar/archivar todos los M,f sintéticos, α,ε y hashes. Medir sólo K0,
max|K| en disco pequeño muestreado(64 ángulos×9 radios hastaρ0=.0005),
y X=maxκ(Dexp) en rx=.001,64 ángulos. Dexp intrínseco tiene valores
singulares1,|j/r|, κ=max/min; no condición euclidiana de coordenadas.
jacsolve archivado intacto a su tolerancia original para este tramo corto.
En la escala máxima K0 rx²≈.01 y rx≈.032π/√10000: pequeño y fijado sin
geodésicas largas. Si deja de ser pequeño en un estado, conservar flag, no
ajustar radios. Verificar h SPD, j/r>0, K MP80 en centro y maxK muestreado,
y comparación de jacsolve con integración propia de control sólo posteriormente.
Fallo predictor→UNKNOWN; estado permanece entre40. No desenlaces en etapa1.
Guardar predictors.csv, su SHA256 y estados en commit **antes de código etapa2**.

## Etapa2: desenlaces

512/1024 rayos, fase0, origenP0=(0,0), velocidad unitaria métrica.
Adaptador propio usa jet/eval importados sin modificación y DOP853rtol1e-12,
atol1e-14. Integra p,v,j,j' y detiene conjunto al primer ||p||∞=150 o Rmax=.2.
El integrador archivado rays no admite eventos: se documenta el adaptador;
no se cambia la fuente ni su tolerancia por monkeypatch. Primer escape común
permite calcular el disco hasta rdeg sin inventar trayectorias exteriores.
Guardar puntos/velocidades/Jacobi en257 radios y último punto. SPD/no finitos
y condición>1e12: INCONCLUSIVE_NUMERICAL, no escape ni censura geométrica.

r_conj: primer cero j>0→j≤0 en257 radios, Brent sobre salida densa, excluir
origen≤1e-10. Conservar primer cero por rayo y mínimo muestreado global.
r_col: Polygon.exterior.is_simple en257 frentes, refinar primer intervalo no
simple con28 bisecciones, guardar segmentos/caras si se resuelve; posibles
contactos entre muestras siguen no certificados. r_esc: evento de norma∞150,
guardar cara(s), p, velocidad, a_min/a_max/Neff y tendencia de últimos8 puntos.
Si falla integración, guardar último radio aceptado si existe y UNKNOWN.

rdeg=min de eventos observados; empates dentro2% se guardan MULTIPLE.
Sin evento tras Rmax: RIGHT_CENSORED_RMAX, rdeg>Rmax; no inventar A_emb.
Triangular discos hasta r_area=(1−1e-6)rdeg, o Rmax si censurado, con32/64
anillos y area7 importada. Ambos n angulares. Reportar A_emb como estimación
lateral del evento sólo cuando evento observado; si censurado, A(Rmax) es
una cota observacional distinta, no A_emb. Convergencia radial/angular5%,
radios2%. Si area falla, el evento puede seguir observado y el área UNKNOWN.

MP80: K y densidad en origen y todos los puntos incidentes críticos de primer
conjugado/colisión/escape, tolerancia relativa1e-6 (max1). M,f son los floats
sintéticos archivados promovidos exactamente, no números de T2. Contraste
local MP no equivale a integrar toda el área en MP. Si hay duda numérica o
MP falla, conservar estado INCONCLUSIVE, no convertirlo en evento confirmado.

## Q1: instrumento

Por estado PASS si ambos n tienen resultado(evento o censura Rmax) coherente,
MP válido, radios≤2% y áreas≤5% y tipo común o empate declarado; FAIL si
ambos resultados numéricos válidos y MP válido discrepan>10% en radio/área;
intermedios/fallos UNKNOWN→INCONCLUSIVE. Global PASS sólo40 PASS, FAIL si
hay fallo estable, resto INCONCLUSIVE. Describir fracción censurada y tipo
dominante por escala, sin hipótesis causal sobre su dominancia.

## Q2: índice de Morse discreto

Rayoθ0 prefijado para TODOS los estados. Integrarlo individualmente hastaRmax
con escape propio para cubrir segmento después del primer evento global, sin
cambiar rayo por el que tenga un conjugado favorable. Registrar esta extensión.
Si hay conjugado propio estable antes de escape: objetivos.75c y1.25c.
Si no, caso INCONCLUSIVE, no sustituirlo por rayo mínimo ni otro objetivo.
Mallas32/64/128, carta normal métrica fija sobre geodésica muestreada, longitud
de segmentos rectos integradaGL8, contraste16. Hessiana AD por arista y bloque
normal bandado, sin reemplazar medición por Jacobi/FEM. Guardar espectros,
bandas y modos negativos, gradiente normal≤1e-3 para aproximación estacionaria.
Umbral=max(1e-8,1e-7 max|λ|); quadraturaH relativa1e-5. Testigo mínimo MP80
analítico de segunda variación de longitud integradaGL16 en malla128 y ambos
objetivos; contraste16/32 y AD relativo1e-4. No se afirma punto discreto exacto.
PASS si índice0/1 en las3 mallas, radio propio y conteos contrastados; FAIL si
patrón diferente estable en todas mallas/contrastes; faltas→INCONCLUSIVE.
Global PASS sólo40 estados elegibles PASS; no seleccionar estados con foco
como evidencia confirmatoria. Dar además denominador de validación condicional.

## Q3: asociación exploratoria

Primarios |K0|,max|K|,X. Kendall tau-b con censurados Rmax tratados como rango
mayor que todo evento (valor centinelaRmax+1); censurado-censurado empata.
Fallo numérico no es censurado: rankUNKNOWN, globalINCONCLUSIVE si falta uno.
Sin p-valores de40 independientes: hay10 bloques/semillas y calibración común.
PASS si las tres tau≤−.2 y diferencia entre n≤.05; FAIL si las tres tau≥+.2
estables; resto INCONCLUSIVE. Correlaciones firmadas secundarias descriptivas.
No invertir predictor/outcome ni mirar desenlaces antes del hash de etapa1.

## Q4: puente descriptivo

A*=.02. Usar intervalo conservador entre áreas32/64 y512/1024, ampliado por
su diferencia. Si evento y upper(A_emb)<.02: disco no construible operacional;
si lower área al evento/censura>.02: construible hasta el radio observado.
Censurado con área<.02 o intervalo que cruza umbral: ?. No inferir fracaso de
área de radio censurado. Reportar fracción/40 y por tipo, denominadores siempre40.
Para rdeg: evento o Rmax censurado es desenlace conocido; fallo numérico es ?.
PASS si fracción?radio menor que?área en ambas resoluciones; FAIL si no disminuye
(incluso igualdad) de modo estable; INCONCLUSIVE si resolución/umbral ambiguo.
No transferir esas fracciones a T2 ni afirmar reducción universal de censura.

## Controles

Esfera K1: conjugadoπ, Hessiana normal de longitud discreta tiene exactamente1
negativa a1.5π y0 a.75π, mallas32/64/128. Hiperbólico K−1 sin conjugados
hasta4 y bloque normal no negativo. Cuadrática AD con IVP AC prefijado, K≈0,
índice0 en las mismas mallas. CuadraturaGL8/16 concuerda1e-5; Jacobi/π1e-8.
Control escape sintético independiente n4: f=(±δ,±δ),δ=.001,M=I; sobreP2=0,
s=σ(2δP1)−.5, de modo r_esc=σ(.3)−.5 alP1=150. Coincidir≤1e-7, sin
leer estados. Verificar MP y cara+P1. area7 plano constante debe recuperar
área poligonal/πR² con error angular≤1e-4. Cualquier control obligatorio falla
→corrida INVALID y Q1–Q4 INCONCLUSIVE. No arreglar estados ni borrar fallos.

Presupuesto7200s total,600s por estado/resolución; sin ampliar. Restantes40
permanecen UNKNOWN. Una corrida y una reproducción exacta (tiempos excluidos).
Código stage2 sólo DESPUÉS del commit de predictores+SHA. Defecto exige nueva
versión congelada y conserva original. No certificados, corte exacto ni
transferencia a T2. ScopeAF/**, sin ninguna lectura de estados T2.
