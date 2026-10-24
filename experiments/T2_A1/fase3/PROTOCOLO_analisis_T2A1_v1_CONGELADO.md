# T2-A1 fase 3 — script de análisis, v1 CONGELADO (2026-10-24)

**Estado:** **CONGELADO** antes de abrir X, por aprobación del responsable el 2026-10-24 a las 13:35 («Sí por favor»). Implementa `../fase0prima/PROTOCOLO_0c_prima_v1_CONGELADO.md` sin cambiarlo.

## 1. Archivos
- **Análisis:** `analisis_T2A1.py`. Solo calcula si los tres insumos coinciden por hash:
  - X: `predictors_locked.csv` de T2-A0, `9458086153e7…ee70a`, el hash de `predictor_lock.json`;
  - desenlaces: `fase2_rho.csv`, `be47e118…02de`;
  - L5: `rho_borde_u5.csv`, `618c263e…df2d`.
- **Comparadores no geométricos del update 5:** `comparadores_ng_u5.py` mide pérdida y precisión en entrenamiento, precisión en validación y norma de pesos. Se corre y se publica por hash **antes** de abrir X. El análisis lo recibe con `--ng` y `--ng-sha`.
- En modo confirmatorio solo se admiten 20 000 permutaciones.

## 2. Reglas que fija el script (complementan 0c′ sin cambiarlo)
- **Faltantes:** una trayectoria con X no finito cuenta como faltante, igual que una con Y_c = ?. El umbral del 5 % de 0c′ se aplica al total de faltantes.
- **Empates en X:** orden (X, init) ascendente.
- **Generador de permutaciones:** `numpy.random.default_rng(semilla)`; los splits se recorren en orden creciente y cada uno usa `rng.permuted` a lo largo del eje 1.
- **W_adj:** MCO dentro del split. Freedman–Lane permuta los residuos sin reestimar β.
- **Semillas de los secundarios** (no deciden): 220020 para el bootstrap de G; 220023 para Δ; 220024–220026 para el W de cada comparador geométrico; 220034–220036 para X ajustado por L5 y cada comparador geométrico; 220027–220030 y 220037–220040 para los mismos dos cálculos con los no geométricos.
- **Orientación de los comparadores geométricos:** la de T2-A0. Para C_A y Λ, mayor valor es más riesgo; para R_eff se usa −R_eff. Los no geométricos se reportan sin orientar.

## 3. Pruebas antes de abrir X (contenedor, con los desenlaces reales y X sintético)
- **Calibración nula:** 200 X sintéticos independientes de Y, con 1000 permutaciones cada uno. Tasas de rechazo al 5 %: W 0.050, W_adj 0.055, regla conjunta 0.045. Mediana de p 0.55.
- **Con efecto:** un X sintético con ρ = 0.3 respecto del residuo da W = 0.335, W_adj = 0.328 y p ≈ 5·10⁻⁵ en ambas. La dirección es correcta.
- **Ruta confirmatoria:** se probó con una tabla de X **falsa** con las mismas columnas que escribe `lock_predictors.py`, con empates, un X vacío y un R_eff vacío, y una copia del script con el hash cambiado. Los faltantes se contaron bien. Un hash incorrecto aborta, y B ≠ 20000 en modo confirmatorio también aborta.

## 4. Declaraciones
- **Copia de X en el repositorio.** `predictors_locked.csv` está en el repositorio, sin cifrar, desde el commit `3bb91da` (2026-10-21, importación del archivo histórico). Las rutas son `docs/archive/import-2026-10-17/originals/Leviathan/Repro/T2_A/` y `…/extracted/Leviathan_T2A_cierre_split8_j5_update25_v1/current/`. Claude localizó el archivo al escribir este script y solo calculó su SHA-256, sin abrirlo: coincide con `predictors_sha256` del bloqueo de T2-A0 (`9458…ee70a`). No se puede verificar si otros agentes que trabajan sobre el repositorio lo leyeron. Las decisiones de T2-A1 (diseño v3, 0c′, fase 2 y este script) se tomaron sin su contenido. Se suma a la desviación de Nemotron ya registrada.
- **Desenlaces vistos sin X.** Las pruebas con X sintético muestran resúmenes de los desenlaces sin relación con X; por ejemplo, la incidencia de Y_b, que fue 248 de 780. No hay ninguna decisión del análisis que dependa de ellos: todas estaban fijadas en 0c′ o en la sección 2.

## 5. Orden
1. Correr `comparadores_ng_u5.py` y publicar su hash.
2. Abrir X: el responsable corre `analisis_T2A1.py` en modo confirmatorio. Es una sola corrida y su salida se publica íntegra.
