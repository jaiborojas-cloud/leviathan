# Corrida 4 de la certificación de T5 (script v4, `9e0c12a2…`, última) — 2026-10-21 ≈21:04–21:25

Corrida del responsable (Windows 11, Python 3.12.10, numpy 2.3.5, scipy 1.18.1, 24 CPU), bajo el protocolo v1 congelado (`3d2e4882…`). Salida en `D:\RIPG_DATA\T2_A\expediente\certificacion_t5\salida_v4_2026-10-21\`; las salidas pequeñas están en `corrida4_v4/`. El texto rojo que mostró PowerShell (`NativeCommandError`) fueron avisos de numpy y scipy enviados a stderr. No hubo interrupción ni relanzamiento.

## Resultado
**`procedimiento_valido` = verdadero** (V1 en j5, j7 y j8; V2 en j8).

| caso | estado T5 | U | U/0.02 | razón |
|---|---|---|---|---|
| **split8_j5_true** | **`T5_CERTIFICADA`** | 0.019426498826 | 0.971 | todos los criterios: (i) C1–C6, (ii) δ_disc 4.8×10⁻⁸, V3 9.4×10⁻⁸, V4 8×10⁻¹², K convergido, U ≤ 0.0195 |
| **split8_j7_true** | `T5_NO_CERTIFICADA` | 0.019743835168 | 0.987 | (iii): U > 0.0195 (aunque U < 0.02) |
| split8_j8_true (control) | `T5_NO_CERTIFICADA`, como se exige | 70.95 | 3547 | 21 rayos sin carta de cara válida; muestreo de K truncado en t = 0.0861; (iii) |

**Validaciones**
- **V1** (la cota no subestima el área medida en t₁):

  | | U(t₁) | A medida en t₁ |
  |---|---|---|
  | j5 | 0.0176388 | 0.0176046 |
  | j7 | 0.0176880 | 0.0176735 |
  | j8 | 0.0241438 | 0.0212637 |

- **V2:** j8 no se certifica y su U (70.9) supera la área medida 0.0239.

**Reproducibilidad.** En j5 y j7, U, T*, κ̂, A₀ y U(t₁) son idénticos bit a bit en las corridas 2, 3 y 4.

## Qué significa (y qué no)
- **j5:** con el procedimiento congelado, el disco construido con la exponencial **deja de existir antes de alcanzar área 0.02**:
  - un rayo (1776) sale de la familia softmax por la arista 6/13 (w20 → 0) en r = 0.0744746462, a distancia intrínseca finita y de forma transversal (db/dr = −228.0);
  - el área en ese radio está acotada por U = 0.01943 < 0.0195.

  Es la primera certificación de T5 (`NOMINAL_DISK_NOT_CONSTRUCTIBLE_RAY_ESCAPE`) del proyecto. **No es aritmética de intervalos** (D-T5-1): es una cadena de desigualdades explícita con factores de seguridad declarados (F_K = 4, F_T = 10, F_disc = 10).
- **j7:** misma salida por la misma arista (r = 0.0746642296), pero la cota (0.01974) no alcanza el margen pactado. **No está certificado.** Tampoco hay evidencia de que su área llegue a 0.02.
- **Estados:** **no reclasifica nada.** j5 y j7 siguen `PAUSED_PENDING_REVIEW` hasta que E2 resuelva el tratamiento de T5 (D3). No asigna Y. La compuerta del piloto no cambia.
- **Advertencia de alcance (anexo 2.2):** T5 se refiere al procedimiento de E1 (exponencial con todos los rayos), no a la bola métrica.

## Historial completo (para la revisión de E2)
Hubo cuatro corridas sobre los mismos tres casos, cada una con su versión registrada antes de correr:
1. **v1:** identificación de cara errónea; no llegó a calcular la cota.
2. **v2:** j8 cayó por una métrica singular en la continuación.
3. **v3:** j8 cayó por un desborde en la carta de cara de un rayo.
4. **v4:** completa.

Las tres correcciones fueron defectos de implementación documentados y no tocaron t₀, factores, margen, tolerancias ni los cálculos de j5 y j7. Estos dieron los mismos números desde la corrida 2. Antes de la corrida 4 quedó escrito el compromiso de cerrar como «no certificado» ante cualquier fallo. Aun así, que hubo varios intentos después de ver resultados intermedios es un hecho que E2 debe ponderar.
