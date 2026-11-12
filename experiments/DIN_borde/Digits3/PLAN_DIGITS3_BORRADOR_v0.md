# DIN-Digits-3: generalidad de la señal temprana en imágenes sencillas · plan BORRADOR v0

**2026-11-09, hora de México.** Autor: Claude. **Borrador para auditoría y decisión del responsable. No autoriza descargar, entrenar ni medir.** Desarrolla la [opción 2 del documento A2](../primaria_robusta/OPCIONES_SIGUIENTE_EXPERIMENTO.md), elegida por el responsable el 2026-11-05 como el siguiente paso después de Q15 («generalidad en Digits-3 con la primaria robusta»). Sigue la estructura de la rama CIFAR ([plan v1](../CIFAR/PLAN_CIFAR_v1.md), [enmienda v2](../CIFAR/PLAN_CIFAR_v2.md) y [cierre](../CIFAR/CIERRE_CIFAR3_2026-11-02.md)): plan, F0 de factibilidad sin medir la señal, F1 de descubrimiento y F2 confirmatorio.

## 1. Pregunta

¿Aparece, de forma robusta, la señal temprana de DIN en otra familia de datos reales: imágenes sencillas con una red que aprende de manera fiable?

- **Señal temprana:** que X10 mejore fuera de muestra la predicción de log ρ_caras(250) sobre una base de log ρ_caras(10), dentro del split. Es la misma pregunta predictiva de C1 y de CIFAR F1.
- **Por qué Digits-3:** CIFAR-3 terminó sin señal robusta, y su PASS lo produjo casi entero una trayectoria que no aprendió. En Digits **se espera** que la red aprenda casi siempre, así que la falla de entrenamiento no debería dominar; F0 lo comprueba antes de medir la señal. Es **otra familia**, no un aislamiento de una variable: cambian a la vez los datos, la entrada y f.
- **Qué no responde:** un PASS en Digits-3 no se transfiere a "todas las imágenes" ni a otras arquitecturas, y no identifica causalidad. La parte (c) de Q15 (si la señal aparece en arquitecturas y datos estándar) sigue abierta.

## 2. Decisiones que fija este plan (a aprobar por el responsable)

**Decisiones del responsable, 2026-11-09, 07:18, hora de México:** preprocesamiento (b), dividir entre 16; criterio del panel en F0 de 0.80; clases 0, 3 y 8 con referencia 8. Quedan fijadas antes de ver datos. El resto del plan sigue en borrador hasta la auditoría.

1. **Datos:** `sklearn.datasets.load_digits` (1 797 imágenes de 8 × 8, valores enteros de 0 a 16). Viene incluido en scikit-learn: no hay descarga. El productor registra la versión de scikit-learn y el SHA-256 de `data` (float64, C-contiguo) y de `target` **convertido explícitamente a int64** (en Windows con numpy < 2 puede venir como int32) antes de medir.
2. **Clases 0, 3 y 8**, con etiquetas 0 → 0, 3 → 1 y 8 → 2. **La clase 8 es la referencia** de los logits reducidos. Quedan fijas antes de medir y se conservan aunque F0 no muestre concentración. Hay 178, 183 y 174 imágenes por clase; cada split usa 118 por clase.
3. **Red: el MLP de Wine con entrada de 64.** 64 → 64 → 32 → 3, con ReLU; cuerpo = (l1, ReLU, l2, ReLU) y cabeza = l3, exactamente la estructura de WineMLP (13 → 64 → 32 → 3) salvo la dimensión de entrada. Unos 6 300 parámetros.
4. **Receta de Wine:** Adam con lr = 0.006, lote de 64 por update (sin reemplazo dentro del lote, como en `core`), 250 updates, CE, float64, sin aumentos de datos. Visitas en 5, 10, 30 y 250. Como en CIFAR, se conserva el **mismo índice de update**, no el mismo número de épocas: con 300 imágenes de entrenamiento, u10 equivale a unas 2.1 épocas, frente a unas 5.2 en Wine (124 de entrenamiento). X10 es comparable como "update 10", no como el mismo punto relativo del aprendizaje.
5. **f, perspectivas:** las **2 primeras componentes principales del panel**, como en CIFAR. No se usan píxeles crudos: 10 de los 64 son constantes en estas tres clases.
6. **Preprocesamiento: elegida la opción (b), x / 16** (decisión del responsable, 2026-11-09). Opciones consideradas (ver §3 y §9):
   - **(a) `StandardScaler` ajustado en el entrenamiento del split**, como propone A2;
   - **(b) dividir entre 16**, fijo y sin ajuste, el preprocesamiento habitual de Digits.
   Recomiendo (b): en las clases 0, 3 y 8 hay tres píxeles (7, 15 y 16) que solo son distintos de cero en 1 o 2 de 535 imágenes. Con (a), esa imagen queda con valores de hasta unos 17 a 23 en ese píxel y puede dominar las PCA del panel, de modo que f dependería de qué split recibió esa imagen. Lo comprobé solo con estadísticas por píxel de las imágenes, sin entrenar ni usar semillas del plan.
7. **Reparto:** Claude implementa el sistema y el productor de F0; el otro agente que designe el responsable diseña y audita F1; el responsable ejecuta y aprueba.

## 3. Sistema Digits-3

- **Split s:** con `numpy.random.default_rng(semilla_split)`, en este orden y para cada clase 0, 3 y 8: se extraen sin reemplazo 118 índices de esa clase; los 100 primeros son entrenamiento, los 9 siguientes panel y los 9 últimos test. Cada grupo se ordena por clase y luego por índice original. Digits no trae una partición oficial: los tres grupos salen del mismo conjunto y son disjuntos dentro del split.
- **Preprocesamiento:** píxeles en float64 divididos entre 16 (opción (b), §2.6), igual para entrenamiento, panel y test. Se conserva abajo la descripción de (a) solo como registro de la alternativa descartada.
  - Con (a), el escalador se ajusta **solo con el entrenamiento del split**. Un píxel constante en entrenamiento queda en escala 1, como hace scikit-learn, y su valor es su desviación respecto a esa constante. Un píxel con varianza pequeña pero no nula **se divide** por esa desviación pequeña: no hay piso ni recorte.
  - Con (b), x / 16, sin parámetros dependientes del split.
- **f:** el panel preprocesado (27 × 64) se centra con su media; las 2 componentes salen de la SVD y sus puntajes se dividen por su desviación estándar en el panel (ddof = 0). **Signo:** cada vector de cargas se orienta para que la suma de sus elementos sea ≥ 0; si es exactamente 0, para que su primer elemento no nulo sea positivo. Se calculan una vez por split y se comparten entre inicializaciones y visitas; nunca salen de representaciones aprendidas. Se usa `perspectivas_pca` de `instrumento_general.py` sin cambios. Si alguna de las dos componentes tiene varianza nula en el panel, esa función lanza un error y todas las trayectorias del split se registran como FALLIDA por PCA, sin sustitución.
- **Inicialización:** la de PyTorch por defecto, con `torch.manual_seed(semilla_init)`. **El tipo por defecto debe ser float64 antes de construir la red**, como en Wine, G3, C2 y el productor de CIFAR (que lo fija al cargar el `core` congelado en cada proceso). Construir en float32 y convertir después daría otros pesos iniciales. Cada proceso usa `torch.set_num_threads(1)`. **Lotes:** `numpy.random.default_rng(semilla_lote)`.
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
  - tiempo de entrenamiento, de geometría por visita y de **una llamada a `rho_borde_v2` en u10 y otra en u250**, las dos visitas que usa la primaria. De cada llamada **solo se guardan el estado y si pasaría los criterios de aceptación de CIFAR F1 §4** (sí o no, con el motivo), nunca el valor de ρ ni sus términos. CIFAR F0 solo cronometró u250; aquí se agrega u10 porque A2 pide que el piloto revise la validez de ρ y la primaria la necesita en las dos visitas;
  - memoria máxima del proceso (`None` si no se pudo medir, nunca 0);
  - **reproducción:** (s0, k0) y (s1, k3) se repiten al final y deben dar los mismos hashes de parámetros, c, q y precisiones, bit a bit.
- **No se guardan** X10, R, ρ ni logits del panel. F0 no puede contaminar el descubrimiento.
- **Criterios descriptivos para pasar a F1** (el responsable decide):
  1. mediana de la precisión de entrenamiento en u250 ≥ 0.90;
  2. mediana de la precisión del panel en u250 ≥ 0.80 (con imágenes sencillas se espera más que en CIFAR);
  3. **u10 todavía es temprano:** mediana de la precisión de entrenamiento en u10 ≤ 0.95. Si la red ya aprendió casi todo en u10, X10 no es una señal temprana y la pregunta pierde sentido;
  4. mediana de c250 en [0.30, 0.97]; se reporta además su distribución;
  5. **ρ aceptada en al menos el 95 % de las trayectorias, en u10 y en u250 a la vez**, coherente con la compuerta de faltantes ≤ 5 % de la primaria. Si no se cumple, decide el responsable; no se cambian las opciones de ρ;
  6. CPU ≤ 60 s por trayectoria, incluidas las dos llamadas a ρ;
  7. compuerta e invariancia PASAN y la reproducción es exacta.

  El criterio 2 (0.80) es más alto que el 0.55 de CIFAR porque Digits es mucho más fácil; el responsable lo aprobó el 2026-11-09 y no se cambia después de correr F0.
- **Respaldo F0b, declarado ahora:**
  - **si falla el criterio 3** (u10 saturado): lr = 0.001, mismo resto;
  - **si fallan 1 o 2** (subentrenamiento): 500 updates con visitas 5, 10, 30 y 500, mismo resto, como F0c de CIFAR. **Ojo:** la primaria robusta v1 fija Y = log ρ_caras(250). Si se usa esta rama, Y pasa a la última visita (u500) y el diseño de F1 tiene que declararlo como desviación explícita y aprobada, no como la primaria v1 tal cual;
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

El MLP de Digits-3 tiene 6 339 parámetros, frente a 26 067 de la CNN de CIFAR, y una entrada de 64 en lugar de 3 072. Entrenar y calcular la geometría debería costar mucho menos que en CIFAR; la llamada a ρ en u250 probablemente domine. Orientativo, sin haber medido (cifras de A2): **F0 en 5 a 15 minutos y F1 en 25 a 50 minutos** con 12 procesos en la PC del responsable. La segunda llamada a ρ en F0 puede alargarlo un poco. F0 mide el costo real antes de comprometer F1.

## 9. Riesgos conocidos

- **X10 saturada por facilidad:** la cubre el criterio 3 de F0 y su respaldo.
- **Poca variación de c entre inicializaciones,** o colapso ausente: se reporta en F0; no se ajusta el entrenamiento por c.
- **PCA inestable con 27 ejemplos:** las cargas cambian entre splits; el signo está fijado y f no se reoptimiza.
- **Píxeles raros:** con la opción (a), una imagen con un píxel casi nunca encendido podía dominar f y la entrada; por eso se eligió (b) en §2.6. Con x / 16 todos los valores quedan en [0, 1].
- **Solapamiento entre splits** por el tamaño de Digits: se declara en el estimando.
- **Un PASS no es generalidad universal:** es una familia más, con una red pequeña.

## 10. Entrega y siguiente paso

Este borrador no incluye código ni datos. Si el responsable lo aprueba (con o sin cambios), Claude implementa `sistema_digits3.py` y el productor de F0 con pruebas sintéticas y publica sus SHA antes de medir; el otro agente audita ese código antes de correr F0.
