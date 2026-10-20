# Leviathan / RIPG

Investigación sobre la **geometría de perspectivas inducida por relevancias**
en modelos y redes neuronales. Una perspectiva define qué se evalúa mediante
un funcional escalar; su relevancia es un covector sobre los parámetros. La
variación entre perspectivas induce una geometría propia:

$$
p\longmapsto S_p(\theta)
\longmapsto\omega_p=d_\theta S_p
\longmapsto B=d_p\omega
\longmapsto h=B C B^T.
$$

Fisher describe la geometría estadística del modelo. La familia de funcionales
especifica la relevancia. Su geometría perspectival depende de ambas elecciones.

## Teoría matemática

El [compendio de teoría RIPG](docs/theory/README.md) reúne fórmulas, axioma,
formulaciones, hipótesis y límites, con fuentes y convenciones de índices.

| Tema | Documento |
|---|---|
| Espacios, funcional, relevancia, Fisher, kernel y axioma | [Fundamentos y admisibilidad](docs/theory/01-fundamentos.md) |
| Métrica ideal, cociente, pseudoinversa y regularización | [Métrica y covariancia](docs/theory/02-metrica-y-covariancia.md) |
| Conexión, curvatura, geodésicas, Jacobi, corte y holonomía | [Geometría diferencial](docs/theory/03-geometria-diferencial.md) |
| Distancias, energía, concentración, Schur y atribución | [Observables geométricos](docs/theory/04-observables-y-atribucion.md) |
| Cartas, subfamilias, agregación y composición escalar | [Composicionalidad y coarse-graining](docs/theory/05-composicionalidad.md) |
| Hipótesis sobre aprendizaje, predicción y extensiones | [Hipótesis y límites de evidencia](docs/theory/06-hipotesis-y-limites.md) |
| Fuentes originales, precedencia y definiciones pendientes | [Procedencia del compendio](docs/theory/fuentes.md) |

El núcleo exige admisibilidad respecto del kernel de Fisher:

$$
\omega_p\in(\ker F_\theta)^\circ,\qquad B\ker F_\theta=0.
$$

Sobre el cociente identificable, la forma ideal es el pullback de la cométrica
Fisher; en coordenadas compatibles se escribe $h=BF^+B^T$. La implementación
regularizada es un estimando distinto, con referencia y escala explícitas.
Los capítulos explican cuándo el tensor es SPD, cómo se transforma y qué
condiciones requiere un descenso a variables agregadas.

## Investigación y evidencia

El marco distingue identidades matemáticas, controles numéricos, hallazgos
condicionados e hipótesis pendientes. No se ha establecido una ley universal del
signo de curvatura, un predictor universal de generalización ni una explicación causal.

- [Estado científico documentado](docs/research-status.md), con su propio corte de fuentes.
- [Índice experimental](docs/experiment-index.md) y [fichas de cierre](experiments/README.md).
- [Roadmap](docs/roadmap.md) y [rutas de investigación](docs/research-directions.md).
- [E16: composicionalidad](experiments/E16/README.md) y [E16-B: instrumentación](experiments/E16/B/README.md).
- [Seguimiento T2-A](experiments/T2_A/README.md), con protocolos y evidencia propios;
  esta actualización documental no altera su trabajo ni el directorio `claude`.

Los cierres prevalecen sobre planes históricos: una réplica inconclusa conserva
ese estado y los supervivientes numéricos no se convierten en confirmación.
El compendio teórico no actualiza outcomes ni ejecuta experimentos.

## Organización y fuentes

`docs/theory/` es la entrada matemática; `docs/foundations/` conserva las síntesis
previas. `docs/archive/` mantiene fuentes históricas inmutables; `experiments/`
contiene protocolos, código y resultados por etapa. [Perspectivas.ipynb](Perspectivas.ipynb)
se conserva como notebook histórico sin reejecutar.

[Catálogo de fuentes](docs/source-catalog.md) · [Faltantes](docs/handoff/missing-sources.md) · [Reglas del repositorio](AGENTS.md).

Los ZIP, checkpoints, arrays pesados, entornos y credenciales quedan fuera de Git.
Las referencias externas autenticadas requieren respaldo accesible; no equivalen
a datos públicos disponibles para cualquier colaborador.

## Verificación documental

```sh
python tools/verify_archive.py
python tools/verify_closed_sources.py
```

Verifican hashes de archivos históricos y fuentes de cierres, sin entrenar ni
calcular outcomes. La [revisión del compendio](docs/theory/review.json) registra
los controles documentales y la preservación del árbol protegido. Véase también
la [decisión de organización histórica](docs/decisions/0002-document-organization.md).
