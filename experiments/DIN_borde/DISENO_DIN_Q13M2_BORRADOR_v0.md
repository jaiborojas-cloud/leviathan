# DIN-Q13-M2 — ¿la modulación de la señal por el colapso depende del manipulador? BORRADOR v0 (2026-10-27)

**Estado:** borrador. Nada está congelado ni entrenado. El responsable eligió la opción 2 a las 08:44: LP y WD, con A0 compartido.

**Antecedentes:**
- **Q13-DR, con LS:** dio MODULA, β = 0.077 [0.028, 0.140], con D de 0.034 a −0.001 al bajar c de 0.87 a 0.40.
- **Calibración M2** (PR #113, solo c, q y precisión; 7000 de 7000): LP y WD son elegibles.

## 1. Pregunta
Si se reduce el colapso de M por **otras dos vías** distintas de LS (penalización de logits, LP, y weight decay, WD), con los mismos datos, ¿la señal temprana **también** baja con el colapso? ¿Y su pendiente es **compatible** con la de LS?

Si las tres vías coinciden, la modulación se atribuye al colapso y no al manipulador.

## 2. Dosis (fijadas ahora, solo con la curva c(λ) publicada)
**Regla:** interpolación lineal de la mediana de c250 en log λ, entre los puntos de la rejilla de calibración, hacia los niveles que alcanzó Q13-DR (c = 0.69, 0.61, 0.56, 0.50, 0.40). La dosis se redondea a 3 cifras significativas. Si un nivel cae fuera del rango interpolable, se usa el punto de la rejilla más cercano y se declara.

| nivel | c objetivo | LP λ (c esperada) | WD λ (c esperada) |
|---|---|---|---|
| A0 (compartido) | — | 0 (0.864) | 0 (0.864) |
| 1 | 0.69 | **1e-4** (0.688; punto de rejilla, 0.69 queda fuera del rango interpolable) | **0.709** |
| 2 | 0.61 | **3.52e-4** | **1.56** |
| 3 | 0.56 | **7.48e-4** | **2.19** |
| 4 | 0.50 | **1.85e-3** | **2.94** |
| 5 | 0.40 | **7.22e-3** | **4** (0.438; el **máximo alcanzable** de la rejilla, porque WD no llega a 0.40) |

**Receta:** la de Q13 v2 y la calibración M2, byte a byte.
- **LP:** CE + λ·media(‖z‖²), con Adam sin decay.
- **WD:** AdamW con weight_decay = λ.

## 3. Cohorte
- **Universo:** 11 niveles (A0, LP1–LP5 y WD1–WD5) × N splits × 5 inicializaciones, **pareados**: comparten datos, inicialización y lotes.
- **Semillas nuevas:** split 911000+s, inicialización 921000+5s+k, lote 931000+5s+k.
- **Tamaño:** **N = 200**, que da 11 000 trayectorias y unos 85 minutos en el equipo del responsable, en dos sesiones. Es el tope que fijó el responsable, hasta 12 000. La potencia lo verifica (§6).
- **IDs:** `q13m2_{A0|LP1…LP5|WD1…WD5}_s{split:04d}_k{k}`.

## 4. Análisis (`Q13M2/analisis_Q13M2.py`)
- **Reutilización:** usa, verificando su SHA, las funciones del análisis Q13-DR v3 congelado (`cc5524a7…`): validación de dominio, D_punto con bloques, pendiente con detección de c constante, rango con máximo − mínimo, bootstrap con todos los fallos y JSON sin NaN.
- **Validación del plan:** estricta, como en Q13-DR v3.
- **Splits comunes:** al menos 3 trayectorias válidas en **los 11** niveles, y al menos el 80 % de N.

**Para cada manipulador m ∈ {LP, WD},** sobre sus 6 niveles (A0 + m1–m5), con la misma lógica que Q13-DR:
1. **Compuerta:**
   - A0 con c ≥ 0.8 y q ≤ 0.05;
   - c estrictamente decreciente de A0 a m5;
   - rango ≥ 0.30;
   - |acc − acc_A0| < 0.05 en m1–m3;
   - acc_A0 − acc ≤ 0.10 en m4–m5.
2. **Señal en el control:** si A0 no da PASS, el resultado es INCONCLUSIVE_SIN_SENAL_CONTROL para los dos manipuladores.
3. **Primaria:** β_m es la pendiente de D sobre c en los 6 niveles, con un bootstrap pareado de splits comunes (2000 réplicas, semilla 960001). **Los mismos remuestreos sirven para LP y WD.**
   - **MODULA_m** si el límite inferior del IC de β_m es > 0;
   - **NO_CONCLUYENTE** en cualquier otro caso.
   - **Multiplicidad (decisión pendiente, §8):** son dos primarias, así que propongo un **IC al 97.5 %** para cada una (Bonferroni, α = 0.025 por manipulador).
4. **Secundarios predeclarados:**
   - **Compatibilidad con LS:** CI95 de β_m − β_LS, con β_LS recalculado de forma determinista desde la tabla de Q13-DR (`ed00364f…`) con el análisis v3 y su semilla 860001. Las cohortes son **independientes**, así que las réplicas se combinan como diferencias independientes.
     - **COMPATIBLE** si el IC contiene 0;
     - **DIFIERE** si lo excluye.
     - Ser compatible **no** es lo mismo que ser igual: se reporta el IC completo.
   - **LP frente a WD, en la misma cohorte:** CI95 pareado de β_LP − β_WD.
   - **Extremo por manipulador:** PERSISTE, DESAPARECE o INDETERMINADO, con la regla de Q13-DR.
   - **Equivalencia por manipulador:** NO_MODULA o NO_ESTABLECIDA, sin potencia prometida.

**Veredicto conjunto** (es solo una etiqueta; se deriva de las primarias):

| LP | WD | lectura |
|---|---|---|
| MODULA | MODULA | **MODULACION_REPRODUCIDA_EN_DOS_VIAS**: con LS son tres mecanismos |
| MODULA | NO_CONCLUYENTE | **REPRODUCIDA_EN_LP**. En WD falta evidencia, posiblemente porque su rango de c es menor (de 0.86 a 0.44) |
| NO_CONCLUYENTE | MODULA | **REPRODUCIDA_EN_WD** |
| NO_CONCLUYENTE | NO_CONCLUYENTE | **NO_REPRODUCIDA**: la modulación podría ser propia de LS |

## 5. Pruebas antes de congelar
Son las de Q13-DR adaptadas a 11 niveles, más:
- un manipulador modula y el otro no;
- la compuerta falla en un solo manipulador: el otro se evalúa igual, y queda declarado;
- el cálculo determinista de β_LS desde la tabla de Q13-DR reproduce exactamente 0.07692466151365258;
- la diferencia β_m − β_LS en casos construidos.

Después, **auditoría y verificación** por el otro agente, como en Q13-DR.

## 6. Potencia (agente de cohorte, antes de entrenar)
- **Escenario:** para cada manipulador, la curva D(c) de LS observada en Q13-DR. Es lineal, con β = 0.077, evaluada en las c esperadas de cada manipulador.
- **Dependencia entre niveles:** ρ = 0, con sensibilidad para ρ = 0.3, 0.6 y la de Q13.
- **Regla:** Wilson inferior ≥ 0.8 para MODULA_m con N = 200, **en cada manipulador**, con el IC al 97.5 % si se aprueba §8. Si WD no llega, por su menor rango de c, se informa y el responsable decide: N mayor dentro del tope, quitar WD o aceptar menos potencia.

## 7. Alcance
- **Qué apoya:** tres manipuladores con mecanismos distintos (suavizar el objetivo, frenar los logits y encoger los pesos) que dan la misma relación entre D y c. Eso apoya que la modulación es **propiedad del colapso**.
- **Qué no prueba:** que lo cause el colapso de M en sí; podría ser otra variable que los tres manipuladores muevan juntos, como la escala de los logits.
- **Una sola familia:** gaussianas s = 0.8.

## 8. Decisiones pendientes del responsable
1. **Multiplicidad:** propongo un IC al 97.5 % por manipulador (Bonferroni), o un IC al 95 % declarando dos primarias sin corrección.
2. **Nivel 5 de WD:** usar λ = 4 (c ≈ 0.44, el máximo alcanzable), o extender la rejilla de WD con otra calibración, que costaría unos 15 minutos del agente.
3. **Compatibilidad con LS:** que «contiene 0» sea la regla, o fijar un margen de equivalencia sobre β_m − β_LS. Con un margen, la potencia sería baja, como pasó con NO_MODULA.
