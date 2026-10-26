# DIN-borde D9 — ¿el colapso de M predice la generalización? (plan exploratorio, 2026-10-26)

**Naturaleza:** **exploratorio o de descubrimiento**. Se registra antes de calcular. Datos: los splits 12–167 de Wine (los de T2-A1, D1–D7 y R1), que ya están gastados para confirmar. La pérdida en **test** **nunca** se ha calculado en ellos, porque ningún análisis previo la usó. Lo pidió el responsable el 2026-10-26 a las 10:00 («primero D9; si algo no sale como esperábamos, medimos Q13»).

## Pregunta
¿Alguna medida **geométrica** del colapso de M en la ventana de los updates 10–30 predice la **generalización final** (pérdida en test en el update 250), **más allá** de las medidas baratas de ese mismo momento: pérdida de entrenamiento, pérdida y precisión de validación, y la confianza X?

## Datos nuevos (`d9_generalizacion.py`, en el equipo del responsable; no entrena nada nuevo más allá del update 50)
- **Updates 10, 20, 30 y 50:** se reentrena desde checkpoint_005 con la mecánica de D6. Se calculan la pérdida y la precisión de entrenamiento, validación (el panel) y **test**, y X(t) = log(1 − p_min,val) por logsumexp.
- **Compuerta:** los parámetros en el update 50 deben quedar a 1e-12 o menos de los del checkpoint del update 50 de la fase 2 de T2-A1.
- **Update 250:** se carga el checkpoint ya guardado de la fase 2 y se calculan las mismas pérdidas y precisiones, incluidas las de test.
- **Partición:** test = `core.load_split(s)`, el tercer bloque (27 ejemplos), nunca usado para entrenar ni para el panel.

## Variables
- **Desenlace primario:** Y_T = pérdida de entropía cruzada en test en el update 250.
- **Desenlaces secundarios:** precisión en test en el 250, y la brecha = pérdida en test − pérdida de entrenamiento en el 250.
- **Candidatos geométricos,** para t ∈ {10, 20, 30} (12 en total):
  - c(t) = M_kk,max/tr (de d6);
  - log tr M(t) (de d6);
  - log ρ_caras(t) (de R1, etapa 2);
  - Δc, la velocidad de colapso entre 10 y 20 y entre 20 y 30.
- **Base barata del mismo t:** pérdida de entrenamiento, pérdida de validación, precisión de validación y X(t), lineales y centradas dentro del split.

## Estimando (por candidato y por t)
- **D fuera de muestra** del candidato sobre la base barata, con la maquinaria de C1:
  - centrado dentro del split;
  - 10 bloques de splits (semilla 260010);
  - permutación del candidato dentro del split (2000, semilla 320001 + índice).
- **Controles:**
  - el D de la base barata frente a nada, para ver cuánto predicen las medidas baratas solas;
  - el D de cada candidato sin base.

## Regla para proponer un confirmatorio (al responsable)
Se propone un candidato si cumple **las tres** condiciones:
- D > 0.02;
- p < 0.05/12 (Bonferroni sobre los 12 candidatos del desenlace primario);
- el mismo signo de la pendiente en los splits pares y los impares.

**Si ninguno pasa:** «la geometría del colapso no añade predicción de la generalización sobre las medidas baratas en Wine». Siguiente paso: Q13.

## Errata (2026-10-26 10:09, antes de calcular nada)
El texto decía «12 candidatos», pero la lista tiene **11**: 3 medidas (c, log tr M y log ρ_caras) en 3 momentos (10, 20 y 30), que son 9, más Δc entre 10 y 20 y entre 20 y 30. El error lo detectó el agente de D9g. **Decisión del responsable:** se analizan **los 11 candidatos enumerados** y se **mantiene el umbral p < 0.05/12**, algo más conservador que 0.05/11. No se añade Δc entre 10 y 30, porque es la suma de los otros dos. La misma corrección vale para D9g.
