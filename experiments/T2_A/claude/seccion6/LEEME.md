# Sección 6 de E1 (enmendada por E2 v1): implementación y pruebas

- `seccion6_sensibilidad.py`: «análisis exploratorio de sensibilidad por completaciones binarias». Implementa E2 v1 (congelada), secciones 5 bis y 5 ter. La cola y el bootstrap son idénticos a `primary_analysis.py` del prerregistro (SHA-256 `817a1783…7de4`).
- `pruebas_seccion6.py`: pruebas por enumeración exhaustiva (E2 5 ter.3, punto 2). `salida_pruebas_seccion6.json` contiene su salida: **PASA, 5095 comprobaciones, 0 fallos**. Contenedor Linux, Python 3.13.16, numpy 2.5.3, 2026-10-21.
- `MANIFIESTO_seccion6_2026-10-21.sha256`: hashes del script, de las pruebas y de su salida, con commit propio (E2 5 ter.3, punto 3).

## Qué cubren las pruebas
| prueba | qué compara |
|---|---|
| 1 | cola idéntica a `primary_analysis.tail` (300 casos, con y sin empates) |
| 2 | extremos de precisión, tasa base, diferencia, lift y lift restringido frente al oráculo (600 casos aleatorios: ND dentro, fuera y en ambos lados; empates en el borde) |
| 3 | casos dirigidos: ND solo dentro, solo fuera, ambos lados; tasa base 0 posible (a+b = 0) y obligatoria; empate en el borde; todas las X iguales; una sola trayectoria |
| 4 | cohorte vacía: nada definido, criterio 4 NO EVALUABLE |
| 5 | réplicas con un split repetido y otro ausente, frente al oráculo con copias empatadas; sorteos idénticos a los de `primary_analysis` |
| 6 | envolvente frente al oráculo réplica a réplica (≤ 10⁻¹²); sin ND coincide con el IC de `primary_analysis.evaluate`; lift indefinido en réplicas → NO EVALUABLE y contado |
| 7 | criterio 6 (retirada de cada split con cola recalculada) frente al oráculo (80 casos) |
| 8 | criterio 4 frente al oráculo (200 casos); criterio 5 = «NO EVALUADO POR ESTE METODO» |

El oráculo enumera las 2^n_ND completaciones en aritmética racional. Una trayectoria duplicada por el remuestreo conserva un único valor en cada completación.

**Control de las pruebas (mutaciones, no versionadas):** con tres fallos introducidos a propósito en copias del script, las pruebas fallan:
- la regla de tasa base de E1 §6.3: 464 fallos;
- una cola sin empates completos: 130 fallos;
- la semilla cambiada: 53 fallos.

## Estado
Con este manifiesto quedan cumplidas las condiciones 1–3 de E2 5 ter.3. La condición 4 (no ajustar reglas a resultados reales) rige desde ahora.

Esto **no** asigna Y, **no** decide nada y **no** modifica el veredicto confirmatorio de T2-A0. Hoy no hay datos de producción a los que aplicarlo: el piloto no tiene Y asignado.

Uso sobre datos, cuando existan, con el script cuyo hash coincida con el manifiesto:
```
python -I seccion6_sensibilidad.py --entrada trayectorias.csv --salida resultado_seccion6.json
```
El CSV lleva las columnas `split, trajectory, X, Y` (Y ∈ {1, 0, ND}) y, opcionalmente, `causa_ND`.
