# E16 — Cierre de la primera fase analítica

Estado: **EXPECTED_GEOMETRIC_CONTROL**, implementación v3, 122/122 comprobaciones
PASS. No resultado confirmatorio empírico ni ventaja predictiva. Fuente de tablas:
[checks.csv](results/run_v3/checks.csv), [espectros](results/run_v3/spectra.csv),
[resumen](results/run_v3/summary.json). Diseño previo: commit `7db497d`;
se conserva [fe de erratas](ERRATA_v2.md) posterior al fallo de referencia manual.

## Operaciones y rango

| Operación exacta | Resultado | Condición / límite |
|---|---|---|
| Carta p=φ(q), Jacobiano invertible | rango 2→2, norma preservada | h_q=Jᵀh_pJ, misma familia y θ fijo |
| Subfamilia φ(t)=(t,2t) de la base SPD | rango 2→1, h_t=14 | rank(BᵀJ)≤min(rank B,dim q) |
| Subfamilia de familia redundante | rango 1→1, h_t=2 | la imagen BᵀJ cubre la imagen Bᵀ |
| Agregación π=x+y de S=θ¹(x+y) | rango 1→1; hbar=2 | h básico, kernel vertical; no hay reducción estricta |
| π=x para h=diag(2,3) | descenso imposible | dirección vertical con norma 3; secciones dan 2 y 5 |
| π=x, S=θ¹xy | valores 2 y 8 en x=1 | dependencia de representante; además hay obstrucción vertical |
| Producto (θ¹x)(θ²y) | B de rango 1; h de espectro (0,22) | cadena completa; omitir Hessiana Ψ falla |
| Suma S₁+S₂ frente a (S₁²+S₂²)/2 | rango 0 frente a 2 | no hay monotonía frente a la suma; det B cuadrática=50 |
| Cociente F=diag(2,0), S=θ¹x | h=1/2 en dirección x, invariante | ω y B anulan K, rango de F constante |
| S=θ²x, mismo F y cambio de carta | contracción ingenua 0 frente a 1/8 | inadmisible: no define geometría del cociente |

La igualdad rank h=rank B usa positividad de la cométrica en la imagen admisible.
Una submersión con descenso tensorial conserva el rango entre h y hbar: las
coordenadas eliminadas ya eran nulas. La restricción puede quitar direcciones
geométricamente activas o sólo redundantes. Para composiciones escalares, el
rango depende de cancelaciones y términos de segunda derivada de Ψ, no sólo de
la no invertibilidad de un mapa verbalmente llamado agregación.

## Identidades y verificación independiente

Se contrastaron simbólicamente pullback, cambio de carta del modelo con C
transportada, cadena completa de ω y B, restricciones y descenso válido.
Diferencias centrales sobre el escalar S, sin usar derivadas simbólicas como
entradas, verificaron ω, B y h en dos pasos para todos los ejemplos y cartas.
Máximo error absoluto FD agregado: 6.800e−8; máximo relativo no nulo 4.441e−10.
Los contrastes float64 de identidades tuvieron error absoluto cero en esta
corrida; eso no es certificado de error para otros sistemas.
Condición máxima positiva de h: ≈113.94 en la carta perspectival, lejos de
singularidad en el punto fijado. Tolerancias originales intactas.
Tiempo medido del ejecutor: ≈0.247 s; memoria máxima registrada 71872 KiB,
Python 3.12, NumPy 2.3.5, SymPy 1.14.0. Detalles en
[entorno](environment.json) y [recursos](results/run_v3/resources.json).

## Fallos y alcance

- v1: interrupción al escribir progreso por mezclar rutas absolutas y relativas;
  A dejó resultados válidos, corrida global INCONCLUSIVE. Se conserva el código
  en `6efaacc` y [diagnóstico](results/run_v1/diagnostic.md).
- v2: 120/121 PASS; referencia manual cuadrática errónea. Se conserva el código
  en `36f71c5`, tablas y [resumen fallido](results/run_v2/summary.json).
- v3: referencia corregida con derivación explícita y control adicional de ω;
  122/122 PASS, reproducidos sin alterar criterios ni ejemplos. No se reemplazan
  las corridas anteriores ni se presenta el conjunto como acierto de primera ejecución.

La geometría de llegada queda indefinida para los mapas con obstrucciones;
no es un outcome pendiente de simulación, sino una imposibilidad bajo el
concepto de descenso tensorial empleado. No se midió curvatura ni se validó
una red. Todos los resultados positivos son controles matemáticos esperados.
Los espectros son descriptores de cartas fijadas. Menor rango no prueba emergencia.

Lo nuevo aquí es una delimitación operativa reproducible de la propuesta
histórica, no el descubrimiento de la regla de cadena o el pullback. El
[siguiente diseño candidato](NEXT_PHASE.md) fija compuertas instrumentales para
una red independiente; su frecuencia de reorganización de rango y posible
valor empírico son hipótesis futuras. No se entrenó, integró ni recuperó T2-A.
