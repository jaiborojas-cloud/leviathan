# E12-D — curvatura durante el aprendizaje

## Objetivo

E12-D compara, con estados emparejados,

\[
K_0(P),\qquad K_t(P),\qquad
\Delta K(P)=K_t(P)-K_0(P)
\]

para aprendizaje con etiquetas verdaderas y memorización de etiquetas aleatorias.

Se mantienen sin cambios la familia no lineal de E12-B, el panel independiente, los observables, \(H=I\), \(\rho=10^{-4}\) y el cálculo analítico de E12-C.

## Diseño

El análisis tiene dos niveles:

1. **Poblacional en el centro:** \(K(0)\) para los 40 pares de E11-O —dos tareas, cuatro repartos y cinco semillas— en los estados inicial, final `true` y final `random`. Son 120 evaluaciones de estado.
2. **Espacial representativo:** mapas de 25 puntos para reparto 0, semilla 0, añadiendo los campos iniciales a los campos finales de E12-C.

El estado inicial es compartido dentro de cada par `true/random`. La comparación es emparejada por tarea, reparto, semilla, arquitectura, inicialización y panel.

## Resultado poblacional en \(P=0\)

### Digits

| Régimen | Mediana \(K_0\) | Mediana \(K_t\) | Mediana \(\Delta K\) | Dirección por par |
|---|---:|---:|---:|---:|
| True | −0.0950 | **−1.6046** | **−1.5132** | 20/20 negativas |
| Random | −0.0950 | **−0.00717** | **+0.08797** | 20/20 positivas |

En `digits` las dos trayectorias parten de una curvatura negativa moderada y divergen:

- aprender etiquetas verdaderas aumenta fuertemente la curvatura negativa;
- memorizar etiquetas aleatorias aproxima el campo a curvatura cero.

La diferencia final

\[
K_{random}-K_{true}
\]

es positiva en 20/20 pares, con mediana +1.598. Las cuatro medias de reparto tienen el mismo signo; con sólo cuatro unidades de reparto, la prueba bilateral de inversión de signos da \(p=0.125\).

### Wisconsin

| Régimen | Mediana \(K_0\) | Mediana \(K_t\) | Mediana \(\Delta K\) | Dirección por par |
|---|---:|---:|---:|---:|
| True | −0.2777 | **+0.04597** | **+0.4320** | 18 positivas, 2 negativas |
| Random | −0.2777 | **−0.00591** | **+0.2622** | 16 positivas, 4 negativas |

Ambos entrenamientos reducen en general la curvatura negativa inicial. `Random` termina nuevamente cerca de cero. `True` presenta mucha más heterogeneidad: \(\Delta K\) varía entre −5.55 y +24.00 y algunos estados finales tienen determinante métrico pequeño, aunque positivo.

La mediana de \(K_{random}-K_{true}\) es −0.0557 y sólo 5/20 pares son positivos. Las medias de reparto no son uniformes; la prueba descriptiva sobre cuatro repartos da \(p=0.25\).

## Magnitud final de curvatura

El signo depende de la tarea, pero la magnitud ofrece una regularidad más consistente:

| Datos | Mediana \(|K_{true}|\) | Mediana \(|K_{random}|\) | Pares con \(|K_{true}|>|K_{random}|\) |
|---|---:|---:|---:|
| Digits | 1.6046 | 0.00717 | **20/20** |
| Wisconsin | 0.1226 | 0.00648 | **16/20** |

En conjunto, la geometría final `true` tiene mayor curvatura absoluta en **36/40 pares**. La afirmación todavía está limitada a dos tareas, pero es más estable que un signo universal de \(K\).

## Evolución espacial representativa

Las integrales se aproximaron sobre la malla con el elemento de área intrínseco

\[
dA=\sqrt{\det G}\,dP^1dP^2.
\]

Se reporta la energía media

\[
\mathcal E_K
=\frac{\int K^2dA}{\int dA}.
\]

| Datos | Estado | Área métrica | Media espacial de \(K\) | \(\mathcal E_K\) | Fracción de área positiva |
|---|---|---:|---:|---:|---:|
| Digits | Inicial | 3.836 | −0.0861 | 0.00798 | 0 % |
| Digits | True | 0.320 | **−1.4773** | **2.7360** | 0 % |
| Digits | Random | 62.821 | −0.00600 | 0.000037 | 0 % |
| Wisconsin | Inicial | 1.023 | −0.2489 | 0.07737 | 0 % |
| Wisconsin | True | 3.084 | +0.00617 | 0.000123 | 82.0 % |
| Wisconsin | Random | 95.616 | −0.00305 | 0.000020 | 0 % |

En el representante `digits`:

- `true` contrae el área métrica a 8.3 % de la inicial y multiplica la energía de curvatura por 343;
- `random` expande el área 16.4 veces y reduce la energía a 0.47 % de la inicial.

En Wisconsin:

- ambos regímenes aplanan fuertemente el campo inicial;
- `true` conserva más estructura y genera regiones de ambos signos;
- `random` expande el área aproximadamente 93 veces y reduce la energía a 0.026 % de la inicial.

## Relación con E12-A

E12-A encontró

\[
\eta_{random}>\eta_{true}
\]

para la participación Schur oculta. E12-D encuentra simultáneamente que `random` suele tener menor \(|K|\).

No existe contradicción:

- \(\eta\) mide qué fracción de la métrica total procede de la corrección oculta;
- \(K\) mide cómo esa métrica cambia intrínsecamente al desplazarse por el espacio de perspectivas.

Una red puede tener gran participación oculta y, al mismo tiempo, un campo amplio pero casi plano. En los ensayos actuales, la memorización aleatoria parece producir precisamente ese patrón: **mayor participación oculta, mayor área métrica y menor organización curvada**.

Esto recupera con una formulación más precisa la distinción histórica de RIPG entre magnitud y organización.

## Auditoría numérica

| Control | Resultado |
|---|---:|
| Pares poblacionales | 40 |
| Estados evaluados en \(P=0\) | 120 |
| Filas de campos representativos | 150 |
| Residuo máximo del solucionador | \(5.00\times10^{-8}\) |
| Menor determinante métrico | \(1.33\times10^{-3}\) |
| Condición métrica máxima | 921.9 |

La gran dispersión de Wisconsin no se explica por falta de convergencia del solucionador. Sí confirma que la curvatura puede crecer al reducirse la escala métrica, por lo que las comparaciones deben conservar explícitamente \(H\), \(\rho\), panel y familia de perspectivas.

## Estado de RIPG tras E12-D

E12-D rechaza una ley universal sobre el signo de \(\Delta K\). La evolución depende de la tarea:

- `digits-true` genera curvatura negativa fuerte;
- Wisconsin `true` aplana y cambia parcialmente de signo;
- `random` conduce a campos casi planos en ambas tareas.

El candidato empírico más consistente es ahora:

\[
\boxed{
|K_{true}(0)|>|K_{random}(0)|
}
\]

observado en 36/40 pares, junto con una reducción marcada de la energía de curvatura bajo memorización aleatoria en los dos atlas espaciales.

Debe conservarse como hipótesis exploratoria, no como ley: sólo hay dos tareas naturales y los mapas espaciales completos corresponden a un representante por tarea.

## Siguiente paso natural

E12-E puede verificar la holonomía como control derivado:

\[
\operatorname{Hol}(\gamma)
\approx
\int_{\Sigma_\gamma}K\,dA
\]

para lazos rectangulares decrecientes alrededor de puntos con:

1. curvatura negativa fuerte (`digits-true`);
2. curvatura cercana a cero (`digits-random`);
3. cambio de signo espacial (Wisconsin `true`).

La holonomía no debe tratarse como nueva hipótesis independiente: su función es verificar la conexión y la curvatura ya calculadas.

## Reproducción

El paquete incluye código, estados derivados, tablas poblacionales, campos representativos, cambios emparejados, resúmenes espaciales y auditoría. Reutiliza los estados de E11-O y las rutinas analíticas de E12-C.
