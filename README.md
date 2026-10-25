# Leviathan / RIPG

<p align="center">
  <img src="Mathematical-Leviathan-Rising.png" width="560" alt="Leviatán emergiendo del mar, trazado con mallas geométricas y nodos luminosos.">
</p>

<p align="center"><em>Mathematical Leviathan Rising</em></p>

**RIPG** (*Relevance-Induced Perspective Geometry*) estudia la **geometría que inducen las perspectivas** sobre una red neuronal. Una perspectiva es un funcional escalar: qué se evalúa del modelo. Su relevancia es un covector sobre los parámetros, y la forma en que esa relevancia cambia de una perspectiva a otra define una métrica, con su curvatura, sus geodésicas y su borde:

$$
p\longmapsto S_p(\theta)
\longmapsto\omega_p=d_\theta S_p
\longmapsto B=d_p\omega
\longmapsto h=B C B^T.
$$

La geometría de Fisher describe el modelo estadístico; la familia de funcionales fija qué es relevante; la geometría perspectival depende de las dos. El proyecto tiene dos frentes:
- **Teoría:** definiciones, axioma de admisibilidad, métrica, conexión, curvatura y composición.
- **Experimentos:** preguntas cerradas sobre redes reales y sintéticas, con protocolos congelados antes de medir.

> **Cómo leer este repositorio.** Todo lo que aquí se afirma enlaza a un documento de cierre, un resultado con hash o una prueba. Se distinguen **identidades matemáticas**, **controles numéricos**, **hallazgos exploratorios** y **resultados confirmatorios**; los resultados negativos e inconclusos se conservan con el mismo peso que los positivos. Si una frase de esta portada no coincide con su fuente enlazada, **manda la fuente**.

## Alcance

| frente | qué abarca | sistemas |
|---|---|---|
| Teoría | fundamentos y admisibilidad respecto del kernel de Fisher; métrica ideal y regularizada; conexión, curvatura, Jacobi, corte y holonomía; observables y atribución; composicionalidad | — |
| Geometría en entrenamiento real | ¿la geometría perspectival distingue o anticipa el aprendizaje? (E10–E15, T1, T2) | MLP 13→64→32→3 en Wine (etiquetas verdaderas y aleatorias); Digits y Wisconsin en E13 |
| Composición y caminos | qué conserva la composición de perspectivas; longitudes, caminos mínimos, conjugados y cotas al borde (E16) | red sintética 2→2→1 y familias softmax sintéticas, sin entrenamiento |
| Dinámica hacia el borde | cómo el entrenamiento lleva la geometría a su borde y cuándo se decide (DIN-borde) | 780 trayectorias Wine de T2-A1 |

## Resultados principales (con su fuente)

| pregunta | estado | resultado | fuente |
|---|---|---|---|
| ¿La geometría anticipa el aprendizaje? (E10) | cerrado, exploratorio | la precisión se separa **antes** que la geometría; sin poder incremental robusto | [E10](experiments/E10/CONCLUSION.md) |
| ¿De qué depende la métrica estimada? (E11) | cerrado, exploratorio | del panel, la referencia, la regularización y el rango; con paneles pequeños el contraste cambia de signo | [E11](experiments/E11/CONCLUSION.md) |
| Curvatura con datos verdaderos frente a aleatorios (E12) | cerrado, exploratorio | mayor \|K\| con etiquetas verdaderas en 36 de 40 pares de dos tareas; depende de la tarea y no es una ley de signo | [E12](experiments/E12/CONCLUSION.md), [A09](docs/research-notes/claims-and-evidence.md) |
| Mapa topológico de 80 estados (T1-A) | descriptivo completo | 2 de 40 estados con etiquetas verdaderas no son inyectivos; 0 de 40 con aleatorias | [T1-A](experiments/T1/A/CONCLUSION.md) |
| ¿La curvatura temprana (X, update 5) predice la no inyectividad futura? (T2-A0) | **INCONCLUSIVE** | el instrumento no cerró las visitas difíciles; X siguió sellado | [cierre T2-A0](experiments/T2_A/claude/CIERRE_T2A0_v1_CONGELADO.md) |
| ¿X predice la cercanía posterior al borde? (T2-A1, confirmatorio, 780 trayectorias) | **NOT_MET** | W = 0.019 (p = 0.33); ajustado, W = 0.011 (p = 0.39); análisis único con X abierto al final | [cierre T2-A1](experiments/T2_A1/CIERRE_T2A1_v1_CONGELADO.md) |
| ¿Qué conserva la composición de perspectivas? (E16) | control geométrico esperado | el rango depende de cancelaciones y de la Hessiana de la composición; hay contraejemplos de descenso | [E16](experiments/E16/CONCLUSION.md) |
| ¿Se estabilizan los caminos óptimos? (E16 J–AB) | inconcluso en todos | **la longitud converge antes que la forma**; los «óptimos» finos son sillas numéricas | [índice E16](experiments/E16/README.md) |
| ¿Qué tan ajustada es la cota ρ_borde? (E16-AG, AH) | exploratorio | sobreestima la distancia de 2 a 4 veces, pero **ordena bien** (Spearman 0.94–0.98) | [AG](experiments/E16/AG/CONCLUSION.md), [AH](experiments/E16/AH/CONCLUSION.md) |
| Piso de ρ_borde cuando M colapsa (DIN-D2) | teoría con condiciones | ρ̃(e_k e_kᵀ) = min(1/n, 1/m_k − 1/n); el instrumento falla en paneles degenerados sintéticos, pero no en los reales | [D2](experiments/DIN_borde/D2/CONCLUSION.md), [auditoría](experiments/DIN_borde/auditoria_q5/AUDITORIA_Q5_estados_reales_2026-10-24.md) |
| ¿Cómo llega el entrenamiento al borde? (DIN-borde D1–D6) | **exploratorio** | M colapsa sobre el ejemplo de validación **menos confiado**; ρ_borde sigue su incertidumbre (Spearman 0.998); el destino se decide entre los updates 10 y 30 | [D1](experiments/DIN_borde/RESULTADO_D1_2026-10-24.md) · [D3](experiments/DIN_borde/RESULTADO_D3_2026-10-24.md) · [D4](experiments/DIN_borde/RESULTADO_D4_2026-10-24.md) · [D5](experiments/DIN_borde/RESULTADO_D5_2026-10-24.md) · [D6](experiments/DIN_borde/RESULTADO_D6_2026-10-24.md) |

Tabla completa, con todas las etapas y su estado oficial: [catálogo de experimentos](docs/CATALOGO_EXPERIMENTOS.md).

**Lo que no se ha establecido:** una ley universal del signo de la curvatura, un predictor universal de la generalización o una explicación causal. Los hallazgos de DIN-borde son exploratorios: salen de datos ya usados y solo un confirmatorio con cohorte nueva puede sostenerlos. Todo lo de entrenamiento real es de **una familia** (MLP en Wine, panel de 27 ejemplos); no se afirma que se transfiera a otras redes o datos.

## En curso
- **DIN-C1:** confirmatorio de la señal temprana de DIN-D6. La hipótesis es que la incertidumbre sobre el ejemplo más difícil en el update 10 predice la cercanía al borde en el 250, más allá de ρ_borde(10). Usará una cohorte nueva (splits 168–323, nunca usados). Está en diseño, **sin congelar** y sin datos.
- **E16:** cotas y caminos al borde en familias sintéticas.

## Teoría matemática

El [compendio de teoría RIPG](docs/theory/README.md) reúne fórmulas, axioma, formulaciones, hipótesis y límites, con sus fuentes y convenciones de índices.

| tema | documento |
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

Sobre el cociente identificable, la forma ideal es el pullback de la cométrica de Fisher; en coordenadas compatibles, $h=BF^+B^T$. La implementación regularizada es un estimando distinto, con referencia y escala explícitas.

## Cómo se trabaja: reglas que hacen verificable lo anterior

- **Diseño antes que datos.** Cada protocolo se congela con su hash antes de medir; los commits siguen el orden diseño → código → mediciones.
- **Predictores sellados.** En T2, X estuvo sellado por hash hasta que el instrumento y el análisis quedaron congelados, y se abrió una sola vez. Las desviaciones se documentan, por ejemplo el [acceso de un agente a las basales](experiments/T2_A/claude/DESVIACION_ACCESO_BASELINE_NEMOTRON_2026-10-21.md).
- **Ningún estado se reemplaza ni se excluye a posteriori.** Los fallos, las versiones inválidas y los INCONCLUSIVE se conservan.
- **Descubrir y confirmar son cosas separadas.** Los datos usados para descubrir una hipótesis no sirven para confirmarla.
- Reglas completas: [AGENTS.md](AGENTS.md).

## Evidencia y fuentes

- [Estado científico documentado](docs/research-status.md) · [índice experimental](docs/experiment-index.md) · [fichas de cierre](experiments/README.md)
- [Afirmaciones y fuentes](docs/research-notes/claims-and-evidence.md) · [resultados negativos](docs/research-notes/negative-results.md) · [preguntas abiertas](docs/research-notes/open-questions.md) · [guía de reproducción](docs/research-notes/reproduction-guide.md)
- [Roadmap](docs/roadmap.md) · [rutas de investigación](docs/research-directions.md) · [catálogo de fuentes](docs/source-catalog.md) · [fuentes faltantes](docs/handoff/missing-sources.md)

**Organización:**
- `docs/theory/` es la entrada matemática.
- `docs/archive/` conserva las fuentes históricas, que no se modifican.
- `experiments/` contiene los protocolos, el código y los resultados de cada etapa.
- [Perspectivas.ipynb](Perspectivas.ipynb) es el notebook histórico; no se ha reejecutado.
- Los checkpoints, arrays pesados, ZIP y entornos quedan fuera de Git; se referencian por SHA-256.

## Verificación

```sh
python tools/verify_archive.py
python tools/verify_closed_sources.py
```

Estos scripts comprueban los hashes de las fuentes históricas y de los cierres sin entrenar ni calcular desenlaces. Además, cada etapa experimental trae su propio manifiesto (`MANIFIESTO_*.sha256`, `manifest.csv` o `verification.json`) para recalcular los hashes de sus resultados.

## Licencia y cita

**© 2026 Jair Rojas. Todos los derechos reservados.**
- **Licencia:** no se concede ninguna. Copiar, modificar, redistribuir o reutilizar cualquier parte de este repositorio requiere autorización previa y por escrito; los detalles están en [LICENSE](LICENSE).
- **Cita:** para referenciar el trabajo, usa [CITATION.cff](CITATION.cff). Citarlo no concede permiso de reproducción.

