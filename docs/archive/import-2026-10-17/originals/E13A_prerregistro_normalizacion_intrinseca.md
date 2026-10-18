# E13-A — prerregistro y normalización intrínseca

**Estado:** congelado antes de E13-B–D.  
**Fecha:** 23 de septiembre de 2026.  
**Dependencia:** cierre formal de E12 y axioma RIPG vigente.

## 1. Pregunta

¿La mayor organización curvatural observada bajo aprendizaje verdadero, frente a memorización aleatoria, se conserva cuando ambos regímenes se comparan en regiones con la misma área intrínseca?

E13 no presupone un signo universal de la curvatura. La señal que se intenta replicar es de **magnitud y energía curvatural**, no de curvatura positiva o negativa.

## 2. Hipótesis congeladas

### Primaria

Para cada par emparejado `true/random`, sea (D_A(P_0)) el disco geodésico centrado en (P_0=(0,0)), cuyo radio se elige para que

\[
\operatorname{Area}_G D_A=A.
\]

Se define la curvatura RMS

\[
C_A=\left(\frac{1}{A}\int_{D_A}K^2\,dA\right)^{1/2}.
\]

El contraste primario es

\[
\boxed{\Delta C_A=C_A^{\rm true}-C_A^{\rm random}}
\]

en el área primaria (A_*=0.02). La hipótesis direccional prerregistrada es (Delta C_{A_*}>0).

### Secundarias

1. Robustez de (Delta C_A) en (A\in\{0.01,0.02,0.04\}).
2. Diferencia de curvatura absoluta media
   \[
   M_A=A^{-1}\int_{D_A}|K|\,dA.
   \]
3. Curvatura firmada media
   \[
   \bar K_A=A^{-1}\int_{D_A}K\,dA,
   \]
   sin hipótesis universal sobre su signo.
4. Holonomía como control derivado:
   \[
   \theta_{\rm hol}(\partial D_A)\approx\int_{D_A}K\,dA=A\bar K_A.
   \]
5. Área, participación oculta (eta) y (C_A) se mantendrán como estimandos distintos; no se inferirá causalidad entre ellos.

## 3. Construcción intrínseca congelada

- Centro: (P_0=(0,0)).
- Regiones: discos formados por la aplicación exponencial de vectores unitarios de (T_{P_0}\mathcal P).
- Áreas objetivo: (0.01, 0.02, 0.04); primaria (0.02).
- El radio de cada disco se obtiene por bisección hasta error relativo de área (le 10^{-6}).
- Malla polar: 128 direcciones angulares y 64 intervalos radiales.
- Geodésicas: RK4 con 256 subpasos desde el centro hasta la frontera.
- Cuadratura: celdas polares en coordenadas de carta ponderadas por (sqrt{\det G}); la celda central se triangula.
- Refinamiento de auditoría: 256 direcciones, 128 intervalos y 512 subpasos. El estimando primario debe cambiar menos de 0.5%; si no, el caso se marca `no_converged` y no se sustituye por otro.
- Orientación: antihoraria en la carta original; el flujo cambia de signo sólo si cambia la orientación, mientras (C_A) y (M_A) no cambian.

No se adaptarán áreas, centro, malla o tolerancias usando diferencias observadas entre `true` y `random`.

## 4. Invariancia exigida antes de analizar redes

La implementación debe superar, usando únicamente métricas sintéticas:

1. plano euclídeo: (K=0), área (pi r^2), perímetro (2pi r);
2. esfera unitaria en coordenadas estereográficas: (K=1), flujo igual al área y perímetro exacto del círculo geodésico;
3. repetición en una carta no lineal fija
   \[
   x^1=u^1+0.2u^1u^2,\qquad
   x^2=0.9u^2+0.1(u^1)^2.
   \]

Criterios congelados:

- error relativo máximo entre cartas (le5\times10^{-4});
- error relativo máximo frente a la solución analítica (le10^{-3});
- todos los controles deben aprobar en las tres áreas.

Si falla un control, sólo se permite corregir la implementación y versionar de nuevo E13-A **antes** de abrir resultados de redes. No se permite relajar el umbral tras observarlos.

## 5. Elementos del protocolo RIPG que no cambian

- Familia de perspectivas exponencial normalizada de E12-B.
- Condición de admisibilidad (omega_P\in K_\theta^\circ) y (BK_	heta=0).
- Estimador (G_\rho=B(F+\rho\lambda_{\max}H)^{-1}B^T).
- Referencia primaria (H=I) en la carta declarada y (ho=10^{-4}), transportando (H) tensorialmente en auditorías de carta.
- Mismo panel, observables y emparejamiento dentro de cada réplica.
- Comparación `true/random` con inicialización, partición, arquitectura y panel compartidos.

Estos elementos quedan condicionados al protocolo: no se reinterpretan como una geometría canónica independiente de (H,ho,S_P) o del panel.

## 6. Semillas y unidades de análisis

### Reanálisis interno E13-B

- Tareas: `digits` y `Wisconsin`.
- Particiones existentes: 0, 1, 2, 3.
- Semillas existentes: 0, 1, 2, 3, 4.
- Total: 20 pares por tarea, sin reemplazo ni selección posterior.
- Unidad descriptiva conservadora: partición; las cinco semillas se agregan dentro de cada partición.

E13-B es una prueba de robustez interna, no la confirmación externa primaria.

### Réplica E13-C/D

- Nueva tarea congelada: `sklearn.datasets.load_wine`.
- Preprocesamiento: partición estratificada 70/15/15; estandarización ajustada sólo con entrenamiento.
- Particiones: semillas 1000–1007.
- Inicializaciones por partición: semillas 2000–2004.
- Arquitectura: MLP de dos capas ocultas 64–32, activación ReLU, salida softmax.
- Regímenes emparejados: etiquetas verdaderas y una permutación de etiquetas de entrenamiento; validación y prueba conservan etiquetas verdaderas.
- La permutación usa semilla (3000+10s+j), donde (s\in\{0,\ldots,7\}) es la partición y (j\in\{0,\ldots,4\}) la inicialización.
- No se sustituyen corridas fallidas. Se reportan y entran en la regla de exclusión predefinida.

## 7. Criterios de inclusión, exclusión y faltantes

Una corrida se incluye si:

1. comparte exactamente el estado inicial entre `true` y `random`;
2. ambas ramas completan el presupuesto de entrenamiento;
3. (B) tiene rango dos en toda la malla utilizada;
4. (G) es definida positiva en todos los nodos;
5. la integración geodésica y el refinamiento satisfacen las tolerancias congeladas.

Si un miembro del par falla, se excluye el par completo y se informa la razón. No se reemplaza la semilla. Si se pierde más del 10% de los pares externos o menos de seis de ocho particiones conservan al menos cuatro pares, E13-D se declara **inconcluso**, no negativo.

Los umbrales numéricos no pueden basarse en el tamaño ni en el signo del contraste `true/random`.

## 8. Análisis confirmatorio y regla de éxito

Para la réplica externa, se promedia (Delta C_{A_*}) sobre las cinco inicializaciones dentro de cada una de las ocho particiones. El contraste confirmatorio usa una prueba de permutación de signos exacta, unilateral, sobre esas ocho medias independientes.

E13-D se considera confirmatoria sólo si se cumplen simultáneamente:

1. mediana de las ocho medias de partición (>0);
2. al menos 6/8 medias de partición son positivas;
3. (p_{\rm exacto}<0.05) unilateral;
4. el intervalo bootstrap BCa del 95% de la mediana, re-muestreando particiones, no cruza cero;
5. la conclusión no cambia en la malla de refinamiento.

No se corrige multiplicidad para el único estimando primario (C_{0.02}). Todas las demás áreas, métricas, tareas internas y análisis por capa son secundarios o exploratorios y se etiquetarán como tales.

## 9. Salidas obligatorias

- Tabla completa por tarea, partición, semilla, régimen y área.
- Radio encontrado, error de área, condición máxima de (G), rango mínimo de (B) y estado de convergencia.
- (C_A), (M_A), (ar K_A), flujo y holonomía.
- Resultados con malla principal y de refinamiento.
- Diagrama de flujo de exclusiones sin ocultar corridas fallidas.
- Código, versiones de dependencias, hashes de datos y archivo de configuración congelado.
- Un resultado nulo, heterogéneo o contrario se reportará sin modificar esta definición.

## 10. Lo que E13-A no autoriza afirmar

- No convierte la señal de E12 en ley universal.
- No demuestra predicción fuera de muestra ni causalidad.
- No hace canónico al estimador respecto de (H,ho,S_P) o el panel.
- No trata la holonomía como variable independiente de la curvatura.
- No permite escoger después el área, tarea, semilla, centro o estadístico que produzca la separación más favorable.

## 11. Bloqueo

El archivo de configuración implícito en este documento queda congelado con el código de validación sintética y su salida. E13-B sólo puede comenzar después de que `all_passed=true`. Cualquier modificación posterior requiere una enmienda fechada que distinga explícitamente análisis confirmatorios de exploratorios.

### Resultado de validación previo al bloqueo

| Geometría | Área | Error máximo entre cartas | Error máximo analítico | Estado |
|---|---:|---:|---:|---|
| Plano | 0.01 | 9.13e-8 | 4.02e-4 | aprobado |
| Plano | 0.02 | 1.83e-7 | 4.02e-4 | aprobado |
| Plano | 0.04 | 3.65e-7 | 4.02e-4 | aprobado |
| Esfera | 0.01 | 2.28e-8 | 4.01e-4 | aprobado |
| Esfera | 0.02 | 4.56e-8 | 4.00e-4 | aprobado |
| Esfera | 0.04 | 9.12e-8 | 3.99e-4 | aprobado |

Resultado global: `all_passed=true`. La validación utilizó sólo geometrías sintéticas y no leyó salidas `true/random` para ajustar áreas, mallas o tolerancias.
