# Dictamen de código y diseño: corregir antes de congelar

Revisión exacta de **e7dfc435ab97cdc8d24bba5d525b193af274f35f**, analista SHA
c9159325c7f22c6e5ded2977f6d208e0282558094fd34ab6f96fb68c00843b10.
Los enlaces apuntan a snapshots íntegros. Ninguna corrección se aplica al original.
Los casos reducidos usan B=39/NB=16 para aislar lógica; los casos CLI y el Monte
Carlo conservan los parámetros nominales indicados en sus archivos.

## F01 — punto y bootstrap estiman pendientes sobre poblaciones distintas

**ALTA, defecto inferencial demostrado.**
[L94](sources/Q13DR/analisis_Q13DR.py#L94) toma las medianas c sobre todas las
filas válidas. D se calcula sólo sobre splits comunes y el bootstrap recalcula c
sólo allí ([L120](sources/Q13DR/analisis_Q13DR.py#L120)). En presencia de faltantes
permitidos no es el mismo estadístico. El caso
[different_observed_and_bootstrap_c_samples](results/cases_v1/different_observed_and_bootstrap_c_samples.json)
tiene 20 splits, tres filas faltantes en un split distinto por nivel (3%), 14
comunes. El c observado empieza [.880,.680,.630,…], el c de los comunes es
[.885,.675,.635,…]. El ejemplo demuestra la discrepancia; no demuestra por sí
solo una tasa de falsos veredictos causada por ella.

El caso más fuerte [singular_beta_after_common_filter](results/cases_v2/singular_beta_after_common_filter.json)
tiene N=12 y 5% exacto de faltantes por nivel. Pasa la compuerta con medianas
decrecientes de todas las válidas; los seis c de los comunes tienen mediana .5.
El bootstrap de la pendiente queda sin rango y produce IC=[NaN,NaN], mientras
el resultado dice NO_CONCLUYENTE y no identifica una degeneración inferencial.

**Confirmado también en N=200**, dentro de la rejilla operativa:
[beta_bootstrap_singular](results/scale_N200/beta_bootstrap_singular.json) tiene
48/1000 faltantes por nivel (4.8%), 104 splits comunes, compuerta válida e
IC=[NaN,NaN]. No depende del tamaño pequeño del caso mínimo.

**Propuesta:** definir explícitamente la población de β. Usar c de las mismas
filas comunes que D tanto en el punto como en cada réplica, separándola del
resumen operacional de la compuerta. Si se quiere c sobre todas las válidas,
el remuestreo debe reproducir también esa población, no eliminarla en bootstrap.
Comprobar rango/finitez antes de calcular β.

## F02 — degeneraciones de bootstrap provocan crash o intervalos no finitos

**ALTA, bloqueante de ejecución.** Sólo se captura la primaria; el bucle
[L115](sources/Q13DR/analisis_Q13DR.py#L115) y sus cuantiles quedan fuera del try.
Caso [L_degenerate_in_bootstrap_only](results/cases_v1/L_degenerate_in_bootstrap_only.json):
N=20, X variable, señal fuerte; rho10=1 salvo un split con rho10=e. Observado
L no es constante, todas las primarias pasan. Un remuestreo omite el único split
distinto, L.std()=0 y D_punto genera **LinAlgError: SVD did not converge**.
El índice/semilla son reproducibles y la tabla cumple las validaciones iniciales.

[La réplica N=200](results/scale_N200/L_bootstrap_constant.json) reproduce el mismo
LinAlgError. Ambos tamaños se fijaron antes de cada ejecución de confirmación.

F01 aporta otra degeneración: β no identificada en bootstrap. Los NaN pasan a
quantile y clasificar_beta; el [serializador](sources/Q13DR/analisis_Q13DR.py#L156)
emite NaN no estándar. `json.dumps(...,allow_nan=False)` rechaza ese resultado.

**Propuesta:** controlar errores/rango/finitez por réplica y emitir INCONCLUSIVE
con motivo, semilla e índice, conservando todos los fallos. No eliminar réplicas
ni redibujar hasta completar2000. Cualquier extensión del estadístico para casos
degenerados debe definirse y probarse antes de congelar; no tocar el Q13 cerrado.

## F03 — el plan no valida dosis ni esquema básico

**ALTA para dosis/procedencia; MEDIA para crashes de entrada.**
[L149](sources/Q13DR/analisis_Q13DR.py#L149) trunca n_splits mediante int;
[L150](sources/Q13DR/analisis_Q13DR.py#L150) sólo compara números de nivel y
**no comprueba eps**.

- [Seis eps=0](results/cases_v1/plan_wrong_eps_accepted.json): CLI nominal, SHA
  correctos, devuelve **NO_MODULA/PERSISTE** y publica ese plan como confirmatorio.
  El caso no afirma que un entrenamiento real con seis dosis0 pasaría la compuerta;
  demuestra que un plan distinto del protocolo no se rechaza antes de analizar.
- [Sin eps](results/cases_v1/plan_missing_eps_accepted.json): se acepta el plan;
  termina INCONCLUSIVE por X constante, no por el plan mal formado.
- [n_splits=20.9](results/cases_v1/plan_fractional_n_accepted.json): se procesa como20.
- [n_splits=0](results/cases_v1/plan_zero_crash.json): **TypeError**, en la compuerta.
- [Sin campo nivel](results/cases_v2/CLI_traceback_classification.json): **KeyError**,
  no un aborto de validación controlado.

**Propuesta:** validar tipos antes de convertir: entero positivo no booleano,
seis diccionarios, nivel entero0..5 sin duplicados, eps numérica finita que coincida
con [0,.002,.005,.01,.02,.05], y tope/tamaño autorizado. Rechazar datos mal formados
con un aborto explícito. Mantener SHA/IDs como comprobaciones adicionales.

## F04 — Spearman inventa orden cuando hay empates

**MEDIA, resultado secundario falso.** El doble argsort de
[L126](sources/Q13DR/analisis_Q13DR.py#L126) asigna rangos diferentes a D iguales.
[complete_identical_levels](results/cases_v1/complete_identical_levels.json) tiene
los seis D idénticos y publica **spearman_D_c=−1**. No existe orden de D que sustente
esa correlación. Con empates parciales tampoco son los rangos medios de Spearman.

**Propuesta:** spearmanr/rankdata con tratamiento de empates; si D es constante,
guardar null y nota «no definido», no un valor de monotonía ni un NaN JSON.
No cambia la primaria, pero impide una lectura secundaria equivocada.

## F05 — el margen de β no implica la variación de D descrita

**MEDIA/ALTA, error matemático del diseño, no del if.**
[Diseño L58](sources/DISENO_DIN_Q13DR_BORRADOR_v1.md#L58) afirma que ±.02 equivale a
un cambio <.006 en el rango c≈.3–.5. En realidad **|ΔD_lineal|≤.02·rango(c)**:
con rango .5 permite hasta .010. La compuerta sólo fija un mínimo .30, no un
máximo .5. Además es un límite ≤, no estrictamente <.

**Propuesta, decide el responsable:** mantener ±.02 y corregir la interpretación
a sus unidades reales; o, si el objetivo es |ΔD|≤.006 entre extremos, fijar
prospectivamente el margen correspondiente (.012 si el rango fijado es .5).
No cambiar el margen después de ver datos. Véase [rules](results/cases_v1/rules.json).

## F06 — la suite puede etiquetar un crash como ABORTA

**MEDIA, cobertura de pruebas engañosa.**
[Pruebas L49](sources/Q13DR/pruebas_Q13DR.py#L49) busca el texto ABORTA en cualquier
parte de stdout/stderr. El traceback de un KeyError en la línea150 incluye la
propia línea fuente, que contiene `sys.exit("ABORTA: niveles del plan")`.
La heurística lo acepta como ABORTA aunque nunca se alcanzó ese sys.exit.

El helper inicial del auditor usó la misma heurística; su etiqueta original se
conserva. La [clasificación explícita v2](results/cases_v2/CLI_traceback_classification.json)
registra raw_helper_status=ABORTA y classification_by_traceback=CRASH con
KeyError:'nivel'. No se ejecutó la suite original ni se abrió su fixture.

**Propuesta:** priorizar detección de traceback y código de salida; exigir un
mensaje de aborto esperado con formato exacto o salida estructurada. Agregar el
caso de clave faltante, no sólo una lista de niveles incompleta pero bien formada.

## Decisiones de diseño pendientes, distintas de un bug literal

| Tema | Evidencia | Qué decidir antes de congelar |
|---|---|---|
| L4–L5 y precisión | [L5=.10](results/cases_v1/L5_accuracy_extreme_loss.json) y L4=.10 pasan: NO_MODULA/PERSISTE. Diseño dice «pueden perder hasta.05»; código dice que sólo se reportan. | Aclarar si hay límite obligatorio. Si lo hay, aplicarlo; si no, corregir el texto y amenaza. |
| Mínimo de splits comunes | [Caso](results/cases_v1/common_splits_only_half.json): 5% de faltantes por nivel, 11/12 splits válidos por nivel, pero sólo6/12 comunes; emite veredicto. | El80% actual es por nivel, no de comunes. No es una infracción literal, pero fijar si se exige un mínimo global y explicitarlo. |
| Inicializaciones comunes | El remuestreo empareja splits, no necesariamente el mismo subconjunto k válido en todos los niveles. | Es lo que dice la selección actual; aclarar la interpretación ante faltantes diferenciales. No filtrar retrospectivamente sin regla. |
| Dominio físico | [q negativo](results/cases_v1/q0_negative.json) y [acc=1.1](results/cases_v1/accuracy_above_one.json) aceptados. | Implementa el contrato «finito», pero faltan límites físicos. Añadirlos y declarar tolerancias antes de congelar si se desean. |
| Umbrales decimales | [.86−.56](results/cases_v1/range_decimal_030.json)=.29999999999999993 rechaza; [.95−.90](results/cases_v1/acc_exact_decimal_005.json)=.04999999999999993 acepta. | Documentar comparación binaria exacta o tolerancia predefinida. No redondear ni ajustar tras medir. Empates exactos de c sí se rechazan correctamente. |
| MODULA y equivalencia se solapan | IC=[.001,.01] cumple ambos criterios; devuelve MODULA por prioridad. | La prioridad sigue el diseño, no es bug. Aclarar que NO_MODULA no es el complemento lógico de MODULA. |
| Tendencia versus monotonía | D=[.05,.01,.04,.005,.03,.01] tiene pendiente positiva pero no es monótona. | La primaria prueba tendencia lineal, no orden de las seis medias. Reescribir alcance o diseñar un contraste de orden prospectivo. |
| Equivalencia nominal | IC95 dentro de la banda es más conservador que TOST al5% (IC90). | Es una elección válida, pero explicitar su potencia y no prometer tamaño5% para ambos criterios. |

## Componentes comprobados como OK

[Traza](results/cases_v1/bootstrap_trace_pairing_folds_D_c_beta.json): mismos draws
en los seis niveles, cada copia en el bloque original, D y mediana c recalculadas
por réplica; β coincide con MCO independiente (error máximo1.18e-15). No se halló
el supuesto bug de reutilizar β puntual o fijar c en el bootstrap completo.

Empates exactos de medianas c: rechazo correcto. q0=.05 aceptado y q0>.05 rechazado.
Pérdida de precisión L2: rechazo. Cinco faltantes/100 admitidos, seis rechazados.
IDs duplicados/ajenos: aborto. X/L constantes observados: INCONCLUSIVE. Orden
PERSISTE antes que DESAPARECE: correcto, incluso si ambos criterios numéricos
pudieran coincidir. Los hashes de Q13/C1 y de todas las fuentes permanecen intactos.

## Reproducción de un caso mínimo

Desde un clon con las dependencias de auditoría y código comprometido, usar una
carpeta de salida nueva, conservando las anteriores:

```bash
python experiments/DIN_borde/Q13DR/auditoria/scripts/cases_v1.py \
  --only L_degenerate_in_bootstrap_only --out /tmp/q13dr-caso-nuevo
```

El archivo del caso contiene la excepción y traceback; el generador fixture no
lee ningún dato real. Los casos CLI guardan sus CSV/plan/resumen y salidas en la
ruta externa indicada en cada resultado; para repetirlos, usar un entorno limpio,
nunca sobrescribir esos directorios. La extensión v2 está congelada por separado.
