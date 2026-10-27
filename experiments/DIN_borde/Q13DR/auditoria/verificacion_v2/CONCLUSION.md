# Dictamen de verificación de la v2, commit245d735f

**Recomendación: corregir los casos residuales antes de congelar.** La v2
resuelve gran parte de #104, pero no se da un aprobado global: una c constante
decimal aún puede producir β/IC arbitrarios y el rango común puede reportarse
negativo. No se modificó el diseño ni el analista.

| Hallazgo anterior | Dictamen v2 |
|---|---|
|F01, población del punto/bootstrap|Resuelto; caso válido95% comunes usa c correcta.|
|F02, degeneraciones|Parcial: casos antiguos salen INCONCLUSIVE sin crash; persiste constancia decimal no detectada.|
|F03, plan|Parcial: casos antiguos abortan correctamente; entradas nuevas aún causan OverflowError/OSError.|
|F04, Spearman|Resuelto, incluidos empates parciales y constantes.|
|F05, interpretación del margen|Texto resuelto; defecto nuevo en rango común no ordenado.|
|F06, ABORTA versus crash|Resuelto en regresiones y nueva heurística.|

Las decisiones de precisión L4–L5, mínimo80% comunes, dominios, comparaciones
exactas, equivalencia secundaria y tendencia lineal están incorporadas. Sus
pruebas y el alcance de cada comprobación están en la matriz completa.

Casos residuales concretos:

- **N01, alta:** tabla válida N200,160 comunes y c común=.1 en los seis niveles:
  publica β=8 e IC=[−8,8], cero réplicas fallidas, en lugar de INCONCLUSIVE por
  parámetro no identificado. Comprobar constancia exacta antes de centrar.
- **N02, media:** otra tabla válida produce rango_c=−.3 y margen=−.006; usar max−min.
- **N03/N04, media:** eps=10**400 y archivos ausentes/directorios aún generan
  traceback/código1 en lugar de ABORTA3.
- **N05, trazabilidad:** cuenta116 fallos de300, pero sólo guarda20 detalles;
  preservar todos los índices/errores o un archivo completo por SHA.

**Monte Carlo repetido:**1.000 réplicas nominales, mismos seeds e inputs/álgebra
bit por bit respecto de v1. MODULA8/400 y10/400 en los nulos,74/200 en β=+.03.
NO_MODULA secundaria0 en las tres celdas; INCONCLUSIVE por control15/400 sólo
en N200. No inflación global >5% observada en los nulos probados; no certifica
calibración universal ni anula los contraejemplos del verificador de entradas.

Todo sintético. Se conservaron resultados v1 y versiones/fallo del verificador;
la repetición final no descartó réplicas. Sin Wine/C2/Q13 reales, redes,
entrenamiento o geometría. Se reporta; el responsable decide correcciones y cierre.

[Matriz F01–F06/decisiones](MATRIZ_HALLAZGOS.md) · [casos nuevos](NUEVOS_DEFECTOS.md) ·
[tasas y límites](TASAS.md) · [verificación](verification.json).
