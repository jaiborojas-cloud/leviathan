# DIN-D9g — conclusión exploratoria

**PROPONER_CONFIRMATORIO_EXPLORATORIO**: proponer **c(u30)** al responsable para un confirmatorio; no se ejecuta ni se congela ese confirmatorio aquí.

En G3, s=.8, c(u30) añade predicción de la pérdida test250 sobre la base LINEAL de pérdida train30, pérdida y precisión panel30 y X30. D=0.021854, p exploratorio=0.0009995 (<.05/12), con pendiente negativa en ambas mitades prefijadas. Es una reducción del **2.185% del SSE restante de la base**, dentro de la variación entre inicializaciones del mismo split. No es una reducción del 2.185% de la pérdida test ni una confirmación de la hipótesis.

La pendiente ajustada es −0.040886 por unidad de c: a medidas baratas fijas, mayor concentración se asocia a MENOR pérdida test; no se afirma que inducir colapso mejore la generalización. Sin base, c30 tiene D=−0.000885. El hallazgo es condicional a ese ajuste, no una asociación marginal ni información nueva sobre toda función de las medidas baratas.

## Primaria completa: s=.8, pérdida test250

100 splits×5 inicializaciones, 500/500 filas; once candidatos, sin exclusiones.

| Candidato | Base en u | D adicional | p exploratorio | β par | β impar | ¿regla completa? |
|---|---:|---:|---:|---:|---:|---|
|c_10|10|-0.008393|0.971514|-0.037018|0.152980|no|
|log_trace_10|10|-0.006772|0.881559|0.040067|0.038852|no|
|log_rho_caras_10|10|-0.000246|0.206397|-0.002666|-0.042871|no|
|c_20|20|0.012246|0.011994|-0.067788|-0.033634|no|
|log_trace_20|20|-0.010950|0.983508|-0.014347|0.004905|no|
|log_rho_caras_20|20|-0.017203|0.999500|-0.027222|0.019149|no|
|c_30|30|0.021854|0.001000|-0.041102|-0.042509|sí|
|log_trace_30|30|-0.011288|0.989505|-0.008894|0.001609|no|
|log_rho_caras_30|30|-0.016436|1.000000|-0.017552|0.009101|no|
|delta_c_10_20|20|0.005943|0.041479|-0.049892|-0.034940|no|
|delta_c_20_30|30|-0.000144|0.197401|-0.008686|-0.014378|no|

La regla anterior a medir exige D>.02, p<.05/12 y el mismo signo en mitades par/impar (y ajuste completo). Sólo c30 la cumple en s=.8. **Errata resuelta ANTES del código:** eran 11, no 12; el responsable conservó /12 y prohibió añadir Δc10→30, suma de los otros dos incrementos.

## Estabilidad y controles de c30 en s=.8

- Base barata sola frente a cero: D_base=0.075126.
- c30 solo frente a cero: D_solo=-0.000885.
- Pendiente completa=-0.040886; pares=-0.041102, impares=-0.042509.
- D adicional en mitades: pares=0.009146, impares=0.010758. Las mitades no superan .02; la regla exige estabilidad de SIGNO, no ese umbral en cada mitad.
- 2.000 permutaciones dentro del split, p con corrección +1 y empates 1e-15; no se repitieron semillas ni se buscaron particiones.

## Otros niveles y agregado, descriptivos

| Conjunto | D c30 | p | β | candidatos que cumplen el umbral de referencia |
|---|---:|---:|---:|---|
|s=.25|0.063287|0.000500|-0.013104|c_30|
|s=.5|0.048894|0.000500|-0.023200|c_20, c_30|
|s=.8|0.021854|0.001000|-0.040886|c_30|
|agregado|0.021345|0.000500|-0.025397|c_30|

s=.25/.5 y agregado no cambian la selección primaria. El agregado centra/permutan en (nivel,split) y bloquea por split compartido, sin tratar 300 paneles emparejados como 300 splits independientes. Tiene pendientes comunes y no sustituye las estimaciones por nivel. La presencia descriptiva de c30 también en niveles que G3 no clasificó como colapso no prueba necesidad del régimen.

## Desenlaces secundarios, c30 en s=.8

| Desenlace | D adicional | p exploratorio | β |
|---|---:|---:|---:|
|pérdida test (primario)|0.021854|0.001000|-0.040886|
|precisión test|0.020305|0.001000|0.007852|
|brecha test−train|0.021859|0.001000|-0.040893|

Los secundarios no deciden. Se conservan las 132 celdas y ambos controles D para todos los candidatos, incluso negativos o desconocidos, en [estimates.csv](results/run_v1/estimates.csv); [salida completa](results/run_v1/analysis.json). No se elige un desenlace tras medir.

## Controles, datos y conservación

Se restauraron 7.500 checkpoints de 1.500 trayectorias G3; **error máximo de reproducción 0** en pérdida/precisión train/panel y X. 300 test de 3.000 ejemplos (1.000/clase), seeds711000..711099, normalización exclusivamente train archivada; ruido test emparejado entre niveles. No reentrenamiento ni nueva medición de rho: se reutilizan G3 y r3 intactos.

Controles FWL: cuatro tablas, todos los D de 2.000 permutaciones contra OLS directo; p idéntica, errorD máximo1.11e-15; contraste adicional con D_cv C1 original. Casos de alias/constante identificados; guarda bloquea C2/T2 antes de leer. [verification.json](verification.json): **PASS**, 9748 archivos externos por SHA, 1.500 registros reversibles y 132 celdas. No hubo fallos ni enmiendas de implementación.

Se conservan todos los logits/pérdidas test por ejemplo, test sintético, pesos originales por referencia/SHA, datos, escalares, D nulos/SSE completos, metadatos y tiempos. Arrays fuera de Git: [manifest externo](external_manifest.csv); los [shards](results/run_v1/record_shards/) restauran bit por bit sin borrar originales.

## Demostración, evidencia y siguiente paso

La construcción algebraica M=R(F+γI)^−1Rᵀ y los residuos de confianza son identidades del instrumento. La relación ajustada de c30 con TEST es evidencia empírica exploratoria; no se deduce de esas identidades. El test grande sigue siendo una muestra finita, compartida entre las cinco inicializaciones de cada split; se guardan errores estándar descriptivos estratificados. El centrado de Y usa la media final del split completo: mide variación entre inicializaciones, no un predictor desplegable sin esas medias.

Proponer al responsable un diseño confirmatorio específico para **c30 + base barata u30 → pérdida test250**, con signo ajustado esperado negativo. Fijar antes tamaño/potencia, semillas de test, estimando y script; no usar D observado sin descontar selección exploratoria. **C2 permanece intacta y reservada** como posible cohorte: no se abrió ningún estado/checkpoint/tabla de C2 ni se calculó su test o asociación. La decisión de cohorte y de congelación corresponde al responsable.

No se afirma causalidad, necesidad del colapso, mejora sobre bases flexibles, certificado geométrico ni transferencia a Wine/Iris/datos reales. La corrección /12 sólo rige la regla primaria fijada; el resto es descriptivo, no una familia confirmatoria nueva. No se calculó potencia prospectiva de D9g; la potencia G3 era de otro estimando y no se transfiere. El efecto observado D=.02185 supera por poco .02; requiere réplica independiente.

[Diseño](DESIGN_FROZEN.md) · [configuración](config.json) · [teoría](THEORY.md) · [reproducción](REPRODUCCION.md).
