# Leviathan / RIPG — E15-B6: integración multifuente y diagnóstico del dominio

Fecha: 24 septiembre 2026. Ejecución numérica sobre el paquete suministrado por el usuario.

## Resultado y alcance

**El esquema radial original falla la independencia entre fuentes en split 6 true. La integración espacial global sobre un contorno denso común sí pasa el umbral multifuente de 0.5%.**

Se ejecutaron seis fuentes para split 6 true, seis para split 6 random y seis para split 5 true. En los dos estados true se hizo además la comparación con seis triangulaciones espaciales que comparten un contorno fijo. En el primario se auditó el contorno a 2048, 4096 y 8192 rayos y se reajustó finalmente el área a 0.02.

Estimación final auditada para el checkpoint split 6 true:

**C_A = 1052.608190**, con concentración por área Λ₁% = 0.962780, Λ₀.₁% = 0.793475 y R_eff = 0.000749250.

La comprobación de seis fuentes se hizo sobre el contorno común de 2048 rayos. Las auditorías de contorno de 4096/8192 rayos y el reajuste final de área se hicieron sobre una fuente representativa, 64×32 fase 0. No se afirma haber ejecutado seis fuentes sobre el contorno final de 8192 rayos ni una prueba matemática de convergencia.

## Integridad y procedencia

- Manifest principal: **28/28** hashes SHA-256 y tamaños correctos.
- Manifest de checkpoints: **16/16** hashes SHA-256 correctos.
- Checkpoint primario: `wine_split6_j0_true.pt`.
- SHA-256: `d733c85ea2f3937aacb0fa230632f6e41f35867a7c42ac50e2737e30315de1c9`.
- No se reentrenaron redes. Se cargaron pesos, índices y escalador del checkpoint; se comprobó la accuracy de validación guardada.
- Se conservan sin modificar el paquete fuente, su protocolo y sus resultados históricos.

**Limitación de reproducción histórica:** el ZIP aporta el núcleo geométrico y una descripción del refinador, pero no el ejecutor completo de B4/B5, los radios históricos ni una definición explícita de todas las métricas de concentración. Una reconstrucción de la regla documentada obtiene aproximadamente 1442.44 (64×32) y 1239.53 (128×64), no 1894.40 y 1362.50. Por ello este informe es una auditoría nueva y trazable de los checkpoints suministrados, no una reproducción exacta ni una corrección demostrada de cada fila histórica. `historical_reproduction.json` guarda la reconstrucción y su alcance.

## Campo y verificación independiente

Se utiliza el campo exacto del paquete, G(P)=C(P)ᵀ M C(P), con M=R(F+ρλmax I)⁻¹Rᵀ y ρ=10⁻⁴. Los pesos de perspectiva son softmax(fP), y C es su jacobiano. No se introducen jets regionales.

Para acelerar la integración se implementó la geometría analítica de esta inmersión: derivadas exactas de softmax, conexión por proyección de la Hessiana y curvatura por la ecuación de Gauss. Se comparó con la autodiferenciación original en tres puntos por estado y en cinco puntos de alta curvatura. En estos últimos, el máximo error relativo fue 8.01e-15. K(0) del primario es −456.9644849734.

Geodésicas DOP853: rtol=2×10⁻¹⁰, atol=2×10⁻¹². Al endurecer ambas tolerancias 100 veces, el máximo desplazamiento de los extremos de 128 rayos fue 6.94e-10 en coordenadas de carta. El error máximo de velocidad métrica al cuadrado fue 5.72e-10. El contorno de referencia es simple y válido; las mallas radiales densas auditadas no mostraron triángulos de orientación negativa. Estas comprobaciones no constituyen una demostración global sobre el cut locus.

## Qué falla en las fuentes radiales

Se fijó un solo radio para todas las fuentes, r=0.07769570588618832. Cada fuente radial aproxima su borde mediante cuerdas entre extremos de rayos. La subdivisión de triángulos mejora la integral sobre ese polígono, pero **no mueve sus cuerdas hacia el verdadero contorno geodésico**.

| Malla inicial | Fase | C_A, polígono radial | C_A, contorno común 2048 |
|---|---|---:|---:|
| 64×32 | 0 | 1501.605341 | 1053.574002 |
| 64×32 | π/64 | 2271.649999 | 1053.578187 |
| 96×48 | 0 | 1694.142367 | 1053.574623 |
| 96×48 | π/96 | 1339.016977 | 1053.572096 |
| 128×64 | 0 | 1251.414343 | 1053.577508 |
| 128×64 | π/128 | 1405.462413 | 1053.567388 |

Rango relativo radial: **70.1900%**. Rango relativo con contorno común: **0.001025%**. Ambos métodos revisan globalmente el error de cuadratura; la diferencia entre columnas aísla principalmente la representación del dominio y la triangulación espacial.

Una auditoría de los centroides ponderados por energía estima que entre 29.17% y 78.56% de la energía de las fuentes radiales queda fuera del polígono denso de referencia. La fracción de área fuera es sólo 0.073%–0.354%. Se trata de una clasificación por puntos de cuadratura, no de una intersección poligonal exacta de cada celda.

**Diagnóstico:** existe una cresta de K² junto al borde, y pequeñas diferencias geométricas del dominio incluyen o excluyen mucha energía. El error de área total, por sí solo, no controla el error de una integral tan localizada. El error del contorno explica gran parte de la dispersión observada en esta ejecución; no se atribuye a él, sin el ejecutor original, toda la discrepancia histórica B4/B5.

## Sustitución numérica aplicada

1. Construir un contorno denso común mediante el campo completo y geodésicas de precisión controlada.
2. Generar seis conjuntos de puntos interiores a partir de las resoluciones y fases especificadas.
3. Triangular espacialmente y verificar que cada triangulación cubra exactamente el mismo polígono: ninguna celda cruza su borde y el área de carta coincide hasta 10⁻¹⁰ relativo.
4. En cada iteración, comparar la contribución del centroide de **cada** triángulo con la de sus cuatro hijos.
5. Refinar los padres que reúnen el 80% del error local normalizado total; no limitarse a los descendientes elegidos en la primera ronda.
6. Exigir dos rondas estables, error estimado relativo de energía <0.0005, cambio de C_A <0.0005 y estabilidad de concentración. Se registran todas las trayectorias. El límite de celdas se comprueba al terminar cada ronda, por lo que puede sobrepasarse durante esa ronda.

El estimador local de error no es una cota rigurosa. La comparación entre fuentes, el cambio de contorno y el control de ODE son comprobaciones independientes necesarias.

## Concentración: definición válida entre mallas

Se fija C_A=√(∫K²dA/A). Para las métricas espaciales, se ordenan las celdas por **densidad K²**, no por energía total de celda, y se acumula área intrínseca. Se interpola la última celda en cada cuantíl.

- Λ_q: fracción de energía contenida en el q de área más intenso.
- f₅₀ y f₉₀: fracciones mínimas de área que contienen 50% y 90% de la energía.
- R_eff=(∫K²dA)² / (A∫K⁴dA).

Las métricas basadas en número de celdas se conservan como `legacy_*` en los JSON, pero no se usan como estimandos independientes de malla. Sus valores históricos no se comparan directamente con los nuevos valores por área. En particular, R_eff≈0.76 del control histórico no equivale al R_eff por área calculado aquí.

| Estimando | Mediana, seis fuentes 2048 | Rango | CV poblacional entre fuentes | Auditoría final 8192, área 0.02 |
|---|---:|---:|---:|---:|
| C_A | 1053.57431 | 1053.56739–1053.57819 | 3.41239e-06 | 1052.60819 |
| lambda_1pct | 0.962848051 | 0.962847794–0.962849201 | 5.29006e-07 | 0.96278003 |
| lambda_01pct | 0.79371626 | 0.793714761–0.793717399 | 1.13447e-06 | 0.793474616 |
| frac50 | 0.000259782717 | 0.000259780046–0.000259784835 | 5.49959e-06 | 0.000260108956 |
| frac90 | 0.00230549766 | 0.0023054206–0.00230553444 | 1.56663e-05 | 0.00230945764 |
| R_eff | 0.000748323108 | 0.000748318048–0.000748336393 | 7.55049e-06 | 0.000749250044 |

Tolerancias fijadas antes de la comparación: rango relativo de C_A y R_eff <0.005; rango absoluto de Λ₁% y Λ₀.₁% <0.005; rango absoluto de f₅₀ y f₉₀ <10⁻⁵. **Las seis métricas pasan en el contorno común.** El CV es descriptivo de fuentes numéricas, no una incertidumbre estadística ni un intervalo de confianza.

## Auditoría de contorno y área

Con el mismo radio y una fuente interior representativa:

| Rayos del contorno | C_A |
|---:|---:|
| 2048 | 1053.574002 |
| 4096 | 1052.751195 |
| 8192 | 1052.544619 |

El último cambio es aproximadamente **0.0196%**, menor que 0.5%. Las cifras 2048 y 8192 difieren aproximadamente 0.098%: la concordancia entre triangulaciones interiores no sustituye a este control de borde.

Se reajustó el radio a **0.07769581817080**, manteniendo 8192 rayos. Una cuadratura de área Dunavant de grado cinco da A=0.01999999999987; error relativo frente a 0.02: -6.59e-12. La suma de áreas del integrador de centroides final es 0.01999998218078, error relativo de aproximadamente −8.91×10⁻⁷. El último cambio de C_A es 0.002110%, y el error estimado de energía es 0.010535%.

Resultado final: C_A≈**1052.61**. No se proporciona un intervalo de confianza estadístico. La precisión sustentada es la de esta auditoría numérica, no todos los decimales impresos.

## Control y réplica

| Estado | Método | Mediana C_A | Rango relativo C_A | Resultado multifuente |
|---|---|---:|---:|---|
| split 6 random | Radial, seis fuentes | 2.6618266×10⁻⁶ | 0.0000285% | Pasa C_A y concentración por área |
| split 5 true | Radial, seis fuentes | 36.792704 | 0.275805% | Pasa C_A; fallan algunas métricas de concentración |
| split 5 true | Contorno común 512, seis fuentes | 36.754974 | 0.001510% | Pasa C_A y concentración por área |

En split 5 true, la versión radial no pasa f₅₀, f₉₀ y R_eff con las tolerancias fijadas. El contorno común resuelve la dispersión entre fuentes. No se realizó para la réplica una auditoría de contorno 512→1024→2048 comparable a la auditoría extensa del primario; su cierre queda limitado a independencia de la triangulación sobre el contorno fijo.

Control random, métricas medianas por área: Λ₁%≈0.010428, Λ₀.₁%≈0.001044, f₅₀≈0.490571, f₉₀≈0.896277, R_eff≈0.999506. Es casi uniforme en área. Réplica true, contorno común: Λ₁%≈0.608544, Λ₀.₁%≈0.142469, f₅₀≈0.006702, f₉₀≈0.032455, R_eff≈0.018505.

## Estado de Leviathan después de B6

- El primario conserva curvatura alta y localización muy fuerte: el 1% de área más intenso contiene aproximadamente **96.28%** de la energía; el 0.1%, **79.35%**.
- Aproximadamente **0.0260% del área** concentra 50% de la energía y **0.231% del área**, 90%.
- El control random sigue siendo casi plano y difuso; la réplica true mantiene concentración mayor.
- Esto es evidencia numérica descriptiva sobre los tres checkpoints especificados. No es una nueva comparación poblacional ni evidencia causal o universal.
- B6 resuelve operativamente la dependencia de triangulación del primario con dominio controlado. No valida retroactivamente los números absolutos B4/B5 ni cierra una auditoría de contorno para toda la población.

Siguiente paso recomendado: antes de reabrir B5 poblacional, completar el control de contorno de la réplica y congelar el nuevo integrador, su definición por área y sus tolerancias de borde. Después recalcular los estados poblacionales con ese instrumento, conservando los resultados anteriores como versiones históricas.

## Reproducibilidad

El ZIP adjunto incluye el ZIP original intacto, scripts nuevos, estados geométricos derivados, configuración fijada, hashes, versiones, tablas por fuente, historiales de convergencia, contornos y las celdas finales del primario. No incluye todas las nubes de celdas intermedias, que se regeneran con los scripts.

Descomprimir el paquete original bajo `repro/` desde la raíz de la entrega. Instalar las versiones indicadas en `E15_B6/environment.json`. Secuencia: `prepare.py`, `reproduce.py`, `boundary.py`, `calibrate.py`, `run_sources.py --mode radial`, `run_sources.py --mode global`, `refine_boundary.py`, las llamadas globales `--boundary 4096 --first` y `--boundary 8192 --first`, `correct_area.py`, la llamada global `--boundary 8192 --disk-suffix _area02 --first`, `control_cases.py`, `audit.py`, `make_figure.py`. Los resultados JSON existentes se reutilizan; para una ejecución limpia, conservar sólo código/configuración y eliminar resultados generados. El núcleo original se mantiene sin modificaciones.

Las tablas completas de medianas, rangos y CV están en `E15_B6_summary.csv`; las estimaciones individuales, en `E15_B6_sources.csv`.
