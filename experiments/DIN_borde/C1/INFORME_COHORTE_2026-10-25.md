# DIN-C1 — informe operacional de la cohorte (2026-10-25)

**Naturaleza:** informe operacional. **No contiene el análisis de X frente a Y** ni distribuciones de desenlaces. El diseño está congelado: `DISENO_DIN_C1_v3_CONGELADO.md`, con su manifiesto.

- **Corrida:** `c1_cohorte.py` v3 (`dc077630…`), en el equipo del responsable con 12 procesos. Terminó el 2026-10-25 a las 12:32 (hora de México).
- **Cobertura:** 780 de 780 trayectorias planificadas: splits 168–323, 156 splits, IDs únicos. **0 errores, 0 valores inválidos** (ρ > 0, X finita).
- **Auditoría de precisión de ρ(10)** en 40 IDs preseleccionados y publicados en el resumen: diferencia relativa máxima con 5760 direcciones y orden 1600 de **8.3·10⁻¹⁵** (mediana 8.7·10⁻¹⁶).
- **Cota de cuerda con caras completas (update 10):** 0 violaciones; cara máxima de 2 puntos, es decir, paneles en posición general.
- **Estabilidad direccional** (`dif_dir`, máximo): 4.4·10⁻³ en u10, 1.5·10⁻⁴ en u30 y 8.5·10⁻⁵ en u250.
- **Tabla:** `cohorte/c1_cohorte.csv`, SHA-256 `554f354e62072e53f983002cb3233c5392756a8a95b08cc137bb3b0b28e5fd84`. Coincide con `cohorte/RESUMEN_c1.json`. Se publica **antes** del análisis.
- **Compuerta** (`compuerta_v3/RESUMEN_c1.json`, SHA `eed9af07…59e`): PASA true, mismo `script_sha256` que la cohorte.
