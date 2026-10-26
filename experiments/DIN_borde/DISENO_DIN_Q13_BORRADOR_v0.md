# DIN-Q13 — ¿el colapso de M es necesario para la señal temprana? BORRADOR v0 (2026-10-26)

**Estado:** borrador. Nada está calculado ni entrenado y nada está congelado. Lo pidió el responsable a las 12:44, porque D9 salió «ninguno pasa» (PR #95) y la regla decía «si algo no sale como esperábamos, medimos Q13».

## 1. Pregunta
En la familia gaussiana de G3 y C2 (s = 0.8), la señal temprana existe: X10 mejora fuera de muestra la predicción de log ρ_caras(250) sobre una base cúbica de log ρ_caras(10). Así lo dieron G3, con D = 0.017, y C2, con PASS y D = 0.0295. **Si se reduce el colapso de M en u250 *con los mismos datos, splits, inicializaciones y lotes*, ¿desaparece la señal?**

## 2. Lo que ya sabemos y por qué hace falta manipular
- **Evidencia observacional en G3:** la señal aparece solo en s = 0.8, el único nivel colapsado (c = 0.86). En s = 0.5 (c = 0.69) y s = 0.25 (c = 0.55) da NOT_MET.
  - Pero s cambia **los datos**, no solo el colapso, así que no separa una cosa de la otra.
  - El propio G3 lo dice: «faltan varios niveles igualmente colapsados para separar esa tendencia del cambio de régimen».
- **Indicio en contra, en G2:** con s = 2, sin colapso (c = 0.32), dio D = 0.044 con p = 0.055 (999 permutaciones, exploratorio). Si la señal pudiera existir sin colapso, Q13 debería poder detectarlo.
- **Por qué el colapso podría ser necesario (mecanismo D2b):** bajo colapso, M ≈ N·diag(odds). ρ(250) queda dominada por el ejemplo más difícil, y X10 mide precisamente la confianza en el ejemplo más difícil. Sin colapso, ρ(250) depende de muchos ejemplos y ese vínculo debería diluirse. **Q13 pone a prueba esa predicción.**

## 3. Manipulación (lo único que cambia entre brazos)
El **instrumento no cambia**: M y ρ se miden igual (v2 r3, `2ac015a2…`) sobre el modelo entrenado. Lo que cambia es **cómo se entrena**. Se proponen dos manipuladores independientes, para no confundir «colapso» con «efecto del manipulador»:

| brazo | entrenamiento | papel |
|---|---|---|
| **A0** | receta C2 idéntica (Adam lr 0.006, lote 64, 250 updates, CE) | control: debe reproducir colapso y señal |
| **LS** | igual, pero con CE con *label smoothing* ε_LS | reduce la saturación de p(y) |
| **WD** | igual, pero con AdamW y weight decay λ_WD | reduce el crecimiento de los logits por otra vía |

- **Pareado:** los tres brazos usan las **mismas** semillas de split, inicialización y lote. La única diferencia es ε o λ. Los X10 de los brazos serán casi iguales al inicio (en u10 los logits todavía son pequeños). Lo que cambia es la geometría final.
- **Calibración de dosis (piloto separado, antes de congelar el tamaño):** con semillas propias (base 701000, que no se reutilizan), 20 splits × 5 y una rejilla de ε ∈ {0.02, 0.05, 0.1, 0.2} y λ ∈ {1e-3, 1e-2, 5e-2, 1e-1}.
  - **Solo** se miden la mediana de c250, la mediana de q250 y la precisión del panel. **No** se calculan X, D ni ninguna asociación.
  - Se elige, para cada manipulador, la dosis más pequeña que lleve la **mediana de c250 a [0.55, 0.70]**, el rango de los niveles sin señal de G3, sin bajar la precisión mediana del panel más de 0.05 respecto de A0.
  - Si ningún valor de la rejilla lo logra, ese brazo **se descarta antes de entrenar** y se informa. Si caen los dos, Q13 queda INCONCLUSIVE_MANIPULACION sin cohorte.

## 4. Cohorte
- **Generador, red y panel:** idénticos a C2 (s = 0.8, d = 13, 13→64→32→3, n = 27).
- **Semillas nuevas:** split 711000, inicialización 721000, lote 731000. Son disjuntas de G2, G3 y C2.
  - **La cohorte C2 no se toca:** queda reservada.
- **Universo:** N splits × 5 inicializaciones × 3 brazos, con IDs `q13_{brazo}_s{split:04d}_k{k}`.
- **Tabla:** las columnas de C2 más `brazo`, `acc_panel250` y `acc_train250`, con todas las trayectorias planificadas, incluidas las fallidas.
- **Tamaño:** el que salga de la potencia (§6). Como referencia, C2 dio N = 200, es decir, 3000 trayectorias.

## 5. Análisis (`Q13/analisis_Q13.py`, se escribe y prueba antes de congelar)
Por brazo, la primaria de C1/C2 **sin cambios**:
- ρ_caras;
- base cúbica;
- 10 bloques con semilla 260010;
- 5000 permutaciones dentro del split con semilla 260001.

Se obtienen D_b, p_b y pendiente_b. Además:
- **Incertidumbre:** bootstrap de splits (2000 réplicas, semilla 760001). Los mismos splits remuestreados valen para los tres brazos, lo que da IC pareados de D_b y de ΔD_b = D_A0 − D_b.

**Validación** (como en C2): IDs duplicados o ajenos → ABORTA. Más del 5 % de faltantes **en cualquier brazo** → INCONCLUSIVE. Plan y resumen deben estar vinculados por SHA.

**Reglas, en este orden:**
1. **Compuerta de manipulación.** Si falla cualquiera de estas condiciones, el resultado es **INCONCLUSIVE_MANIPULACION**:
   - A0 con mediana de c250 ≥ 0.8 y de q250 ≤ 0.05;
   - cada brazo reducido con mediana de c250 ≤ 0.70;
   - la precisión mediana del panel de cada brazo reducido a menos de 0.05 de la de A0.
2. **Señal en el control.** Si A0 no da PASS (p < 0.05, D > 0 y pendiente > 0), el resultado es **INCONCLUSIVE_SIN_SENAL_CONTROL**.
3. **Por brazo reducido:**
   - **CAE:** el IC95 superior de D_b es menor que 0.006 **y** el IC95 inferior de ΔD_b es mayor que 0.
   - **SE_MANTIENE:** PASS en el brazo **y** el IC95 inferior de ΔD_b es ≤ 0.
   - **INTERMEDIO:** cualquier otro caso.
4. **Veredicto:**

| LS | WD | veredicto |
|---|---|---|
| CAE | CAE | **NECESARIO_APOYADO**, en esta familia y con estos manipuladores |
| SE_MANTIENE | SE_MANTIENE | **NO_NECESARIO** |
| CAE | SE_MANTIENE (o al revés) | **DEPENDE_DEL_MANIPULADOR** |
| cualquier INTERMEDIO | | **NO_CONCLUYENTE** |

**Secundarios** (no deciden):
- la DE intra-split de Y y X por brazo;
- la pendiente estandarizada;
- D con ρ_vert;
- la relación dosis-respuesta en el piloto (solo c).

## 6. Potencia (agente de cohorte, antes de entrenar)
- **Método:** el de C2, con piloto = cohorte G3 s = 0.8, D_obj ∈ {0, 0.006, 0.012} y 400 réplicas.
- **Regla:** el **primer** N en {200, 256, 320, 400} que cumpla **las dos** condiciones:
  - límite inferior de Wilson ≥ 0.8 para el PASS de A0 con D_obj = 0.012;
  - límite inferior de Wilson ≥ 0.8 para «IC95 superior < 0.006» cuando D_obj = 0, que es la potencia para declarar CAE.
- **Si ningún N lo cumple, no se entrena** y se discute.

## 7. Alcance y amenazas
- **Qué estima:** un efecto causal *de la manipulación del entrenamiento* sobre la señal, en una familia sintética. No es necesidad lógica ni transferencia a Wine o a datos reales.
- **Amenaza 1, Y menos variable:** si un manipulador reduce mucho la varianza de log ρ250, D podría caer por falta de rango y no por falta de colapso. Por eso se reporta la DE de Y por brazo. El veredicto CAE exige IC estrecho, no solo p alta.
- **Amenaza 2, manipulador ≠ colapso:** LS y WD cambian más cosas que c. Por eso hay **dos** vías distintas. Si coinciden, la lectura «es el colapso» gana peso; si no, se dice DEPENDE_DEL_MANIPULADOR.
- **Lo que no prueba:** que todo modelo colapsado tenga señal, ni que el colapso sea suficiente.

## 8. Reparto y orden (como en C2)
1. **Este diseño:** con la aprobación del responsable, pasa a v1 y se congela junto con `analisis_Q13.py` y `pruebas_Q13.py` probados.
2. **Agente de cohorte:** calibración de dosis (solo c, q y precisión) → potencia → `q13_plan.json` → compuerta de reproducción → entrenamiento → tabla y resumen por SHA, **sin calcular D ni p**.
3. **Claude:** análisis único.
4. **Responsable:** cierre.
