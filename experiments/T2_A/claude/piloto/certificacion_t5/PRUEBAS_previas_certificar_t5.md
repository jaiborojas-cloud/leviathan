# Pruebas previas de `certificar_t5.py` (sección 9 del protocolo) — 2026-10-21

**No cuentan para la certificación.** Se hicieron solo con geometrías sintéticas y con split8_j6_true (sin escape). **Antes de registrar el hash no se ejecutó nada sobre j5, j7 ni j8.** Contenedor Linux, Python 3.13, numpy 2.5.3, scipy 1.18.1, mpmath 1.4.1, 2 CPU. `geometry.py` b4d1e0e4… y `audit.py` d357bfcc… del archivo importado (`docs/archive/import-2026-10-17/extracted/j7_update25_execution_sources/instrument/`).

## 1. Pruebas unitarias de la carta de cara (sintética de 27 componentes)
En tres puntos con |p| = 3.2, 8.2 y 20.9:
- **K por los tres evaluadores** (float64 en P, mpmath de 50 dígitos en P, carta de cara): coinciden a ≈ 10⁻¹³ relativo (p. ej., −1338.27458599337 / …35 / …56).
- **C2** (identidad de jacobianos): ≈ 10⁻¹⁵.
- **Geodésica integrada en la carta P y en la carta de cara** sobre 0.01 de radio: diferencias de 3.5×10⁻¹⁴ en a y de 4×10⁻¹⁴ relativo en b.

## 2. Defectos encontrados y corregidos (antes de registrar el hash)
1. **Cara elegida demasiado pronto.** El script tomaba la arista con los pesos en |p| = 40, cuando el rayo aún no se ha decidido, y la carta resultante no llegaba al borde. Ahora la arista es aquella **hacia la que se dirige** el rayo (su último estado disponible), que es lo que dice 4.4.1.
2. **El rayo designado no siempre llega a |p| = 40 dentro del haz**, porque el haz se detiene cuando *otro* rayo llega a 150. Ahora se sigue solo ese rayo en la carta P (mismo DOP853 y tolerancias) hasta |p| ≥ 40. El protocolo no fija cómo se llega a ese punto.
3. **Memoria.** Una sintética con escape lento llenó la memoria del contenedor, unos 0.5 MB por paso con 2048 rayos. Se añade un tope operacional de 5000 pasos por integración; si se alcanza, el resultado es «no certificado», sin cuelgue. Los casos reales llegan a |p| = 150 en 110–220 pasos. Además, el muestreo de K se evalúa ahora por lotes acotados, sin acumular millones de puntos.
4. **Tolerancias relativas cuando K ≈ 0.** En la sintética plana, el solape float64/mpmath (10⁻⁶) y la convergencia 513/1025 de κ̂ (10⁻³) daban errores relativos sin sentido sobre valores de 10⁻²⁵. **Interpretación declarada:** ambas se miden frente a **max(|K|, 1)**. Una curvatura de orden 1 es despreciable frente al κ admisible (≈ 10⁵), así que esto no relaja nada que importe para la cota.

## 3. Corridas de extremo a extremo
| Prueba | Qué ejercita | Resultado |
|---|---|---|
| Sintética de 3 componentes (`s8`, plana) | haz hasta \|p\| = 150, t₀, área y variantes, Jacobi, V3, escape del rayo designado (C1–C6, T* con tolerancias ×1 y ×1/100), continuación con 148 rayos a carta de cara, solape, muestreo 513/1025, cota y V1 | C1–C6 OK; T* = 0.00512844693035, δ_T = 2.7×10⁻¹³; V3 1.5×10⁻⁶; **V1 OK** (U(t₁) = 3.39×10⁻⁵ ≥ A medida 2.77×10⁻⁵); 16 min. Única falla: la convergencia de κ̂ con K ≈ 0, corregida en (4). Esta corrida usó la versión anterior a esa corrección |
| **split8_j6_true** (curvatura real, sin escape), t₀ forzado en 0.05 y T⁺ forzado en el radio nominal 0.07883553716312588 (allí el área es exactamente 0.02) | cota en geometría real con curvatura | κ̂ = 522.3 (513 y 1025 iguales); Δ = 0.0255; cosh = 1.76; **U = 0.02980 ≥ 0.02**: la cota no subestima el área real. V3 1.25×10⁻⁶; δ_disc 3.4×10⁻⁸; ε_θ ≈ 3×10⁻¹⁶. Versión final del script (SHA-256 abajo); 95 s |

La prueba de j6 es una falsación con curvatura real sobre un tramo ≈ 8 veces más largo que el de j5 y j7. La cota sobreestima por un factor de 1.49, como se espera de una comparación de Grönwall con κ uniforme.

**Lo que no se probó:** la carta de cara con 27 componentes y β ≥ 8, como en j5 y j7. Las sintéticas de 27 componentes escaparon hacia aristas con β < 2 o por caminos lentos. Esa parte se valida en la corrida real con V1, V2 y C1–C6.

## 4. Versión registrada
`certificar_t5.py` SHA-256 `afc23c71640616778a79e28ed667b82aa9d746f3ad9c2bb7fc1aef1f04ebb268` (en `MANIFIESTO_scripts_certificacion_T5.sha256`).

## 5. v2 (2026-10-21 ≈15:45), tras la corrida 1
- **Cambio único:** la cara se identifica por la dirección de avance (tasas f·v) y no por los pesos actuales. Motivo y evidencia en `RESULTADO_corrida1_v1_2026-10-21.md`.
- **Regresión en la sintética de 3 componentes:** resultado idéntico al de v1 hasta el escape y la continuación (T* = 0.005128446930349743, δ_T = 2.7×10⁻¹³, C1–C6 OK, 148 rayos a carta de cara, 0 problemas). El resto del código no cambió.
- **No se ejecutó la v2 sobre j5, j7 ni j8 antes de registrar su hash.**
- SHA-256 v2: `5009cab8262149079430307176d854501c959901b2f26c0ff978a4132ba439c4`.

## 6. v3 (2026-10-21 ≈16:05), tras la corrida 2
- **Cambio único:** si la carta P se vuelve singular (float64) en la continuación, ya sea al iniciar el integrador o dentro de un paso, los rayos con |p| ≥ 40 pasan a la carta de cara desde su último estado aceptado. Si no hay ninguno, la continuación se detiene y el muestreo de K se trunca (registrado como problema). Motivo: `RESULTADO_corrida2_v2_2026-10-21.md`.
- **Prueba forzada en la sintética de 3 componentes:** con `LinAlgError` inyectado en la continuación cuando |p| > 120, se detectó la singularidad al iniciar, 1113 rayos pasaron a la carta de cara, hubo 0 problemas y el muestreo de 513 puntos terminó (18 921 puntos en carta de cara). Script de la prueba: `forzar_singular.py`, fuera del repositorio.
- **No se ejecutó la v3 sobre j5, j7 ni j8 antes de registrar su hash.**
- SHA-256 v3: `7e2fc5b6f3e112657bbcc21fef15f223d90c64959edc395550c81d88edf5c8b5`.

## 7. v4 (2026-10-21 ≈16:56), tras la corrida 3; última versión (opción B del responsable)
- **Cambio único:** cualquier excepción al construir o integrar la carta de cara de un rayo, o al calcular el límite del rayo designado, se registra como **problema de ese rayo**. Su muestreo de K se trunca en el punto de entrega. El caso sigue y, con algún problema, queda «no certificado».
- **Prueba forzada en la sintética de 3 componentes:** singularidad inyectada en la continuación más desborde forzado en la carta de cara de 3 rayos entregados. Se registraron 3 problemas (rayos 574–576, `OverflowError`), el caso terminó sin errores, U y V1 se calcularon igual que en las pruebas anteriores (U = 0.00012274; V1 OK) y el veredicto fue «no certificada» por esos 3 problemas.
- **No se ejecutó la v4 sobre j5, j7 ni j8 antes de registrar su hash.**
- SHA-256 v4: `9e0c12a2a3d2fde95bf04cd729e2e7df5a237fc757ca8ee82d40dd7935b90b7d`.
