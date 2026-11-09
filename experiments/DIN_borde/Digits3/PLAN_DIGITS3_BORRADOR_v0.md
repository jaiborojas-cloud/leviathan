# DIN-Digits-3: generalidad de la señal temprana en imágenes sencillas · plan BORRADOR v0

**2026-11-09, hora de México.** Autor: Claude. **Borrador para auditoría y decisión del responsable. No autoriza descargar, entrenar ni medir.** Desarrolla la [opción 2 del documento A2](../primaria_robusta/OPCIONES_SIGUIENTE_EXPERIMENTO.md), elegida por el responsable el 2026-11-05 como el siguiente paso después de Q15 («generalidad en Digits-3 con la primaria robusta»). Sigue la estructura de la rama CIFAR ([plan v1](../CIFAR/PLAN_CIFAR_v1.md), [enmienda v2](../CIFAR/PLAN_CIFAR_v2.md) y [cierre](../CIFAR/CIERRE_CIFAR3_2026-11-02.md)): plan, F0 de factibilidad sin medir la señal, F1 de descubrimiento y F2 confirmatorio.

## 1. Pregunta

¿Aparece, de forma robusta, la señal temprana de DIN en otra familia de datos reales: imágenes sencillas con una red que aprende de manera fiable?

- **Señal temprana:** que X10 mejore fuera de muestra la predicción de log ρ_caras(250) sobre una base de log ρ_caras(10), dentro del split. Es la misma pregunta predictiva de C1 y de CIFAR F1.
- **Por qué Digits-3:** CIFAR-3 terminó sin señal robusta, y su PASS lo produjo casi entero una trayectoria que no aprendió. Digits es una familia de imágenes donde la red sí aprende casi siempre, así que la falla de entrenamiento no debería dominar. Es **otra familia**, no un aislamiento de una variable: cambian a la vez los datos, la entrada y f.
- **Qué no responde:** un PASS en Digits-3 no se transfiere a "todas las imágenes" ni a otras arquitecturas, y no identifica causalidad. La parte (c) de Q15 (si la señal aparece en arquitecturas y datos estándar) sigue abierta.

## 2. Decisiones que fija este plan (a aprobar por el responsable)

1. **Datos:** `sklearn.datasets.load_digits` (1 797 imágenes de 8 × 8, valores enteros de 0 a 16). Viene incluido en scikit-learn: no hay descarga. El productor registra la versión de scikit-learn y el SHA-256 de `data` (float64, C-contiguo) y de `target` (int64) antes de medir.
2. **Clases 0, 3 y 8**, con etiquetas 0 → 0, 3 → 1 y 8 → 2. **La clase 8 es la referencia** de los logits reducidos. Quedan fijas antes de medir y se conservan aunque F0 no muestre concentración. Hay 178, 183 y 174 imágenes por clase; cada split usa 118 por clase.
3. **Red: el MLP de Wine con entrada de 64.** 64 → 64 → 32 → 3, con ReLU; cuerpo = (l1, ReLU, l2, ReLU) y cabeza = l3, exactamente la estructura de WineMLP (13 → 64 → 32 → 3) salvo la dimensión de entrada. Unos 6 300 parámetros.
4. **Receta de Wine:** Adam con lr = 0.006, lote de 64 por update (sin reemplazo dentro del lote, como en `core`), 250 updates, CE, float64, sin aumentos de datos. Visitas en 5, 10, 30 y 250. Mantener la receta de Wine hace que X10 signifique lo mismo que en C1 y G3.
5. **f, perspectivas:** las **2 primeras componentes principales del panel**, como en CIFAR. No se usan píxeles crudos: 10 de los 64 son constantes en estas tres clases.
6. **Reparto:** Claude implementa el sistema y el productor de F0; el otro agente que designe el responsable diseña y audita F1; el responsable ejecuta y aprueba.

## 3. Sistema Digits-3

- **Split s:** con `numpy.random.default_rng(semilla_split)`, en este orden y para cada clase 0, 3 y 8: se extraen sin reemplazo 118 índices de esa clase; los 100 primeros son entrenamiento, los 9 siguientes panel y los 9 últimos test. Cada grupo se ordena por clase y luego por índice original. Digits no trae una partición oficial: los tres grupos salen del mismo conjunto y son disjuntos dentro del split.
- **Preprocesamiento:** píxeles en float64, estandarizados con `StandardScaler` ajustado **solo con el entrenamiento del split**. Un píxel constante en entrenamiento queda en escala 1, como hace scikit-learn, y su valor estandarizado es su desviación respecto a esa constante.
- **f:** el panel preprocesado (27 × 64) se centra con su media; las 2 componentes salen de la SVD y sus puntajes se dividen por su desviación estándar en el panel (ddof = 0). **Signo:** cada vector de cargas se orienta para que la suma de sus elementos sea ≥ 0; si es exactamente 0, para que su primer elemento no nulo sea positivo. Se calculan una vez por split y se comparten entre inicializaciones y visitas; nunca salen de representaciones aprendidas. Si la segunda componente tiene varianza nula en el panel, el split se registra como FALLIDA por PCA y no se sustituye.
- **Inicialización:** la de PyTorch por defecto, con `torch.manual_seed(semilla_init)`. **Lotes:** `numpy.random.default_rng(semilla_lote)`.
- **Instrumento:** `make_geom_state_general` con cabeza reducida (W3r = W[:2] − W[2], b3r = b[:2] − b[2]), `subset_M` y `rho_borde_v2` r3, **sin cambiar sus SHA**. La compuerta de equivalencia ya PASA con error 0 sobre el MLP de Wine, que es la misma estructura; el productor registra el JSON y el SHA de esa compuerta y agrega la prueba de invariancia de la cabeza en la red de Digits-3.

## 4. Semillas

Banda nueva, por encima de las reservas existentes (Q13-SEP llega a 73 249 999). En el repo no hay ningún literal entre 81 y 84 millones, comprobado con `git grep` sobre `main` el 2026-11-09. Antes de congelar se repetirá el cotejo con el método de [SEMILLAS_PROPUESTAS_v1](../Q13SEP/SEMILLAS_PROPUESTAS_v1.md).

| Fase | Split | Inicialización | Lote | Tamaño |
|---|---|---|---|---|
| F0, factibilidad | 81 000 000 + s | 81 100 000 + 5s + k | 81 200 000 + 5s + k | 20 × 5 |
| F0b, respaldo (solo si hace falta) | 81 300 000 + s | 81 400 000 + 5s + k | 81 500 000 + 5s + k | 20 × 5 |
| F1, descubrimiento | 82 000 000 + s | 82 100 000 + 5s + k | 82 200 000 + 5s + k | 100 × 5 |
| F2, reserva sin N elegido | 83 000 000 + s | 83 100 000 + 5s + k | 83 200 000 + 5s + k | hasta 10 000 splits |

Ninguna fase reutiliza semillas de otra. Las semillas de split distintas no garantizan imágenes distintas: con 1 797 imágenes, los splits se solapan. El estimando es sobre particiones e inicializaciones de Digits-3, no sobre imágenes nuevas.

## 5. F0: factibilidad (no se mide X, ρ ni D)

- **Muestra:** 20 splits × 5 inicializaciones = 100 trayectorias.
- **Qué se mide por trayectoria:**
  - c y q en cada visita;
  - precisión y CE de entrenamiento, panel y test en **u10 y u250**;
  - tiempo de entrenamiento, de geometría por visita y de una llamada a `rho_borde_v2` en u250, de la que **solo se guarda el estado** (válida o no), nunca su valor;
  - memoria máxima del proceso (`None` si no se pudo medir, nunca 0);
  - **reproducción:** (s0, k0) y (s1, k3) se repiten al final y deben dar los mismos hashes de parámetros, c, q y precisiones, bit a bit.
- **No se guardan** X10, R, ρ ni logits del panel. F0 no puede contaminar el descubrimiento.
- **Criterios descriptivos para pasar a F1** (el responsable decide):
  1. mediana de la precisión de entrenamiento en u250 ≥ 0.90;
  2. mediana de la precisión del panel en u250 ≥ 0.80 (con imágenes sencillas se espera más que en CIFAR);
  3. **u10 todavía es temprano:** mediana de la precisión de entrenamiento en u10 ≤ 0.95. Si la red ya aprendió casi todo en u10, X10 no es una señal temprana y la pregunta pierde sentido;
  4. mediana de c250 en [0.30, 0.97]; se reporta además su distribución;
  5. CPU ≤ 60 s por trayectoria;
  6. compuerta e invariancia PASAN y la reproducción es exacta.
- **Respaldo F0b, declarado ahora:**
  - **si falla el criterio 3** (u10 saturado): lr = 0.001, mismo resto;
  - **si fallan 1 o 2** (subentrenamiento): 500 updates con visitas 5, 10, 30 y 500, mismo resto;
  - si fallan ambos tipos, decide el responsable;
  - F0b usa sus propias semillas y los mismos criterios. **Ninguna otra corrida exploratoria de configuración** entre F0, F0b y F1.
- **Si solo falla c:** decide el responsable, sin más ajustes de entrenamiento. c no se usa para afinar.
- **Nunca se cambian** las clases ni f después de F0.

## 6. F1: descubrimiento con la primaria robusta (lo diseña y congela el otro agente después de F0)

- **Muestra:** 100 splits × 5 inicializaciones = 500 trayectorias, con las semillas de F1.
- **Registro por visita:** el de [CIFAR F1 §3–4](../CIFAR/DISENO_CIFAR_F1_v2_CONGELADO.md): X5, X10, X30 y X250; M, f, logits y etiquetas en arrays externos; c, q, k_star y R; precisiones y CE; estados MEDIDA / INVALID_RHO / FALLIDA, con los mismos criterios de aceptación de ρ y el watchdog externo de 120 s.
- **Primaria:** la [primaria robusta v1](../PRIMARIA_ROBUSTA_v1.md), con su [analista](../primaria_robusta/analisis_robusta_v1.py) (hoy en BORRADOR, 58 de 58 pruebas sintéticas; se congela dentro del diseño de F1, antes de ver sus datos):
  - NO_APRENDIO: precisión de entrenamiento en la última visita < 0.5, cuenta como faltante y nunca se sustituye;
  - base cúbica con la z de prueba recortada al rango de entrenamiento del bloque;
  - **PASS = p < 0.05, D > 0, pendiente > 0 y D_sin_max > 0**; si D_sin_max ≤ 0, **NO_ROBUSTO**.
- **Compuertas de calidad:** faltantes ≤ 5 % y al menos 80 % de los splits con 3 o más trayectorias elegibles.
- F1 es **descubrimiento**: un PASS justifica proponer F2, no lo activa.

## 7. F2: confirmatorio

Con las semillas de la reserva, un tamaño elegido antes de entrenar por potencia con F1 como piloto, y todo congelado y auditado. No se fija N ahora.

## 8. Costo estimado

El MLP de Digits-3 tiene unas 6 300 parámetros, frente a unos 26 000 de la CNN de CIFAR, y una entrada de 64 en lugar de 3 072. Entrenar y calcular la geometría debería costar mucho menos que en CIFAR; la llamada a ρ en u250 probablemente domine. Orientativo, sin haber medido: **F0 en 5 a 15 minutos y F1 en 25 a 50 minutos** con 12 procesos en la PC del responsable. F0 mide el costo real antes de comprometer F1.

## 9. Riesgos conocidos

- **X10 saturada por facilidad:** la cubre el criterio 3 de F0 y su respaldo.
- **Poca variación de c entre inicializaciones,** o colapso ausente: se reporta en F0; no se ajusta el entrenamiento por c.
- **PCA inestable con 27 ejemplos:** las cargas cambian entre splits; el signo está fijado y f no se reoptimiza.
- **Solapamiento entre splits** por el tamaño de Digits: se declara en el estimando.
- **Un PASS no es generalidad universal:** es una familia más, con una red pequeña.

## 10. Entrega y siguiente paso

Este borrador no incluye código ni datos. Si el responsable lo aprueba (con o sin cambios), Claude implementa `sistema_digits3.py` y el productor de F0 con pruebas sintéticas y publica sus SHA antes de medir; el otro agente audita ese código antes de correr F0.
