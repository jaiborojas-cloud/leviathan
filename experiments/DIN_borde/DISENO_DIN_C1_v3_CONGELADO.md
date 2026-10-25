# DIN-C1 — confirmatorio de la señal temprana, v3 CONGELADO (2026-10-25)

**Estado:** **CONGELADO** el 2026-10-25 a las 11:56 (hora de México) por aprobación del responsable («congela»). El contenido es idéntico a `DISENO_DIN_C1_BORRADOR_v3.md` (que se conserva), más la sección 7. Antes de congelar no se entrenó ninguna trayectoria de la cohorte confirmatoria (splits 168–323).

## 1. Cambios respecto del v2 (y defecto de D2c que atienden)
| D2c | defecto | corrección |
|---|---|---|
| D01 | los faltantes y los splits se contaban sobre la tabla recibida: una cohorte con filas o splits omitidos, o con filas duplicadas, podía dar PASS | **Universo planificado constante**: 780 IDs y 156 splits (168–323, regla de init). Un ID duplicado o ajeno al universo hace que el análisis **aborte**. Los faltantes se cuentan contra 780: un ID ausente, con error o con dominio inválido es faltante. `c1_cohorte.py` v3 entrega **todas** las trayectorias planificadas, también las fallidas con su error |
| D02 | ρ ≤ 0 o un X no finito provocaban un crash | **Dominio antes del log:** ρ > 0 y finita, X finita. Lo inválido cuenta como faltante y se aplica el umbral del 5 % (39 de 780 se permiten; 40 no) |
| D03 | L constante o Y constante provocaban un crash | Las condiciones se revisan **antes** de calcular; L sin variación, X sin variación, SSE_base = 0 o un fallo de ajuste dan INCONCLUSIVE sin perder el informe. Los secundarios no definidos se reportan como no definidos |
| D04 | la cota de cuerda solo tomaba pares de vértices; con una cara de 26 puntos no era cota inferior | La cota usa las **caras completas**: todos los índices sobre cada arista del casco. Se reporta el tamaño máximo de cara. En el caso de D2c ahora da 0.0014245, igual a la longitud del rayo |
| — (vinculación) | la compuerta se verificaba solo con PASA | Se exige un resumen de cohorte con `tabla_sha256` igual al de la tabla, y una compuerta con `PASA` **booleano** true y el **mismo** `script_sha256` que la cohorte |
| (opcional) | PASS no exigía D > 0 | **PASS = p < 0.05, D > 0 y pendiente > 0** |

## 2. Pregunta, cohorte, variables (igual que en el v2)
- **Pregunta:** ¿la incertidumbre sobre el ejemplo de validación más difícil en el update 10, X = log(1 − p_min), mejora fuera de muestra la predicción de Y = log ρ_borde(250) respecto de una base cúbica de L = log ρ_borde(10), dentro del split?
- **Cohorte:** splits 168–323 × 5. Se entrena con `c1_cohorte.py` **v3** y su compuerta numérica se **repite con la v3**.

## 3. Análisis (`C1/analisis_C1_v2.py`)
- **Primaria D:**
  - base cúbica centrada en el split;
  - 10 bloques de splits (semilla 260010);
  - nulo con X permutada dentro del split, 5000 permutaciones (semilla 260001);
  - **PASS = p < 0.05 y D > 0 y pendiente > 0.**
  - La holgura de 1e-15 en p solo sirve para los empates de punto flotante.
- **INCONCLUSIVE** (se evalúa antes de calcular):
  - la compuerta o el resumen no son válidos;
  - hay más de 39 faltantes de 780;
  - menos del 80 % de los 156 splits tienen al menos 3 trayectorias válidas;
  - X sin variación intra-split (atol 1e-8);
  - L sin variación;
  - SSE_base = 0 o un fallo de ajuste.
- **Secundarios:** los mismos que en el v2. D de grado 5 usa 2000 permutaciones. Se suma la auditoría de ρ(10) en 40 IDs **publicados** en el resumen de cohorte, y la cota de cuerda con caras completas.

## 4. Alcance de un PASS (precisado con D2b y D2c)
- **Base de comparación:** un PASS dice que X mejora fuera de muestra **a una base cúbica concreta** de log ρ(10). **No** prueba información condicional nueva sobre *toda* función de L. Un X = h(L) con h escalonada, logarítmica o sinusoidal puede pasar porque amplía la clase de funciones (D2c, caso 6/6).
- **El nulo:** la permutación de X dentro del split es exacta bajo intercambiabilidad. No garantiza un tamaño exacto para el nulo amplio de «ningún incremento dado L» cuando X depende de L. En los nulos estudiados por D2c, la tasa fue conservadora (0.75–1.5 %).
- **Predictivo, no causal:** si ρ(10) mide con ruido la variable que mueve el desenlace, X puede ganar por medirla mejor.
- **Familia única:** WineMLP en Wine, sin transferencia.

## 5. Pruebas antes de congelar
`C1/pruebas_C1_v2.py` usa semillas y orden fijos: la tabla de descubrimiento sale de d1 + d6 y la cohorte se arma como fixture sintético re-etiquetado. Sus resultados están en `C1/PRUEBAS_C1_v2_2026-10-25.md`.
- **Casos CLI de D2c:** filas omitidas, errores 39/40/47, 40 splits omitidos, duplicados, ID ajeno, dominio inválido, L/Y/X constantes y compuerta no vinculada.
- **Controles:** X = L, X = L³, Y = g(L) con X afín, X constante, ruido, incremento real, L con error (limitación) y escalón en L (alcance).
- **Reproducción del descubrimiento.**

## 6. Pendiente para congelar
1. Que todas las pruebas de la sección 5 den lo esperado.
2. Repetir la compuerta con `c1_cohorte.py` v3.
3. La aprobación del responsable. Al congelar se publican los SHA de este diseño, de `c1_cohorte.py` v3, de `analisis_C1_v2.py` y de `pruebas_C1_v2.py`.

## 7. Congelación
- **Pruebas:** las tres condiciones de la sección 6 se cumplieron. Las regresiones dan 24 de 24 (`C1/PRUEBAS_C1_v2_2026-10-25.md`). La compuerta con `c1_cohorte.py` v3 pasa (5/5 y 5/5). El responsable aprobó.
- **Hashes:** los archivos congelados y sus SHA-256 están en `C1/MANIFIESTO_DIN_C1_v3_CONGELADO.sha256`.
- **Orden:**
  1. Correr la cohorte (`c1_cohorte.py` v3, splits 168–323).
  2. Publicar la tabla `c1_cohorte.csv` y `RESUMEN_c1.json` por hash, como informe operacional.
  3. Correr **un solo** análisis con `analisis_C1_v2.py` en modo confirmatorio, con `--tabla-sha`, `--resumen-cohorte` y `--compuerta` (el `RESUMEN_c1.json` de `compuerta_v3`).
  4. Publicar la salida íntegra.
- **Cambios:** después de congelar, cualquier cambio exige una enmienda congelada antes de usarlo, y no puede depender de los desenlaces de la cohorte.

