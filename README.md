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
| ¿La confianza temprana anticipa el borde? (DIN-C1, confirmatorio, cohorte nueva de 780 trayectorias) | **PASS** | la incertidumbre sobre el ejemplo de validación más difícil en el update 10 mejora fuera de muestra la predicción de ρ_borde(250) más allá de ρ_borde(10): D = 0.026, p = 1/5001; efecto modesto, predictivo y no causal; se sostiene con ρ_borde v2 (D = 0.022) | [cierre DIN-C1](experiments/DIN_borde/CIERRE_DIN_C1_v1_CONGELADO.md) |
| ¿Aparece la señal fuera de Wine? (DIN-G1–G3, exploratorio) | exploratorio | no en Iris (G1); en mezclas gaussianas aparece **solo donde M colapsa** (G3: D = 0.017, p = 0.003); hipótesis H-colapso | [G1](experiments/DIN_borde/G1/CONCLUSION.md) · [G2](experiments/DIN_borde/G2/CONCLUSION.md) · [G3](experiments/DIN_borde/G3/CONCLUSION.md) |
| ¿Es fiable la medida de distancia al borde? (DIN-I2, R1) | instrumento validado | v1 medía solo rayos a vértices; v2 cubre todas las caras; la reevaluación de 7800 estados de Wine no cambia ningún veredicto | [I2](experiments/DIN_borde/I2/CONCLUSION.md) · [R1](experiments/DIN_borde/R1/RESULTADO_R1_etapa2_2026-10-25.md) |
| ¿Se replica en otra familia? (DIN-C2, confirmatorio, mezclas gaussianas en régimen de colapso, cohorte nueva de 1000 trayectorias) | **PASS** | D = 0.0295, p = 1/5001, pendiente +1.72; compuerta de régimen cumplida. Con DIN-C1, confirmado en dos familias; no establece que el colapso sea necesario ni transferencia a otras redes | [cierre DIN-C2](experiments/DIN_borde/CIERRE_DIN_C2_v1_CONGELADO.md) |

| ¿La geometría del colapso predice la generalización? (DIN-D9, exploratorio, Wine) | **ninguno pasa** | 11 candidatos geométricos (u10–30) sin incremento sobre pérdida/confianza baratas para la pérdida en test u250 (máx. D = 0.005); solo ≈ 10 % de su varianza es intra-split | [D9](experiments/DIN_borde/RESULTADO_D9_2026-10-26.md) |
| ¿El colapso es **necesario** para la señal temprana? (DIN-Q13, manipulación pareada, 12 000 trayectorias) | **INCONCLUSIVE_MANIPULACION**; análisis de un manipulador **NO_CONCLUYENTE** | WD no bajó el colapso lo suficiente (c250 = 0.74 > 0.70). Con *label smoothing* (c250 0.86 → 0.60), la señal cae ≈ 79 % pero **sobrevive**: D 0.039 → 0.0083 (p = 0.0002). No apoya necesidad estricta; compatible con que el colapso la amplifique | [Q13 v2](experiments/DIN_borde/Q13/resultado/RESULTADO_Q13_2026-10-26.md) · [Q13-LS](experiments/DIN_borde/Q13/q13_ls/RESULTADO_Q13_LS_2026-10-26.md) |
| ¿El colapso **modula** la intensidad de la señal? (DIN-Q13-DR, confirmatorio, 6 dosis de *label smoothing*, 6000 trayectorias nuevas) | **MODULA** | D baja con el colapso de forma monótona: 0.034 (c = 0.87) → 0.011 → 0.0037 → 0.0013 → −0.0004 → −0.001 (c = 0.40); β = 0.077 [0.028, 0.140]. Deja de detectarse desde c ≈ 0.56; que desaparezca queda indeterminado. Un manipulador: no separa el colapso del efecto propio de LS | [Q13-DR](experiments/DIN_borde/Q13DR/resultado/RESULTADO_Q13DR_2026-10-26.md) |
| ¿La modulación es propia del *label smoothing*? (DIN-Q13-M2, confirmatorio, penalización de logits y weight decay, 17 600 trayectorias nuevas) | **MODULACION_REPRODUCIDA_EN_DOS_VIAS** | LP: β = 0.051 [0.016, 0.098]; WD: β = 0.056 [0.013, 0.110] (IC 97.5 %); ambas sin diferencia detectada frente a LS (β = 0.077). La relación señal-colapso aparece con **tres intervenciones** distintas; no identifica al colapso como causa | [Q13-M2](experiments/DIN_borde/Q13M2/resultado/RESULTADO_Q13M2_2026-10-28.md) |

Tabla completa, con todas las etapas y su estado oficial: [catálogo de experimentos](docs/CATALOGO_EXPERIMENTOS.md).

**Lo que no se ha establecido:** una ley universal del signo de la curvatura, un predictor universal de la generalización o una explicación causal. Los hallazgos de DIN-borde son exploratorios: salen de datos ya usados y solo un confirmatorio con cohorte nueva puede sostenerlos. Todo lo de entrenamiento real es de **una familia** (MLP en Wine, panel de 27 ejemplos); no se afirma que se transfiera a otras redes o datos.

## En curso
- **Después de Q13-M2:** la revisión de literatura (Q15) es ahora obligatoria. Después: transferencia a otros modelos y datos, y separar el colapso de otras variables que las tres intervenciones mueven juntas (por ejemplo, la escala de los logits).
- **Q14:** ¿la distancia al borde dice algo en modelos que razonan en latente o cuantizan conceptos? Analogía sin resultado.
- **E16:** cotas y caminos al borde en familias sintéticas.
- **Q15, revisión de literatura** (qué es nuevo): pendiente. Es obligatoria antes de cualquier publicación externa, antes de diseñar la transferencia a otros modelos o al cerrar Q13-M2, lo que ocurra primero. Ver [preguntas abiertas](docs/research-notes/open-questions.md).

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

