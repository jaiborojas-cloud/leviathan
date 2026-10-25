# DIN-D2c · conclusión de la auditoría independiente

**El script reproduce el estadístico D del diseño v2, pero recomiendo corregir
la validación de cohorte y el manejo numérico antes de congelarlo.**
No se modificó C1 ni se tomó la decisión de congelación.

| Pregunta | Veredicto | Lo establecido |
|---|---|---|
| A1 revisión contra diseño | FAIL | Núcleo correcto; denominadores y entradas permiten decisiones inválidas o crashes |
| A2 referencia independiente | PASS | Descubrimiento+24 tablas sintéticas+7 controles del autor; D≤1.07e-14 y p operativo idéntico |
| A3 controles/adversarios | FAIL | Cohortes incompletas/duplicadas pueden dar PASS; casos numéricos sin informe; contraejemplo de cuerda |
| A4 tamaño y potencia | PASS al alcance congelado | Sin inflación detectada en nulos válidos estudiados; potencia compatible con §6 dentro de incertidumbre |
| A5 recomendación | PASS_DESCRIPTIVE | Lista de cambios necesarios y opcionales; decide el responsable |

Sujeto exacto: `6b17d25216381238f5a0f38f8eb9e7eb87f0a4da` de la rama
claude/din-confirmatorio-diseno. No se certifica una versión posterior.
[Resumen](results/run_v1/summary.json) · [Verificación](verification.json).

## A1 y A3 · defectos reproducidos

**D01, pérdida del universo planificado.** c1_cohorte.py125 elimina de la
tabla final las trayectorias con error. analisis_C1_v1.py102/107/111–112 calcula
faltantes y splits sobre la tabla recibida. El hash autentica esa tabla, pero
no garantiza que contenga las780 trayectorias/156 splits previstos.

| Entrada sintética al CLI ORIGINAL,5000/BW20000 | Resultado | ¿Cumple contrato? |
|---|---|---|
|780 filas completas, señal fuerte | PASS | Sí |
|47 de780 filas marcadas con error | INCONCLUSIVE | Sí |
|Las mismas47 filas omitidas; quedan733 | **PASS**,0 faltantes contados | **No**,faltan6.03% de las planificadas |
|40 de156 splits omitidos; quedan116 | **PASS**,116/116 válidos | **No**,sólo74.36% del universo planificado |
|Cada fila/ID duplicado;1560 filas | **PASS** | **No**,no son1560 trayectorias independientes |
|39 errores explícitos (5% exacto) | PASS | Sí |
|40 errores explícitos (>5%) | INCONCLUSIVE | Sí |
|Compuerta falsa o ausente | INCONCLUSIVE | Sí |
|X constante o sólo entre splits | INCONCLUSIVE | Sí |
|Todos los splits con2 filas / tabla vacía | INCONCLUSIVE | Sí |

Los casos son totalmente sintéticos; la compuerta PASA de prueba es un fixture,
no prueba de reproducción de una red. [17 casos CLI](results/run_v1/A3_CLI.csv).

**D02, dominio del log:** rho0 y negativa pasan el filtro de finitud previo,
generan inf/nan y el proceso termina con LinAlgError sin RESULTADO_C1.
Una política corregida puede contarlas como faltantes y aplicar el5%:
no se exige arbitrariamente INCONCLUSIVE por un único dato inválido.
**D03:** L constante falla en normalización/OLS; Y constante divide por SSEbase0.
El estado científico para degeneraciones debe fijarse; el crash está demostrado.
Todos los stdout/stderr y códigos de salida se conservan.

**D04, cuerda:** la función de cohorte50–55 sólo contempla vértices y pares
de vértices. Con26 de27 puntos en una cara y M=e0e0ᵀ+1e-12I (SPD), devuelve
.037037037043, mientras un rayo concreto al borde tiene longitud
.001424501425. Es26 veces mayor y NO puede ser una cota inferior.
No se deduce que el panel Wine tenga esa degeneración: no se leyó su f.
[Caso y SHA](results/run_v1/chord_face26.json) ·
[Aclaración del rango de líneas del JSON](ERRATAS_METADATA.md).

[Revisión completa con líneas, OK/AMBIGÜEDAD/DEFECTO](A1_REVISION_LINEA_POR_LINEA.md).

## A2 · independencia y reproducción numérica

La referencia propia sólo importa NumPy; no llama ni importa el sujeto.
Usa centrado por acumulación de grupos, SVD explícita y una versión FWL por
lotes contrastada con la explícita. El sujeto original se ejecutó intacto en
proceso separado. Semillas y flujo de permutaciones coinciden; no se parcheó
el script para acelerar Monte Carlo.

32/32 comparaciones PASS: descubrimiento con5000 permutaciones;31 pruebas
con199 (24 enteramente sintéticas y7 controles que transforman descubrimiento).
Máximo |Delta D|1.0658e-14, contra tolerancia1e-10. Máximo error de D por FWL
observado1.2213e-14; en nulos comparados con SVD explícita1.8297e-13.
p operativo idéntico; tampoco hubo discrepancias respecto a p literal >=D.
El código usa >=D−1e-15: queda como ambigüedad documental, no fallo observado.

La unión autorizada dio780 trayectorias,156 splits, sin ausencias/duplicados.
X/L vienen de d6u10; Y de d1u250. [Procedencia](results/run_v1/discovery_provenance.json).
En descubrimiento: D=.0776678038308447, p=1/5001=.0001999600,
pendiente1.1621966673. D/pendiente reproducen §6; el p publicado.002 usó
500 permutaciones y era el mínimo posible1/501. Esto NO es confirmación.
[Tabla de comparaciones](results/run_v1/A2_comparisons.csv).

## A3 · alcance de los adversarios estadísticos

X=L, X cúbica y Y_g_L con X afín dieron NOT_MET; X constante INCONCLUSIVE;
L con error e incremento real dieron PASS. El control ruido del autor tuvo
D=.01007,p=.005 pero pendiente negativa: NOT_MET por la regla conjunta.
Las magnitudes de algunos controles difieren de §6 (con semilla1 y nuestro
orden de filas, D errorL=.6268 e incremento r=.3=.05405); sus clasificaciones
coinciden. §6 no fija semillas/orden de esos controles, por lo que no se
atribuye esa diferencia a un defecto de implementación.

Nuevas pruebas de heterocedasticidad por split,3–4 trayectorias, outlier en L,
empates masivos de X y dependencia sólo entre splits no produjeron PASS
espurio en las dos semillas prefijadas. Dos semillas no certifican un tamaño.
El escenario de empates prueba80% de valores repetidos, no vuelve a calcular
X desde p saturadas; la fórmula logsumexp de cohorte se revisó estáticamente.

**Escalón, log y seno dieron PASS en6/6 casos con X=h(L).** No hay información
condicional nueva dado L; sí una mejora REAL respecto a la clase cúbica usada.
Los D fueron≈.858–.877,.400–.497 y.925–.927. Por ello no los llamamos falsos
positivos de ese estimando limitado ni prueba de una tautología temporal.
No se observó un PASS con D≤0. Las réplicas nulas de A4 tienen falsos
positivos estocásticos esperables, sin una inflación demostrada.

## A4 · calibración y potencia con incertidumbre

400 réplicas POR fila,156 splits×5 remuestreados,199 permutaciones por réplica.
Regla exacta de signo/p del diseño. Intervalos Wilson95%:

| Escenario | PASS/n | Tasa | IC95% |
|---|---:|---:|---:|
|N0 X independiente, bootstrap del descubrimiento |3/400 |0.75% |0.26–2.18% |
|N1 X dependiente de L, Y cúbica correcta |6/400 |1.50% |0.69–3.23% |
|N2 X/Y con heterocedasticidad independiente por split |6/400 |1.50% |0.69–3.23% |
|Potencia r=.10 |289/400 |72.25% |67.67–76.41% |
|Potencia r=.15 |386/400 |96.50% |94.21–97.90% |

N0/N2 son nulos de intercambiabilidad estudiados: no hay inflación al alcance
de la regla previa (límite superior≤7.5%). N1 es una prueba descriptiva de
nulo condicional correcto; permutar X no es en general una prueba exacta
de independencia condicional cuando X depende de L.

Las tasas son conservadoras frente a5%. Un D que detecta asociación de ambos
signos MÁS un requisito de pendiente positiva no necesariamente tiene tamaño
5%; bajo simetría puede acercarse a2.5%, con discreción adicional. No se
ajusta ningún umbral para obtener una tasa deseada.

Los intervalos se solapan con las pruebas pequeñas de §6:4/96 de nulo,
≈22/32 de potencia.10 y32/32 de potencia.15. «1.00» en32 semillas no prueba
potencia100%; nuestro96.5% es compatible con esa incertidumbre. r es parámetro
del generador X=r e/std(e)+sqrt(1-r²)ruido; correlaciones realizadas medias
.09780 y.14837. e usa el Y completo remuestreado: potencia RETROSPECTIVA de
ese generador, no garantía prospectiva sobre la nueva cohorte.

Se ejecutaron además réplicas0–4 de N0 y cada potencia con5000 permutaciones:
15/15 conservaron clasificación. No equivale a400 réplicas con5000.
[Tasas](results/run_v1/A4_rates.csv) · [simulaciones completas](results/run_v1/monte_carlo.jsonl).

## A5, integridad y límites

[Cambios necesarios y opcionales](RECOMENDACION_ANTES_DE_CONGELAR.md):
manifest de780 IDs/156 splits, filas fallidas retenidas, validación previa de
logs/degeneraciones, y resolución de la precondición de cuerda. Precisar el
nulo y el alcance «base cúbica» antes de congelar.

Diseñoa6ad5d0 → código0f22130 → mediciones; postproceso09c1b1a.
Tiempo153.74s, dos procesos, BLAS/OMP1. No hubo errores de ejecución propios,
exclusiones o sustituciones; los4 crashes son casos del sujeto auditado.
Se conserva la errata de metadatos de líneas sin reescribir el retorno.
Datos T2 permitidos: sólo los dos CSV publicados; no estados/checkpoints,
entrenamiento, core, geometry ni rho. No se repitió una compuerta real.
No se cambió ningún archivo fuera de D2c ni ningún estado previo.
