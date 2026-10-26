# Retención de datos: inventario y revisión pendiente

**Regla:** no se borra nada sin una revisión explícita y la aprobación del responsable (AGENTS.md: «no borrar ni mover datos existentes innecesariamente»). Esta nota registra qué se conserva fuera de Git y deja **pendiente una depuración**. Cuando se haga, se preguntará de cada conjunto si sigue siendo relevante: si lo necesita algún cierre, alguna reproducción o alguna pregunta abierta. Lo decidió el responsable el 2026-10-26 a las 10:00.

| conjunto | dónde | contenido | lo usan | ¿candidato a depurar? |
|---|---|---|---|---|
| Basales T2-A0 (800) | `D:\RIPG_DATA\T2_A\data\baselines\…` | checkpoints del update 5, basales sellados, fuentes | todo T2/DIN (X, checkpoint_005, sources) | **no**: es la raíz de la reproducibilidad |
| Lote 0 de T2-A0 | `D:\RIPG_DATA\T2_A\produccion` | 128 visitas, unos 150 GB | cierre T2-A0 (INCONCLUSIVE) | revisar: el cierre ya está congelado |
| T2-A1 (fase 0, diagnóstico, fase 2, ρ_u5) | `D:\RIPG_DATA\T2_A1` | estados y checkpoints de los updates 5, 50, 150 y 250 de los splits 8–167 | cierre T2-A1, D1–D7, R1 | revisar después de un posible R2 |
| DIN-borde D6 | `D:\RIPG_DATA\T2_A1\DIN_borde\d6` | estados de los updates 10–50 | D6, D7, R1, D9 | no por ahora (D9) |
| Cohorte DIN-C1 | `D:\RIPG_DATA\DIN_C1` | estados de los updates 5, 10, 30 y 250 (splits 168–323) y compuertas | cierre DIN-C1, R1 | no por ahora |
| Cohorte DIN-C2 | entorno del agente de cohorte (manifiesto en `experiments/DIN_borde/C2/cohorte/external_manifest.csv`) | checkpoints y estados | cierre DIN-C2 | no por ahora |
| G1, G2 y G3 (sintéticos) | entorno del otro agente (manifiestos en cada carpeta) | pesos, estados y arrays | cierres exploratorios | revisar: regenerables desde las semillas |
| Cuarentena de Nemotron | `leviathan\nemotron\cuarentena_X` | copia en claro de medidas basales | desviación documentada | revisar con cuidado (cegado histórico) |

**Cuándo revisar:** al terminar la línea DIN (después de D9 y, si se hace, Q13), o si el disco baja de 20 GB libres.
