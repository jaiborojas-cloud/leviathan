# E16-C — Diseño congelado v1 antes del código y la ejecución

Fecha: 2026-10-19. Identificador libre E16-C; rama propia. E16-B no se reabre:
se estudia otro método instrumental en la misma cohorte conocida. Diseño
informado por el diagnóstico de segundo orden de B, no validación empírica nueva.
Ningún resultado de este método abierto antes del commit de congelación.

## Datos, métricas y métodos

config.json es copia byte a byte del de B, con hash de procedencia. Mismos tres
estados, tres paneles, tres puntos y tres composiciones: 81 configuraciones.
Añadir 18 controles (cero y duplicado por nueve estado/panel) =99 resultados de rango.
Red sin entrenamiento. Ningún artefacto de T1/E15/T2-A. No modificar archivos de A/B.

1. Referencia independiente explícita: fórmulas de mathematical_spec.md, mpmath
   a 80 y 120 dps; F,g,C,L derivados analíticamente en ambas precisiones.
2. Autodiff float64 directo de S_macro; F de Jacobiano de logits, g=F+0.01I.
   No importar ni ejecutar los scripts históricos de B; implementación nueva
   del forward sólo para comparar la maquinaria.
3. FD central de cuarto orden sobre S, δ=0.002 y 0.001, mpmath80.
   No alimentar derivadas de referencia al FD. Cachear sólo evaluaciones forward.
4. Control de implementaciones truncadas en las 54 configuraciones no lineales.

Dependencias disponibles: Python 3.12.14, NumPy 2.3.5, autograd 1.8.0,
mpmath 1.3.0. CPU, una hebra BLAS, sin aleatoriedad ni semillas. Presupuesto
120 s por corrida, memoria objetivo 512 MiB. No entrenamiento ni geodésicas.
Versionar protocolos, fórmulas, código y tablas pequeñas; sin binarios de red.

## Criterios congelados

Para cada una de las 99 configuraciones, U*=B_120 L_120:
τ=1e−8 max(1,σ_max(U*)). No se cambia el prefactor de B; se transporta
correctamente el error antes de compararlo. Clasificación de referencia:
σ_i<τ/10 es nulo operacional; σ_i>10τ positivo; en la banda restante,
INCONCLUSIVE, conservando todos los valores y sin sustituir estado.

Precisión 80/120: ||U_80−U_120||F≤1e−50 max(1,||U_120||F).
Se espera holgura de decenas de dígitos; esto no certifica exactitud real.
Autodiff: e_triangle≤τ/10 y error máximo de B≤1e−10+1e−9 max|B*|.
FD: e_FD=||(B_FD−B*)L*||F≤τ/10 para AMBOS pasos. También registrar errores
absolutos y relativos de B y h, sin usar esos valores para ajustar criterios.
La tolerancia se justifica por O(δ⁴) con δ≤0.002 (δ⁴≤1.6e−11), pesos y
entradas O(1), referencia de 80 dígitos que evita cancelación float64, y
C con g≽0.01I en la carta inicial. Es una expectativa, no garantía a priori
de las constantes de truncamiento: si excede el umbral queda INCONCLUSIVE.
No se exige un cociente fijo de convergencia (ceros y cancelaciones lo impiden).

Exigir que cada ruta dé el mismo rango operacional y que sus σ_i queden
al mismo lado de τ con margen e_triangle o e_FD. Para controles se exigen
además rangos 0 y 1, respectivamente. Clasificar PASS_NUMERICAL si pasan
precisión, márgenes, concordancia y controles. INCONCLUSIVE por margen, precisión,
rango ambiguo, dependencia o presupuesto insuficientes. FAIL por error de
identidad analítica, distinto rango inequívoco o incumplir los controles conocidos.
La clasificación conjunta no convierte error FD grande en refutación del rango.

Identidad de transporte del error: residual Frobenius entre diferencia directa
y suma de los dos términos ≤1e−60 max(1,||U*||F) en cálculo mpmath120.
La norma directa debe ser ≤e_triangle+1e−60 max(1,||U*||F).
Negativo truncado: ||(B_trunc−B*)L*||F>τ en las 54 configuraciones; si no,
INCONCLUSIVE de sensibilidad del negativo, sin modificar composición ni punto.
Preservar todos los fallos y corridas; cualquier corrección de implementación
requiere guardar versión fallida, causa y nueva corrida, sin alterar el diseño.

## Entrega e interpretación

Guardar checks.csv, ranks.csv y negative_controls.csv, resumen, entorno,
versiones, tiempos, hashes y progreso por grupo estado/panel. Tiempos fuera de
las tablas deterministas para reproducirlas sin exigir duraciones idénticas.
No son 81 réplicas independientes. PASS_NUMERICAL valida instrumentación para
estos puntos, no rango exacto en un dominio, emergencia, aprendizaje, predicción
ni generalización. E16-B permanece INCONCLUSIVE bajo su propio protocolo.
Si la precisión se resuelve, evaluar después una fase independiente sobre
estados nuevos; no ampliar automáticamente a entrenamiento ni modificar T2-A.
