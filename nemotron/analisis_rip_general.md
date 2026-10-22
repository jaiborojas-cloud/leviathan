# Análisis del marco general de RIPG (Nemotron)

Análisis documental del marco general sin centrarse en el experimento T2-A. Distingue identidad matemática de hallazgo empírico condicionado. No modifica implementaciones científicas ni resultados originales.

## Objeto de estudio

RIPG estudia cómo una familia de perspectivas (funcionales escalares sobre parámetros de modelo) induce una geometría entre perspectivas. El flujo central es:

$$p \mapsto S_p(\theta) \mapsto \omega_p = d_\theta S_p \mapsto B = d_p\omega \mapsto h = BCB^T \mapsto \nabla, R, K, \text{Hol}$$

## Qué es y qué no es el marco

| Es | No es |
|---|---|
| Construcción geométrica condicionada al funcional, familia, modelo, panel, cométrica y regularización | Una ley universal del signo de curvatura |
| Marco para describir diferencias estructurales entre estados y procesos de aprendizaje | Un predictor universal de generalización |
| Hipótesis de trabajo de magnitud ($|K_{\text{true}}| > |K_{\text{random}}|$) | Causalidad ni explicación del aprendizaje |
| Herramienta matemática para controles y hallazgos condicionados | Evidencia confirmatoria por sí misma |

## Jerarquía de afirmaciones

Nivel | Ejemplo | Qué lo respalda
---|---|---
Definición | $\omega_p = d_\theta S_p$ | Especificación del objeto operacional
Axioma | $\omega_p \in (\ker F)^\circ$ | Condición exigida al marco
Identidad bajo hipótesis | $h_q = J^T h_p J$ | Regla de cadena y transporte tensorial
Control numérico | Concordancia de cartas o derivadas | Implementaciones, errores y tolerancias declaradas
Hallazgo condicionado | Diferencia true/random en una cohorte | Protocolo, estimador, datos y cobertura de esa cohorte
Hipótesis predictiva | Señal temprana anticipa evento futuro | Validación prospectiva separada
Hipótesis causal o universal | La geometría explica aprender | No establecida por correlaciones ni controles

«PASS» de un control no demuestra una ley científica; una prueba matemática de pullback no establece que un descriptor prediga generalización.

## Hipótesis de trabajo central

La formulación defendible es que una familia de relevancias operacionalmente especificada y compatible con Fisher permite describir diferencias estructurales entre estados y procesos de aprendizaje. La geometría puede existir antes del entrenamiento; aprender puede deformarla. Funcional, panel, referencia, regularización y alcance tangente condicionan lo que se mide.

No se adopta como ley que mayor desplazamiento signifique mejor aprendizaje. El signo del contraste de distancia cambió al variar el subespacio y el estimador.

## Hipótesis espaciales condicionadas

Las hipótesis de mayor $\Lambda_q$, menor $f_\beta$ y menor $R_{\text{eff}}$ distinguen localización de magnitud. La participación oculta $\eta$ y la atribución por profundidad describen otro eje. No se colapsan en un único score ni se convierten en causa del desempeño.

## Formulación temporal (diseño, no resultado)

Esquemáticamente:

$$X = \max_\alpha \kappa(D\exp_{p_0}(r_* u_\alpha)), \qquad
Y = \mathbf 1\{\text{evento geométrico confirmado en alguna visita futura}\}$$

$$\operatorname{precision}(Q) = \frac{\sum_{i \in Q} Y_i}{|Q|}, \qquad
\pi = \frac{\sum_{i \in E} Y_i}{|E|}, \qquad
\operatorname{lift} = \frac{\operatorname{precision}(Q)}{\pi}$$

Los denominadores deben estar definidos; incidencia cero, falta de eventos y outcomes desconocidos se tratan según las compuertas originales. El evento no es «falló el integrador». Una trayectoria sin seguimiento completo no se vuelve negativa. Repetidos checkpoints no son réplicas independientes.

## Qué debilitaría las hipótesis

- Un fallo de covariancia o de derivadas limita el instrumento.
- Una señal que cambia al variar decisiones no justificadas limita su interpretación.
- Una réplica externa válida sin efecto debilita la generalidad de la señal.
- Una réplica sin cobertura suficiente permanece inconclusa.
- Predicción requiere comparar con baselines y medir desempeño fuera de muestra; causalidad requiere otro diseño.

No se sustituyen faltantes por valores favorables ni se redefine el estimando para rescatar una conclusión.

## Rutas abiertas del marco

| Ruta | Pregunta formal | Condición necesaria |
|---|---|---|
| Canonicidad | ¿Qué depende de $S, H, \rho$ y del panel? | Comparar elecciones explícitas y transportadas |
| Dimensión mayor | ¿Qué geometría tiene una familia $\mathcal P_m$? | Especificar ambiente, inmersión y términos extrínsecos |
| Tomografía Grassmanniana | ¿Cómo cambia $\operatorname{Sec}(\Pi)$ con el plano? | Fijar la familia y separar geometría local/global |
| Conjugados y corte | ¿Cuándo deja de ser invertible/minimizante el exponencial? | Dominio válido y controles de eventos distintos |
| Composición | ¿Cómo se reorganiza la imagen de $d_p\omega$? | Mapas, cométrica, regla de cadena y criterio de rango |
| Coarse-graining | ¿Desciende un tensor a variables agregadas? | Horizontalidad e independencia de representante |
| PINNs/Boltzmann | ¿Se recuperan restricciones físicas conocidas? | Problema físico y predicciones falsables nuevos |
| Aproximación | ¿Dimensión geométrica efectiva informa complejidad? | Definición operacional y validación independiente |
| Predicción externa | ¿Transfiere una señal a otra tarea/arquitectura? | Diseño nuevo sin reutilizar datos de descubrimiento |
