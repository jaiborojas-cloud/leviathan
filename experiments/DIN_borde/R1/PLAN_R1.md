# DIN-R1 — reevaluación posterior con ρ_borde v2 (plan, 2026-10-25)

**Naturaleza:** reevaluación **posterior y declarada**. **No cambia ningún veredicto congelado**: ni T2-A1 (NOT_MET) ni DIN-C1 (PASS). Se registra antes de calcular. El objetivo es saber si las conclusiones dependen del límite angular del v1 (`rho_borde.py`, `d8ec69f8…`), que mide en la práctica el mínimo de los rayos que terminan en un vértice y, como mostró DIN-I2, también puede perder conos.

## Instrumento
`rho_borde_v2.py`, versión r3 de DIN-I2 (PR #83), SHA `2ac015a2…8df0`. Se copia aquí sin cambios como `rho_borde_v2_r3_copia.py`, con las opciones por defecto, y se usa `geometry.py` (`b4d1e0e4…`). Se reportan **ρ_caras** (todas las semirrectas) y **ρ_vert** (rayos a vértices).
- **Preprocesado:** M se simetriza, (M + Mᵀ)/2, porque v2 rechaza asimetrías de 1e-12. Si v2 rechaza un estado (por ejemplo, M no PSD) o se queda sin presupuesto, el estado se reporta como fallo y no se sustituye.

## Etapa 1 (en la VM, ya): la cohorte DIN-C1
1560 estados (780 trayectorias en los updates 10 y 250).
- **Descriptivos:** ρ_caras/v1 y ρ_vert/v1 por update.
- **Sensibilidad de la primaria de C1:** el mismo análisis congelado (`analisis_C1_v2.analizar`, 5000 y 20 000 permutaciones) con L = log ρ_caras(10) e Y = log ρ_caras(250); también solo con L corregido y con ρ_vert. **No es confirmatorio.**

## Etapa 2 (después, en el equipo del responsable): los estados de T2-A1 y DIN-borde
Updates 5, 50, 150 y 250 de los splits 12–167. Se reevalúan el análisis de T2-A1 y los descriptivos D1, D3, D4 y D6 con ρ_caras. Se planificará por separado.
