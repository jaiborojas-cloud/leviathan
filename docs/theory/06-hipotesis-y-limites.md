# 6. Hipótesis, formulaciones de investigación y límites

Fuentes: [contexto](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md),
[estado tras E11-C](../archive/import-2026-10-17/originals/Estado_hipotesis_RIPG_E11C.md),
[cierre E13](../archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md),
[rutas históricas](../archive/import-2026-10-17/RUTAS_INVESTIGACION_texto_extraido.md)
y [prerregistro A0](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md).
No se actualizan outcomes ni estados operacionales T2-A en esta síntesis.

## 6.1 Qué tipo de afirmación se está haciendo

| Nivel | Ejemplo | Qué lo respalda |
|---|---|---|
| Definición | $\omega_p=d_\theta S_p$ | Especificación del objeto operacional |
| Axioma | $\omega_p\in(\ker F)^\circ$ | Condición exigida al marco, no consecuencia de cualquier $S$ |
| Identidad bajo hipótesis | $h_q=J^Th_pJ$ | Regla de cadena y transporte tensorial |
| Control numérico | Concordancia de cartas o derivadas | Implementaciones, errores y tolerancias declaradas |
| Hallazgo condicionado | Diferencia true/random en una cohorte | Protocolo, estimador, datos y cobertura de esa cohorte |
| Hipótesis predictiva | Señal temprana anticipa evento futuro | Validación prospectiva separada, con faltantes preservados |
| Hipótesis causal o universal | La geometría explica aprender | No establecida por correlaciones ni por controles de cartas |

«PASS» de un control no demuestra una ley científica; una prueba matemática de
pullback tampoco establece que un descriptor prediga generalización.

## 6.2 Hipótesis de trabajo central

La formulación defendible es que una familia de relevancias operacionalmente
especificada y compatible con Fisher permite describir diferencias estructurales
entre estados y procesos de aprendizaje. La geometría puede existir antes del
entrenamiento; aprender puede deformarla. Funcional, panel, referencia,
regularización y alcance tangente condicionan lo que se mide.

No se adopta como ley que mayor desplazamiento signifique mejor aprendizaje.
El signo del contraste de distancia cambió al variar el subespacio y el estimador.
La ausencia de una mejora incremental robusta en E10 no demuestra información
mutua condicional exactamente cero; limita la afirmación a esos ensayos.

## 6.3 Curvatura y estructura: hipótesis empíricas condicionadas

El contraste de interés ha sido magnitud, no signo universal:

$$
|K_{\rm true}(p_0)|>|K_{\rm random}(p_0)|,
\qquad \Delta C_A=C_A^{\rm true}-C_A^{\rm random}>0.
$$

E12 reportó la dirección de magnitud en 36/40 pares; es evidencia exploratoria
en dos tareas, no un teorema. E13 conservó señal interna bajo su procedimiento,
pero la réplica externa quedó INCONCLUSIVE al perder cobertura por positividad
del jet: los supervivientes no la confirman. Los cierres E15-B6/B7/B8 documentan
controles y una reconstrucción acotada; no autorizan extrapolar a toda red moderna.

Las hipótesis espaciales de mayor $\Lambda_q$, menor $f_\beta$ y menor
$R_{\rm eff}$ distinguen localización de magnitud. La participación oculta $\eta$
y la atribución por profundidad describen otro eje. No se colapsan en un único
score ni se convierten en causa del desempeño.

## 6.4 Formulación temporal: diseño, no resultado

El protocolo histórico T2-A0 distingue una señal basal y un evento futuro.
Esquemáticamente:

$$
X=\max_\alpha\kappa(D\exp_{p_0}(r_*u_\alpha)),\qquad
Y=\mathbf1\{\text{evento geométrico confirmado en alguna visita futura}\}.
$$

La regla de selección usa la cola superior fijada de $X$. Para un conjunto
seleccionado $Q$ de una cohorte elegible $E$:

$$
\operatorname{precision}(Q)=\frac{\sum_{i\in Q}Y_i}{|Q|},\qquad
\pi=\frac{\sum_{i\in E}Y_i}{|E|},\qquad
\operatorname{lift}=\frac{\operatorname{precision}(Q)}\pi.
$$

Los denominadores deben estar definidos; incidencia cero, falta de eventos y
outcomes desconocidos se tratan según las compuertas originales. El evento no
es «falló el integrador». Una trayectoria sin seguimiento completo no se vuelve
negativa. Repetidos checkpoints no son réplicas independientes.

El protocolo fija tiempos, radio, elegibilidad, empates, comparadores, remuestreo
jerárquico y criterios conjuntos. Esta formulación matemática no sustituye ese
contrato ni lo modifica. No se declara aquí PASS prospectivo ni resolución de
casos pendientes. El contenido de `experiments/T2_A/claude` queda intacto.

## 6.5 Rutas abiertas

| Ruta | Pregunta formal | Condición que sigue siendo necesaria |
|---|---|---|
| Canonicidad | ¿Qué depende de $S,H,\rho$ y del panel? | Comparar elecciones explícitas y transportadas |
| Dimensión mayor | ¿Qué geometría tiene una familia $\mathcal P_m$? | Especificar ambiente, inmersión y términos extrínsecos |
| Tomografía Grassmanniana | ¿Cómo cambia $\operatorname{Sec}(\Pi)$ con el plano? | Fijar la familia y separar geometría local/global |
| Conjugados y corte | ¿Cuándo deja de ser invertible/minimizante el exponencial? | Dominio válido y controles de eventos distintos |
| Composición | ¿Cómo se reorganiza la imagen de $d_p\omega$? | Mapas, cométrica, regla de cadena y criterio de rango |
| Coarse-graining | ¿Desciende un tensor a variables agregadas? | Horizontalidad e independencia de representante |
| PINNs/Boltzmann | ¿Se recuperan restricciones físicas conocidas? | Problema físico y predicciones falsables nuevos |
| Aproximación | ¿Dimensión geométrica efectiva informa complejidad? | Definición operacional y validación independiente |
| Predicción externa | ¿Transfiere una señal a otra tarea/arquitectura? | Diseño nuevo sin reutilizar datos de descubrimiento |

En dimensión mayor, si una superficie está inmersa isométricamente en un ambiente
riemanniano, la ecuación de Gauss introduce contribuciones de la segunda forma
fundamental. No se deduce su geometría del mero cambio de dimensión o de medir
una curvatura en un plano. La igualdad local de curvaturas en un punto no permite
trasladar conjugados o corte a lo largo de geodésicas completas.

## 6.6 Qué debilitaría las hipótesis

Deben distinguirse una refutación del instrumento y una de la hipótesis empírica.
Un fallo de covariancia o de derivadas limita el instrumento; una señal que
cambia al variar decisiones no justificadas limita su interpretación. Una réplica
externa válida sin efecto debilita la generalidad de la señal. Una réplica sin
cobertura suficiente permanece inconclusa. Predicción requiere comparar con
baselines y medir desempeño fuera de muestra; causalidad requiere otro diseño.
No se sustituyen faltantes por valores favorables ni se redefine el estimando
para rescatar una conclusión.
