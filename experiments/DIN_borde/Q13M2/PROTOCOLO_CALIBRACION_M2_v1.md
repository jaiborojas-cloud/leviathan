# DIN-Q13-M2 — calibración de un segundo manipulador del colapso · protocolo v1 (2026-10-27)

**Estado:** registrado **antes** de cualquier medición. Lo pidió el responsable a las 08:13.
- **Qué mide:** **solo** c250, q250 y la precisión del panel.
- **Qué no mide:** X, ρ, D ni ninguna asociación.
- **Para qué sirve:** elegir el manipulador y sus dosis del confirmatorio Q13-M2, que se diseña aparte.

## 1. Por qué
- **Lo que mostró Q13-DR:** con *label smoothing* (LS), la señal temprana se modula con el colapso (MODULA, β = 0.077).
- **Lo que no separa:** el colapso del efecto propio de LS.
- **Qué hace falta:** otro manipulador que reduzca el colapso **por otra vía**, para comprobar después si reproduce la misma relación entre D y c.

## 2. Manipuladores candidatos
La receta es la de Q13 v2 y Q13-DR **byte a byte**: generador s = 0.8, MLP 13→64→32→3, Adam lr 0.006, lote 64, 250 updates e instrumento v2 r3. Solo cambia lo que se indica:

| brazo | cambio único | rejilla de dosis |
|---|---|---|
| **A0** | ninguno (referencia) | — |
| **LP**, penalización de logits | pérdida = CE + λ · media del lote de ‖z‖², con z = logits **sin** suavizar etiquetas; Adam sin decay | λ ∈ {1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3} |
| **WD**, weight decay | AdamW(lr 0.006, weight_decay = λ); CE normal | λ ∈ {0.2, 0.5, 1, 2, 4} |

- **Por qué LP:** limita la escala de los logits sin tocar las etiquetas. Es la vía más distinta de LS, que suaviza el objetivo.
- **Por qué WD otra vez:** en el piloto de 20 splits dio 0.675 y en la cohorte 0.740. Aquí se recalibra con **5 veces más splits**, para ver si su curva es estable.
- **Cómo queda escrito LP:** `loss = cross_entropy(z, y) + lam * (z ** 2).sum(dim=1).mean()`, con z = model(xt[ids]).

## 3. Muestra
- **Tamaño:** **100 splits × 5 inicializaciones** por condición. Son 14 condiciones (A0, 8 de LP y 5 de WD), es decir, 7000 entrenamientos.
- **Semillas nuevas,** disjuntas de G2, G3, C2, Q13 y Q13-DR: split 901000+s, inicialización 902000+5s+k, lote 903000+5s+k.
- **Pareado:** todas las condiciones comparten datos, inicialización y lotes.

## 4. Qué se publica
- **Tabla:** con todas las ejecuciones, incluidas las fallidas, y las columnas `id, brazo, dosis, split, k, c250, q250, acc_panel250, status, error`.
- **Resumen por condición:**
  - medianas de c250, q250 y acc_panel250;
  - **IC95 de la mediana de c250** por bootstrap de splits (2000 réplicas, semilla 904001);
  - fracción de ejecuciones con c250 ≤ 0.70.

## 5. Criterios de elegibilidad de un manipulador
Se fijan **antes** de medir y se usan en el diseño del confirmatorio. Un manipulador es **elegible** si cumple las tres condiciones:
1. **Mediana de c250 monótona no creciente** en su rejilla. Se reporta cualquier inversión.
2. **Alcanza el rango de Q13-DR:** alguna dosis da una mediana de c250 ≤ 0.45, y la caída de precisión de esa dosis frente a A0 es ≤ 0.10.
3. **Precisión preservada:** en las dosis con mediana de c250 ≥ 0.55, |acc − acc_A0| < 0.05, como en L1–L3 de Q13-DR.

## 6. Qué **no** decide esta calibración
- **Las dosis del confirmatorio:** se elegirán en su diseño, por interpolación log-lineal de la curva c(λ) hacia los niveles de c que alcanzó Q13-DR (0.69, 0.61, 0.56, 0.50 y 0.40). La regla exacta se congelará allí.
- **Si ambos manipuladores son elegibles:** el responsable decide si van uno o los dos.
- **Si ninguno es elegible:** se informa, y la pregunta «¿es LS o el colapso?» queda abierta con estos manipuladores.

## 7. Reparto
- **Agente de cohorte:** implementa, ejecuta y publica por SHA. No calcula X, ρ ni D.
- **Claude:** revisa el resultado y diseña el confirmatorio.
- **Responsable:** aprueba.
