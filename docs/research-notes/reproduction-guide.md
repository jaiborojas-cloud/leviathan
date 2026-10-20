# Guía de integridad y reproducción

Esta guía clasifica capacidades disponibles; no ejecuta ciencia ni garantiza
acceso a artefactos externos. Un informe, una tabla, un script y un checkpoint
son piezas distintas. Las rutas y permisos originales deben verificarse antes
de cualquier ejecución autorizada de una etapa.

## Niveles de operación

| Nivel | Operación | ¿Calcula ciencia nueva o repite experimentos? |
|---|---|---|
| I0 | Leer fuentes, comparar hashes, validar enlaces | No |
| R1 | Volver a ejecutar controles sintéticos y sus tablas | Sí, reproducción de controles; requiere tarea científica autorizada |
| R2 | Reconstruir métricas o integrar sobre checkpoints | Sí; requiere datos, entorno y protocolo exactos |
| R3 | Entrenar, continuar visitas o recuperar seguimiento | Sí; no autorizado por esta tarea documental |

## Lo que está disponible por etapa

| Etapa | Material local y fuente | Qué puede verificarse sin ejecutar ciencia | Límite para reproducción completa |
|---|---|---|---|
| E1–E8 | [Notebook histórico](../../Perspectivas.ipynb) y [revisión estática](../archive/review-before-import/docs/experiment-index.md) | Contenido y procedencia de celdas referenciadas | Dependencia E8 ausente y procedencia de salidas E6 pendiente |
| E9/E10 | [Contexto](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md), [cierre E10](../archive/import-2026-10-17/originals/Cierre_E10_RIPG_y_ruta_E11.md) y tablas archivadas | Alcance de las afirmaciones y hashes | Cierre autónomo E9 no recuperado; no prometer insumos completos |
| E11/E12 | [Fichas de cierre](../../experiments/README.md), informes y fuentes archivadas | Decisiones de estimador, ecuaciones y tablas conservadas | Paquetes/checkpoints externos no equivalen a archivos descargados y verificados aquí |
| E13/E15/T1 | [Índice experimental](../experiment-index.md), cierres y manifests | Estado de cada cierre y discrepancias preservadas | Reconstrucción geométrica exige los datos y dependencias de su protocolo |
| E16-A | [README](../../experiments/E16/README.md), código y resultados pequeños | Hashes de manifest/fuentes; diseño y errata | La reproducción R1 requiere NumPy/SymPy y ejecuta los controles |
| E16-B | [README](../../experiments/E16/B/README.md), configuración, protocolo y tablas | Hashes y conservación de INCONCLUSIVE | La reproducción R1 requiere autograd; `verify.py` también vuelve a ejecutar la red |
| E16-C | [Commit de referencia](https://github.com/jaiborojas-cloud/leviathan/tree/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C) | Consultar la fuente fijada; objeto Git local consultado para esta síntesis | No está importado en esta base; no usar rutas locales inexistentes ni ejecutar su rama implícitamente |
| T2-A | [README existente](../../experiments/T2_A/README.md), [nota codex](../../experiments/T2_A/codex/README.md) y archivo de fuentes | Procedencia y distinción diseño/avance/visita/outcome | No es un lanzador de recuperación; no tocar estados ni scripts existentes |

## Comandos exclusivamente documentales

Desde la raíz del repositorio:

```sh
python tools/verify_archive.py
python tools/verify_closed_sources.py
```

Son comprobaciones de hashes de la remesa y las fuentes de cierres. No verifican
por sí solas que una ecuación esté bien implementada ni que un outcome sea válido.
No confundirlas con `experiments/E16/scripts/verify.py` o el verificador de B:
esos verificadores llaman a sus ejecutores científicos y son de nivel R1.
Los README por etapa documentan sus comandos, sin que esta guía los autorice.

## Antes de una reproducción científica futura

Comprobar fuente y versión, dependencias, archivos de entrada accesibles, hashes,
semillas o ausencia de aleatoriedad, parámetros congelados, política de salidas
nuevas y presupuesto. Guardar entorno y resultados fuera de las salidas originales.
Un código de retorno 0 no necesariamente equivale a PASS científico: leer el
resumen y distinguir INCONCLUSIVE. Conservar fallos y diagnosticar antes de corregir.

El [catálogo externo](../archive/import-2026-10-17/EXTERNAL_ARTIFACTS.json) contiene
referencias históricas autenticadas; no prueba acceso actual. No se descargan
archivos ni se solicitan credenciales en esta tarea. El [inventario de faltantes](../handoff/missing-sources.md)
es la referencia para material no recuperado.
