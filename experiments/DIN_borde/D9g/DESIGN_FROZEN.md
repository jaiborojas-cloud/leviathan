# DIN-D9g — diseño exploratorio CONGELADO antes del código y del test

Fecha: 2026-10-26 (México). Rama research/din-d9g desde main 0dbc973.
Este commit precede a TODO código D9g, generación de test, carga de pesos para
medir y asociaciones nuevas. [Configuración exacta](config.json). No se entrena.

## Pregunta, errata y alcance

¿La geometría u10–u30 añade predicción de la pérdida de generalización final sobre
cuatro medidas baratas del mismo momento? Todo es descubrimiento G3. No se usa C2:
queda reservada como posible confirmatorio del estimando. No Wine/Iris/T2/DIN-C1.
Se leen sólo código C1 y los documentos de contexto expresamente autorizados.

**Errata acordada por el responsable antes del código:** son **11 candidatos**,
no 12: nueve medidas en tres tiempos y dos incrementos. Se mantiene **p<0.05/12**,
más conservador. No se añade Delta c(10→30), suma de los otros dos incrementos.
La misma errata está en PLAN_D9_generalizacion.md, commit c5cea08, preservado por SHA.

## Datos y test independiente

Universo completo: G3, tres niveles s=.25/.5/.8, splits0..99, k0..4: 1.500
trayectorias. Sólo checkpoints existentes de u10,20,30,50,250 (7.500). No se
retoma Adam ni se modifica una red. Se reutilizan c, tr M y rho_caras de G3 r3;
no se vuelve a medir rho, ni se cambia el instrumento.

Por split generar epsilon_test iid N(0,I13), 3.000×13, seed=711000+split;
1.000 ejemplos por clase, medias (2,0),(-1,sqrt3),(-1,-sqrt3) en primeras dos
coordenadas, otras cero, raw=mu_y+s epsilon. El mismo ruido test se empareja
entre niveles; ningún ruido train/panel se reutiliza. Estandarizar usando EXCLUSIVAMENTE
scaler_mean y scaler_scale archivados de TRAIN G3 por nivel/split. Test no ajusta
modelos, normalización ni hiperparámetros. Semillas nuevas disjuntas de G3.

Cargar la red exacta G3 13→64→32→3, ReLU, double, en eval, y pesos archivados.
Recalcular train/panel/X en las cinco visitas; comparar con G3 antes de permitir
interpretación: pérdidas/X |error|≤1e-10+1e-10|referencia|; precisión≤1e-14.
Por trayectoria, evaluar test SÓLO en u250. Guardar logits/pérdidas individuales,
datos test, pesos originales por referencia/SHA y todos los fallos, fuera de Git.
No reemplazar fallos. Una discrepancia de reproducción invalida la corrida para
interpretar hasta investigar con versión nueva; no ajustar tolerancias después.

## Desenlaces

Primario: Y=media de entropía cruzada de los 3.000 ejemplos de test u250, sin log.
Secundarios: precisión test250 y brecha pérdida test250−pérdida train250.
Son estimaciones en un test grande finito, no riesgo poblacional exacto. Conservar
SE descriptiva estratificada (tres clases fijas) de las métricas de test.
No usar los secundarios para promover un candidato que falle en la primaria.

## Once candidatos fijados y base barata

Orden j=0..8: para t=10,20,30, en orden c(t), log tr M(t), log rho_caras(t).
j=9: c20−c10, base barata u20. j=10: c30−c20, base barata u30.
Delta es incremento por diez updates, sin dividir por diez; esa división positiva
no cambiaría D ni p. No hay candidato adicional ni búsqueda posterior de tiempos.

Para cada candidato, B(t)=[pérdida train, pérdida panel, precisión panel, X(t)]
**lineal**, todo centrado dentro del split. X=max_n log(1−p_y_n), por logsumexp.
No hay base cúbica: se reutiliza la maquinaria D_cv, no la base log-rho de C1.
Se escalan columnas centradas por su RMS para estabilidad; registrar escala y
pendiente en unidades originales. Columnas exactamente constantes se conservan
como cero; OLS con rcond=None/SVD resuelve el rango. Ningún término no lineal nuevo.

## Estimando y agregación

D=1−SSE(B+candidato)/SSE(B), fuera de muestra, como C1. Diez bloques de splits:
default_rng(260010).permutation(splits), posición mod10. OLS sin intercepto tras
centrado; no entrenar redes. Permutar sólo candidato dentro del split, 2.000
veces, RNG default_rng(320001+j), reiniciada en cada conjunto analizado.
p=(1+#{D_perm≥D−1e-15})/2001, cola superior, sin truncar D negativo.
Se guardan todos los D nulos y SSE. Mantener empates con la holgura de C1.

Tres análisis por nivel (500 filas/100 splits) y uno agregado (1.500 filas).
En agregado, centrar/permutar dentro de (nivel,split), cinco inicializaciones;
los TRES niveles del MISMO split quedan siempre en el MISMO bloque. No tratar
300 paneles emparejados como 300 splits independientes. Pooled OLS usa pendientes
comunes, peso igual por fila/nivel. Reportar que es un estimando distinto al de nivel.

Por cada uno de los tres desenlaces se reportan las once D/p por nivel y agregado
(132 celdas en total). Controles por celda: D_base=1−SSE(B)/SSE(0), y
D_candidato_solo=1−SSE(candidato)/SSE(0), mismos bloques. Sin p selectivas adicionales
para controles. Comparar signo de pendiente completa en mitades de split par/impar,
recentradas por los mismos grupos; registrar además D de cada mitad descriptivamente.

Se podrá usar FWL vectorizado para las permutaciones SI coincide con las funciones
C1 intactas en controles artificiales: |D diferencia|≤1e-10, p idéntica para misma
semilla, SSE relativo≤1e-10. Comprobar todos los D nulos de al menos cuatro tablas
(2.000 permutaciones) contra un OLS independiente y muestras contra D_cv original.
Si una columna es aliada de B (residuo relativo≤1e-10), marcar NO_IDENTIFICABLE;
no promoverla. Permutaciones con alias se resuelven con OLS directo, sin inventar p.

## Compuertas y reglas anteriores a medir

Validar IDs únicos y universo planificado. Dominios: cantidades finitas, tr M>0,
rho>0, Y definido. No reemplazar estados ni errores. Por candidato/desenlace,
INCONCLUSIVE si >5% de filas previstas inválidas, <80% de splits con≥3 filas,
o tras mantener splits válidos quedan <95% de filas previstas; conservar conteos.
Alias, candidato centrado sin variación (atol1e-8) o Yc sin varianza: NO_IDENTIFICABLE,
sin p inventada. Fallo de control/reproducción: corrida INVALIDA, conservar todo.
Todas las salidas desconocidas permanecen desconocidas.

**Regla para proponer al responsable**, exclusivamente pérdida test250, s=.8:
D>.02 Y p<.05/12 Y pendientes de mitades par/impar no nulas y mismo signo
(también consistente con la pendiente completa), con compuertas válidas.
Veredicto PROPONER_CONFIRMATORIO_EXPLORATORIO si alguno cumple; si ninguno válido
cumple: NINGUNO_CUMPLE_REGLA (no demostrar efecto cero); si controles o datos
insuficientes: INCONCLUSIVE. El responsable decide si confirma y con qué cohorte.

s=.25/.5 y agregado se reportan completos con D/p/signos y umbral de referencia,
pero no rescatan un fallo en s=.8, ni amplían la familia primaria. No seleccionar
personas por colapso. Secundarios no alteran la regla ni sirven para elegir ganador.

Predicción exploratoria: si el colapso contiene información residual sobre la
memorización/generalización, al menos un candidato superará la regla en s=.8.
Si las medidas geométricas sólo reexpresan confianza ya capturada por B, no lo hará.
No se fija un signo de promoción: c alto podría indicar concentración en un difícil
que perjudique test o sólo incertidumbre; la estabilidad de signo se evalúa como
se pidió. Ningún resultado se fuerza a una interpretación causal.

## Conservación y límites

Registrar entorno/tiempos y SHA antes de ejecutar. Dos procesos, un hilo BLAS/Torch;
presupuesto total 14.400s. Si se agota, conservar faltantes, no cambiar presupuesto
por resultado. Código → controles → medición → análisis, cada salida exclusiva.
Cualquier defecto: conservar versión/fallo, enmienda congelada ANTES de corregir.
Sólo D9g se modifica; arrays fuera de Git. No escribir a C2 ni acceder a sus datos.

La identidad M=R(F+gamma I)^−1R^T y su dependencia de gradientes son algebraicas.
La predicción temporal de TEST es un hallazgo empírico potencial, no identidad.
Sólo mejora sobre esta base LINEAL, no sobre toda función de medidas baratas;
no causalidad, no transferencia, no resultado confirmatorio ni riesgo exacto.
El centrado del desenlace usa la media de cada split completo; el estimando mide
variación entre inicializaciones, no un predictor desplegable sin esa información.

[Progreso previo](progress_00.md), [plan gemelo con errata](sources/PLAN_D9_generalizacion_c5cea08.md),
[cierre C2, sólo contexto](sources/CIERRE_DIN_C2_v1_CONGELADO.md).
