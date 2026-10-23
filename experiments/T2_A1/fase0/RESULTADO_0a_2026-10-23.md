# T2-A1 fase 0a — resultado (2026-10-23)

Instrumento: `instrumento_D.py` **v2** (`254ebd83…9663`), que importa sin cambios `certificar_t5.py` v4 (`9e0c12a2…0b7d`). Protocolo: `PROTOCOLO_instrumento_D_v1_CONGELADO.md` (`a380e6c3…1f97`).

## Compuerta 0a: **PASA**
| prueba | dónde | resultado |
|---|---|---|
| P1 equivalencia con v4 | contenedor | j6 con t₀ y T⁺ forzados: U = 0.02980103, igual que v4 (`PRUEBAS_0a_contenedor_2026-10-23.md`) |
| **P2** equivalencia en j5, j7, j8 | equipo del responsable (Windows 11, Python 3.12.10, numpy 2.3.5), 2026-10-23 11:20–11:41 | **bit a bit idéntico a la corrida 4** en U, T*, κ̂, A₀ y U(t₁) de los tres casos (tabla abajo) |
| P3 asignación del piloto | sección 3 | conforme a lo previsto |
| P4 sin escape | contenedor | j6 sin forzar → «sin escape en la carta P» → D = ? |

### P2 (salidas en `P2_v2/`; originales en `D:\RIPG_DATA\T2_A1\fase0a\P2_2026-10-23_v2\`)
| | j5 | j7 | j8 (control) |
|---|---|---|---|
| U (= corrida 4) | 0.019426498826093774 | 0.019743835167572048 | 70.94700900141211 |
| T* (= corrida 4) | 0.07447464619553969 | 0.07466422956747366 | 0.08746544626359999 |
| κ̂ (= corrida 4) | 14092.703289198169 | 25680.04960840616 | 311421.34124829003 |
| A₀ (= corrida 4) | 0.016879598137949883 | 0.017138841638158733 | 0.01954285154776756 |
| V1 | ok | ok | ok |
| veredicto de `un_caso` | certificada, pendiente de V1/V2 | no certificada: U > 0.0195 | no certificada: 22 rayos sin carta de cara y U > 0.0195 (como en la corrida 4) |
| U releído de `rayos.csv` | coincide | coincide | coincide |
| **U₂ (factores dobles)** | **0.020153** | 0.020809 | 4971.4 |
| tiempo | 310 s | 312 s | 621 s |

**Controles de corrida (sección 3.3 del protocolo):** j5 da U = 0.019426498826 con V1 (control positivo válido); j8 no certifica, con U ≥ 0.0239 y V1 (V2 válido). Los controles exigen el veredicto de `un_caso` con factores normales, no U₂; ver la sección 4.

**Intento previo con v1:** falló en Windows por `PicklingError` antes de calcular nada. Se conserva en `D:\RIPG_DATA\T2_A1\fase0a\P2_2026-10-23\` (ver `PRUEBAS_0a_contenedor_2026-10-23.md`, sección v2).

## 3. P3: asignación de las 20 visitas u25 del piloto
Las salidas del piloto vienen de ejecutores anteriores al v12, con formatos distintos. P3 aplica la regla de la sección 2 del protocolo a sus disposiciones documentadas (`../../T2_A/claude/piloto/CIERRE_PILOTO_20_2026-10-21.md`) y a la cota de P2.

| visitas | salida del ejecutor | D | vía |
|---|---|---|---|
| 15 | evaluadas, INJECTIVE_AT_NOMINAL_RADIUS | 0 | A |
| split8_j8 | INJECTIVE por la reevaluación D4 (T4′) | 0 | A |
| split10_j17, split8_j9 | evaluadas, GEOMETRIC_NONINJECTIVITY | 1 | B |
| split8_j5 | calibración pausada sin radio nominal → paso 3 | **?** | U = 0.019426 ≤ 0.0195, pero **U₂ = 0.020153 > 0.0195** |
| split8_j7 | calibración pausada sin radio nominal → paso 3 | ? | U = 0.019744 > 0.0195 |

Así lo prevé el protocolo para j5 (P3: «D = 1 si U₂ ≤ 0.0195; si no, ?; cualquiera de los dos se acepta»). Esto es un resultado de desarrollo sobre el update 25. **No reclasifica nada de T2-A0**: j5 sigue certificado T5 bajo el protocolo de T2-A0.

## 4. Lectura
- **El instrumento queda congelado** en v2 (sección 4 del protocolo): código, factores, t₀, rayo designado y topes. 0b lo aplica sin cambios. Queda una versión de reserva (D0-3) solo para defectos de implementación.
- **Con factores dobles, ni j5 certifica.** j5 era el caso más favorable conocido (U/0.02 = 0.971). Es **previsible**, aunque no está medido, que la vía C resuelva pocas de las pausas de calibración del lote 0, y que la compuerta de cobertura de 0b (≤ 3 visitas con D = ? de 60) falle. 0b es la medición que lo decide. Relajar los factores ahora, tras ver j5, sería ajustar la regla a los datos.
- **Control positivo:** en las corridas de 0b, el control j5 se valida con U (factores normales), como dice la sección 3.3. Con factores dobles no existe hoy ningún caso conocido que certifique, así que la vía C completa con U₂ no tiene control positivo. Se declara como limitación.
