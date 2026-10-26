# DIN-D9g-b — diseño exploratorio CONGELADO antes del código

Fecha:2026-10-26 (México). Rama research/din-d9g-b, main0dbc973.
Este commit precede a código de medición, covariables nuevas y resultados flexibles.
[Configuración exacta](config.json). Único candidato c30, único desenlace pérdida
test250 ya archivada. C2 queda RESERVADA y bloqueada: no leer sus tablas/estados/
checkpoints ni calcular test/asociaciones. Sin Wine/Iris/T2/DIN-C1.

## Datos congelados y alcance

Exactamente las 1.500 trayectorias G3 de D9g (s=.25/.5/.8;100splits×5inicios).
Reutilizar la pérdida test250 publicada y el test seeds711000..711099. **No**
regenerar test, reentrenar, recalcular test ni medir rho/M. D9g no está fusionado:
fuentes copiadas por commit8996c2c y SHA dentro de D9g_b/sources/, sin tocar D9g.
Se conocen B1 y sus controles anteriores; ninguna base flexible fue calculada.

Para B4 se permite sólo restaurar pesos u30 de G3 y hacer forward sobre el panel
original (27 puntos). Usar los datos estandarizados train/panel archivados. Contrastar
pérdida/precisión/X panel30 contra D9g, error≤1e-10+1e-10|ref|, precisión≤1e-14.
Una discrepancia invalida interpretación; conservar fallo, no relajar tolerancia.

## Tres covariables adicionales de u30

1. **Margen medio firmado**: (1/27) sum_n [z_n,y_n − max_{c≠y_n} z_nc], logits
   originales de la red de tres clases, sin reducir logits ni transformar por softmax.
2. **Entropía media panel**, en nats: −(1/27) sum_n sum_c p_nc log p_nc,
   p=softmax(z), log p por log_softmax; 0·log0 se interpreta como0.
3. **Norma L2 de todos los parámetros**: sqrt(sum_l ||W_l||_F²+||b_l||²),
   incluyendo las tres matrices y sus tres sesgos, en el checkpoint original.

Son resúmenes forward/paramétricos; no se introducen en M ni se calculan mediante
M/gradientes. Probabilidades y pesos también sustentan M: no se afirma que sean
matemáticamente independientes de su construcción. No cambiar pesos ni gauge.
Las tres se añaden linealmente en B4; no crear sus cuadrados/interacciones nuevos.

## Bases anidadas y transformación estrictamente dentro de cada bloque

Medidas originales q=(loss_train30,loss_panel30,acc_panel30,X30). Diez bloques
con default_rng(260010).permutation(splits), posición mod10, igual que D9g.
En cada bloque exterior estimar **sólo en entrenamiento** media mu_j y desvío
poblacional sigma_j de q_j. Si sigma=0, usar1 y registrar columna constante.
z_j=(q_j−mu_j)/sigma_j; aplicar esas mismas mu/sigma al bloque de prueba.

- **B1**: los cuatro z_j lineales; reproduce la base lineal D9g por invariancia OLS.
- **B2**: B1 + z_j² y z_j³ para cada una de las cuatro medidas (12 columnas).
- **B3**: B2 + z_i z_j para todas las seis parejas i<j (18 columnas).
- **B4**: B3 + las tres medidas nuevas, estandarizadas con mu/sigma del entrenamiento
  exterior (21 columnas). Ningún término extra. **B5 NO se incluye.**

Después de formar los términos, centrar CADA término dentro del grupo de cinco
inicializaciones. Grupos train/test están separados por split completo; no se
mezclan. Escalar columnas centradas por RMS calculado sólo en entrenamiento,
usando1 si es cero. Registrar transformaciones, rango y condición por bloque.
OLS por SVD, rcond=eps·max(n_train,p), sin ridge ni selección de términos.
Todas las pendientes se comparten dentro del conjunto analizado, no por split.
Y y candidato c se centran intra-grupo como C1/D9g. El escalado del candidato
usa RMS train del bloque y no cambia D; β se reporta en unidades originales.

Análisis por s:500 filas/100splits. Agregado:1.500 filas; centrar/permutar por
(nivel,split), pero mantener todos los niveles del MISMO split en el mismo bloque.
No tratar 300 paneles emparejados como splits independientes. Pendientes pooled comunes.

## Estimando, permutaciones y estabilidad

D=1−SSE(base+c30)/SSE(base) fuera de muestra. D_base=1−SSE(base)/SSE(0).
Conservar negativos. 2.000 permutaciones de c30 dentro del grupo, RNG320007
para cada base/conjunto, común para comparar y reproducir p de B1/D9g.
La base se ajusta sin candidato ni Y de prueba; permutar c no altera sus términos.
p=(1+#{D_perm≥D−1e-15})/2001. Guardar todos D nulos y SSE. FWL vectorizado
se permite si coincide con OLS directo, |D error|≤1e-9, p idéntica en controles.

β completo se obtiene con la misma construcción entrenada en todas las filas del
conjunto y se convierte a unidades originales. Para mitades split par/impar,
recalcular TODA la transformación y diez bloques dentro de cada mitad. Reportar
D de mitad, β y signos. Signo estable = β_par·β_impar>0, consistente con β_completo.
No se requiere D>.01 en cada mitad. No se cambia partición ni signo tras resultados.
B1 debe reproducir D9g c30 para cuatro conjuntos: |D diferencia|≤1e-10 y p idéntica.
Fallo de reproducción: INVALIDA, no calificar robustez hasta versión documentada.

## Controles obligatorios antes de analizar la cohorte

**Negativo, por cada B_j:** en cada bloque entrenar OLS c30_tilde~B_j,training;
usar c_hat_train=B_j,train a y c_hat_test=B_j,test a. Volver a correr la adición
mediante el mismo código. El candidato está exactamente en el espacio de la base,
por lo que |D adicional|≤1e-8; coeficiente NO_IDENTIFICABLE, no interpretarlo como0.
En B4 es la predicción de c30 desde B4 solicitada. Usar B4 contra B1 sería una
función que B1 no contiene y NO un control que necesariamente deba tener D0.
Este control comprueba el instrumento, no garantiza calibración universal.
Se ejecuta primero en tablas sintéticas y después por base/conjunto en la cohorte.

**Positivo sintético:**100splits×5, siete covariables normales con offsets de split,
r,eta,xi independientes N(0,1); Y=.5q0−.2q1²+.1q2q3+r+.2eta;
c_sintético=r+.2xi. Semilla731001, sin datos G3/C2. En las cuatro bases exigir
D>.1, p<.05/4 y β de mismo signo positivo en mitades. Verdadera señal independiente
más allá de todas las funciones baratas; no comparar potencia con el efecto real.

**Comprobación no lineal adicional fijada:** Y=z0²+ruido pequeño y c=z0²
como función barata. B1 puede tener incremento; B2–B4 deben dar |D|≤1e-8
por alias. No usar su incremento sobre B1 para acusar sesgo: es la motivación
para probar flexibilidad. Guardar resultados aun si falla un control.

Control numérico de todos D nulos contra OLS directo en tablas artificiales con
cuatro bases, incluidas columnas constantes; mu/sigma se guardan por bloque.
Si cualquier obligatorio falla, INVALIDA y conservar salidas. No pasar a interpretar
G3. Ninguna tolerancia se ajusta después del resultado.

## Regla de lectura ANTES de medir (decide sólo s=.8)

Con controles, reproducción y datos válidos:
- **ROBUSTO_EXPLORATORIO** si B2,B3,B4 cumplen TODAS D>.01, p<.05/4 y signo
  estable en mitades (cada base). No se exige signo adicional distinto del solicitado;
  se reportará si la dirección cambia entre bases.
- **ARTEFACTO_DE_BASE_LINEAL_EXPLORATORIO** si **B3 Y B4** tienen D≤0. Es la
  lectura operacional más conservadora de «B3/B4», no una prueba de causa única.
- **FRAGIL_EXPLORATORIO** si falla la regla con alguna flexible sin satisfacer
  la condición anterior. Si sólo una de B3/B4 tiene D≤0, se reporta explícitamente.
- Datos/controles/reproducción insuficientes: **INCONCLUSIVE/INVALIDA**, no frágil.

s=.25/.5 y agregado se reportan completos y descriptivos, sin rescatar una falla
en s=.8. B1 referencia no decide. No elegir bases, tiempos, λ ni desenlaces nuevos.
Un alias real c~B se declara NO_IDENTIFICABLE y su D≈0; no inventar β/p. Conserva
conteos de filas previstas, errores y ausentes. >5% faltantes, <80%splits con≥3
filas o <95% filas tras retener splits válidos → INCONCLUSIVE.

## Conservación y límites

Sólo D9g_b se modifica. Todos los archivos/números de D9g y etapas previas intactos.
Registrar código/entorno/tiempos/SHA. Dos procesos, un hilo BLAS/Torch, presupuesto
14.400s. Escritura exclusiva; conservar todos los fallos/arrays fuera de Git.
Un defecto obliga a enmienda congelada ANTES de corregir. No reentrenar ni repetir
mediciones para sustituir fallos. No acceder a C2. PR en borrador sin fusión.

La regla evalúa robustez a estas bases concretas, no a toda función de medidas
baratas. El centrado del desenlace usa media final del grupo, como D9g: predicción
entre inicializaciones, no predictor desplegable sin esa media. Permutación
exploratoria y Bonferroni no demuestran exchangeabilidad o calibración universal.
No conclusión confirmatoria, causal ni transferencia a datos reales. Un «artefacto»
operacional significa que desaparece el incremento al flexibilizar B3/B4, no que
se haya identificado algebraicamente toda la causa. El responsable decide si procede
un confirmatorio; esta tarea no lo ejecuta ni usa su cohorte reservada.
