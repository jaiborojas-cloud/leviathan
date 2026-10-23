# T2-A1, fase 0 — Protocolo del instrumento D, v1 CONGELADO (2026-10-23)

**Estado:** **CONGELADO** el 2026-10-23 a las 08:35 (hora de México) por aprobación del responsable («aprobado, adelante con a0»). Contenido técnico idéntico a `PROTOCOLO_instrumento_D_BORRADOR_v1.md` (que se conserva); solo cambian este encabezado y la sección 7. El código se escribe **después** de esta congelación y sus hashes se registran antes de cualquier corrida sobre j5, j7 o j8. Diseño marco: [DISENO_T2A1_BORRADOR_v2.md](../DISENO_T2A1_BORRADOR_v2.md).

**Naturaleza.** Instrumento nuevo de T2-A1. **No es una v5 de la certificación T5 de T2-A0**: el compromiso de no hacer v5 sigue vigente y los resultados de j5 y j7 en T2-A0 no se tocan. Aquí se reutiliza el *método* T5 v1 (`../../T2_A/claude/piloto/certificacion_t5/PROTOCOLO_certificacion_T5_v1_CONGELADO.md`), con sus factores y margen sin cambios, dentro de una regla de decisión nueva. **La única exigencia añadida** es que la cota pase también con factores dobles (sección 2, paso 3).

## 1. Qué mide
Para una visita (trayectoria, update k) con estado (M, f) del update k, D responde: **¿se puede construir con la exponencial desde P0 = (0,0) un disco simple de área 0.02?**

| D | significado | vía |
|---|---|---|
| 0 | sí: disco de área 0.02 sin pérdida de inyectividad detectada | **A**: auditoría heredada, INJECTIVE_AT_NOMINAL_RADIUS |
| 1 | no: antes de llegar a 0.02 el mapa se pliega o tiene conjugado | **B**: auditoría heredada, GEOMETRIC_NONINJECTIVITY |
| 1 | no: una geodésica sale de la familia softmax a longitud finita y el área alcanzada es < 0.02 | **C**: cota de área certificada (método T5 v1) |
| ? | no se establece ninguna de las anteriores | se registra la razón; **nunca** cuenta como 0 |

La vía C es una propiedad geométrica de (M, f): la geodésica sale del dominio de la familia (los pesos fuera de una cara tienden a 0 con P finito, criterio C6), no por una singularidad de la carta. D agrupa tres mecanismos; la vía (A, B o C) se registra siempre para el análisis descriptivo.

## 2. Procedimiento por visita
**Paso 1. Ejecutor v12 sin cambios** (`../../T2_A/claude/produccion/visita_produccion_v12.py`, `2381fbcc…3347`), con los topes del anexo v1.1. En 0b se reutilizan las salidas del lote 0, que usaron este mismo ejecutor.

**Paso 2. Asignación según la salida del ejecutor:**

| salida del ejecutor | D |
|---|---|
| VISIT_EVALUATED, INJECTIVE_AT_NOMINAL_RADIUS | 0 (A) |
| VISIT_EVALUATED, GEOMETRIC_NONINJECTIVITY | 1 (B) |
| VISIT_EVALUATED, INCONCLUSIVE o NUMERICAL_FAILURE | ? |
| PAUSED, con `nominal.json` (el radio nominal existe, pero la pausa ocurrió **durante** la auditoría, que quedó interrumpida y **sin clasificación**) | ? **[DECISIÓN D0-1]** |
| PAUSED, **sin** `nominal.json` (la calibración no alcanzó 0.02, ni con T4′) | **paso 3** |
| ERROR_DE_EJECUCION | una repetición en `u<k>_r1`; si persiste, ? |

**Paso 3. Cota de área (vía C).** Método T5 v1 sin cambios de fondo:
- t₀ = primer paso aceptado con max|p| ≥ 10; rayo designado = argmax|p| en t₀; 2048 rayos, DOP853 2×10⁻¹⁰/2×10⁻¹², `t_bound` 0.09;
- (i) C1–C6 en la carta de cara del rayo designado;
- (ii) δ_disc ≤ 10⁻⁵ y V3 ≤ 10⁻⁵;
- (iii) U = A₀ + F_disc·δ_disc + Δ·L⁺·(1 + 10 ε_θ), con F_K = 4, F_T = 10, F_disc = 10;
- **D = 1 (C)** si se cumplen (i), (ii), V1 del propio caso (U(t₀→t₁) ≥ A medida en t₁), V4, **U ≤ 0.0195** y además **U₂ ≤ 0.0195**, donde U₂ es la misma cota con factores dobles (F_K = 8, F_T = 20, F_disc = 20). Si falla cualquiera, **D = ?**, con la razón.
- **Por qué los factores dobles:** los factores de T5 v1 se validaron en solo tres estados. Si la cota subestimara el área con más frecuencia en estados de curvatura alta (por ejemplo, por un pico de |K| no muestreado), los falsos D = 1 podrían correlacionarse con X y sesgar el resultado a favor de la hipótesis. Los factores dobles hacen la vía C más conservadora: resuelve menos casos, pero corta ese canal de sesgo.
- Tope de pared del paso 3: **[DECISIÓN D0-2]**, propuesta 60 min. Al agotarse, D = ?.

**Paso 4. Registro** `D.json` por visita: D, vía, razón si es ?, U, U₂ y U/0.02 si hubo paso 3, hashes de `state.npz`, del ejecutor y del script D, y tiempos. **Sin X.**

## 3. Generalización necesaria del script T5 v4
Lo único que cambia respecto a `certificar_t5.py` v4 (`9e0c12a2…0b7d`):
1. Acepta cualquier `state.npz` (ruta y hash como argumentos), en vez de los tres estados escritos en el código.
2. Un caso sin escape (ningún rayo llega a |p| ≥ 10 antes de `t_bound`) termina como «sin escape», D = ?.
3. **Controles por corrida** (lote de visitas): en cada corrida se ejecutan también j5/u25 (debe dar `T5_CERTIFICADA` con U = 0.019426498826, a 10⁻⁹ relativo) y j8/u25 (V2: no certificado, U ≥ 0.0239). **Si un control falla, ningún caso de esa corrida cuenta.**
4. Cálculo de U₂ con factores dobles a partir de los mismos ingredientes (A₀, δ_disc, κ̂, δ_T, j y j′ en t₀). No se integra nada nuevo.
5. Salida `D.json` (paso 4).

No cambian t₀, rayo designado, carta de cara, κ̂, F_K, F_T, F_disc (para U), margen ni tolerancias.

## 4. Pruebas de la fase 0a (antes de tocar los datos de 0b)
| prueba | caso | se exige |
|---|---|---|
| P1 sintéticas | geometrías de `PRUEBAS_previas_certificar_t5.md` | mismas salidas que v4 |
| P2 equivalencia | j5, j7, j8 en u25 con el script generalizado | U, T*, κ̂ y A₀ idénticos bit a bit a la corrida 4; se reporta U₂ |
| P3 asignación | las 20 visitas u25 del piloto (salidas ya existentes) | j8 → 0 (A, vía D4); j5 → 1 (C) **si U₂ ≤ 0.0195**, y si no → ? (cualquiera de los dos se acepta y se reporta: no es un fallo de la prueba); j7 → ? (U = 0.019744 > 0.0195); el resto según su clasificación del piloto |
| P4 sin escape | split8_j6/u25 (sin escape) | paso 3 termina como «sin escape» si se le fuerza |

Los casos de P2 y P3 ya son conocidos: son controles, no evidencia.

**Compuerta 0a:** P1–P4 pasan. **Al cerrarla, el instrumento queda congelado** (código con su hash, factores, t₀, rayo designado, topes); 0b lo aplica sin cambios. Si un defecto de implementación lo impide, se corrige como en T5: versión nueva registrada antes de correr y causa documentada. **Máximo 3 versiones [DECISIÓN D0-3]**; si la tercera falla, la vía C se abandona y D se queda solo con A y B.

## 5. Fase 0b: cobertura (resumen; protocolo propio al congelar 0a)
- **Visitas de cobertura primaria:** los updates 50, 150 y 250 de los splits 8–11, es decir, 20 trayectorias × 3 = 60 visitas. 43 ya existen en el lote 0; faltan split10_j19 u150 y u250 y las 15 de split 11, que se corren con el ejecutor v12.
- **Cobertura secundaria:** las 128 visitas del lote 0.
- **Compuerta 0b (diseño v2):** D = ? en ≤ 5 % de las 60 visitas primarias, es decir, a lo sumo 3. Se reporta también la fracción de trayectorias con Y = ? (20 trayectorias).
- **0b solo mide.** Si la compuerta falla, el instrumento no se reajusta con esos datos: o una versión nueva documentada que repite 0a y 0b, o se abandona el diseño.
- **Pausas en la auditoría [D0-1]:** en 0b se repiten una vez con `--extra-budget` para medir si se resuelven. La regla para la fase confirmatoria se fija en 0c.
- Se miden tiempo y disco por visita y por vía. X sigue cerrado. Los desenlaces D de la muestra de desarrollo se ven: está previsto.

## 6. Qué no se afirma
- La vía C no es aritmética de intervalos: es una cadena de desigualdades con factores de seguridad declarados (D-T5-1 de T2-A0).
- V1 y V2 prueban que la cota no subestima en los casos de control, no en general.
- D ≠ Y de T2-A0. Ningún D reclasifica visitas de T2-A0.

## 7. Decisiones adoptadas (2026-10-23 08:35)
- **D0-1.** Las pausas durante la auditoría (radio nominal existente, sin clasificación) son D = ? en el paso 2. En 0b se repiten **una vez** con `--extra-budget` para medir si se resuelven; la regla para la fase confirmatoria se fija en 0c.
- **D0-2.** Tope de pared del paso 3: **60 min** por visita. Al agotarse, D = ?. En 0b se reportan los tiempos reales.
- **D0-3.** Máximo **3 versiones** del script en 0a. Si la tercera no pasa P1–P4, la vía C se abandona y D se queda con A y B.
