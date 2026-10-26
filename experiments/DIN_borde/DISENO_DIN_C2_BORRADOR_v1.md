# DIN-C2 — réplica confirmatoria independiente en la familia gaussiana explorada por G3, BORRADOR v1 (2026-10-26)

**Estado:** borrador. **No congelado.** Sustituye al v0, que se conserva. Incorpora las decisiones del responsable del 2026-10-26 a las 08:05.

## 1. Decisiones del responsable (08:05)
1. **Un único nivel primario: s = 0.8.** No hay multiplicidad entre niveles. **Se elimina** el nivel secundario s = 1.0 del v0.
2. **Tamaño planificado para D_obj = 0.012**, con el límite inferior de Wilson al 95 % de la potencia simulada ≥ 0.8. N sale del cálculo; no se da por supuesto.
3. **Funciones separadas:**
   - el agente de cohorte genera y publica la tabla por SHA, **sin calcular D ni p**;
   - Claude ejecuta el análisis congelado **una sola vez**;
   - el responsable aprueba la congelación y el cierre.
4. **Compuerta completa de G3:** mediana de c250 ≥ 0.8 **y** mediana de q250 ≤ 0.05. Se reporta además la fracción individual colapsada (en G3 fue 58 %), que no filtra.
5. **Antes del primer entrenamiento** quedan congelados el diseño, el script de análisis probado y el tamaño.
6. **Alcance:** «réplica confirmatoria independiente en la familia gaussiana explorada por G3». C2 conserva ese generador. No establece la necesidad del colapso, la causalidad ni la transferencia a datos reales.

## 2. Cohorte
- **Generador, red y entrenamiento:** idénticos a G3 (`G3/scripts/run_v1.py`, config v1): d = 13, 30 por clase en entrenamiento, 9 por clase en el panel (n = 27), radio 2.0, 13→64→32→3, Adam con lr 0.006 y lote 64, 250 updates.
- **Nivel:** s = 0.8.
- **Visitas:** 5, 10, 30 y 250 como mínimo; se pueden conservar las 7 de G3.
- **Semillas nuevas**, disjuntas de G2 y G3: bases 611000 (split), 621000 (inicialización) y 631000 (lote).
- **Universo:** N splits × 5 inicializaciones, con IDs `c2_s{split:04d}_k{k}`.
- **Tabla publicada** (`c2_cohorte.csv`): las columnas `trajectory, split, k, X10, R250, c250, q250, rho_caras_10, rho_caras_250, rho_vert_10, rho_vert_250, error`, con todas las trayectorias planificadas, incluidas las fallidas.
  - X10 = max_n [logsumexp_{c≠y} − logsumexp], como en G3.
  - ρ con v2 r3 (`2ac015a2…`).
- **Plan publicado** (`c2_plan.json`, al congelar el tamaño): `n_splits` y `ids_sha256`, el SHA-256 de los IDs unidos por "\n".
- **Resumen** (`RESUMEN_c2.json`): `tabla_sha256` y `plan_sha256`.

## 3. Análisis (`C2/analisis_C2.py`, borrador; `d24ac5a7…`)
- **Reutilización sin cambios:** `cen`, `D_cv`, `primaria` y `W_perm` de `C1/analisis_C1_v2.py`; el script verifica su SHA, `8711f468…`.
- **Orden:**
  1. **Validación:** IDs duplicados o ajenos → ABORTA. Los faltantes (ausente, error o dominio inválido) se cuentan contra 5N; si superan el 5 %, el veredicto es INCONCLUSIVE. También: menos del 80 % de splits válidos, X o L sin variación, fallo de ajuste, o plan y resumen no vinculados.
  2. **Compuerta de régimen:** si no se cumple, el veredicto es **INCONCLUSIVE_REGIMEN**.
  3. **Primaria:** D de C1 con ρ_caras (base cúbica, 10 bloques con semilla 260010, 5000 permutaciones con semilla 260001). **PASS si p < 0.05, D > 0 y pendiente > 0.**
- **Secundarios** (no deciden): D_X | R250; D con ρ_vert; W_adj legado; D en el subconjunto colapsado individualmente (descriptivo).

## 4. Pruebas antes de congelar (`C2/pruebas_C2.py`; resultados en `pruebas_C2.json`)
Usan como fixture la cohorte G3 (PR #86) re-etiquetada; **no es un dato confirmatorio**. **16 de 16 dan lo esperado:**

| caso | esperado | obtenido |
|---|---|---|
| G3 con s = 0.8, completa (100 splits) | PASS | PASS: D = 0.017348 (coincide con G3), p = 0.0052 |
| G3 con s = 0.25 (sin colapso) | INCONCLUSIVE_REGIMEN | INCONCLUSIVE_REGIMEN (mediana de c = 0.55) |
| 26 omitidas / 26 con error (> 5 % de 500) | INCONCLUSIVE | INCONCLUSIVE |
| 25 con error (5 % exacto) | PASS | PASS |
| 21 de 100 splits omitidos | INCONCLUSIVE | INCONCLUSIVE |
| duplicados / ID ajeno | ABORTA | ABORTA |
| 3 valores de dominio inválido | PASS (cuentan como faltantes) | PASS |
| L constante / X constante | INCONCLUSIVE | INCONCLUSIVE |
| c250 forzado a 0.5 | INCONCLUSIVE_REGIMEN | INCONCLUSIVE_REGIMEN |
| plan con otros IDs / resumen de otra tabla | INCONCLUSIVE | INCONCLUSIVE |
| control X = L / X de ruido | NOT_MET | NOT_MET |

## 5. Potencia y tamaño (agente de cohorte, antes de entrenar)
- **Piloto:** la cohorte G3 con s = 0.8 (100 × 5), que ya es de descubrimiento. El método es el de G3: remuestreo de splits completos, modelo gaussiano y estimando exacto con 1999 permutaciones.
- **D_obj:** {0, 0.010, 0.012, 0.015, 0.017}, con 400 réplicas por celda.
- **Regla:** el **primer** N en {200, 256, 320, 400, 512, 640} con límite inferior de Wilson ≥ 0.8 para D_obj = 0.012 y límite superior de Wilson ≤ 0.10 para los falsos PASS con D_obj = 0. Si ninguno lo cumple, **no se entrena**.

## 6. Orden de congelación
1. Este diseño, con `analisis_C2.py` y `pruebas_C2.py` congelados por SHA. Requiere la aprobación del responsable.
2. Potencia → `c2_plan.json` con N → SHA publicado.
3. Código de cohorte → compuerta de reproducción (3 reconstrucciones de M, como en G3) → entrenamiento → tabla y resumen por SHA.
4. Claude: análisis único. Responsable: cierre.
