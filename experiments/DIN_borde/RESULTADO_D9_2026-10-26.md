# DIN-borde D9 — resultado (exploratorio, 2026-10-26)

**Veredicto según la regla del plan:** **NINGUNO PASA.** La geometría del colapso no añade predicción de la generalización (pérdida en test en u250) sobre las medidas baratas en Wine, dentro del split.

## Procedencia
- **Datos nuevos:** `d9_generalizacion.py`, corrido en el equipo del responsable.
  - Hubo 780 trayectorias: la compuerta pasó en las 780, sin fallos ni errores.
  - La tabla es `d9/d9_tabla.csv`, con sha256 `e67fe37d…6043`, que coincide con `RESUMEN_d9.json`.
- **SHA del script en el equipo:** `fe3ee543…dc05`. Es el script registrado `6c759808…4676` con finales de línea CRLF, por el checkout de git en Windows. Se verificó convirtiendo el registrado a CRLF: da exactamente `fe3ee543…`. El contenido es idéntico.
- **Integridad frente a d6:** en los updates 10, 20 y 30, train_loss difiere como máximo 1.7e-16 y val_acc coincide exactamente. Es la misma trayectoria reentrenada.
- **Análisis:** `analisis_D9.py`, que guarda su resultado en `d9/RESULTADO_D9.json`. Antes de calcular dejó fijadas, en su cabecera, las concreciones que el plan no especificaba:
  - Y es la pérdida cruda;
  - Δc usa la base del momento final;
  - el signo se compara entre splits pares e impares;
  - los secundarios se calculan con B = 499 permutaciones.

## Primaria: Y = pérdida en test en u250, base barata del mismo t; umbral D > 0.02, p < 0.05/12 ≈ 0.0042 y signo estable
| candidato | D | p | signo estable |
|---|---|---|---|
| c u10 | −0.0007 | 0.27 | no |
| log tr M u10 | −0.0015 | 0.38 | sí |
| log ρ_caras u10 | −0.0028 | 0.54 | no |
| c u20 | −0.0018 | 0.54 | no |
| log tr M u20 | −0.0044 | 0.75 | no |
| log ρ_caras u20 | −0.0054 | 0.83 | sí |
| c u30 | 0.0023 | 0.045 | sí |
| log tr M u30 | −0.0046 | 0.84 | no |
| log ρ_caras u30 | −0.0061 | 0.93 | no |
| Δc 10→20 | −0.0014 | 0.39 | sí |
| Δc 20→30 | 0.0046 | 0.020 | sí |

- **Ningún candidato pasa.**
- Los dos más altos son c en u30 y Δc entre 20 y 30. En ambos la pendiente es negativa: más colapso tardío se asocia a menor pérdida en test.
- **Esos dos quedan lejos del umbral:**
  - su D es 0.002–0.005, entre 4 y 10 veces menor que 0.02;
  - su p no sobrevive a la corrección por multiplicidad.
- Se registran como **señal débil sin respaldo**, no como hallazgo.
- **Secundarios:** la precisión en test y la brecha dan el mismo patrón. Ninguno supera D = 0.005.

## Controles
- **Base barata frente a nada:** D = −0.006 en u10, 0.008 en u20 y 0.004 en u30. Las medidas baratas **tampoco** predicen la pérdida en test dentro del split.
- **Candidatos solos, sin base:** todos dan |D| < 0.008.

## Lectura (no forma parte del veredicto)
**Dentro del split, la pérdida en test en u250 es casi impredecible desde la ventana 10–30, con cualquier medida, geométrica o barata.**
- **Por qué:** solo el **9.7 %** de su varianza es intra-split, es decir, diferencias entre las 5 inicializaciones. El **90 %** se debe a *qué* conjunto de test de 27 ejemplos le toca al split.
- **Qué deja fuera el diseño:** como centra dentro del split, el diseño solo mira la parte de la generalización que depende de la inicialización. Esa parte es pequeña y ruidosa.
- **Pregunta abierta, distinta y post hoc:** saber si la geometría de un split predice qué tan difícil es su test sería una pregunta *entre splits*. **No** se analizó aquí. Si se quisiera, tendría que registrarse como pregunta nueva.

## Consecuencia (regla del responsable)
D9 no sale como esperábamos, así que el siguiente paso es **Q13**: ¿es necesario el colapso? Para eso hay que manipularlo. D9g-c, del otro agente, sigue pendiente y se evaluará con su propia regla; no cambia este resultado.
