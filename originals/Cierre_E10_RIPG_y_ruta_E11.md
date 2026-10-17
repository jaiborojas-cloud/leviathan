# RIPG — cierre de E10 y ruta E11

**Estado:** E10 cerrado como fase exploratoria; fecha: 22 de septiembre de 2026.

## Marco que permanece fijo

Una perspectiva admisible (P) define (S_P) y (omega_P=d_\theta S_P). Si (K_\theta=\ker F_\theta), se exige

\[
\omega_P\in K_\theta^\circ,\qquad
d_Pd_\theta S_P(K_\theta)=0\quad(BK=0).
\]

La geometría inducida en el espacio de perspectivas usa el cociente Fisher (Q_\theta=T_\theta M/K_\theta): (h=\Phi^*\bar g_F^{-1}). Fisher es el control geométrico de base; la familia de relevancias dependiente de (P) aporta el objeto perspectival. Una transformación de coordenadas del modelo o de las perspectivas no equivale a cambiar la perspectiva operativa. Para \(\omega=dS\), \(d\omega=0\); curvatura u holonomía de una conexión no autorizan atribuir circulación a \(\omega\).

## Hallazgos de E10

| Experimento | Resultado conservado | Límite |
|---|---|---|
| E10-A/B | Las mediciones de geometría perspectival evolucionan durante entrenamiento y se diferencian entre regímenes true/random en este protocolo. | No prueban por sí mismas una ley general de generalización o causalidad. |
| E10-C | `field_modulation` mostró separación geométrica reproducible, pero la accuracy ya se separaba antes. | No se verificó \(t_{\rm geom}<t_{\rm accuracy}\). |
| E10-D/E | El desplazamiento \(D_G\) no fue monótono con corrupción de etiquetas; un supuesto pico en \(\rho=.75\) no se reprodujo al refinar el barrido y ampliar el subconjunto Fisher. | No se sostiene un máximo universal de «frustración». |
| E10-F/G | La distancia escalar ni la firma local de deformación mejoraron de modo robusto la predicción fuera de muestra de accuracy futura condicionada a accuracy presente. | Este resultado para predictores y protocolo concretos **no prueba** independencia condicional ni información mutua nula. |
| E10-H | Accuracy similar (y alto acuerdo de predicciones) coexistió con métricas diferentes entre Adam y SGD. | La deriva entre checkpoints próximos fue comparable a la diferencia entre optimizadores: no se identificó una firma específica del optimizador. |
| E10-I | Con diez semillas se calcularon velocidades promedio y longitudes observadas entre tres estados de accuracy emparejada. Las diferencias Adam–SGD no fueron robustas. | Un solo intervalo local de cuatro updates superó toda la longitud observada entre umbrales en 5 de 40 trayectorias: no está estimada la longitud total. No hay trayectorias densas true/random ni de corrupción. |

**Conclusión formal de cierre:** E10 aporta evidencia de una geometría perspectival dinámica que no queda determinada por un solo número de accuracy. No establece anticipación funcional, poder predictivo incremental robusto, una ley simple de corrupción ni una eficiencia geométrica característica. Estas negaciones están limitadas a los diseños y estimadores ensayados. La geometría no se presenta como medida de calidad predictiva ni como marcador causal.

## Camino natural: E11, estabilidad y geometría de trayectorias

### E11-A — hacer medible la dinámica

Reconstruir exactamente el observable admisible y la implementación de (G\) usados en E10, con Fisher, perspectiva, cociente, regularización y muestra de evaluación documentados. Usar un panel Fisher **fijo**, balanceado y ajeno a la selección de checkpoints. En estados congelados, repetir estimación con submuestras Fisher independientes y varios tamaños; estimar la distribución del error en (d_{\rm SPD}(G_t,G_{t+4})\). Comprobar positividad, condicionamiento, invariancia bajo cambio de coordenadas y sensibilidad a regularización. Criterio de paso: el movimiento medido entre checkpoints debe superar la variación instrumental y ser estable frente a tamaño de panel y regularización.

### E11-B — registrar trayectorias densas

Con mismas semillas, datos, arquitectura, minibatches y horizonte de updates, cruzar optimizador (Adam/SGD) y régimen de etiquetas (true/random; corrupción parcial sólo después). Guardar (G_t\) y train/test accuracy desde (t=0\) cada 2–4 updates, siempre con los mismos observables y panel Fisher. Calcular

\[
v_G(t;\Delta)=\frac{d_{\rm SPD}(G_t,G_{t+\Delta})}{\Delta},\qquad
L_G^{(\Delta)}(T)=\sum_{k}d_{\rm SPD}(G_{k\Delta},G_{(k+1)\Delta}).
\]

Repetir el cálculo con mallas anidadas \(\Delta=2,4,8\). La longitud de una poligonal observada no debe tratarse como longitud convergida si cambia materialmente al densificar checkpoints. Reportar longitud, velocidad, ganancia de accuracy, duración y cociente \(\Delta A/L_G\) **juntos**. Comparar tanto a horizonte fijo como a accuracy emparejada, sin escoger los puntos de registro mediante accuracy de test.

### E11-C — interpretación con controles

Evaluar contrastes pareados por semilla con incertidumbre y definir de antemano los contrastes primarios. Comprobar si una diferencia de longitud o velocidad persiste tras controlar el ruido de estimación, el tamaño de (G\), la duración y el acuerdo entre predicciones. Si no persiste, cerrar también la hipótesis de eficiencia geométrica en este banco. Si persiste y se reproduce, ampliar a otra arquitectura y conjunto de datos; sólo entonces estudiar si la dinámica anticipa algún resultado funcional distinto de accuracy.

**Pregunta central de E11:** ¿existe una dinámica perspectival reproducible, superior al ruido de medida y estable al refinar el tiempo, que distinga trayectorias de aprendizaje comparables?

## Regla de comunicación

Presentar RIPG como marco geométrico matemático con resultados empíricos exploratorios. Mantener separados: (1) invariancia/admisibilidad formal, (2) cambio geométrico observado, (3) valor predictivo y (4) explicación causal. E10 respalda algunos resultados de (2); no establece (3) ni (4).
