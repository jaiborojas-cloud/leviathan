# Leviathan / RIPG — T2: diseño de validación fuera del panel de descubrimiento

**Estado: hipótesis y diseño congelados por escrito; ejecución NO iniciada.** Este diseño no cambia C1 ni T1-A/B. No es validación ya obtenida ni una afirmación de descubrimiento causal.

## Hipótesis exacta H-T2-1

En estados Wine true nuevos, la cola superior predefinida de la condición intrínseca de Dexp a radio geodésico fijo está enriquecida en pérdida de inyectividad detectada antes del radio nominal necesario para A=0.02.

La dirección esperada es positiva: mayor condición previa, mayor frecuencia posterior de GEOMETRIC_NONINJECTIVITY dentro del dominio nominal. Es una hipótesis **predictiva de transportabilidad**, coherente con Jacobi; no una nueva ley ni una hipótesis causal.

Origen exploratorio: los dos positivos conocidos ocuparon los lugares 1 y 2 a r*=0.05697156262709151 en T1-B. Ya se conocía su condición positiva. Ese dato no se considera confirmación. Además, j3 ocupó lugares 15 y 8 a radios menores; no se permite reinterpretar el resultado como una señal universal a toda escala.

## Observable y resultado fijados

- Centro: P0=(0,0).
- Radio único primario: **r*=0.05697156262709151**, sin recalibrarlo en los estados nuevos.
- Predictor: máximo angular sobre el borde de κ(Dexp), con la misma definición intrínseca j/r, 512 direcciones y fases 0/media celda; control a256, mismas compuertas T1-B y DOP853 rtol2e-10/atol2e-12.
- Cola: top10% de los estados true del nuevo panel, ordenados por el predictor **antes de abrir los resultados nominales**. Con160 true corresponde a16 estados. Empates exactos en el punto de corte se incluyen completos y se reporta el tamaño real de la cola; no se desempata usando el resultado.
- Resultado: clasificación GEOMETRIC_NONINJECTIVITY obtenida por el instrumento escalonado congelado T1-A/A2 antes del radio nominal de A=0.02. Se conservan todas las demás clasificaciones y errores. No se reduce el área ni se sustituye un estado.
- No se utiliza C_A como predictor, no se imputa para dominios inválidos y no se inventa un score combinado.

## Panel futuro fijo

Primera validación fuera del panel de descubrimiento: **32 splits nuevos ×5 inicializaciones nuevas ×2 regímenes =320 estados (160 pares)**.

- Identificadores split: s=8,…,39; inicialización j=5,…,9. Ninguno fue usado en el panel T1-A/B.
- Se conserva la regla original de semillas: split=1000+s; init=2000+j; minibatches=4000+10s+j; random labels=3000+10s+j.
- Se preservan Wine, arquitectura13→64→32→3 ReLU/float64, protocolo de entrenamiento y parada C1, panel geométrico, rho=1e-4, constructor RIPG y definición de área.
- Los regímenes true/random mantienen emparejamiento e inicialización/minibatches comunes por par, tal como C1.
- Tamaño operativo fijado antes de resultados; no constituye un cálculo de potencia fiable a partir de sólo dos eventos. No se amplía hasta lograr un resultado favorable.
- Esta fase es externa al panel de descubrimiento, **no a Wine**. Los splits todavía comparten ejemplos y las inicializaciones se reutilizan entre splits; no se consideran datasets independientes.

## Orden prospectivo obligatorio

1. Congelar y guardar hashes de este diseño, scripts y listado de semillas.
2. Entrenar todos los estados previstos y persistir checkpoints; no reemplazar fallos.
3. Calcular y guardar el predictor a r* para todos los estados, con compuertas. Congelar su tabla, rangos y cola mediante SHA antes de abrir la clasificación nominal.
4. Ejecutar la auditoría nominal con reglas heredadas. No modificar el predictor, la cola ni el radio tras conocer clases.
5. Abrir resultados y efectuar una única evaluación primaria. Guardar análisis por split y dejar-un-split-fuera sin elegir el subconjunto favorable.

## Compuertas y decisión operativa

El panel T2 consta de **320 estados**. Deben estar presentes los320 checkpoints originales y todas las clasificaciones; los160 true deben tener predictor válido y resultado nominal resuelto para la evaluación primaria. Se mantienen errores explícitos y nunca se reemplazan.

- Si un nuevo estado pierde validez antes de r*, no se reduce r* ni se le asigna κ infinito para favorecer la hipótesis: la evaluación primaria queda INCONCLUSIVE.
- Si existe algún true con predictor o desenlace no resuelto, la evaluación primaria queda INCONCLUSIVE; no se confirma sobre supervivientes.
- Para evaluar transportabilidad predictiva se requieren al menos8 positivos true distribuidos en al menos3 splits. Si no se alcanzan, el resultado es INCONCLUSIVE por información insuficiente, sin corridas de reemplazo o ampliación oportunista.
- Métrica primaria: **lift = prevalencia de GEOMETRIC_NONINJECTIVITY en la cola / prevalencia en los160 true**.
- Éxito empírico predefinido: lift≥3 y lift>1 al retirar cualquiera de los32 splits, manteniendo los indicadores de cola previamente congelados. Si las compuertas técnicas/informativas pasan y esta condición no se cumple: criterio predictivo NOT_MET.
- Se reportan también sensibilidad, precisión, tasa de falsos positivos y prevalencia por split, y el tamaño real de la cola si hay empates. No se cambia la decisión por métricas secundarias favorables.
- Estos umbrales son un requisito práctico fijado para el ensayo futuro, no una estimación de rendimiento obtenida de los dos positivos de T1-B. Con una cola exactamente10%, lift3 corresponde a capturar30% de los positivos.
- Intervalos por remuestreo de splits y análisis de sensibilidad son descriptivos. El éxito operativo no se presenta como una prueba estadística de ley universal, independencia entre datasets o causalidad.

## Controles secundarios y límites

Random aporta un control geométrico separado; no se selecciona retrospectivamente un régimen o umbral para mejorar el predictor. La correlación C_A–κ a radio común puede repetirse como EXPECTED_GEOMETRIC_CONTROL donde C_A sea admisible, sin alterar la evaluación predictiva primaria ni rescatar C1.

Los residuos de T1-B no proporcionaron un mecanismo fuerte: la anisotropía de borde no explicó sus signos y C_A Rnom² no mejoró. No se registra aquí una confirmación de esos mecanismos. Medir K(s,θ) a lo largo de rayos sería un estudio exploratorio separado; cualquier observable derivado necesitaría una nueva validación independiente.

Una tarea o arquitectura externa sería deseable después. Antes de ejecutarla deberá congelarse un anexo completo con dataset, arquitectura, geometría, escala y compuertas. No se permite asumir que este radio numérico se transfiere automáticamente a otra geometría.

## Persistencia y prohibiciones

Usar una carpeta propia de T2 y guardado incremental por estado/lote, con progress, estados pendientes, scripts, manifiestos y hashes. No iniciar automáticamente desde este documento. No reutilizar los80 estados T1-A/B como confirmación; no redefinir el top10%, el radio, la población ni las compuertas tras abrir resultados nuevos.
