# RIPG — estado de la hipótesis tras E11-C

**Actualizado:** 22 de septiembre de 2026. Documento de continuidad para la investigación.

## Núcleo matemático

Una perspectiva admisible (P\) es una familia suave de funcionales escalares (S_P\) sobre el espacio de modelos. Su relevancia es el covector (\omega_P=d_\theta S_P\). Con Fisher (F_\theta\) y (K_\theta=\ker F_\theta\), se exige

\[
\omega_P\in K_\theta^\circ,
\qquad B=d_Pd_\theta S_P,
\qquad BK_\theta=0.
\]

La relevancia vive por tanto en el dual del cociente (Q_\theta=T_\theta M/K_\theta\). La métrica inducida sobre perspectivas se expresa en coordenadas como (h=BF_\theta^+B^T\), entendiendo el pseudoinverso sobre el cociente Fisher y verificando su covariancia. La métrica/Fisher describe estructura identificable del modelo; (P\mapsto\omega_P\) especifica qué es relevante. El (\omega=dS\) exacto satisface (d\omega=0\); una variación covariante o la holonomía de la conexión no constituyen circulación no nula de (\omega\).

El marco matemático y los controles de E9 respaldan admisibilidad, transformaciones de coordenadas, invariancia del cociente y una geometría perspectival inducida **en los ejemplos probados**. La elección operativa de (S_P\) sigue siendo una decisión científica sustantiva, no derivada únicamente de Fisher.

## Evidencia empírica acumulada

| Pregunta | Estado tras E10–E11 |
|---|---|
| ¿Cambian las métricas perspectivales durante el aprendizaje? | Sí, en los protocolos concretos ensayados. |
| ¿Se distinguen regímenes true/random? | Sí en varias comparaciones, pero **no existe una dirección estable**: E11-C encuentra mayor distancia en true con subespacios proyectados de 16 y 32 dimensiones; a 64 desaparece la diferencia y con toda la capa final random muestra mayor distancia. La magnitud también depende del observable y del corte de Fisher. |
| ¿La geometría se separa antes que accuracy? | No en E10-C: accuracy era detectable antes. |
| ¿(D_G\) sigue una ley simple con corrupción? | No se verificó monotonicidad ni un máximo universal; el pico de 0.75 de E10-D no se reprodujo en E10-E. |
| ¿Predice accuracy futura sobre la accuracy presente? | E10-F/G no observaron mejora incremental robusta con (D_G\) ni su firma local bajo validación por seed. Esto no demuestra información mutua condicional igual a cero. |
| ¿Accuracy similar determina una única geometría? | No en E10-H; pero la deriva local fue comparable a diferencias entre optimizadores. |
| ¿Está resuelta la longitud (L_G\) o eficiencia geométrica? | No. E10-I tenía tres estados por trayectoria. E11-B mostró que el panel Fisher compacto y la malla temporal pueden ocultar variación. E11-C emparejó accuracy de entrenamiento casi al 99%, pero midió sólo estados 0, 90% y 99% en un subespacio, no longitud continua. |

## Nuevo resultado E11-C, con alcance delimitado

Diez pares de MLP `64→128→10` compartieron semillas, arquitectura, datos y minibatches; ambas condiciones alcanzaron aproximadamente 99.1–99.2% de accuracy de entrenamiento. Test accuracy verdadera: alrededor de 96.6% en true y 10.0% en random. En una métrica RIPG del subespacio de 16 características fijas de la capa final, construida sobre 450 imágenes de referencia, (d(G_0,G_{99})\) fue mayor en true en 9–10 de diez pares, dependiendo de una de tres proyecciones; el contraste bilateral exacto fue \(p\approx0.002\)–0.004. Con relevancia uniforme se mantuvo la dirección en las diez semillas de cada proyección, con magnitudes distintas. Las proyecciones son controles correlacionados, no nuevas semillas.

Pero el control de dimensión es decisivo: con 32 características true sigue mostrando más distancia; con 64 la diferencia desaparece; con **toda la capa final (128)** random tiene más distancia en 8/10 pares (medias 5.44 frente a 3.58; \(p=0.0078\) con corte Fisher relativo \(10^{-10}\)). La magnitud random varía aproximadamente de 4.63 a 6.04 al mover el corte entre \(10^{-8}\) y \(10^{-12}\). La dirección del efecto **se invierte** al cambiar qué direcciones paramétricas incluye Fisher. El residual numérico de admisibilidad llega a (3\times10^{-4}\) en la capa final completa debido al corte de rangos pequeños; hace falta un tratamiento más estable del cociente antes de extraer una afirmación general.

Por tanto E11-C refuerza que la geometría responde al entrenamiento, pero **falsifica una lectura simple de sentido o magnitud robustos** del contraste true/random. La elección de relevancia altera la escala, y las funciones aprendidas siguen teniendo test accuracy muy distinta. No demuestra información independiente de desempeño ni valida la métrica de todos los parámetros o la longitud total.

## Hipótesis de trabajo actual

> Una familia de relevancias operacionalmente especificada y compatible con el cociente Fisher induce una geometría del espacio de perspectivas capaz de describir diferencias estructurales entre procesos de aprendizaje. Para atribuirle una propiedad predictiva, causal o universal se requieren controles adicionales de función, medida de evaluación, subespacio paramétrico y estabilidad temporal.

**No adoptar** como hipótesis principal que RIPG predice accuracy tempranamente o que más desplazamiento significa mejor aprendizaje. Ambas lecturas fueron presionadas experimentalmente y no obtuvieron respaldo general.

## Ruta siguiente

1. **Resolver la dependencia del cociente:** estudiar qué direcciones casi nulas de Fisher cambian el resultado al aumentar de 16 a 128 características; barrer corte, regularización y estimadores numéricos y verificar (BK=0\) al nivel de tolerancia requerido. La métrica del modelo completo continúa pendiente.
2. **Estabilidad poblacional y temporal:** mantener un panel fijo grande, estudiar convergencia del estimador y registrar estados densos, especialmente durante la memorización aleatoria. Sólo informar (L_G\) si se estabiliza frente a tamaño de panel, espacio tangente y refinamiento temporal.
3. **Control funcional:** buscar estados con rendimiento y acuerdo de predicciones comparables alcanzados mediante trayectorias distintas; comparar sus métricas y cambios locales con control de deriva. Definir previamente el contraste y validar en otras arquitecturas o datos.

La afirmación publicable más defendible hoy es **un marco matemático explícito y una serie de resultados experimentales limitados, con controles negativos informativos**. E11-C aporta una advertencia concreta: un efecto pareado fuerte en un subespacio puede invertirse al ampliar el espacio tangente. No convierte RIPG en ley general de entrenamiento.
