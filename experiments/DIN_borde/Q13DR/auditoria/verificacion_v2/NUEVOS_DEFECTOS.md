# Casos nuevos y residuales en la v2

Fuentes originales intactas, revisión245d735f. La recomendación es corregir antes
de congelar, principalmente N01. Estos casos no se mezclan con las tasas del
Monte Carlo regular: son tablas adversariales distintas, también sintéticas.

## N01 — c constante decimal puede producir β finita y arbitraria

**ALTA; protección F02 incompleta.** En
[pendiente, L82](sources/v2/Q13DR/analisis_Q13DR.py#L82), comprobar den>0 después
de restar la media no detecta siempre una constante. Para seis valores .1,
la media calculada puede ser .09999999999999999: todos los residuos iguales
son pequeños pero no0 y la suma de cuadrados es positiva.

[Caso puro](results/cases/new_constant_decimal_c_rules.json):
`pendiente([.1,.2,.3,.4,.5,.6],[.1]*6)` devuelve **−2.0**, no una excepción;
con .2 devuelve−1 y con .7 devuelve.25. .5 sí dispara la excepción y por eso
el único caso binario de la suite del autor no descubre el problema.

[Caso íntegro N200](results/cases/new_constant_decimal_c_common80.json):160/200
splits comunes, todos los dominios válidos, faltantes≤2.1% por nivel, compuerta
operacional válida. Los seis c comunes son **.1**. El analista publica:

```text
beta = 8.0
IC95_beta = [-8.0, 8.0]
replicas_fallidas = 0
veredicto = NO_CONCLUYENTE
```

Debería ser INCONCLUSIVE por β no identificada. No se observó un falso MODULA
en este ejemplo: el defecto demostrado es publicar una pendiente y un IC para
un parámetro sin rango. Tanto el punto como las réplicas eluden la protección.

**Corrección propuesta:** rechazar c no finita o con `np.ptp(c)==0` antes de
centrar (o todos los valores iguales a c[0]); conservar además controles de den y
finitud. Es igualdad exacta, sin añadir tolerancia ni cambiar el estimando válido.
Repetir constantes decimales además de .5.

## N02 — rango común negativo y margen de equivalencia negativo

**MEDIA, salida científica secundaria incorrecta.**
[L198](sources/v2/Q13DR/analisis_Q13DR.py#L198) usa cs[0]−cs[-1], asumiendo que
los c comunes conservan el orden de las medianas operacionales. La compuerta
se aplica a todas las válidas; no garantiza ese orden en el subconjunto común.

[Caso admitido N200](results/cases/new_reversed_common_c_range.json):160 splits
comunes, punto c=[.3,.35,.4,.45,.5,.6], compuerta válida y cero réplicas fallidas.
Publica **rango_c=−.3** y **margen_dD_equivalencia=−.006**, junto a NO_MODULA
secundaria. El rango real es .3 y el límite en magnitud es +.006.

**Corrección propuesta:** max(cs)−min(cs), con diferencia L0−L5 en otro campo si
se desea. Cambiar la compuerta para exigir orden en comunes sería otra decisión
de diseño; no hace falta para corregir esta aritmética. No cambia aquí el
veredicto primario, pero sí la interpretación cuantitativa prometida por F05.

## N03 — eps entero grande provoca OverflowError en la nueva validación

**MEDIA, crash nuevo del validador.**
[L69](sources/v2/Q13DR/analisis_Q13DR.py#L69) convierte numbers.Real mediante float
sin controlar OverflowError. [Plan JSON con eps=10**400](results/cases/new_plan_huge_integer_eps.json):
código1 y traceback, no ABORTA/código3. No se ejecuta ningún análisis estadístico
en ese caso; es una entrada inválida que debería rechazarse limpiamente.

**Corrección propuesta:** capturar errores de conversión como Aborta, o rechazar
primero valores distintos del eps esperado antes de convertirlos. No modificar
la rejilla ni añadir tolerancias.

## N04 — archivos de entrada ausentes/directorios todavía eluden ABORTA

**MEDIA, ruta heredada que incumple el nuevo contrato de lectura.** Los hashes
se leen en [L225](sources/v2/Q13DR/analisis_Q13DR.py#L225) antes del try de lectura
de JSON; el manejador externo sólo captura Aborta.

- [Plan ausente](results/cases/new_plan_missing_file.json): FileNotFoundError,
  código1 con traceback.
- [Plan es directorio](results/cases/new_plan_directory.json): IsADirectoryError.
- [Tabla ausente](results/cases/new_table_missing_file.json): FileNotFoundError.
- [Resumen ausente](results/cases/new_summary_missing_file.json) sí termina
  ABORTA/código3: su lectura está en la región protegida.

**Corrección propuesta:** convertir los OSError/errores de decodificación de
hash/lectura de entradas en Aborta antes de analizar. No presentar estos crashes
como un veredicto estadístico ni suponer que validación estricta cubre todos.

## N05 — se cuentan todos los fallos, pero sólo se guardan veinte detalles

**MEDIA de trazabilidad; la decisión INCONCLUSIVE es correcta.** En
[L193](sources/v2/Q13DR/analisis_Q13DR.py#L193), fallos_primeros=fallos[:20] elimina
del resultado los demás índices/errores y no enlaza un archivo completo.

[Caso NB300](results/cases/new_degenerate_logging_300.json): se generan exactamente
300 draws, sin reintentos;116 fallan y se reportan116, pero sólo se conservan20
registros de error. La traza independiente recupera los116 índices. No se afirma
que el código descarte réplicas para calcular un IC: regresa INCONCLUSIVE como debe.

**Corrección propuesta:** conservar todos los fallos o archivarlos con SHA y
mantener veinte sólo como vista previa. El costo de guardar≤2000 índices es pequeño
y evita tener que reejecutar el análisis para reconstruir el diagnóstico.

## Qué no se interpreta como defecto nuevo

Las comparaciones decimales exactas siguen sus efectos binarios conocidos, ahora
declarados por diseño. No se introduce redondeo. Tampoco se exige monotonía de D,
misma k en todos los niveles o potencia de equivalencia: esos alcances ya están
aclarados. Los defectos anteriores de Spearman, planes ordinarios y población
puntual tienen pruebas de corrección; véase la [matriz](MATRIZ_HALLAZGOS.md).
