# DIN-C2 — confirmatorio en una segunda familia (mezclas gaussianas en régimen de colapso), BORRADOR v0 (2026-10-25)

**Estado:** borrador. **No congelado.** Lo pidió el responsable el 2026-10-25 a las 23:34 («Diseñémoslo»). Nada se entrena hasta congelar.

## 1. Pregunta (hipótesis H-colapso, formulada en DIN-G3)
En mezclas gaussianas de 3 clases (generador de G2/G3) con solapamiento s = 0.8, el régimen en el que M colapsa sobre el ejemplo difícil, ¿la incertidumbre del modelo sobre su ejemplo de validación más difícil en el update 10 mejora fuera de muestra la predicción de log ρ_borde(250) sobre una base cúbica de log ρ_borde(10), dentro del split?

## 2. Antecedentes (exploratorios)
- **DIN-C1** (Wine, confirmatorio): D = 0.026, p = 1/5001.
- **G3** (sintético, 3 niveles × 100 splits):
  - s = 0.8: D = 0.0173, p = 0.003, mediana de c = 0.86 (colapso);
  - s = 0.25 y 0.5: D de 0.0002 y 0.0027, sin colapso.
- **G2:** con potencia baja, sin patrón.
- **G1** (Iris): colapso parcial, sin señal.
- **Selección:** s = 0.8 se elige **por** G3. Su D de 0.0173 es el máximo de 3 niveles y probablemente está inflado. La potencia se planifica para efectos menores.

## 3. Cohorte
- **Generador y entrenamiento:** el mismo de G3, sin cambios (`G3/scripts/run_v1.py`, config v1): d = 13, 30 por clase en entrenamiento, 9 por clase en el panel (n = 27), radio de medias 2.0, red 13→64→32→3, Adam con lr 0.006 y lote 64, 250 updates, visitas en los updates 5, 10, 30 y 250.
- **Nivel primario único:** s = 0.8.
- **Semillas nuevas,** disjuntas de G2 y G3: bases 611000 (split), 621000 (init) y 631000 (lote). Se verifica que no haya colisiones.
- **Tamaño N:** por la regla de potencia de la sección 5. Son 5 inicializaciones por split.
- **Nivel secundario opcional,** solo descriptivo: s = 1.0, con N/2 splits, para ver si el colapso y la señal se extienden. No entra en la decisión.

## 4. Variables y análisis (primaria única)
- **Variables:** X = log(1 − p_min,val) en el update 10 (logsumexp); L = log ρ_caras(10); Y = log ρ_caras(250); ρ_caras de **ρ_borde v2 r3** (`2ac015a2…`), sin cambios.
- **Primaria:** el estimando de DIN-C1 exacto (`C1/analisis_C1_v2.py`: `cen`, `D_cv` y `primaria`).
  - Base cúbica centrada dentro del split.
  - 10 bloques de splits (semilla 260010).
  - **5000 permutaciones** de X dentro del split (semilla 260001).
  - **PASS: p < 0.05, D > 0 y pendiente > 0.**
- **Compuerta de régimen** (fijada antes): la mediana de c = M_kk,max/tr en el update 250 debe ser ≥ 0.8, y la mediana de q (fracción de Frobenius fuera de la diagonal) ≤ 0.05. Si no se cumple, el veredicto es **INCONCLUSIVE_REGIMEN**: la cohorte no estaría en el régimen que H-colapso pregunta.
- **Validación de entrada** (lecciones de D2c): un universo planificado de IDs, sin duplicados y con las fallidas conservadas; faltantes contados contra N·5 (más del 5 % → INCONCLUSIVE); splits válidos ≥ 80 %; dominio de ρ > 0 antes del log; degeneraciones sin crash.
- **Secundarios** (no deciden): D_X | R(250) (D7); D con ρ_vert; W_adj legado; D en el subconjunto colapsado individualmente (descriptivo); nivel s = 1.0.

## 5. Potencia y tamaño (antes de entrenar)
- **Piloto:** la cohorte s = 0.8 de G3 (100 splits × 5). Ya es de descubrimiento.
- **Simulación:** se sigue el método de G3, con remuestreo de splits completos, un modelo gaussiano y el estimando exacto con 1999 permutaciones, para D_obj ∈ {0, 0.010, 0.012, 0.015, 0.017}.
- **Regla de tamaño (propuesta):** el primer N en {200, 256, 320, 400, 512} cuyo límite inferior de Wilson al 95 % para la potencia sea ≥ 0.8 con **D_obj = 0.012**, más un control nulo cuyo límite superior de Wilson sea ≤ 0.10. Si ninguno lo cumple hasta 512, no se entrena y se replantea.
- **Coste estimado:** G3 hizo 1500 trayectorias en unos 48 min con 2 procesos. Con N = 400 serían 2000 trayectorias, del orden de 1 h.

## 6. Ejecución y separación de funciones
1. **Otro agente** (entorno con el pipeline de G3):
   - potencia;
   - congelar N;
   - entrenar la cohorte;
   - publicar `c2_cohorte.csv` y su resumen por SHA (informe operacional, **sin análisis**).
2. **Claude** corre **una sola vez** el análisis congelado sobre la tabla publicada (`analisis_C2.py`, derivado de `analisis_C1_v2.py` con el universo y la compuerta de régimen de C2, probado antes de congelar con controles y regresiones como en C1).
3. **Responsable:** aprueba la congelación y el cierre.

## 7. Qué no se afirmará
- **Un PASS** confirma la señal en una segunda familia **sintética** y en un régimen concreto. No prueba su transferencia a otros datos reales ni su causalidad.
- **Límite de la comparación:** la base sigue siendo cúbica, no cualquier función de L.
- **H-colapso:** un PASS no demuestra que el colapso sea **necesario**, porque C2 no manipula el colapso. Para eso haría falta otro diseño.

## 8. Decisiones del responsable
1. ¿Nivel primario único s = 0.8, o varios niveles con colapso como co-primarios (con corrección por multiplicidad)?
2. ¿D_obj = 0.012 para fijar el tamaño (conservador frente al 0.017 observado)?
3. ¿Confirmas la separación de funciones: el otro agente entrena y Claude analiza?
