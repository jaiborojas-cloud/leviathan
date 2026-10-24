# T2-A1 fase 2 — informe operacional (2026-10-24)

**Naturaleza:** informe operativo. **X sigue cerrado.** No se analiza la relación de los desenlaces con ningún predictor.

- **Script:** `fase2_rho.py` (`4e0d76e8…14d3`), registrado en el commit `eb9b460` antes de correr. Usó el ejecutor v12 (`2381fbcc…3347`) en modo `--solo-entrenamiento` y `rho_borde.py` congelado (`d8ec69f8…416b`).
- **Corrida:** en el equipo del responsable, con 12 procesos. Terminó el 2026-10-24 a las 13:19 (hora de México), aproximadamente una hora después de arrancar. Antes se hizo una prueba con `split12_j25_true` (3 visitas, todas correctas) en otra carpeta; no cuenta para el análisis.
- **Cobertura:** 2340 de 2340 visitas con ρ_borde: 780 trayectorias de los splits 12–167, en los updates 50, 150 y 250. **0 errores.** Todos los checkpoint_005 coincidieron con el manifiesto de cohorte.
- **Tiempo por visita (medianas):** 8.6 s de entrenamiento y 7.9 s de ρ_borde.
- **Calidad numérica:** la diferencia relativa máxima entre los órdenes de Gauss–Legendre 400 y 800 fue 3.7·10⁻⁹. La diferencia máxima entre 720 y 1440 direcciones fue 8.7·10⁻⁴.
- **Tabla de desenlaces:** `resultado/fase2_rho.csv`, SHA-256 `be47e118886627ba61252b7f7dd7793032b42482fd01c44da89efb0cbffb02de`. El hash se recalculó sobre la copia y coincide con `RESUMEN_fase2.json`. La tabla queda publicada **antes** de abrir X.
