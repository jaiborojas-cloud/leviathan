# T2-A1 fase 0b — resultado de cobertura (2026-10-24)

Protocolo: `PROTOCOLO_0b_v1_CONGELADO.md` (`17b93333…caab`). Instrumento congelado: `instrumento_D.py` v2 (`254ebd83…9663`), sin cambios. Combinación: `cerrar_0b.py` (`060a7a68…9fc2`, solo lectura; no calcula cotas). Salidas en `resultado_0b/`, con originales en `D:\RIPG_DATA\T2_A1\fase0b\`. **Sin X.** Es la muestra de desarrollo (splits 8–11).

## 1. Compuerta: **FALLA**
**D = ? en 44 de 60 visitas primarias** (umbral ≤ 3). Ya fallaba sin terminar el paso 3: las pausas en auditoría son «?» por regla y eran 7.

| | visitas |
|---|---|
| D = 0 (vía A, inyectiva) | 13 |
| D = 1 (vía B, no inyectividad) | 0 |
| D = 1 (vía C, cota con factores dobles) | 3 |
| D = ? | 44 |

Trayectorias (20): Y = 0 en 4, Y = 1 en 1, **Y = ? en 15 (75 %)**.

## 2. Por split
| split | D = 0 | D = 1 | D = ? | qué pasa |
|---|---|---|---|---|
| 9 | 13 | 0 | 2 | geometría sana; 2 auditorías interrumpidas (j13) |
| 8 | 0 | 3 (j9: u50, u150, u250) | 12 | **degeneración temprana**: en 9 casos el haz agota 5000 pasos con los rayos ya lejos en la carta (\|p\| ≈ 60–150) a t ≈ 0.005–0.02; en 2 hay escape pero falla C5; en j9 el escape está limpio y se certifica con U = 0.00017–0.0013 (U₂ = 0.00018–0.0028), entre 15 y 100 veces por debajo de 0.02 |
| 10 | 0 | 0 | 15 | **presupuesto, no geometría**: 8 calibraciones pausadas (sobre todo por tope de tiempo) en las que la cota no encuentra escape hasta t = 0.09; 4 auditorías interrumpidas; 3 evaluadas como INCONCLUSIVE |
| 11 | 0 | 0 | 15 | **degeneración temprana** como split 8 (12 calculadas, todas agotan 5000 pasos), aunque en el update 25 del piloto pasó limpio; 1 auditoría interrumpida; 4 cotas no calculadas |

## 3. Razones de D = ?
| razón | visitas |
|---|---|
| el haz agota 5000 pasos antes de \|p\| = 150 (splits 8 y 11) | 20 |
| sin escape hasta t_bound = 0.09 (split 10) | 8 |
| auditoría interrumpida, sin clasificación (D0-1) | 7 |
| evaluada con clasificación INCONCLUSIVE | 3 |
| escape en el que fallan C5 y V3 (split8 j5 y j7, u50) | 2 |
| paso 3 no calculado (I2 interrumpida) | 4 |

## 4. Medición secundaria D0-1
Las 4 pausas en auditoría del lote 0, repetidas una vez con `--extra-budget`, **siguen pausadas** (tope de pasos, 430–500 intentos, casi el doble del tope normal). Más presupuesto no resuelve las auditorías interrumpidas.

## 5. Recursos
- **Paso 3:** 33 cotas, mediana 34 min, máximo 53 min, 14.5 h en total, sin agotar el tope de 60 min. Las de split 10 tardan 2–6 min; las de split 8 y 11, 20–53 min.
- **Ejecutor:** las visitas nuevas de split 11 se pausan en unos 2 min; las de auditoría, 7–12 min.
- **Disco por visita nueva:** 0.2–1 GB en pausas de calibración; 2–4 GB en pausas de auditoría.
- **Controles:** válidos en I1 y en I2, con U de j5 bit a bit idéntico a P2.

## 6. Cronología de las corridas
| corrida | qué | notas |
|---|---|---|
| I1 (lote 0) | 2026-10-23 15:49 → 2026-10-24 00:31 | completa |
| visitas nuevas (`correr_visitas_0b.py`) | prueba en seco 18:56; corrida ≈18:57 → 19:12 | 21/21 terminadas; todas pausadas |
| I2 (visitas nuevas) | inicio ≈19:16 (controles terminados a las 19:22 y 19:33); **interrumpida** por decisión del responsable a las 21:38–21:41 (Ctrl+C y terminación del proceso hijo de split11_j20 u250, sin `cota.json`) | **se reanudó sola a las 00:31**, al terminar I1, muy probablemente por un comando en cola en la misma consola (el responsable no recuerda haberla relanzado). Recalculó split11_j20 u250 y siguió hasta split11_j23 u150 (05:08). **Interrumpida de nuevo** a las 05:35. 4 cotas sin calcular. Instrumento determinista con reanudación: no afecta a los resultados calculados |
| I3 (repeticiones) | 2026-10-23 21:39 | inmediata |

I2 no escribió su `D_visitas.csv`. Sus filas se reconstruyen con las funciones del instrumento congelado (`asignar_paso2`, `certifica`, `controles`) a partir de las salidas existentes (`cerrar_0b.py`).

## 7. Lectura y consecuencia
- **Lo que se aprende:** hay tres regímenes distintos, y se agrupan por split.
  1. Geometría sana (split 9): el instrumento funciona.
  2. **Falta de presupuesto de calibración** (split 10): la exponencial avanza normal, pero la búsqueda del radio de área 0.02 agota su tiempo.
  3. **Degeneración temprana** (splits 8 y 11): la métrica colapsa a radios diminutos. Cuando el escape es limpio, la vía C lo certifica incluso con factores dobles (split8_j9); cuando el integrador se arrastra, nada lo resuelve.
- **Consecuencia según el diseño v2:** el instrumento **no** se reajusta con estos datos. El desenlace «disco de área 0.02» no es viable en esta cohorte. Toca decidir entre una **versión nueva documentada del desenlace o del instrumento** (repetiría 0a y 0b) y abandonar el diseño.
- Antecedentes para el replanteo:
  - E16-AF Q1: r_deg se mide de forma estable en geometrías sin patología;
  - split 10 parece recuperable con más tiempo de calibración o con un radio fijo;
  - splits 8 y 11 necesitan entender primero **por qué** se arrastra el integrador (diagnóstico de desarrollo, con X cerrado).
