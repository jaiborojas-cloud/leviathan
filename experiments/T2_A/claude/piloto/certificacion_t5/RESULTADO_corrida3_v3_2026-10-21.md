# Corrida 3 de la certificación de T5 (script v3, `7e2fc5b6…`) — 2026-10-21 ≈16:13–16:21

Mismo equipo y entorno que las corridas 1 y 2. Salida en `D:\RIPG_DATA\T2_A\expediente\certificacion_t5\salida_v3_2026-10-21\`; las salidas pequeñas están en `corrida3_v3/`. **Se conserva tal cual.**

## Resultado oficial de esta corrida
`procedimiento_valido` = falso. El control j8 volvió a terminar en `ERROR_DE_EJECUCION`, así que V1 en j8 y V2 no se evaluaron.
- **j5:** `T5_NO_CERTIFICADA`, solo por la invalidez del procedimiento. U = 0.019426498826093774.
- **j7:** `T5_NO_CERTIFICADA` por (iii): U = 0.019743835167572048 > 0.0195.

Ningún estado cambia. No asigna Y.

## Reproducibilidad
En j5 y j7, U, T*, κ̂, A₀ y U(t₁) de V1 son **idénticos bit a bit** a la corrida 2 (v2). El cambio de v3 no los tocó, como se había declarado.

## j8
- La singularidad de la carta P en la continuación se detectó al iniciar el integrador, en t = 0.0861038198 (nueva vía de v3).
- Los rayos con |p| ≥ 40 pasaron a la carta de cara.
- La integración en la carta de cara de uno de esos rayos desbordó al evaluar el punto de arranque (`OverflowError` en `exp(α·a)`). Lo compatible con eso es un rayo cuya dirección de avance no apunta a una arista (dos componentes sobrevivientes), sino probablemente a un vértice o a otra arista. j8 tiene varios sectores que escapan. La carta de cara no es válida para ese rayo, y el script no trataba ese fallo por rayo como un «problema»: lo dejaba caer como error de ejecución.

## Decisión del responsable (2026-10-21 ≈16:37): opción B, último intento
Se prepara una v4 con un único cambio: si un rayo no admite carta de cara (cualquier excepción al construirla o al integrarla), se registra como **problema de ese rayo** y su muestreo de K se trunca en el punto de entrega, en lugar de detener el caso. **Compromiso escrito antes de correr la v4:** si la corrida 4 falla por cualquier motivo, se cierra como la opción A. El resultado oficial queda entonces «T5 no certificado» para j5 y j7, y U = 0.019426 y U = 0.019744 se reportan a E2 como evidencia, no como certificación. No habrá v5.
