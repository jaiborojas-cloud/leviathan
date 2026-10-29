# DIN-CIFAR — transferencia de la señal temprana a imágenes reales · plan v1 (2026-10-28)

**Estado:** plan v1, con las decisiones del responsable del 2026-10-28 (mensaje posterior a «comencemos CIFAR»). Sustituye al borrador v0, que se conserva. **Nada está descargado ni entrenado.** F0 (§4) se ejecuta con el protocolo de esta página.

## 1. Decisiones del responsable (2026-10-28)
1. **Clases difíciles: gato (3), ciervo (4) y perro (5)** de CIFAR-10. Quedan fijadas antes de medir y **se conservan aunque F0 no muestre concentración**.
2. **CNN pequeña**, de unos 30 000 parámetros (§3). F0 mide el costo real en CPU antes de comprometer las 500 trayectorias de F1.
3. **Perspectivas f:** las **2 primeras componentes principales del panel**.
   - Sin etiquetas, calculadas **una vez por split** sobre las imágenes del panel ya preprocesadas, y compartidas entre inicializaciones y visitas.
   - **Nunca** se recalculan desde representaciones aprendidas.
   - Preprocesamiento, escalado y convención de signos congelados (§3).
4. **Reparto:**
   - **Claude** implementa el instrumento generalizado, la compuerta de equivalencia y el productor;
   - **el otro agente** prepara el diseño y el análisis de F1 y F2;
   - **el responsable** ejecuta y aprueba.

## 2. Instrumento generalizado (`CIFAR/instrumento_general.py`)
- **Reutiliza sin cambios:** `subset_M` del `core` congelado (`b5251d2f…`), con la regularización de Woodbury (γ = RHO·λ_max, RHO = 1e-4), y `rho_borde_v2` (r3, `2ac015a2…`).
- **Generaliza solo `make_geom_state`** a un modelo = cuerpo + cabeza Linear de 3 salidas, con la **misma parametrización reducida** de los logits del original:
  - W3r = W[:2] − W[2] y b3r = b[:2] − b[2];
  - logits reducidos = [h·W3rᵀ + b3r, 0].
  - Los gradientes se calculan respecto a todos los parámetros del cuerpo y a (W3r, b3r), **no** respecto a la cabeza completa, porque usar los 3 vectores de salida cambiaría M aunque las probabilidades fueran iguales.
  - El orden de los bloques y la construcción de R y U (raíz de p_c/N por gradiente de log p_c) son los del original.
- **Compuerta de equivalencia (antes de cualquier uso en CIFAR):**
  - **Datos:** estados de WineMLP de los splits 0–2 (`core.load_split`) en los updates 0, 10, 250 y 2000. El de 2000 está cerca del borde (p mínima del panel < 1e-3).
  - **Requisito:** el instrumento generalizado, aplicado con cuerpo = (l1, ReLU, l2, ReLU) y cabeza = l3, debe reproducir R y U por bloque, M (bloques {0,1,2}, {2} y {0,1}) y ρ (caras y vértices, en los updates 10, 250 y 2000) de `core` y `rho_borde_v2` con error relativo ≤ 1e-12.
  - **Control negativo:** la parametrización completa de la cabeza (sin reducir) debe dar un M **distinto** (rel > 1e-9), en Wine y en la CNN, para mostrar que la compuerta detecta ese error.
  - **Invariancia en la CNN:** sumar un vector común a las filas de la cabeza y un escalar común al sesgo no cambia las probabilidades ni el M reducido (≤ 1e-12).
  - **PCA:** f es determinista y la convención de signo se cumple.
  - Script: `compuerta_equivalencia.py`. Primera corrida de desarrollo (en el contenedor, con otras versiones de numpy, scipy y sklearn; **no es la corrida oficial**): PASA, con error máximo exactamente 0.

## 3. Sistema «CIFAR-3»
- **Datos:** el archivo oficial `cifar-10-python.tar.gz`, verificado por MD5 `c58f30108f718f92721af3b95e74349a` y SHA-256 registrado al descargarlo. Se lee con numpy, sin torchvision.
- **Split s:**
  - entrenamiento: 300 imágenes por clase de los `data_batch_1..5`;
  - panel: 9 por clase del `test_batch`;
  - test: otras 9 por clase del `test_batch`, disjuntas del panel.

  Las muestras salen de `numpy.random.default_rng(semilla_split + s)`, en este orden: primero 300 de entrenamiento por clase (3, 4, 5); después 18 del test por clase, de los que los 9 primeros son el panel y los 9 siguientes el test. Cada grupo se ordena por clase y luego por índice original.
- **Etiquetas:** gato → 0, ciervo → 1, perro → 2. **Perro es la clase de referencia** de los logits reducidos.
- **Preprocesamiento:** píxeles / 255 y estandarización por canal con la media y la desviación del **entrenamiento del split**. Se usa float64.
- **f, perspectivas:** se aplana el panel preprocesado (27 × 3072) y se centra con la media del panel.
  - Las 2 componentes salen de la SVD; los puntajes se dividen por su desviación estándar en el panel (ddof = 0).
  - **Signo:** cada vector de cargas se orienta para que la suma de sus elementos sea ≥ 0; si es exactamente 0, para que el primer elemento no nulo sea positivo.
- **Red** (unos 26 000 parámetros):
  - conv 3→8 (3×3, padding 1), ReLU, maxpool 2;
  - conv 8→16 (3×3, padding 1), ReLU, maxpool 2;
  - aplanado de 1024, densa 1024→24 y ReLU;
  - **cabeza** densa 24→3.

  La inicialización es la de PyTorch por defecto, con `torch.manual_seed(semilla_init)`.
- **Entrenamiento:** Adam con lr = 0.001, lote 64 sin reemplazo y 250 updates (unas 18 épocas de 900 imágenes), con CE y sin aumentos de datos. Visitas en los updates 5, 10, 30 y 250.

## 4. F0, factibilidad (protocolo; **no se mide X, ρ ni D**)
- **Muestra:** 20 splits × 5 inicializaciones = 100 trayectorias, con semillas propias: split 1 010 000 + s, inicialización 1 020 000 + 5s + k y lote 1 030 000 + 5s + k. **Estas semillas no se reutilizan en F1 ni en F2.**
- **Qué se mide por trayectoria:**
  - c y q en cada visita;
  - precisión en entrenamiento, panel y test en u250;
  - tiempo de entrenamiento, de geometría por visita y de una llamada a `rho_borde_v2` en u250. Esta llamada **solo se cronometra: su valor no se guarda ni se reporta**, solo su estado (válida o no);
  - memoria máxima del proceso;
  - **reproducción:** las trayectorias (s0, k0) y (s1, k3) se re-ejecutan al final y deben dar los mismos hashes de parámetros, c, q y precisiones, bit a bit.
- **No se guardan** X10, log(1 − p_min) ni ρ. F0 no puede contaminar el descubrimiento.
- **Regla para pasar a F1** (descriptiva; el responsable decide):
  - mediana de la precisión del panel en u250 ≥ 0.55 (el azar es 0.33);
  - mediana de c250 en [0.30, 0.97], es decir, ni plana ni degenerada; se reporta también la distribución;
  - costo por trayectoria ≤ 60 s de CPU, para que 500 trayectorias quepan en unas 45 min con 12 procesos;
  - compuerta de equivalencia PASA y reproducción exacta.
- **Ajustes permitidos solo entre F0 y F1, y con declaración:** lr, número de updates o ancho de la red, si la precisión o el costo no cumplen. **No** se cambian las clases ni f.

## 5. F1 y F2
Como en el v0: F1 de descubrimiento con unos 100 × 5 trayectorias (exploratorio, primaria descriptiva de C1), y F2 confirmatorio con splits nuevos y todo congelado y auditado. Los diseña el otro agente después de F0.
