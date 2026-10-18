# Leviathan / RIPG — E15-B7: validación externa del protocolo mesh-independent

Fecha: 24 septiembre 2026.

## Decisión

**Wine split 5 / j=0 / true: PASS. Wine split 6 / j=0 / random: PASS.** Ambos casos satisfacen la convergencia interna y las seis compuertas multifuente congeladas. El protocolo pasa la validación externa numérica en estos dos estados adicionales. Se habilita y se ejecuta B8 por autorización condicional del usuario.

"Externa" significa fuera del caso primario split 6 true; no constituye una validación estadística ciega, en otro dataset o arquitectura. B6 ya contenía exploración a 512 rayos de estos estados; B7 ejecuta las seis fuentes globales a 2048 como se pidió.

## Integridad, protocolo y referencia

- ZIP original descomprimido en una nueva carpeta: 28/28 hashes y tamaños del manifest principal; 16/16 hashes de checkpoints correctos.
- Checkpoints, semillas, índices de panel, escaladores y pesos originales. No se reentrenó ningún modelo.
- `geometry.py` y `adaptive.py` se recuperaron del ZIP persistente de B6, se verificaron por SHA-256 y permanecen sin cambios.
- Protocolo fijado en `protocol_frozen_B7_B8.json` antes de ejecutar B7. Regla de refinamiento, observables, tolerancias y clasificación no cambiaron tras abrir resultados.
- Referencia B6: split 6 true, seis fuentes con contorno común 2048, dispersión 0.001025%; auditoría representativa 8192, C_A=1052.60819. No se mezcla este último valor con las medianas multifuente a 2048.
- Los valores históricos B4/B5 ≈1362 y ≈1894 no son muestras de incertidumbre estadística: permanecen como estimaciones históricas afectadas por aliasing/subresolución.

## Método y compuertas congeladas

Para cada estado se construye su propio disco geodésico completo de área 0.02, con el campo exacto RIPG y sin jets ni surrogates. El mismo contorno de 2048 rayos y el mismo radio se conservan en las seis fuentes de ese estado. Las fuentes cambian los puntos interiores: 64×32, 96×48 y 128×64, con fase 0 y π/n. No son seis entrenamientos ni seis réplicas estadísticas independientes.

Geodésicas DOP853, rtol=2e-10, atol=2e-12. Calibración de radio mediante Brent (xtol=1e-13) y cuadratura de área Dunavant de grado cinco con 32 anillos radiales. Se verifica |A/0.02−1|≤1e-6. Cada triangulación espacial debe cubrir exactamente el mismo polígono, sin triángulos que crucen su borde.

Refinamiento B6 sin cambios: comparar cada padre con sus cuatro hijos; refinar padres que reúnen 80% del error local normalizado. Dos rondas consecutivas deben cumplir error estimado de energía <0.0005, cambio relativo de C_A <0.0005 y cambio de concentración <0.001. Se mantienen 18 rondas y la comprobación del límite de 1.2 millones de celdas al final de cada ronda; una ronda puede sobrepasar ese límite.

**Compuerta primaria multifuente:** (máximo C_A−mínimo C_A)/mediana C_A <0.005. Se calcula sólo tras disponer de las seis fuentes válidas; no se infiere a partir del error interno.

Compuertas espaciales originales B6: rango absoluto de Λ₁% y Λ₀.₁% <0.005; rango absoluto de f₅₀ y f₉₀ <1e-5; rango relativo de R_eff <0.005. PASS exige que todas pasen y que las seis fuentes hayan convergido internamente. Falta de fuentes, excepción numérica o agotamiento sin convergencia implica INCONCLUSIVE; seis fuentes convergidas que incumplan una compuerta implican FAIL.

Definiciones: C_A=√(∫K²dA/∫dA); Λ_q acumula energía en el q de **área intrínseca** de mayor K²; f₅₀/f₉₀ son fracciones mínimas de área; R_eff=(∫K²dA)²/(A∫K⁴dA). Se usa interpolación parcial de la celda del cuantíl. No se reemplazan por fracciones de número de celdas. CV=desviación estándar poblacional entre fuentes (ddof=0)/media; es dispersión numérica descriptiva, no error estadístico.

## Wine / split 5 / j=0 / true: PASS

Checkpoint SHA-256: `cbac77c796486b1ea232923b0a966248a0defe18eeb8219602bf4867059adc9a`. Semillas split/init/batch: 1005/2000/4050; random labels: None. Paso guardado: 25. Radio común: 0.079799540273847.

### Seis fuentes: C_A y errores de área

| Fuente | Fase (rad) | C_A | A por centroides | (A−0.02)/0.02 | Convergencia interna |
|---|---|---|---|---|---|
| 64x32_phase0 | 0 | 36.7529088699 | 0.0200003224698 | 1.61234908385e-05 | 1 |
| 64x32_phase1 | 0.0490873852123 | 36.7528707116 | 0.0200003445485 | 1.72274254691e-05 | 1 |
| 96x48_phase0 | 0 | 36.7533543531 | 0.0200001665456 | 8.32727939226e-06 | 1 |
| 96x48_phase1 | 0.0327249234749 | 36.7532900443 | 0.0200001847223 | 9.23611712e-06 | 1 |
| 128x64_phase0 | 0 | 36.753105768 | 0.0200001639759 | 8.19879409542e-06 | 1 |
| 128x64_phase1 | 0.0245436926062 | 36.7532177867 | 0.0200001620433 | 8.10216416647e-06 | 1 |

### Seis fuentes: concentración por área

| Fuente | Λ₁% | Λ₀.₁% | f₅₀ | f₉₀ | R_eff |
|---|---|---|---|---|---|
| 64x32_phase0 | 0.608588245707 | 0.142481626882 | 0.0067005662018 | 0.0324517451994 | 0.0185019313334 |
| 64x32_phase1 | 0.608583652762 | 0.142483377444 | 0.00670076868575 | 0.0324514993858 | 0.0185015728603 |
| 96x48_phase0 | 0.608590553536 | 0.142492572082 | 0.00670057091104 | 0.032452581949 | 0.0185012456461 |
| 96x48_phase1 | 0.608590649515 | 0.142494469173 | 0.00670057294403 | 0.0324526954053 | 0.0185009950345 |
| 128x64_phase0 | 0.608588294188 | 0.142493359416 | 0.00670077057024 | 0.0324522608974 | 0.0185017506224 |
| 128x64_phase1 | 0.608589234734 | 0.142473505961 | 0.0067007452781 | 0.0324522944614 | 0.0185012980014 |

### Estadísticas entre fuentes

| Estimando | Mediana | Mínimo | Máximo | Rango relativo | CV |
|---|---|---|---|---|---|
| C_A | 36.7531617773 | 36.7528707116 | 36.7533543531 | 1.31591828835e-05 | 4.9700102029e-06 |
| lambda_1pct | 0.608588764461 | 0.608583652762 | 0.608590649515 | 1.14966856415e-05 | 3.85102282492e-06 |
| lambda_01pct | 0.142487974763 | 0.142473505961 | 0.142494469173 | 0.000147122673346 | 5.35849101212e-05 |
| frac50 | 0.00670065911107 | 0.0067005662018 | 0.00670077057024 | 3.04997516945e-05 | 1.43436351843e-05 |
| frac90 | 0.0324522776794 | 0.0324514993858 | 0.0324526954053 | 3.68547178649e-05 | 1.31888372489e-05 |
| R_eff | 0.0185014354309 | 0.0185009950345 | 0.0185019313334 | 5.06068231972e-05 | 1.71992540412e-05 |

### Compuertas

| Estimando | Dispersión evaluada | Umbral | Resultado |
|---|---|---|---|
| C_A | 1.31591828835e-05 | 0.005 | PASS |
| lambda_1pct | 6.99675370996e-06 | 0.005 | PASS |
| lambda_01pct | 2.09632117668e-05 | 0.005 | PASS |
| frac50 | 2.04368439077e-07 | 1e-05 | PASS |
| frac90 | 1.19601953795e-06 | 1e-05 | PASS |
| R_eff | 5.06068231972e-05 | 0.005 | PASS |

Dispersión primaria en porcentaje: **0.001315918288%**. Las seis fuentes convergieron internamente: **True**.

Área del contorno por la cuadratura de calibración: 0.02; error relativo 0. La tabla anterior informa por separado el error de la suma de áreas del integrador de centroides. No se ajustó el radio por fuente.

SPD: menor autovalor observado 0.00042813099; máxima condición observada 131.547466. Cero métricas no positivas/no finitas, cero singularidades reportadas y cero excepciones de integración. El control evalúa cada G usado por la rutina de geometría; no es una garantía analítica global fuera de esos puntos.

Coste por caso: 72.801 s de pared, 72.750 s de CPU, pico RSS 473.84 MiB. Tiempo de construcción/calibración del disco: 44.090 s. Los casos se ejecutaron con dos procesos de un hilo; sus tiempos de pared se solapan.

| Fuente | Rondas (índice final) | Celdas finales | Tiempo pared (s) | CPU (s) | Error energía interno | Último cambio C_A |
|---|---|---|---|---|---|---|
| 64x32_phase0 | 4 | 92824 | 3.195728166 | 3.191241266 | 0.000173030219878 | 3.46358076653e-05 |
| 64x32_phase1 | 4 | 90328 | 2.992608481 | 2.991495107 | 0.000173221967294 | 3.55432229184e-05 |
| 96x48_phase0 | 4 | 181856 | 5.232690846 | 5.224838515 | 8.29414903771e-05 | 1.6897399884e-05 |
| 96x48_phase1 | 4 | 162824 | 4.917962446 | 4.915933384 | 9.37221007119e-05 | 1.88780543908e-05 |
| 128x64_phase0 | 3 | 133208 | 4.690930505 | 4.686191637 | 0.000154729676212 | 2.44726425485e-05 |
| 128x64_phase1 | 3 | 138068 | 6.259627261 | 6.25409672 | 0.000136709889387 | 2.10039240074e-05 |

## Wine / split 6 / j=0 / random: PASS

Checkpoint SHA-256: `c679ec2f396050e9da498f9a0de05bbcad4eea6b04284008e6984442ed89ba13`. Semillas split/init/batch: 1006/2000/4060; random labels: 3060. Paso guardado: 125. Radio común: 0.079788518607098.

### Seis fuentes: C_A y errores de área

| Fuente | Fase (rad) | C_A | A por centroides | (A−0.02)/0.02 | Convergencia interna |
|---|---|---|---|---|---|
| 64x32_phase0 | 0 | 2.66182701644e-06 | 0.0200000000006 | 3.02902147808e-11 | 1 |
| 64x32_phase1 | 0.0490873852123 | 2.66182701654e-06 | 0.0200000000006 | 2.99960056793e-11 | 1 |
| 96x48_phase0 | 0 | 2.66182702477e-06 | 0.0200000000003 | 1.37319045024e-11 | 1 |
| 96x48_phase1 | 0.0327249234749 | 2.66182702475e-06 | 0.0200000000003 | 1.38267175487e-11 | 1 |
| 128x64_phase0 | 0 | 2.66182702772e-06 | 0.0200000000002 | 7.8852480101e-12 | 1 |
| 128x64_phase1 | 0.0245436926062 | 2.66182702774e-06 | 0.0200000000002 | 7.84150522293e-12 | 1 |

### Seis fuentes: concentración por área

| Fuente | Λ₁% | Λ₀.₁% | f₅₀ | f₉₀ | R_eff |
|---|---|---|---|---|---|
| 64x32_phase0 | 0.0104281384224 | 0.00104413694754 | 0.490567816109 | 0.896275298755 | 0.999506093605 |
| 64x32_phase1 | 0.010428139878 | 0.00104413742829 | 0.490567828681 | 0.896275285901 | 0.999506093673 |
| 96x48_phase0 | 0.0104281941998 | 0.00104418480361 | 0.490567745714 | 0.896275242863 | 0.999506082101 |
| 96x48_phase1 | 0.0104281986355 | 0.00104418544419 | 0.490567744852 | 0.896275240438 | 0.999506082005 |
| 128x64_phase0 | 0.0104282100506 | 0.00104419559272 | 0.4905677207 | 0.896275222653 | 0.999506077924 |
| 128x64_phase1 | 0.010428210526 | 0.00104419484869 | 0.490567720886 | 0.89627522268 | 0.999506077953 |

### Estadísticas entre fuentes

| Estimando | Mediana | Mínimo | Máximo | Rango relativo | CV |
|---|---|---|---|---|---|
| C_A | 2.66182702476e-06 | 2.66182701644e-06 | 2.66182702774e-06 | 4.24298450916e-09 | 1.78621755032e-09 |
| lambda_1pct | 0.0104281964176 | 0.0104281384224 | 0.010428210526 | 6.91429190636e-06 | 2.95549655136e-06 |
| lambda_01pct | 0.0010441851239 | 0.00104413694754 | 0.00104419559272 | 5.61635830615e-05 | 2.42458907808e-05 |
| frac50 | 0.490567745283 | 0.4905677207 | 0.490567828681 | 2.20114319066e-07 | 8.85627647318e-08 |
| frac90 | 0.89627524165 | 0.896275222653 | 0.896275298755 | 8.49092876363e-08 | 3.30763665855e-08 |
| R_eff | 0.999506082053 | 0.999506077924 | 0.999506093673 | 1.57571263345e-08 | 6.65058943404e-09 |

### Compuertas

| Estimando | Dispersión evaluada | Umbral | Resultado |
|---|---|---|---|
| C_A | 4.24298450916e-09 | 0.005 | PASS |
| lambda_1pct | 7.21035940884e-08 | 0.005 | PASS |
| lambda_01pct | 5.86451779378e-08 | 0.005 | PASS |
| frac50 | 1.07980985209e-07 | 1e-05 | PASS |
| frac90 | 7.61020922946e-08 | 1e-05 | PASS |
| R_eff | 1.57571263345e-08 | 0.005 | PASS |

Dispersión primaria en porcentaje: **4.242984509e-07%**. Las seis fuentes convergieron internamente: **True**.

Área del contorno por la cuadratura de calibración: 0.02; error relativo 0. La tabla anterior informa por separado el error de la suma de áreas del integrador de centroides. No se ajustó el radio por fuente.

SPD: menor autovalor observado 916.20912; máxima condición observada 5.0327783. Cero métricas no positivas/no finitas, cero singularidades reportadas y cero excepciones de integración. El control evalúa cada G usado por la rutina de geometría; no es una garantía analítica global fuera de esos puntos.

Coste por caso: 51.592 s de pared, 51.573 s de CPU, pico RSS 467.87 MiB. Tiempo de construcción/calibración del disco: 18.907 s. Los casos se ejecutaron con dos procesos de un hilo; sus tiempos de pared se solapan.

| Fuente | Rondas (índice final) | Celdas finales | Tiempo pared (s) | CPU (s) | Error energía interno | Último cambio C_A |
|---|---|---|---|---|---|---|
| 64x32_phase0 | 2 | 104980 | 2.381921149 | 2.379441486 | 3.420075844e-08 | 8.57467785664e-09 |
| 64x32_phase1 | 2 | 105064 | 2.45561536 | 2.455409085 | 3.39746267411e-08 | 8.51721737583e-09 |
| 96x48_phase0 | 2 | 216080 | 4.984207124 | 4.980983436 | 1.54858237785e-08 | 3.88204357549e-09 |
| 96x48_phase1 | 2 | 215996 | 4.855549347 | 4.855337962 | 1.55259882178e-08 | 3.89218168806e-09 |
| 128x64_phase0 | 2 | 370700 | 8.318066335 | 8.314101766 | 8.83547441541e-09 | 2.21487694851e-09 |
| 128x64_phase1 | 2 | 370964 | 8.27288006 | 8.272362065 | 8.81019676269e-09 | 2.20859619482e-09 |

## Excepción operativa y trazabilidad

Tras guardar ambas clasificaciones, la escritura de un booleano NumPy en el log produjo `TypeError: Object of type bool is not JSON serializable`. Se corrigió únicamente la serialización del log y se añadió un recibo explícito de hashes para verificar ese parche del ejecutor. Se conservan el ejecutor previo, el log fallido y el recibo `operational_patch_receipt.json`. Los JSON numéricos ya guardados se reutilizaron. Ni el código de geometría/integración B6 ni las reglas de clasificación cambiaron. No se ocultó esta excepción como si no hubiera ocurrido; se distingue de un fallo numérico.

## Alcance de PASS y transición a B8

Los dos casos obligatorios pasan todas las compuertas, por lo que el protocolo se valida fuera de split 6 true **para estos checkpoints y para triangulaciones que comparten un contorno de 2048 rayos**. No demuestra invariancia frente a cualquier discretización del borde ni convergencia de todas las fuentes a 8192 rayos.

En split 5 true, la suma de áreas por centroides presenta errores relativos del orden de 8e-6 a 1.7e-5, mayores que el error de la calibración de alto orden. Se informan sin cambiar la tolerancia del integrador ni la definición de C_A. El PASS es el de las compuertas fijadas, no una afirmación de que toda suma de áreas por centroides tenga error ≤1e-6.

B8 se abre sólo después de guardar las dos clasificaciones PASS. Reutiliza estos dos estados y ejecuta los restantes 14 con el mismo protocolo. El estado B6 primario se recalcula a 2048 como comprobación adicional; el resultado representativo 8192 permanece separado. No se mezclan valores históricos B5 con la nueva reconstrucción para fabricar una población completa.
