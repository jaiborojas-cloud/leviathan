# DIN-C1 — diagnóstico de la compuerta de reproducción (2026-10-24)

**Hecho.** La compuerta exacta de `c1_cohorte.py` v0 (`13600b6c…`) no pasó: 0 de 5 en el update 5 y 0 de 5 en el 50, con las trayectorias split12_j25 a j29. Se conserva su resultado.

**Diagnóstico.** `diag_compuerta.py` se corrió en el equipo del responsable: Python 3.12.10, torch 2.14.1+cpu, numpy 2.3.5, sklearn 1.9.1, Windows 11.
- **Update 0:** los pesos iniciales difieren de checkpoint_000 de T2-A0 en a lo sumo 5.6·10⁻¹⁷ (1 ulp). El estado del RNG de numpy es **idéntico**.
- **Update 5 desde cero:** la diferencia máxima de parámetros frente a checkpoint_005 va de 1.1·10⁻¹⁶ a 2.5·10⁻¹⁵. El RNG de numpy es idéntico.
- **Update 50:**
  - el camino desde checkpoint_005 (como en D6 y la fase 2) es **byte a byte igual** a la fase 2: diferencia 0;
  - el camino desde cero difiere de la fase 2 en una diferencia relativa de M ≤ 1.9·10⁻¹²;
  - entre los parámetros de los dos caminos, la diferencia es ≤ 2.8·10⁻¹⁵.

**Conclusión.** La mecánica es la misma: semillas, partición, lotes y optimizador. La diferencia es de redondeo entre entornos, porque T2-A0 generó sus checkpoints en otra máquina, y no se amplifica de forma apreciable hasta el update 50. La compuerta exacta exigía una identidad de bits entre plataformas que no es alcanzable ni necesaria: la cohorte nueva se genera completa en un solo entorno.

**Cambio (v1 del script, todavía borrador).** La compuerta pasa a ser numérica:
- **(a)** |Δθ|max en el update 5 ≤ 1·10⁻¹², con el RNG de numpy idéntico;
- **(b)** la diferencia relativa de M(u50) frente a la fase 2 ≤ 1·10⁻¹⁰.

Las tolerancias dejan márgenes de unos 400 y 50 veces sobre lo observado. Se fijaron **después** de ver estas diferencias, y así se declara; no tocan ningún desenlace.
