# DIN-Q13-DR — ¿el colapso modula la intensidad de la señal temprana? (dosis-respuesta) BORRADOR v0 (2026-10-26)

**Estado:** borrador. Nada está congelado, calibrado ni entrenado. Lo pidió el responsable a las 19:18.

**Origen:** la pregunta se formuló **después** de Q13-LS. Con LS, c250 bajó de 0.86 a 0.60 y la señal bajó de D = 0.039 a 0.0083 sin desaparecer. Por eso Q13-DR usa **semillas nuevas** y se congela antes de ver sus datos. Es confirmatorio para la pregunta reformulada, no una reutilización de Q13.

## 1. Pregunta
En la familia gaussiana s = 0.8, si se reduce el colapso de M en u250 de forma **graduada** y pareada, ¿la intensidad de la señal temprana baja de forma **monótona** con el colapso?

La señal es D de X10 sobre la base cúbica de log ρ_caras(10). Si baja, ¿llega a cero en el extremo de menos colapso o persiste?

## 2. Manipulador y dosis: solo LS, con rejilla fijada **ahora** con la calibración existente
- **Por qué solo LS:** en las calibraciones de v1 y v2 (semillas 701000 y 741000, solo c, q y precisión), LS fue **monótono y estable**. Su piloto dio 0.61 con ε = 0.005 y la cohorte dio 0.601.
- **Por qué no WD:** fue inestable. Su piloto dio 0.675 y la cohorte 0.740.
- **Rejilla de 6 niveles:**

| nivel | ε | mediana de c250 en la calibración | precisión del panel (A0: 0.926) |
|---|---|---|---|
| L0 | 0 | 0.81–0.84 | 0.926 |
| L1 | 0.002 | 0.70 | 0.926 |
| L2 | 0.005 | 0.61 | 0.926 |
| L3 | 0.01 | 0.54 | 0.926 |
| L4 | 0.02 | 0.42 | 0.889 |
| L5 | 0.05 | 0.36 | 0.889 |

- **No se recalibra.** La rejilla sale de mediciones ya publicadas que nunca incluyeron X, ρ ni D. Se omite ε = 0.1 y 0.2 porque su precisión cae ≥ 0.05 o casi.

## 3. Cohorte
- **Generador, red, receta e instrumento:** los de Q13 v2, con `cohorte_v2.py` adaptado solo en los brazos y dosis del plan. La receta se mantiene byte a byte.
- **Semillas nuevas:** split 811000+s, inicialización 821000+5s+k, lote 831000+5s+k.
- **Pareado:** los 6 niveles comparten datos, pesos iniciales y lotes.
- **Universo:** N splits × 5 inicializaciones × 6 niveles. N sale de la potencia (§6), con un **tope operativo del responsable** de 12 000 trayectorias, unas dos sesiones de 1 h en su equipo. Eso permite N ≤ 400.
- **Ejecución:** en el equipo del responsable, como Q13 v2, con las versiones fijadas (torch 2.9.1+cpu, numpy 2.3.5, scipy 1.17.0, sklearn 1.8.0).

## 4. Análisis (`Q13DR/analisis_Q13DR.py`, se escribe y prueba antes de congelar)
Por nivel ℓ, la primaria C1 sin cambios: D_ℓ, p_ℓ y pendiente_ℓ (5000 permutaciones, semilla 260001; 10 bloques con semilla 260010). Se usa además un bootstrap pareado de splits (2000 réplicas, semilla 860001), con las copias en el bloque de su split original.

**Validación:** la de Q13. ID duplicado o ajeno → ABORTA. Más del 5 % de faltantes en cualquier nivel → INCONCLUSIVE. Se usan los splits comunes con al menos 3 trayectorias válidas en todos los niveles.

**Reglas, en este orden:**
1. **Compuerta de manipulación:**
   - L0 con mediana de c250 ≥ 0.8 y de q250 ≤ 0.05;
   - medianas de c250 **estrictamente decrecientes** de L0 a L5;
   - rango (c_L0 − c_L5) ≥ 0.30;
   - en L1–L3, la precisión mediana del panel a menos de 0.05 de L0. L4 y L5 pueden perder hasta 0.05; se reporta.

   Si falla, el resultado es **INCONCLUSIVE_MANIPULACION**.
2. **Señal en el control:** si L0 no da PASS, el resultado es **INCONCLUSIVE_SIN_SENAL_CONTROL**.
3. **Primaria, la pendiente dosis-respuesta β:** la pendiente de la regresión de D_ℓ sobre la mediana de c250_ℓ, con los 6 niveles, por mínimos cuadrados ordinarios. Su IC95 sale del bootstrap pareado, recalculando D_ℓ y c_ℓ en cada réplica.
   - **MODULA:** el IC95 inferior de β es > 0. Menos colapso, menos señal.
   - **NO_MODULA:** el IC95 de β está contenido en [−0.02, 0.02]. Equivale a que la señal cambie menos de 0.006 en todo el rango de c (≈ 0.3–0.5).
   - **NO_CONCLUYENTE:** en cualquier otro caso.
4. **Clasificación del extremo** (secundaria pero predeclarada):
   - **PERSISTE:** L5 da PASS.
   - **DESAPARECE:** el IC95 superior de D_L5 es < 0.006.
   - **INDETERMINADO:** en cualquier otro caso.

   Con MODULA, esto distingue «graduada y persistente» de «graduada con umbral».

**Secundarios** (no deciden):
- **Monotonía:** Spearman entre D_ℓ y c_ℓ.
- **Control de la restricción de rango no uniforme:** la fracción de la varianza de Y intra-split que queda después de la base, por nivel. Si D baja mientras esa fracción no baja, la caída no se debe a la base.
- **Robustez:** D con ρ_vert.
- **Un nivel por trayectoria:** D por cuartiles de c250 *dentro* de L0. Es observacional y descriptivo.

## 5. Pruebas antes de congelar (`Q13DR/pruebas_Q13DR.py`)
Con un fixture G3 s = 0.8 copiado en 6 niveles sintéticos:
- **Controles:** β > 0 (D decreciente construida) → MODULA; niveles idénticos → NO_MODULA (con N grande); N = 100 → NO_CONCLUYENTE.
- **Compuertas:** c no monótona, rango < 0.30 y L0 sin señal.
- **Validación:** los casos de Q13.

## 6. Potencia (agente de cohorte, antes de entrenar)
- **Método:** el de Q13 v2, con piloto G3 s = 0.8.
- **Escenarios:**
  - **(a)** dosis-respuesta lineal de 0.039 (en c = 0.86) a 0.008 (en c = 0.60), extrapolada a 0 en c ≤ 0.47, con c_ℓ de la calibración;
  - **(b)** D constante igual a 0.02 en todos los niveles.
- **Regla:** el **primer** N en {200, 256, 320, 400} con Wilson inferior ≥ 0.8 para MODULA en (a) **y** para NO_MODULA en (b).
- **Si ninguno cumple con N ≤ 400:** se informa y el responsable decide antes de entrenar. Las opciones son subir el tope, quitar niveles o aceptar menos potencia para NO_MODULA.

## 7. Alcance y amenazas
- **Un manipulador:** no separa el «colapso» del «efecto propio de LS sobre la confianza». Una MODULA dice «el LS que reduce el colapso reduce la señal en proporción», no «el colapso causa la señal».
- **La precisión cae en L4 y L5:** el extremo mezcla menos colapso con un ajuste un poco peor. Por eso la clasificación del extremo es secundaria.
- **Familia única:** mezclas gaussianas s = 0.8, MLP 13→64→32→3.

## 8. Reparto (como en C2 y Q13)
1. El responsable aprueba y congela el diseño, con el análisis probado.
2. El agente de cohorte: potencia → plan → script portable → pausa.
3. El responsable corre la compuerta, la prueba corta y la cohorte en su equipo.
4. Claude hace el análisis único.
5. El responsable aprueba el cierre.
