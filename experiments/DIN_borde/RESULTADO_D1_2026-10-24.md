# DIN-borde D1 — resultado exploratorio (2026-10-24)

**Naturaleza:** exploratorio, según `PLAN_D1_exploratorio.md` (commit `5e696e5`, registrado antes de calcular). Son 3120 estados: 780 trayectorias de los splits 12–167 en los updates 5, 50, 150 y 250. **No confirma nada**; los datos ya se usaron en T2-A1.
- **Script:** `d1_escala_forma.py`, corrido en la VM del equipo del responsable (unos 50 s).
- **Salidas:** `d1/d1_estados.csv` y `d1/d1_resumen.json`.
- **Panel:** f es idéntico entre updates en las 780 trayectorias.

## 1. Lo que pasa con M
| update | ρ_borde (Q1 / mediana / Q3) | tr M (mediana) | rango efectivo de M (mediana) | λ_max / tr (mediana) | log ρ̃ (mediana) |
|---|---|---|---|---|---|
| 5 | 4.10 / 4.60 / 5.05 | ≈ 768 | 24.3 (de 27) | 0.065 | −1.79 |
| 50 | — / ≈ 0.2 / — | — | 1.27 | 0.88 | −3.27 |
| 150 | 0.042 / 0.189 / 1.01 | ≈ 24 | 1.19 | 0.91 | −3.28 |
| 250 | 0.037 / 0.179 / 1.09 | ≈ 22 | 1.16 | 0.93 | −3.29 |

**Dos cambios a la vez, casi todo antes del update 50:**
1. **Colapso de forma.** M pasa de casi lleno (rango efectivo ≈ 24 de 27) a **casi rango 1**: un solo modo concentra ≈ 90 % de la traza.
2. **Contracción de escala.** tr M baja en un factor de ≈ 30.

**Piso empírico de la forma.** log ρ̃ se acumula en un piso muy preciso: el mínimo de los 2340 estados posteriores es −3.29588, y log(1/27) = −3.29584, con n = 27 puntos del panel. Es decir, **ρ_borde ≳ √(tr M)/n cuando M colapsa**. Es una observación numérica, no un teorema; queda por demostrar.

## 2. Reparto del cambio, Δlog ρ = ½·Δlog tr M + Δlog ρ̃ (entre el update 5 y cada visita)
| | mediana de Δlog ρ | escala | forma | fracción de la varianza por escala | por forma | por 2·cov |
|---|---|---|---|---|---|---|
| u5 → u50, total | −2.98 | −1.52 | −1.44 | 1.08 | 0.01 | −0.09 |
| u5 → u250, total | −3.22 | −1.72 | −1.46 | 1.05 | 0.01 | −0.05 |
| u5 → u250, dentro del split | −0.01 | +0.01 | −0.01 | 0.99 | 0.05 | −0.04 |

- **En el nivel típico**, la caída de ρ (≈ e³, unas 20 veces) se reparte casi por mitades entre escala y forma.
- **Las diferencias entre trayectorias**, en cambio, salen **casi todas de la escala**, tanto entre splits como dentro del split. La forma colapsa en todas más o menos por igual y se queda en el piso, así que ya no discrimina.
- **Lo que domina es el split:** la varianza total de Δlog ρ es ≈ 4.2, y dentro del split solo ≈ 0.29 (≈ 7 %).

## 3. Precisión en validación (nota exploratoria de T2-A1)
Spearman dentro del split entre la precisión en validación del update 5 y el cambio hasta el update 250: −0.14 con Δlog ρ, −0.09 con la escala y −0.18 con la forma. Va en el mismo sentido que en el cierre: más precisión temprana, más acercamiento al borde. La asociación es algo más fuerte con el término de forma, que es el que menos varianza aporta.

## 4. Lectura (hipótesis, no resultados)
- M = R(F + reg)⁻¹Rᵀ, con R los gradientes de log p(y) de los ejemplos del panel. Que tr M baje y M colapse a rango 1 es compatible con que **el modelo gana confianza en el panel**: los gradientes de la clase correcta se apagan y queda una sola dirección de influencia dominante.
- Si eso es cierto, **acercarse al borde es la forma geométrica de la saturación del softmax por aprendizaje**, no una patología. Y ρ_borde ≈ √(tr M)/n sería, casi, una medida de confianza en el panel.
- Pasos posibles, también exploratorios:
  - comprobar el piso 1/n analíticamente con un M de rango 1;
  - relacionar tr M con la confianza media p(y) sobre el panel en cada update;
  - mirar qué ejemplo o modo domina tras el colapso;
  - medir cuándo ocurre el colapso con updates intermedios entre 5 y 50.
