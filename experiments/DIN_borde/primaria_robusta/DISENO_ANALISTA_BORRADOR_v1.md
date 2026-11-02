# A1 · analista genérico de la primaria robusta DIN v1

2026-11-02, hora de México. **BORRADOR para auditoría de Claude; no congelado ni autorizado para medir o analizar una cohorte real.** La [especificación adoptada](../PRIMARIA_ROBUSTA_v1.md) rige solo para diseños nuevos. No se modifican C1, C2, Q13, CIFAR ni sus resultados. Se compromete este contrato y las pruebas antes del código y de su ejecución.

## 1. Fuentes y alcance

Base: main `5eff9b5e5907123ee936540c364e14d424de94ee`. Se leyó el reparto del PR #130 en `f45e320a160514554165488ed719bf2902cb7fff`, pendiente de fusión; [snapshot](fuentes/reparto_PR130.md). La especificación adoptada tiene SHA `493a5eabe15028a3522ce5971a07343a806f8379c84288c7a2c2446efe8ad49a`. Referencia C1: únicamente código `analisis_C1_v2.py`, SHA `8711f468d0df110a94c9cfdf6a1d0777f495537546cdce516929f0cb129858d5`, usado sobre datos sintéticos para comprobar equivalencia. No se abren tablas de cohortes anteriores ni pesos.

El analista recibe un universo explícito por ID y split. No deduce el split del nombre ni exige un dataset, una red o cinco inicializaciones. El umbral de entrenamiento .5 se aplica a **tres clases**, como la adopción: otro número de clases requiere otro diseño, no cambiarlo aquí. Este borrador no incluye productor, selección de experimento, potencia ni tamaño de una futura cohorte.

## 2. Entrada y calidad

El plan declara `protocolo=DIN-PRIMARIA-ROBUSTA-v1`, `estado`, `tipo_datos`, `n_clases=3` y `universo`, lista ordenada de objetos `{trajectory, split}`. IDs únicos y no vacíos; split entero no negativo, sin booleanos. Se conserva el orden del universo para salidas y desempates. Tipos, IDs duplicados o ajenos, identidad split discordante o columnas distintas: ABORTA, sin resultado científico.

Una fila por trayectoria, CSV UTF-8 con estas columnas exactas:

```text
trajectory,split,estado_10,estado_final,error,X10,rho_caras_10,rho_caras_250,acc_train_final
```

Las dos visitas deben ser MEDIDA y no tener error. Se admiten también FALLIDA e INVALID_RHO para conservar fallos. Acc_train_final debe ser finita en [0, 1]. Si es **< .5**, se registra **NO_APRENDIO**, cuenta una vez como faltante y se conservan todos sus motivos. **.5 exacto es admisible**, sin tolerancia ni sustitución. X10 debe ser finita, como C1; no se recorta ni se cambia su escala. Las dos rho deben ser finitas y positivas antes de aplicar log. El productor del futuro experimento es responsable de la fórmula de X, la auditoría de rho, sus estados y sus fuentes congeladas; esta capa genérica no certifica geometría ni reabre el instrumento.

Ausente, estado fallido, dominio inválido o NO_APRENDIO: faltante contra el universo completo. Cada ID cuenta una sola vez aunque tenga varios motivos. No se reemplaza ni se imputa. Después se usan únicamente splits con ≥ 3 elegibles; los elegibles de splits menores se reportan aparte y no se convierten artificialmente en fallos de medida.

Compuertas: faltantes ≤ 5 % de trayectorias planificadas y ≥ 80 % de los splits planificados con ≥ 3 elegibles, usando comparaciones enteras exactas. No hay filtro por concentración, confianza, resultado o influencia antes de esta selección. X sin variación intra-split (atol = 1e−8, como C1), L constante, SSE_base ≤ 0, menos de dos splits utilizables o ajuste no finito: INCONCLUSIVE. Se conservan todos los motivos y las medidas ya definidas.

## 3. Núcleo numérico

X = X10, L = log rho_caras_10, Y = log rho_caras_250, sobre las filas usadas después de las compuertas. Y y X se centran dentro del split, con pendientes comunes. z = (L − media L) / DE L, ddof = 0, sobre el mismo conjunto usado, como C1. La transformación no se estima con Y ni X.

Bloques: `default_rng(260010).permutation(np.unique(split))`; bloque = posición mod 10. Todas las filas del split van juntas. En cada bloque se conserva z de entrenamiento y se **recorta solo z de prueba** a [min z_train, max z_train], antes de formar cada potencia z, z², z³ y centrar cada columna por split. El recorte nunca se aplica a X, Y o rho. Se reportan los límites por bloque, IDs recortados y z antes/después. El centro de los términos de prueba usa las filas de su propio split, igual que C1. Esto es un estimando entre inicializaciones de un split, no un predictor individual desplegable que desconozca su media final.

OLS sobre entrenamiento del bloque, sin ridge y sin intercepto adicional. SSE se acumula por los diez bloques en el mismo orden que C1. D = 1 − SSE_completo/SSE_base, sin truncar. Se conservan los residuos fuera de muestra por ID. **Pendiente de X:** coeficiente del ajuste global completo, con la base global original centrada, como C1; al usar toda la muestra no hay puntos fuera de su propio rango. Esta precisión operacional no cambia la pendiente definida por C1.

Permutación: 5.000, `default_rng(260001)`, X reasignada dentro de cada split en el orden de `np.unique`. Se vuelve a centrar X y se recalcula D, manteniendo bloques y bases (solo dependen de L y split). p = (1 + #{D_perm ≥ D − 1e−15})/5001, cuantiles del nulo y número de empates registrados. No se permuta la compuerta NO_APRENDIO ni se vuelve a seleccionar la muestra. La CLI no permite cambiar B, grado, semillas, recorte o umbrales. El API de pruebas admite B menor y una variante sin recorte, identificadas como diagnósticas.

## 4. Influencia y decisiones

Para cada ID usado: g_i = e_base,i² − e_completo,i², con residuos fuera de muestra de esta misma primaria. Se reportan todos los g_i, su suma, el máximo y el ID ganador. La fracción es max(g_i)/Σg_i **si la suma es positiva**; si no, null con motivo. Puede superar 1 si otras contribuciones son negativas: no se limita a [0, 1]. No se impone un umbral nuevo a esa fracción.

D_sin_max se obtiene quitando únicamente el ID de mayor g_i, recalculando media y DE de L, centrados, recorte y bloques con la misma regla y semilla. No se recalculan p ni las compuertas de faltantes. **Se conservan las restantes filas del split**, aunque pase de 3 a 2: es un diagnóstico de omisión de una trayectoria, no una cohorte filtrada nueva, consistente con el script exploratorio de referencia. Esta convención se declara para auditoría. Empates exactos en g: primer ID en el orden del universo, reportando también todos los empatados; sin tolerancia añadida. Un ajuste sin máximo degenerado queda null con su error conservado y hace la decisión INCONCLUSIVE.

| Condición | Veredicto |
|---|---|
| Calidad o cálculo inválido, incluido D_sin_max no definido | INCONCLUSIVE |
| p < .05, D > 0, pendiente > 0 y D_sin_max > 0 | PASS |
| Las tres primeras se cumplen y D_sin_max ≤ 0 | NO_ROBUSTO |
| Cualquier otro resultado numéricamente definido | NOT_MET |

Se conservan siempre la triple condición original y la compuerta de influencia por separado. NO_ROBUSTO no se transforma en PASS exploratorio. La omisión diagnóstica no cambia el universo, no reemplaza datos y no reescribe el resultado con todas las filas. Un PASS no certifica ausencia de otras influencias, información nueva frente a toda función de L, generalización a otra familia ni causalidad. La permutación mantiene la definición de C1; no se promete tamaño nominal universal ante cualquier dependencia X–L.

## 5. Reproducibilidad y entrega

Implementación en archivos nuevos `analisis_robusta_v1.py`, `pruebas_robusta_v1.py` y `config_BORRADOR_v1.json`. El analista no importa C1, core ni geometry en producción. Las pruebas cargan solo las funciones de C1 por SHA, sin sus datos o su CLI. Requisitos numéricos de validación: numpy 2.3.5, scipy 1.17.0, Python 3.12; sin torch ni red.

La CLI valida SHA publicados de tabla y plan, y enlaces con resumen, productor y compuerta. Salida exclusiva, JSON estricto sin NaN; bloquea cohortes reales mientras la implementación siga BORRADOR. El API expone el núcleo para futuras integraciones auditadas, no autoriza ejecutar una cohorte. Se publican esquema, resultados sintéticos, manifest y verification; fixtures/arrays completos fuera de Git con SHA, sin sobreescribir corridas. El [protocolo de pruebas](PROTOCOLO_PRUEBAS_v1.md) se compromete con este diseño. Si aparece un defecto, se documenta y compromete una enmienda antes de corregir y se conserva la corrida fallida.

La elección de experimento y congelación pertenecen al responsable. Claude auditará A1/A2; implementará después el productor elegido. Ninguna sección adopta retrospectivamente esta primaria para etapas cerradas.
