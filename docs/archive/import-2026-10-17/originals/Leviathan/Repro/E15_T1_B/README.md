# Leviathan / RIPG — E15-T1-B

Análisis descriptivo de 80 estados existentes a cuatro radios comunes. No cambia C1 ni T1-A y no confirma hipótesis nuevas en el panel usado para descubrirlas.

## Ejecución y recuperación

1. Recuperar los archivos de `/Leviathan/Repro/E15_T1_B/` y extraer cada `split*_j*_*.zip` en la carpeta de trabajo. Cada archivo contiene `states/<estado>/` con insumos, cuatro tareas Jacobi (256/512, dos fases), arrays, comprobaciones y `result.json` final.
2. Verificar SHA y CRC con `manifest.csv` y `final_audit.json`. Los estados finalizados no se recalculan. Resultados fallidos no se sustituyen.
3. Recuperar T1-A desde `/Leviathan/Repro/E15_T1_A/`, incluido su manifiesto y los 80 paquetes; extraer sus estados. Adaptar sólo la ruta local de `source_locations.json`, preservando identidades y hashes científicos. Las fuentes C1/A2 y sus hashes están en `input_integrity.json`.
4. Dependencias numéricas: numpy 2.3.5, scipy 1.17.0, shapely 2.1.2, scikit-learn 1.8.0, matplotlib 3.10.8. No hay nuevo entrenamiento: se usan los M/f exactos ya reconstruidos y verificados en T1-A. Los 80 checkpoints se conservan y verifican por SHA.
5. Confirmar `protocol_T1_B_frozen.sha256`, ejecutar `run_common.py` sólo para pendientes. El código usa DOP853 rtol=2e-10/atol=2e-12 y el mismo núcleo `geometry.py`/`audit.py`.
6. Persistencia: `persist.py` requiere helpers oficiales actuales de Library en `../helpers_t1b/`. En una sesión nueva, recuperar identidades/versiones actuales de archivos mutables antes de reemplazarlos; nunca suponer versiones. Los recibos locales no son credenciales. Si un estado terminó pero su guardado se interrumpió, guardar el resultado existente, sin reintegrarlo.
7. Con los 80 estados, ejecutar `analyze.py`, `figures.py`, `final_audit.py` y el generador de cierre. Las tablas declaran n y las compuertas; un parcial no se presenta como cierre.

## Precisiones científicas

- Primario: máximo angular sobre el borde a radio común. Secundario: máximo dentro del prefijo del disco. Se separan ambas definiciones también en el radio nominal.
- El coeficiente previo ~0.972 usaba el máximo dentro del disco. La comparación de bordes evita confundir un cambio de resumen con un cambio de radio.
- Los dos positivos tienen métricas de Dexp y rangos a todos los radios válidos, pero no C_A ni residuos respecto de C_A artificiales.
- El bootstrap agrupa por split y es una sensibilidad descriptiva. Los splits comparten muestras Wine; los intervalos no son inferencia confirmatoria independiente.
- Los residuos se expresan en log10(κ−1), no en κ. En random una diferencia relativa grande puede corresponder a una deformación absolutamente diminuta.
- C_A sigue siendo el estimando original sobre el dominio propio de área 0.02. Fijar el radio del resultado Dexp no uniforma retrospectivamente el dominio de C_A.
- La curvatura angular de borde usa medida de ángulo de lanzamiento, no área espacial. No equivale a Lambda1% ni Lambda0.1%.
- Censura de r_conj/r_inj/A_embed se conserva. No se declara que un borde simple certifique inyectividad global ni se identifica un cut locus completo.

## Incidencias archivísticas

El manifiesto T1-A enumera un temporal histórico ausente de su ZIP (`split1_j4_true/jacobi/n512_phase1.tmp.npz`). Los 780 arrays finales, 80 paquetes y 80 checkpoints fueron verificados. Se conserva la salvedad; no se fabricó el temporal ni se alteró T1-A.

Un conflicto de versión durante el guardado de 40 estados se resolvió leyendo la versión actual: las 144 filas previas eran idénticas y se añadieron las 16 filas terminadas. No hubo recálculo ni cambio científico. Ver `persistence_recovery.json`.
