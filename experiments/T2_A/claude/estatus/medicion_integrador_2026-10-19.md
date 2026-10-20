# Medición de intentos y rechazos de DOP853 — 2026-10-19

Exploratorio. Salida literal de la terminal del usuario (Windows 11, AMD64 Family 23 Model 113 = Ryzen 3900X según el usuario, 24 núcleos lógicos, BLAS a 1 hilo, python 3.12.10, numpy 2.3.5, scipy 1.18.1). No clasifica ninguna visita; no hay outcomes.
Método: contador alrededor de `scipy.integrate._ivp.rk.rk_step`; cada llamada es un intento; rechazos = intentos − pasos aceptados. DOP853 rtol 2e-10 atol 2e-12, 2048 rayos, `dense_output` incluido, mismo problema que `Geometry.rays`.

## Casos

| | j6 update 25 (visita cerrada) | j5 update 25 (copia regenerada) |
|---|---|---|
| script | `scripts/medicion_rechazos.py` `7b0af99d…3328` | `scripts/medicion_rechazos_v2.py` `07318964…d37a` |
| estado | `state_025_regen_j6.npz` `0e3fbfd3…6cac` | `state_025_regen.npz` `845c2251…4776` |
| radio pedido | 0.07883553716312919 (nominal registrado) | 0.0797751845662646 (R_ref basal; el nominal de update 25 no está determinado) |
| terminó | sí (radio alcanzado) | no: tope de 180 s, en t = 0.07443884962628282 (0.933108 R_ref) |
| pasos aceptados | 16 | 469 |
| intentos / rechazos | 21 / 5 (24 %) | 511 / 42 (8 %); paso interrumpido: 0 intentos |
| rhs por intento (medido) | 12.000 | 12.000 |
| nfev | 302 = 16·15 + 5·12 + 2 | 7541 |
| tiempo por paso, mediana (máx) | 0.2975 s (0.6186 s) | 0.3555 s (2.5790 s) |
| dt mínimo / último | 7.70e-4 / 3.96e-3 | 4.51e-8 / 4.64e-8 |

CSV y logs en `margen\` (no versionados): `medicion_rechazos_j6.csv` `8d5a186d…976f`, `medicion_rechazos_j5.csv` `527ebb33…1c69`, `medicion_rechazos.log` `02971725…e21a`, `medicion_rechazos_j5.log` `68fbcb19…8222`.

## Lectura (lo que sí y no se desprende)

- La regla 15 evaluaciones por paso aceptado + 12 por rechazo queda medida en este scipy (j6: 302 = 240 + 60 + 2).
- En j5 el tiempo no se va en rechazos (8 % de los intentos): el paso aceptado se encoge a ~5e-8 y casi todos los intentos se aceptan. El coste por paso (≈0.35 s) es igual al de j6; lo que cambia es cuántos pasos hacen falta.
- Cercanía a la frontera: en el replay MPFR de 169 bits (`RIPG_RESULTADOS_PC.zip`, `task_log.csv`, radios cada 4 pasos) el avance por paso entre r = 0.07432 (paso 118) y 0.07441 (paso 122) fue ≈2.1e-5, y entre 0.07441 y 0.07445 (paso 126) ≈1.0e-5. A r ≈ 0.07444 el float64 avanza ≈4.6e-8 por paso, unas 200–400 veces menos.
- **Hipótesis, sin probar:** en float64 el paso está limitado por el ruido de redondeo en el estimador de error cuando cond(G) es muy grande, no por la geometría. Es compatible con la diferencia de paso, pero no se ha probado (haría falta la misma integración a mayor precisión con estado idéntico, o inspeccionar el estimador de error).
- Limitaciones: una sola medición por caso; la copia regenerada de j5 difiere de `state.npz` de la otra corrida en max|ΔM| = 1.3e-12; el nominal de j5 update 25 no se conoce; el tope de 180 s no es un criterio científico.
- Para el anexo: el tiempo por paso no discrimina entre un caso sano y uno cercano a la frontera; el tamaño de paso aceptado (≈1e-3–4e-3 en j6 frente a ≈5e-8 en j5) y el número de pasos sí cambian órdenes de magnitud. Los rechazos por sí solos no. No se proponen aquí umbrales.

## Adenda: MPFR en j6 y comparación float64/MPFR (2026-10-19)

Salida literal de la terminal del usuario. `scripts/medicion_mpfr_j6.py` (SHA `e1638568…f066`), aceleración MPFR de 169 bits del instrumento (`fast_mpfr_acceleration.py`, `b3d4a804…478e6f63e`), j6/update25, 2048 rayos, radio nominal 0.07883553716312919.

- MPFR: 16 pasos aceptados, 21 intentos, 5 rechazos, 12.000 rhs por intento, nfev 302, paso mínimo 7.70315009666454×10⁻⁴, 15.5 s de mediana por paso (máx. 28.4 s), 308.6 s en total. CSV `12bf3c08…b1b8`, log `baaa2d69…661c`.
- float64 frente a MPFR en j6 (CSV de ambos): mismos intentos por paso (21 = 21); |Δt| ≤ 1.1×10⁻⁷; cociente de dt entre 0.99998 y 1.00002 salvo el último paso; MPFR cuesta 50 veces más (306.6 s frente a 6.1 s).
- j5: float64 y MPFR **coinciden** en la meseta de paso aceptado ≈ 3.2×10⁻⁵ en r ∈ [0.0725, 0.0743); divergen para r ≳ 0.0743. En float64, la meseta se alcanza tras ≈ 61 pasos y 29.3 s (117 pasos y 50.6 s hasta r < 0.0743).
- **Corrección:** la afirmación de arriba de que float64 avanza 200–400 veces menos que MPFR «a ese mismo radio» solo vale para r ≳ 0.0744 (4.6×10⁻⁸ frente a 10⁻⁵). En r ∈ [0.0725, 0.0743) los dos coinciden. Por eso el paso aceptado en la meseta distingue j5 de j6 en ambos regímenes, y la hipótesis del redondeo solo explicaría el colapso final.
