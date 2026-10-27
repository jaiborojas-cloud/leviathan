# Auditoría independiente DIN-Q13-DR — diseño prospectivo

Objeto: borrador v1 y código de PR #103, commit e7dfc435ab97cdc8d24bba5d525b193af274f35f.
Se copian sus bytes como fuentes de lectura; ninguna modificación al diseño,
analista ni pruebas originales. Rama de auditoría desde main; PR aparte sólo con
adiciones en Q13DR/auditoria. No se lee Wine, C2 ni cohorte Q13 real.
No se ejecuta la suite original porque abre C2/fixtures/G3_trajectories.csv.

## Inspección y casos mínimos previstos

Registrar líneas del snapshot, diferencia entre contrato e implementación y
separar DEFECTO reproducible, AMBIGÜEDAD del diseño y OK. Revisar:
bootstrap pareado seis niveles, copias en bloque original, recálculo D/c/β;
medianas observadas frente a muestra común; IDs/faltantes/80%/dominios;
constancia de X/L, degeneración de L sólo en bootstrap; planes de niveles/dosis;
monotonía/igualdad/rango/precisión; Spearman con empates; reglas que se solapan.

Casos totalmente sintéticos, seed910100: tablas completas con señal fuerte,
faltantes al límite/exceso, pérdidas disjuntas y falta de inicializaciones comunes,
medianas en subconjuntos diferentes, X/L constantes, L casi constante por un split,
empates, límites exactos, precisión L1-L3 y L4-L5, dominio finito pero imposible,
planes cero/negativos/no enteros/niveles mal formados/dosis incorrectas. No se
adaptan umbrales del analista para obtener un fallo.

Un trazador en memoria registra argumentos sin cambiar cálculos: Q.D_punto y
pendiente se envuelven para verificar mismos splits, bloques y recálculo por
réplica. Toda alteración numérica simulada o control aislado se rotula; no se
presenta como ejecución íntegra. Casos CLI usan hashes reales de sus fixtures.

## Tamaño/potencia: semillas y celdas fijadas antes del código

Niveles c=[.86,.70,.61,.54,.42,.36], q=.001, acc=.93: compuerta válida y fija.
Cada réplica genera covariables nuevas; seis resultados con ruido normal
**independiente entre niveles**, compartiendo X/L por split como pareado.
Sin fixture/piloto real. X=-4+.25·Normal y L=Normal+.3·efecto de split.
Base cúbica centrada intra-split como C1; residuo de X tras la base normalizado a
varianza media1. Y_l=base·[.3,-.05,.02]+b_l·X_res+ruido centrado por split.
Varianza del ruido centrado esperada .8; b_l=sqrt(d_l/(1-d_l)·.8).
d_l=.02+β·(c_l−media(c)), salvo nulo0 donde todos son0. d es efecto poblacional
condicional del modelo, no el D_CV observado finito.

| Celda | N splits ×5 | β verdadero | d central | Réplicas |
|---|---:|---:|---:|---:|
| null_N200 |200|0|.02|400|
| null_N400 |400|0|.02|400|
| zero_N400 |400|0|0|200|
| positive_N400 |400|+.03|.02|200|
| negative_N400 |400|−.03|.02|200|

Semilla por réplica SeedSequence([910300,índice_celda,réplica]). Bootstrap2000,
seed860001; permutaciones5000, seed260001; bloques260010, como el nominal.
Las dosis c son constantes dentro del nivel en estas celdas: recalcular su
mediana en bootstrap equivale exactamente al valor fijado. Casos aparte con c
variable verifican que el código sí las recalcula.

Se acelera el álgebra, sin modificar estimando ni tamaños: FWL para permutaciones
y productos cruzados ponderados por multiplicidades de splits en bootstrap,
manteniendo bloque original. Contraste contra funciones congeladas y ejecuciones
del analista antes de usar el motor. Error D/β≤1e-10 y p idéntica con mismo RNG.
Si falla, preservar fallo y congelar enmienda antes de corregir.

Reportar veredictos globales y entre réplicas con L0 PASS: el condicionamiento
puede afectar las tasas; no confundir denominadores. Bajo β=0, MODULA es falso;
NO_MODULA es potencia de equivalencia, no falso positivo. Para falso NO_MODULA,
usar las alternativas ±.03 fuera de [−.02,.02]. Para β negativo, MODULA también
es un error de dirección. Reportar extremo PERSISTE/DESAPARECE por separado.
IC95 Wilson de todas las tasas. Exceso demostrado sobre5% sólo si Wilson inferior
>.05; ausencia de evidencia no demuestra calibración. IC95 unilateral positivo
implica idealmente2.5% bajo nulo simétrico, más estricto que la consulta de5%.

Controles y casos no tienen criterios ajustados tras ver resultados. Dos procesos,
un hilo BLAS, conservar todas las réplicas/errores en arrays fuera de Git, JSON/CSV
de resultados y manifiestos en Git. No entrenar redes ni medir geometría. No
afirmar certificado, calibración universal ni transferencia a otras cohortes.
