# Teoría matemática de RIPG

RIPG estudia la geometría de perspectivas inducida por relevancias. Una familia
operacional de funcionales sobre un modelo define covectores; la variación de
estos covectores induce una geometría entre perspectivas. Este compendio reúne
las formulaciones recuperadas del repositorio y sus condiciones de validez.

$$
p\longmapsto S_p\longmapsto\omega_p=d_\theta S_p
\longmapsto B=d_p\omega
\longmapsto h=B C B^T
\longmapsto\nabla,R,K,\operatorname{Hol}.
$$

Es una síntesis documental, sin nuevas ejecuciones ni cambios a protocolos,
resultados o a `experiments/T2_A/claude`. Las fórmulas de geometría diferencial
son herramientas matemáticas; las hipótesis sobre aprendizaje necesitan evidencia
adicional. No toda semimétrica inducida permite construir curvatura riemanniana.

## Lectura por capítulos

| Tema | Contenido |
|---|---|
| [1. Fundamentos y axioma](01-fundamentos.md) | Espacios, funcional, relevancia, Fisher, kernel, cociente, admisibilidad y familias |
| [2. Métrica y covariancia](02-metrica-y-covariancia.md) | Pullback, rango, cambios de carta, pseudoinversa, regularización y precisión |
| [3. Geometría diferencial](03-geometria-diferencial.md) | Derivadas métricas, conexión, curvatura, geodésicas, Jacobi, corte y holonomía |
| [4. Observables y atribución](04-observables-y-atribucion.md) | Distancias SPD, área, energía, concentración, Schur y participación oculta |
| [5. Composicionalidad](05-composicionalidad.md) | Cartas, subfamilias, agregación, descenso, regla de cadena y contraejemplos |
| [6. Hipótesis y límites](06-hipotesis-y-limites.md) | Qué es definición, axioma, identidad, control, evidencia o pregunta abierta |
| [Fuentes y precedencia](fuentes.md) | Procedencia, alcance de cada fuente, faltantes y conflictos históricos |

## Convención común

$M$ es el espacio de modelos, $\theta\in M$ tiene dimensión $d$;
$\mathcal P$ es la familia de perspectivas, $p\in\mathcal P$ tiene dimensión $m$.
Índices $i,j$ recorren parámetros; $a,b,c$ recorren perspectivas.
$\omega$ es columna $d\times1$, $B$ es $m\times d$, $C$ es $d\times d$ y
$h$ es $m\times m$. $C$ siempre significa cométrica; el observable regional
$C_A$ es otro objeto. $\ker F$ no debe confundirse con la curvatura gaussiana $K$.

Las derivadas en $\theta$ fijan $p$; las derivadas en $p$ fijan $\theta$ y el
panel. Si un panel, regularizador o mapa de perspectivas depende de $p$ o de
$\theta$, deben incluirse sus derivadas: las fórmulas simplificadas lo indican.
Suavidad se presupone en el dominio declarado; redes con ReLU requieren cuidar
fronteras entre regiones de activación y no heredan suavidad global por notación.

## Alcance y estado de evidencia

El núcleo es una construcción geométrica condicionada al funcional, familia,
modelo, panel, cométrica y regularización. No se ha establecido un predictor
universal, una explicación causal ni una ley universal del signo de curvatura.
El [estado científico](../research-status.md) conserva su propio corte histórico;
los cierres y protocolos de cada etapa prevalecen sobre planes anteriores.

Para una consulta rápida: [fundamentos existentes](../foundations/overview.md),
[índice experimental](../experiment-index.md), [rutas abiertas](../research-directions.md).
No se reemplazan ni se reescriben fuentes primarias. Los hashes de las fuentes
consultadas se guardan en `source_manifest.csv`.

## Evidencia e historia de las formulaciones

Consultar el [mapa de afirmaciones](../research-notes/claims-and-evidence.md) y la
[historia de decisiones matemáticas](../research-notes/mathematical-decisions.md).
La [guía complementaria](../research-notes/README.md) añade resultados negativos,
contraejemplos, reproducción y preguntas abiertas, sin ejecutar ciencia nueva.
