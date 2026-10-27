# Cohorte DIN-Q13-DR: potencia, plan y productor

**Listo para ejecución externa: N200,6.000 trayectorias. No se entrenó la cohorte en este entorno.**

- [Potencia y sensibilidades](potencia/RESULTADO_v1.md): independencia395/400 MODULA, Wilson inferior.971076; sensibilidades≥.819837. Son simulaciones, no resultados de cohorte.
- [Plan fijo por SHA](q13dr_plan.json), [SHA](q13dr_plan.sha256).
- [Productor Windows](scripts/cohorte_v3.py), [SHA](scripts/cohorte_v3.sha256), [versiones exactas](requirements_windows_v3.txt).
- [Comandos PowerShell y reanudación](EJECUCION_WINDOWS_v3.md).
- [Validación sin entrenar](VALIDACION_PRODUCTOR_v1.md).
- [Procedimiento previo de potencia](PROCEDIMIENTO_POTENCIA_v1_CONGELADO.md), [fuentes por SHA](config_potencia_v1.json), [equivalencia](source_equivalence.json).

SHA plan: `e7c99a0188abc84cce6504fb6882b9373775f8aaba8d0eebdf597c752c1fed64`.
SHA script: `7b855802d0cf1b4bce7a3ede0a465b876284c847aeb1bec4508af7b1228fc9cb`.

Secuencia publicada: procedimiento b039bf49→código c1973943→potencia6587ba6a→plan fe8dd9c8→productor2452bf47; validación sin entrenamiento tras comprometer su código b1b0ccc7. No se modifica el diseño congelado ni Q13/C2 u otra etapa. La única asociación en datos Q13 fue la correlación A0–LS autorizada para sensibilidad; no D,p ni X–Y. No hay tabla de la nueva cohorte publicada: se generará en Windows.
