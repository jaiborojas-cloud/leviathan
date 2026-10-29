# DIN-E-escala — ¿la modulación sigue a la concentración de M o a la escala de los logits? Plan exploratorio v1 (2026-10-28)

**Naturaleza:** **exploratorio**, registrado antes de calcular. Lo pidió el responsable a las 20:50 («camino 1»).
- **Datos:** se reutilizan las cohortes Q13-DR y Q13-M2, ya gastadas para confirmar. No se entrena nada.
- **Qué no puede hacer:** ningún resultado de aquí confirma algo. Si aparece una separación, necesita un confirmatorio con datos nuevos.

## 1. Pregunta
En Q13-DR y Q13-M2, la señal temprana D baja al bajar la concentración de M (c250). Las tres intervenciones (LS, LP y WD) también reducen la escala de los logits; según Beck et al., LS y LP fijan un logit objetivo finito por ejemplo.

**¿D sigue mejor a c o a la escala de los logits?**

## 2. Medidas nuevas (solo de los logits del panel en u250, ya guardados)
Por trayectoria, con z_i ∈ R³ los logits del ejemplo i del panel (n = 27):
- **S, escala (primaria):** S = media sobre el panel de la desviación estándar de los 3 logits de cada ejemplo. Es invariante a sumar una constante, igual que la softmax.
- **m, margen (secundaria):** media sobre el panel de z_{i,y} − max_{c≠y} z_{i,c}.
- **p, confianza (secundaria):** media sobre el panel de la probabilidad softmax máxima.

**Script:** `extraer_escala.py`. Solo lee `u250_state.npz` (clave `logits`) y la columna `labels` del mismo archivo. Escribe una tabla nueva por cohorte, sin tocar nada existente. No lee X, ρ ni D.

## 3. Análisis (todo descriptivo)
**E1, por nivel (17 puntos):**
- **Niveles:** Q13-DR L0–L5 (6) y Q13-M2 A0, LP1–LP5 y WD1–WD5 (11).
- **Variables:**
  - D_ℓ: el D de los JSON congelados;
  - c_ℓ: la mediana de c250 de las filas comunes, de los JSON;
  - S_ℓ, m_ℓ y p_ℓ: medianas de las trayectorias del nivel.
- **Qué se reporta:**
  - Spearman de D con c y de D con S;
  - Spearman **parcial** de D con c dado S, y de D con S dado c, sobre los residuos de los rangos;
  - MCO de D sobre c y S estandarizados.
- **Diagnóstico clave:** a c parecida, ¿S difiere entre familias (WD frente a LS/LP)? Si a igual c la escala difiere y D no, c sigue a D mejor que S, y al revés.

**E2, dentro de los controles sin manipular (observacional):**
- **Datos:** Q13-DR L0 (200 × 5) y Q13-M2 A0 (320 × 5). Ahí c y S varían solo por azar de los datos y de la inicialización.
- **Qué se calcula:** el D de C1 por cuartiles de c y por cuartiles de S, como en el descriptivo de Q13-DR. Usa 499 permutaciones, solo como referencia.

**Lectura** (regla fijada ahora; sigue siendo descriptiva):
- **«c sigue mejor a D»:** el Spearman parcial de D con c dado S supera al de D con S dado c por al menos 0.2, **y** en E2 el gradiente de D entre cuartiles es mayor con c que con S.
- **«S sigue mejor a D»:** lo inverso.
- **En otro caso:** **«no se separan con estos datos»**, que es lo esperable si c y S se mueven juntos.

## 4. Limitaciones declaradas antes de ver nada
- **Pocos puntos:** 17 niveles, y c y S probablemente muy correlacionados. La separación puede ser imposible con estos datos.
- **Cohortes distintas:** Q13-DR y Q13-M2 tienen semillas distintas. Sus A0 sirven como referencia cruzada.
- **Sin confirmación posible:** cualquier patrón se trata como hipótesis para un diseño nuevo que mueva c y S por separado.
