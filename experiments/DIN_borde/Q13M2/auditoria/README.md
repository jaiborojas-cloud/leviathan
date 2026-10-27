# Auditoría independiente DIN-Q13-M2

**Antes de congelar:** [conclusión](CONCLUSION.md), [defectos F01–F04](DEFECTOS.md), [matriz de revisión](MATRIZ_REVISION.md). Se propone corregir el aislamiento de fallos puntuales, preservar salidas y actualizar la evidencia. No se modifican fuentes, diseño, instrumentos ni etapas previas.

| Recurso | Contenido |
|---|---|
| [DESIGN_FROZEN.md](DESIGN_FROZEN.md) | Diseño de esta auditoría, comprometido antes de código/medición |
| [sources/provenance.json](sources/provenance.json) | Commit objetivo, snapshots y SHA; referencias #104/#105/#107 |
| [config.json](config.json) | Semillas y presupuestos inalterados |
| [results/cases/summary.json](results/cases/summary.json) | 23 casos adversariales y trazas, incluidos fallos esperados |
| [results/validation/schema.json](results/validation/schema.json) | 109 casos de plan |
| [results/domain/domain.json](results/domain/domain.json) | 27 controles de dominio e integraciones |
| [results/api_edges/results.json](results/api_edges/results.json) | Límites adicionales de API; no fallos CLI demostrados |
| [results/reference_LS/reference.json](results/reference_LS/reference.json) | Única referencia real autorizada, como LS secundaria |
| [results/monte_carlo_v1/summary.json](results/monte_carlo_v1/summary.json) | 800 tablas nulas, nominal5000/2000 |
| [rates.csv](rates.csv) | Tasas globales/condicionadas e IC Wilson95 |
| [external_manifest.csv](external_manifest.csv) | Arrays y fixtures externos por SHA, fuera de Git |
| [verification.json](verification.json) | 826 condiciones de integridad, no aprobación del analista |
| [verification_publicacion.json](verification_publicacion.json) | Comprobaciones finales de publicación |
| [manifest.sha256](manifest.sha256) | SHA de todos los miembros, salvo manifests de cierre |

## Reproducción

Python3.12.14, [dependencias exactas](requirements.txt). Desde la raíz, con un solo hilo BLAS:

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/Q13M2/auditoria/scripts/cases_v1.py
python experiments/DIN_borde/Q13M2/auditoria/scripts/validation_v1.py
python experiments/DIN_borde/Q13M2/auditoria/scripts/domain_v1.py
python experiments/DIN_borde/Q13M2/auditoria/scripts/reference_LS_v1.py
python experiments/DIN_borde/Q13M2/auditoria/scripts/reference_numeric_check.py
python experiments/DIN_borde/Q13M2/auditoria/scripts/monte_carlo_v1.py
python experiments/DIN_borde/Q13M2/auditoria/scripts/api_edges_v1.py
python experiments/DIN_borde/Q13M2/auditoria/publicacion/verify_v1.py
```

**Escrituras exclusivas:** estos comandos sirven en una copia limpia de la implementación anterior a resultados, no sobre esta entrega ya poblada. Las carpetas de salida deben estar ausentes; no borrar los resultados archivados para reejecutar. Para una réplica nueva, usar otro checkout/copia y una ubicación externa vacía; cualquier cambio de rutas/config se versiona antes de medir y queda explícito como réplica, conservando semillas/criterios. La guarda exige código comprometido y verifica los snapshots por SHA. Una ruta externa de esta sesión no implica almacenamiento remoto permanente: los arrays se regeneran con receta y semillas, verificando su SHA en un entorno idéntico.

La CLI de validación genera sus tablas y planes sintéticos fuera de Git y puede leer exclusivamente la tabla LS publicada para el contraste autorizado. No se ejecuta análisis de ninguna cohorte M2 ni se usa G3 como piloto. La suite del autor se revisó sin ejecutar su fixture entrenado.

## Secuencia de commits

1. `01b6dc9e`: diseño, configuración y fuentes antes del código.
2. `a04cb766`: motor independiente, casos, Monte Carlo y referencia antes de medir.
3. `734e679f`: dominio antes de ejecutarlo.
4. `e6861815`: contraste numérico puntual LS antes de ejecutarlo.
5. `7321fff2`: verificación antes de su ejecución.
6. `b41caa99`: límites adicionales de API previstos en el diseño antes de medirlos.
7. Resultados e informe, conservación de todas las salidas y publicación en PR aparte, borrador sin fusión.

Los SHA del analista y pruebas auditados son `2e69516e62b59d90d8abd9d91e1468e538c07b50dc059a6814cd7a20197030fa` y `063c15e455bef12ba89dc4c68c509e928deaf65938171721726d0b33bbe0d1f3`. La publicación no congela el confirmatorio ni decide por el responsable.
