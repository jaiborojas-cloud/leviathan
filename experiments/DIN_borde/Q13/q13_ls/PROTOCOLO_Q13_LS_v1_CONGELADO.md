# DIN-Q13-LS — análisis de un manipulador (A0 frente a LS) sobre la cohorte Q13 v2 · v1 CONGELADO (2026-10-26)

**Estado:** **CONGELADO** el 2026-10-26 a las 18:54 por aprobación del responsable («si»). Contenido idéntico a `PROTOCOLO_Q13_LS_BORRADOR_v1.md` (se conserva). Ningún D, p ni bootstrap calculado antes de esta congelación.

## Etiqueta obligatoria (en todo informe que cite este resultado)
> «Análisis de un solo manipulador (label smoothing), **decidido después** de que la compuerta de manipulación de Q13 v2 fallara en WD (mediana c250 = 0.740 > 0.70), y **antes** de calcular cualquier D. **No sustituye** el veredicto de Q13 v2, que es INCONCLUSIVE_MANIPULACION.»

## Por qué es admisible y qué pierde
- **Admisible:** la decisión de quitar WD depende **solo** de la compuerta (c250 de WD), que es una variable de manipulación. No depende del desenlace de Q13, que es la señal D, ni de nada correlacionado con D que alguien haya mirado.
  - La tabla de A0 y LS no se altera; solo se filtran filas completas.
  - El análisis, las semillas, las permutaciones, el bootstrap y los umbrales son los congelados.
- **Lo que pierde frente al diseño de dos vías:**
  - Con un solo manipulador no se separa «colapso» de «efecto propio del *label smoothing*», que también achica las probabilidades máximas y, con ellas, X10.
  - Un CAE aquí se lee como «LS que reduce el colapso elimina la señal», no como «el colapso es necesario».
  - Un SE_MANTIENE sí es informativo en contra de la necesidad: se reduce el colapso y la señal sigue.

## Datos (derivados, sin recalcular nada)
- **Tabla:** `q13_ls_cohorte.csv`, las 8000 filas de A0 y LS de `cohorte_q13/q13_cohorte.csv` (`d360b313…`), copiadas **byte a byte** con la misma cabecera y el mismo orden. SHA `e88a964f…`.
- **Plan:** `q13_ls_plan.json`, con n_splits = 800, brazos [A0, LS], dosis LS = 0.005 e `ids_sha256` del universo A0/LS de `analisis_Q13.universo`. SHA `f0651c42…`.
- **Resumen:** `RESUMEN_q13_ls.json`, que vincula tabla y plan.

## Análisis
- **Script:** `analisis_Q13.py` **sin cambios** (`9998a1b2…`). Con dos brazos aplica el veredicto de un manipulador, probado en `pruebas_Q13` (casos N800_un_brazo_cae y un_brazo_mantiene).
- **Compuerta:** se evalúa de nuevo sobre A0 y LS, con las mismas condiciones. En v2 ambos la cumplieron.
- **Primaria y bootstrap:** primaria C1 por brazo (5000 permutaciones, semilla 260001) y bootstrap pareado de splits (2000 réplicas, semilla 760001).
- **Clasificación de LS:**
  - **CAE:** IC95 superior de D_LS < 0.006 **y** IC95 inferior de ΔD > 0.
  - **SE_MANTIENE:** PASS en LS **y** IC95 inferior de ΔD ≤ 0.
  - **INTERMEDIO:** en cualquier otro caso.
- **Veredicto:** NECESARIO_APOYADO_UN_MANIPULADOR, NO_NECESARIO_UN_MANIPULADOR o NO_CONCLUYENTE. También puede salir INCONCLUSIVE_SIN_SENAL_CONTROL si A0 no da PASS.
- **Potencia:** la simulación de v2 con N = 800 corresponde exactamente a este par A0/LS: PASS de A0 con Wilson inferior 0.99, y CAE completo con Wilson inferior 0.806.
- **Ejecución:** una sola vez, por Claude, después de congelar.

**Comando:**

```
python3 -I experiments/DIN_borde/Q13/analisis_Q13.py --tabla q13_ls/q13_ls_cohorte.csv --tabla-sha e88a964f… \
  --plan q13_ls/q13_ls_plan.json --plan-sha f0651c42… --resumen q13_ls/RESUMEN_q13_ls.json --out q13_ls/resultado
```
