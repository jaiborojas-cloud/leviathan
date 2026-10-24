# DIN-borde D6 — ¿cuándo se decide el destino? (plan exploratorio, 2026-10-24)

**Naturaleza:** **exploratorio o de descubrimiento**. Se registra antes de correr. Usa las 780 trayectorias de T2-A1 (splits 12–167), ya gastadas para confirmar. Lo que se elija aquí se confirma **solo** en la cohorte nueva de DIN-C1. Lo motiva D5: el destino de ρ_borde se decide entre los updates 5 y 50.

## Estados nuevos
- **Entrenamiento:** para cada trayectoria se reproduce el bloque de entrenamiento del ejecutor v12 sin cambios de mecánica: new_session, carga de checkpoint_005 (modelo, optimizador, RNG de numpy y de torch) y `training.updates`. Se entrena de forma continua del update 5 al 50 y se guardan los estados (M, f) en los updates **10, 20, 30, 40 y 50**.
  - El ejecutor solo admite múltiplos de 25, por eso no se usa directamente.
  - El entrenamiento continuo es equivalente al del ejecutor: una sola sesión con los mismos RNG.
- **Compuerta de reproducción:** el state.npz del update 50 debe coincidir **byte a byte** (SHA-256) con el de la fase 2 de T2-A1, en las 780 trayectorias. Si falla en alguna, esa trayectoria se marca y sus estados nuevos no se usan. Se reporta.
- **Medidas por estado nuevo (10–40):**
  - ρ_borde con `rho_borde.py` congelado (`d8ec69f8…`);
  - p(y) en el panel de validación: argmin (k_min), min p(y) y número de mal clasificados;
  - de M: k* (índice del mayor M_kk), M_kk,max/tr y tr M;
  - precisión y pérdida en entrenamiento.

## Descriptivos (sin veredicto)
Para t ∈ {5, 10, 20, 30, 40, 50}, con los updates 5 y 50 tomados de tablas ya existentes:
1. W(t), la media de la Spearman dentro del split entre log ρ_borde(t) y log ρ_borde(250). Es la **curva de predictibilidad**.
2. W(t) para log(1 − min p_val(t)), para la precisión en validación en t y para la pérdida de entrenamiento en t.
3. La fracción de trayectorias en las que k*(t) = k*(250), y la mediana de M_kk,max/tr en t.
4. Para t < 50: W_adj(t), la predicción de log ρ(250) más allá de log ρ(t) por parte de log(1 − min p_val(t)).

La permutación es dentro del split, con 5000 permutaciones y semilla 240001 + índice. Los p-valores son descriptivos.

## Regla para proponer el predictor de DIN-C1 (al responsable)
- **t\***: el primer t en el que W(t) de log ρ_borde(t) llega a ≥ 0.5, con el mismo signo en splits pares e impares.
- **Propuesta:** «log ρ_borde(t*) predice log ρ_borde(250) dentro del split», con ajuste por log ρ_borde(u5) para descontar lo que ya veía el update 5.
- **Si ningún t < 50 llega a 0.5:** se informa que la ventana es estrecha, cerca del update 50.
