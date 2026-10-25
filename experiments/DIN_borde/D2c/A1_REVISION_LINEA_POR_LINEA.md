# A1 · revisión contra §4–§5 del diseño v2

**Veredicto A1: FAIL.** El núcleo primario coincide; la entrada a la decisión
no garantiza los denominadores ni la validez numérica requeridos.
Todas las líneas se refieren al sujeto6b17d25, copiado byte por byte en sources.
[Diseño](sources/DISENO_DIN_C1_BORRADOR_v2.md) ·
[análisis](sources/analisis_C1_v1.py) · [cohorte](sources/c1_cohorte.py).
Las discrepancias demostradas llevan caso reproducible; una ambigüedad no se
presenta como un fallo estadístico probado. No se ejecutó cohorte/entrenamiento.

| Requisito / operación | Líneas del análisis, salvo indicación | Clasificación | Evidencia / alcance |
|---|---|---|---|
| Encabezado y contrato declarado | 1–18 | OK | Describe primaria v2 y secundarias |
| Imports, hash tabla | 20–24,97 | OK | Hash exigido en modo confirmatorio |
| Conversión numérica finita | 25,102–104 | DEFECTO D02 | Acepta rho0 o negativo antes del log; ambas CLI terminan con error |
| Controles disponibles | 26,78–89 | OK | Siete fórmulas de §6; semillas de sus pruebas publicadas no especificadas |
| Centrado intra-split | 29–32 | OK | Se resta media del propio split, sin mezclar folds |
| z con media/de poblacional global | 35–36 | OK | Coincide con «en la cohorte»; usa L del fold de prueba de forma transductiva prevista |
| Base z,z²,z³ y centrado de CADA potencia | 36,50 | OK | No equivale a elevar sólo Lc, y el código sigue la fórmula escrita |
| Escala L nula | 36 | DEFECTO D03 | CLI L_constant: división por0 y LinAlgError; falta salida controlada |
| Folds por splits enteros | 39–44,49–50 | OK | np.unique ordenado, permutación260010, posición mod10 |
| OLS sin intercepto tras centrar | 43 | OK | Equivale al contrato de contrastes intra-split |
| Predicción sólo fuera de fold | 42–44 | OK | Coeficientes se ajustan en otros9 folds; Y del fold de prueba sólo se usa para centrar/evaluar el contraste previsto |
| D=1−SSEfull/SSEbase | 44–45 | OK | No se trunca D negativo |
| SSEbase=0 / Y constante | 45 | DEFECTO D03 | CLI Y_constant: ZeroDivisionError antes de INCONCLUSIVE |
| Pendiente X completa | 52 | OK | Ajuste en toda cohorte para signo, exactamente como diseño |
| Umbral de variación X | 51 | AMBIGÜEDAD A01 | np.allclose usa atol1e-8 no declarado; no es invariante a reescalar X; caso constante sí funciona |
| RNG de permutaciones | 53–57 | OK |260001,5000 en confirmatorio, X permutado sólo dentro de cada split |
| Reajuste completo en cada permutación | 57,39–45 | OK | Se reutilizan folds; se vuelven a ajustar base/completo |
| Fórmula de p | 58 frente a docstring12 | AMBIGÜEDAD A02 | Código usa >=D−1e-15, texto >=D; sin discrepancias de p en las32 comparaciones |
| PASS p<.05 y pendiente>0 | 114 | OK | Cumple regla textual; el control ruido del autor tiene p=.005 pero beta<0 y NO pasa |
| D positivo no exigido | 114 | AMBIGÜEDAD A03 | El diseño tampoco lo exige; aclarar si «mejora» requiere D>0. No se observó PASS con D≤0 en esta auditoría |
| Promedio de rangos y exclusión de empates constantes | 61–71 | OK | rankdata promedio; se cuenta sin_var y se omiten grupos<3 |
| W secundario v1, sentido unilateral | 69–75,115 | OK | Semilla260002/BW20000; su afirmación sigue acotada |
| W flexible por rangos | 116–119 | AMBIGÜEDAD A04 | Implementa residuo de rankY sobre potencias de rankL; conviene escribir fórmula exacta, no independencia condicional |
| Control X=L y cúbica | 80–81 | OK | D0, NOT_MET en pruebas nuevas |
| Control Y_g_L | 82 | OK | Con ruido evita SSE nula; el contraejemplo original exacto de D2b es degenerado para esta base |
| L con error | 84–86 | OK | PASS previsto; es aproximación de L latente, no nueva dinámica |
| Incremento real y ruido | 87–88 | OK | Se reproducen fórmulas; r es parámetro generador, no correlación muestral exacta |
| Flags de modo y B/BW | 92–98 | OK | Confirmatorio bloquea reducción de permutaciones; descubrimiento/controles permiten pruebas |
| Compuerta booleana | 99,110 | OK | Falsa o ausente da INCONCLUSIVE en las CLI válidas |
| Identidad/versionado de la compuerta | 99,110,129 | AMBIGÜEDAD A05 | Sólo prueba truthiness de PASA; no exige SHA de cohorte v2 ni vínculo con tabla/protocolo |
| Rango de cohorte | 101 | DEFECTO D01 | Sólo rechaza splits<168; no comprueba lista168–323 ni5 init esperadas |
| Validación de faltantes | 102,112 | DEFECTO D01 | Denominador N=filas recibidas;47 omitidas pasan,47 con error dan INCONCLUSIVE |
| Exclusión de splits con<3 | 106–107 | OK | Se aplica antes de primaria; tests n3/n4 y all_n2 conservados |
| Umbral80% de splits | 107,111 | DEFECTO D01 | Se divide por splits presentes;40 splits omitidos dejan116 y aun así PASS |
| Unicidad de trayectoria/ID | 100–107 | DEFECTO D01 | Tabla con cada fila/ID duplicados da PASS con1560 «trayectorias» |
| Orden de controles de validez | 108 antes de109–114 | DEFECTO D02/D03 | Se calcula primaria antes de las salvaguardas; errores numéricos impiden emitir resultado |
| X sin variación | 113 | OK | X constante o sólo entre splits da INCONCLUSIVE; no se inventan rangos |
| Secundaria A, rho30 | 120–122 | OK |260004, sólo si todas las rho30 recibidas son finitas; positividad requiere la misma validación D02 |
| Resumen de auditoría rho10 | 123–124 | AMBIGÜEDAD A06 | Sólo informa n/máximo/mediana; no comprueba que sean las40 preseleccionadas ni fija consecuencia de precisión insuficiente |
| Violaciones de cuerda | 125–126 | OK | Descriptivo y tolerancia1e-6 explícita en código; validez de la cota condicionada a D04 |
| D base grado5 | 127 | AMBIGÜEDAD A07 | Código limita a2000 permutaciones; diseño indica semilla260005 sin fijar ese B |
| Metadatos/hashes y salida | 128–133 | OK | Registra tabla/script SHA y gate; resultados de auditoría en directorios nuevos evitan sobrescritura |

## Integración con c1_cohorte.py v2

| Operación | Líneas de cohorte | Clasificación | Evidencia |
|---|---|---|---|
| X=logsumexp incorrectas−logsumexp todas | 76–83 | OK | argmax de log-error corresponde a min confianza; py/X_prob sólo diagnósticos |
| Umbrales compuerta | 27–28,65–75,128–130 | OK estático | Coinciden con §3; NO se repitió compuerta ni se accedió a checkpoints |
| rho estándar y auditada | 84–90 | OK estático | Defaults y5760/1600, sin parchear instrumento |
| Selección40 trayectorias antes de medir | 103,113–114 | OK estático | RNG270001 sobre cola planificada, estable ante reanudación |
| Error por trayectoria y progreso | 118–123 | OK operacional | Conserva errores en PROGRESO, pero no en tabla entregada al análisis |
| Construcción de tabla sólo con éxitos | 125,132–135 | DEFECTO D01 | Borra del denominador analítico los fallos aun presentes en progreso; no hace falta entrenar para probar la integración |
| Cuerda de todas las caras | 50–55 | DEFECTO D04 | Sólo vértices y pares de vértices; omite puntos interiores a una arista expuesta |
| Límite de la revisión | _init/una/main | OK, alcance | Lectura únicamente; no se certifica operatividad de entrenamiento ni procedencia de fuentes en PC externa |

## Casos mínimos que justifican los defectos

- **D01:** misma tabla sintética con señal fuerte y47 de780 trayectorias
  faltantes. Como47 filas con error: INCONCLUSIVE; sin esas47 filas: PASS,
  N733 y0 faltantes contados. Con40 splits enteros ausentes: PASS, N580,
 116 splits considerados como100% del universo. Con filas/IDs duplicados:
 PASS, N1560. [Retornos CLI](results/run_v1/cli/).
- **D02:** una rho0 o negativa se considera «ok» por fnum; np.log produce
  inf/nan y el proceso falla sin RESULTADO_C1. [rho_zero](results/run_v1/cli/rho_zero/stderr.txt),
  [rho_negative](results/run_v1/cli/rho_negative/stderr.txt).
- **D03:** L constante o Y constante no tienen manejo controlado. El diseño
  no define completamente estos casos, por eso el ESTADO científico apropiado
  debe fijarlo el responsable; el crash del software sí está demostrado.
- **D04:**27 puntos,26 colineales en una cara y uno fuera, M=e0e0ᵀ+1e-12I
  (SPD). La curva hacia la cara completa es un segmento en a, de longitud
 .001424501425; la «cota inferior» del sujeto devuelve.037037037043,26 veces
 más. No puede ser cota inferior para ese panel. No se sabe si Wine presenta
 esa degeneración porque no se leyeron sus estados.

Defectos del software de auditoría: no hubo fallo de ejecución propio.
Un campo de metadatos de cuerda señaló líneas imprecisas; se conserva y se
aclara en [ERRATAS_METADATA.md](ERRATAS_METADATA.md), sin cambiar la medición.
