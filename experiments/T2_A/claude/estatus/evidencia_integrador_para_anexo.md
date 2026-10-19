# Evidencia sobre integración y registros — insumo para el anexo operativo de E1 (sin valores propuestos)

**Fuentes.** (1) Informes A1–C6 de una inspección de solo lectura de `sources/` de la compacta, hecha con otro modelo (Nemotron 3.5 super VL); las citas de línea no se verificaron contra los archivos. (2) `RIPG_RESULTADOS_PC.zip` (task_log, progress, index y segmentos 91–139), revisado directamente.

## 1. Qué hay en `sources/` (según la inspección)
- Un solo integrador ODE de SciPy: `solve_ivp` DOP853, rtol 2e-10, atol 2e-12, sin max_step, first_step, min_step, events ni timeout; comprueba `success` y lanza `RuntimeError(sol.message)` (geometry.py:41–42, audit.py:87–88).
- RK4 manual de paso fijo (`rk4`, `exp_map_rays`): sin control de error ni comprobación de éxito.
- Refinamiento adaptivo de malla (`adaptive.integrate`): tope de 18 rondas y 1.2 M de celdas.
- Registros: `nfev` total por integración; wall y CPU por tarea; hilos = 1 por variables de entorno; peak RSS en case_engine; versiones solo en replay_gate.json (torch). **No se cuentan ni registran pasos rechazados.**
- Reanudación: `save_checkpoint` guarda pesos, Adam, RNG numpy y torch, step y semillas; **no hay función de reanudación en el camino productivo** (`replay()` solo la prueba); `baseline()` se niega a continuar si existe una trayectoria parcial. El solver ODE no se reanuda: cada integración parte de t = 0.

## 2. Lo que NO está en `sources/`
El integrador de visitas que produjo `RIPG_RESULTADOS_PC.zip` (avance por pasos con checkpoint cada 4 pasos aceptados, estado del solver en `replay.pkl`, PAUSED y reanudación, aceleraciones MPFR con gmpy2, `task_log.csv` de 6 campos) y el código de continuación 5 → 250. La inspección no dice nada sobre ellos; sus conclusiones «único integrador ODE» y «no existe reanudación del solver» valen solo para `sources/`.

## 3. Corrida pausada (split8_j5_true, update 25), verificada
- Estado guardado del solver: DOP853, rtol 2e-10, max_step = inf, t_bound = 0.09 (objetivo de búsqueda), 8192 variables (2048 rayos × [P(2), v(2)]).
- `task_log.csv` (sin encabezado): marca de tiempo, estado, paso aceptado, radio, nfev acumulado, **tiempo de integración (wall) acumulado** (el campo 6 no es CPU: CPU acumulada = 2589.28 s en progress.md/index.json).
- Tamaño de paso aceptado: ≈ 3.3×10⁻⁵ en los pasos 91–118; luego 1.9×10⁻⁵ (121), 5.6×10⁻⁶ (127), 1.6×10⁻⁶ (133), 4.3×10⁻⁷ (139). Cociente entre pasos consecutivos desde el 125: 0.805–0.816 (mediana 0.808).
- Rechazos inferidos de `nfev`, suponiendo 15 evaluaciones por paso aceptado (12 de etapas + 3 de salida densa) y 12 por intento rechazado (**supuesto a verificar en el código del integrador de visitas y en la versión de SciPy**): 0 o 1 rechazo por bloque de 4 pasos hasta el 118; 4 por bloque (1 por paso aceptado) desde el ~119 hasta el 139. Todos los valores inferidos salen enteros.
- Tiempo de pared por paso aceptado: 16–20 s hasta el 118 y ≈ 29 s desde entonces.

## 4. Errores o límites de la inspección detectados
- Dice 12 segmentos; hay 13 (pasos 91–139).
- Deja sin nombre los campos 5 y 6 del `task_log.csv` (nfev y tiempo de integración acumulado).
- Las citas de línea y las ausencias («sin coincidencias») dependen de la búsqueda de ese modelo; no verificadas.

## 5. Qué falta obtener antes del anexo
1. Código del integrador de visitas y de lo que escribe `replay.pkl`, `task_log.csv`, `index.json` y `progress.md`.
2. Código de continuación 5 → 250 y de su reanudación exacta (pesos, Adam, RNG).
3. Registros de una visita normal completa (p. ej. split8_j6_true update 25), para conocer la variabilidad sin patología y poder estimar falsas alarmas.
4. Hardware, hilos y versiones de esa corrida.
5. Si el recuento de rechazos por `nfev` es válido en esa implementación, o si hay que registrarlos de forma explícita.
