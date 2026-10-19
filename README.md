# Leviathan / RIPG

Investigación sobre la geometría inducida por familias de perspectivas en redes neuronales. Una perspectiva P define un funcional S_P sobre los parámetros del modelo; su relevancia es el covector ω_P = d_θS_P. La métrica del modelo y la geometría entre perspectivas cumplen papeles distintos.

## Estado documentado

Corte de fuentes: 17 de octubre de 2026, 03:46 UTC. Esta organización no ejecuta experimentos.

- **C1-A: INCONCLUSIVE**. La auditoría C1-A2 documenta dos casos GEOMETRIC_NONINJECTIVITY.
- **T1-A/T1-B:** mapa histórico y análisis descriptivos; la correlación a radio común es control geométrico esperado, no validación predictiva nueva.
- **T2-A:** 800 basales sellados, 1/8000 visitas cerradas y 0/800 horizontes completos. J5/update25 sigue sin resolución geométrica; j7/update25 está pausado en el paso128.

Fuentes y límites en el [estado científico](docs/research-status.md).

## Navegación

| Contenido | Entrada |
|---|---|
| Fundamentos y axioma | [Marco matemático](docs/foundations/mathematical-framework.md) |
| Etapas y resultados | [Índice experimental](docs/experiment-index.md) |
| Próximos pasos | [Roadmap](docs/roadmap.md) |
| Vertientes conceptuales | [Rutas de investigación](docs/research-directions.md) |
| Procedencia e integridad | [Catálogo](docs/source-catalog.md) |
| Fuentes pendientes | [Faltantes](docs/handoff/missing-sources.md) |
| Reglas para agentes | [AGENTS.md](AGENTS.md) |

## Organización

`docs/` contiene síntesis actuales; `docs/archive/` conserva fuentes e importaciones históricas; `experiments/` ofrece accesos por etapa; `tools/` contiene utilidades documentales. [Perspectivas.ipynb](Perspectivas.ipynb) se conserva como notebook histórico sin reejecutar.

Los ZIP, checkpoints y arrays pesados quedan fuera de Git. Las referencias externas son autenticadas y requieren respaldo independiente para colaboradores; no equivalen a un dataset público.

## Verificación documental

```sh
python tools/verify_archive.py
```

Comprueba los hashes de los 398 archivos de la remesa. No entrena modelos ni calcula outcomes. Véase la [decisión de organización y reparación CRLF](docs/decisions/0002-document-organization.md).

## Línea independiente E16

[Composicionalidad y coarse-graining perspectival](experiments/E16/README.md):
controles analíticos pequeños; EXPECTED_GEOMETRIC_CONTROL. Sin cambios en T2-A.
