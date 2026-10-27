# DIN-Q13-DR — ¿el colapso modula la intensidad de la señal temprana? (dosis-respuesta) v3 CONGELADO (2026-10-26)

**Estado:** **CONGELADO** el 2026-10-26 a las 22:24 (hora de México), con la aprobación del responsable («apruebo congelar»). Los SHA están en `Q13DR/MANIFIESTO_DIN_Q13DR_v3_CONGELADO.sha256`. Nada está calibrado ni entrenado.

**Historial:**
- v0 → v1: decisiones del responsable de las 19:29.
- v1 → v2: auditoría independiente del PR #104 y decisiones de las 20:53.
- v2 → v3: verificación del PR #105, que encontró los defectos N01–N05; la v3 fue confirmada en el PR #107.
- Los borradores v0, v1 y v2 se conservan.

**Cambios de la v3 sobre el texto de la v2:**
- c constante en el punto o en una réplica (comparación exacta, ptp = 0) da INCONCLUSIVE;
- **rango(c) = máximo − mínimo** de las c comunes, que es el que define el margen de equivalencia 0.02 × rango(c); L0 − L5 se reporta aparte;
- un eps no convertible o archivos de entrada ilegibles o ausentes dan ABORTA;
- se guardan **todos** los fallos del bootstrap.

**Archivos congelados:**
- `analisis_Q13DR.py` v3: `cc5524a7…`
- `pruebas_Q13DR.py` v3: `03acf7e7…`, con 39 de 39 casos y 23 reglas puras

**Origen:** la pregunta se formuló **después** de Q13-LS. Con LS, c250 bajó de 0.86 a 0.60 y D bajó de 0.039 a 0.0083 sin desaparecer. Por eso usa **semillas nuevas** y se congela antes de ver sus datos.

## 1. Pregunta
En la familia gaussiana s = 0.8, al reducir el colapso de M en u250 de forma graduada y pareada con *label smoothing*, ¿la intensidad de la señal temprana **baja con tendencia lineal** al bajar el colapso?

La señal es D de X10 sobre la base cúbica de log ρ_caras(10). La primaria contrasta una **tendencia**, no el orden de las seis medias.

## 2. Manipulador y dosis (sin cambios respecto del v1)
Solo LS, con la rejilla fijada con calibraciones ya publicadas, que midieron solo c, q y precisión:

| nivel | ε | c250 en la calibración | precisión |
|---|---|---|---|
| L0 | 0 | 0.81–0.84 | 0.926 |
| L1 | 0.002 | 0.70 | 0.926 |
| L2 | 0.005 | 0.61 | 0.926 |
| L3 | 0.01 | 0.54 | 0.926 |
| L4 | 0.02 | 0.42 | 0.889 |
| L5 | 0.05 | 0.36 | 0.889 |

## 3. Cohorte (sin cambios respecto del v1)
- **Receta:** la de Q13 v2, byte a byte.
- **Semillas:** split 811000+s, inicialización 821000+5s+k, lote 831000+5s+k. Los 6 niveles van pareados.
- **IDs:** `q13dr_L{l}_s{split:04d}_k{k}`.
- **Tope:** N ≤ 400, que son 12 000 trayectorias.
- **Ejecución:** en el equipo del responsable, con las versiones fijadas.
- **Plan:** `n_splits`, `niveles` = [{nivel, eps}] e `ids_sha256`.

## 4. Análisis (`Q13DR/analisis_Q13DR.py` v3)
**Validación estricta del plan (F03).** Si falla, ABORTA, siempre con código de salida 3 y sin traceback:
- n_splits es un entero (no bool) entre 1 y 400;
- 6 niveles con `nivel` = 0..5 en orden;
- `eps` numérico, finito y **exactamente** [0, 0.002, 0.005, 0.01, 0.02, 0.05];
- `ids_sha256` presente;
- plan y resumen legibles.

**Dominio de una fila (decisión 5).** Primero se comprueba la finitud de X10, c250, q250, acc_panel250 y ρ_caras_10 y _250. Después:
- ρ > 0;
- q y acc dentro de [0, 1];
- c dentro de (0, 1].

Lo inválido cuenta como faltante. Las comparaciones son exactas, sin redondear medianas ni añadir tolerancias.

**INCONCLUSIVE si:**
- en cualquier nivel los faltantes superan el 5 % de 5N, o menos del 80 % de los splits tienen al menos 3 trayectorias válidas;
- **los splits comunes son menos del 80 % de N** (decisión 4). Un split es común si tiene al menos 3 trayectorias válidas en **cada uno** de los 6 niveles;
- X o L no varían en algún nivel;
- falla un ajuste;
- el plan o el resumen no están vinculados.

**Pasos, en este orden:**
1. **Compuerta de manipulación.** Usa las medianas de todas las filas válidas de cada nivel, como resumen operacional:
   - L0 con c250 ≥ 0.8 y q250 ≤ 0.05;
   - c250 estrictamente decreciente de L0 a L5;
   - c_L0 − c_L5 ≥ 0.30;
   - en L1–L3, |acc_Lℓ − acc_L0| < 0.05, sin cambios;
   - **en L4–L5, acc_L0 − acc_Lℓ ≤ 0.10** (decisión 3). Una mejora de precisión no provoca rechazo.

   Si falla, el resultado es INCONCLUSIVE_MANIPULACION.
2. **Señal en el control:** si L0 no da PASS, el resultado es INCONCLUSIVE_SIN_SENAL_CONTROL.
3. **Primaria, sobre las filas comunes** (F01). Se usan **las mismas filas** en el punto y en el bootstrap:
   - β es la pendiente por mínimos cuadrados de D_ℓ sobre la mediana de c250_ℓ de esas filas;
   - su IC95 sale del bootstrap pareado de splits comunes (2000 réplicas, semilla 860001), con las copias en el bloque de su split original y D_ℓ y c_ℓ recalculados en cada réplica.
   - **Degeneraciones (F02):** se valida cada réplica: que L varíe en cada nivel, que D sea finito, que c no sea constante y que β sea finita. Si alguna falla, el resultado es **INCONCLUSIVE**, con el motivo, los índices y el error. No se descartan ni se redibujan réplicas. Si en el punto c es constante, también es INCONCLUSIVE. El JSON se escribe sin NaN.
   - **Veredicto primario (decisión 2):** **MODULA** si el IC95 inferior de β es > 0; si no, **NO_CONCLUYENTE**.
4. **Secundarios predeclarados:**
   - **Equivalencia:** NO_MODULA si el IC95 de β está contenido en [−0.02, 0.02]; si no, NO_ESTABLECIDA.
     - Interpretación (decisión 1): |ΔD lineal| ≤ 0.02 × rango(c). Por ejemplo, hasta 0.010 si el rango es 0.5. **No** es un límite universal de 0.010: depende del rango observado, que se reporta.
     - **No se promete potencia para la equivalencia:** la auditoría la midió en 0 de 400 con ruido independiente.
     - **Puede coexistir con MODULA:** NO_MODULA no es el complemento lógico de MODULA.
   - **Extremo, en L5:**
     - **PERSISTE** si L5 da PASS;
     - **DESAPARECE** si L5 no da PASS y el IC95 superior de D_L5 es < 0.006;
     - **INDETERMINADO** en cualquier otro caso.

**Descriptivos** (no deciden):
- Spearman entre D_ℓ y c_ℓ con **rangos medios en los empates**. Si D o c son constantes, null (F04).
- La fracción de la varianza intra-split de Y que queda tras la base, por nivel.
- D con ρ_vert.
- D por cuartiles de c250 dentro de L0.

## 5. Pruebas (`Q13DR/pruebas_Q13DR.py` v2)
Cubren los casos del v1 adaptados al veredicto primario, más los de la auditoría:
- F01: el punto usa la c de las filas comunes.
- F02: L constante en las réplicas da INCONCLUSIVE.
- Splits comunes por debajo del 80 %.
- Dominio: q < 0, acc > 1, c = 0, c > 1, ρ = 0 y c = 1 válido.
- Precisión en L4 y L5: pérdida de 0.09 aceptada, de 0.11 rechazada; una ganancia se acepta. En L2, una ganancia o pérdida de 0.07 se rechaza.
- Plan: seis ε = 0, sin ε, sin clave `nivel`, n fraccional, n = 0, n bool, n = 401 y plan ilegible, todos ABORTA.
- Spearman con empates y constantes.
- β no identificada.

La CLI clasifica como ABORTA **solo** si el código de salida es 3, el mensaje empieza por «ABORTA:» y no hay traceback (F06).

## 6. Potencia (agente de cohorte, antes de entrenar; decisión 2)
- **Regla:** el **primer** N en {200, 256, 320, 400} con Wilson inferior ≥ 0.8 para **MODULA** en el escenario (a). No se exige potencia para NO_MODULA, pero su tasa se reporta.
- **Escenario (a):** D lineal en c, de 0.039 (c = 0.86) a 0.008 (c = 0.60), extrapolado y truncado en 0, con c_ℓ de la calibración.
- **Dependencia entre niveles:** el ruido de Y entre niveles de un mismo split e inicialización se fija **de antemano en el escenario conservador de independencia** (ρ = 0). Como los niveles comparten datos, inicialización y lotes, se espera una correlación positiva, que haría más precisa a β.
  - **Sensibilidad** (se reporta, no decide): ρ ∈ {0.3, 0.6} y la correlación A0–LS estimada en la cohorte Q13 v2.
  - Q13 orienta la sensibilidad, pero no identifica la matriz completa de seis dosis.
- **Si ningún N ≤ 400 cumple:** se informa y el responsable decide antes de entrenar.

## 7. Alcance y amenazas
- **Un manipulador:** MODULA dice «el LS que reduce el colapso reduce la señal con tendencia lineal», no «el colapso causa la señal».
- **Tendencia, no orden:** una pendiente positiva no implica que las seis medias estén ordenadas.
- **Extremo:** L4 y L5 pueden perder hasta 0.10 de precisión; el extremo mezcla menos colapso con peor ajuste. Por eso es secundario.
- **Familia única.**

## 8. Reparto
1. El agente auditor verifica la v2.
2. El responsable congela.
3. El agente de cohorte se encarga de la potencia, el plan y el script.
4. El responsable ejecuta en su equipo.
5. Claude hace el análisis único.
6. El responsable aprueba el cierre.
