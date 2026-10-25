# DIN-C1 — sensibilidad posterior: rayos normales a las aristas (2026-10-25)

**Naturaleza:** auditoría **posterior** al cierre de DIN-C1. **No cambia** el veredicto, que fue PASS sobre el desenlace operacional congelado. La motivó el suplemento angular de DIN-G1 (PR #80): en un estado sintético de Iris, el ρ_borde nativo superaba en un 47 % a la longitud de un rayo axial concreto.

## Qué se midió
Para los 1560 estados de la cohorte (780 trayectorias en los updates 10 y 250), Claude integró con `rho_borde.rho_quad` (instrumento congelado, sin cambios) las semirrectas en direcciones **normales exteriores a cada arista** del casco de f, más las cuatro direcciones axiales. Lo hizo con `aristas.py` (`df7f89bc…`) en la VM del equipo del responsable, en lotes. Hubo varios cortes por tiempo y los lotes faltantes se repitieron; al final no falta ningún estado. La tabla resultante es `aristas_c1.csv` (`3e7399e7…`).

**Por qué importa:** en una dirección exactamente normal a una arista, la semirrecta termina en la **arista**, no en un vértice. La longitud es discontinua en esa dirección, y la búsqueda uniforme de `rho_borde.py` (1440 direcciones más un refinamiento local) no puede caer exactamente ahí. El ρ_borde nativo mide, en la práctica, el **mínimo sobre las semirrectas que terminan en un vértice**.

## Resultados
| update | estados con una normal de arista más corta que el nativo | cociente normal/nativo: mínimo / mediana / máximo |
|---|---|---|
| 10 | **67.8 %** | 0.52 / 0.89 / 1.61 |
| 250 | 12.8 % | 0.83 / 1.002 / 1.77 |

- En el update 10, antes del colapso, el nativo **sobreestima** el mínimo de las semirrectas en la mayoría de los estados (mediana −11 %).
- En el update 250, con M colapsada, el efecto es pequeño.

## Sensibilidad de la primaria (análisis congelado aplicado a desenlaces corregidos; exploratorio)
| variante | veredicto | D | p | pendiente | W_adj lineal | D con grado 5 |
|---|---|---|---|---|---|---|
| **Congelado** (nativo) | PASS | 0.0256 | 0.0002 | +0.81 | 0.199 | 0.026 |
| L = log min(nativo, normales) en u10 | PASS | 0.0220 | 0.0004 | +0.82 | 0.198 | 0.040 |
| L e Y corregidos | PASS | 0.0217 | 0.0004 | +0.81 | 0.195 | 0.040 |

**Lectura:** el resultado de DIN-C1 **no depende** de la limitación angular del instrumento. Con la distancia corregida por las aristas, X sigue mejorando la predicción fuera de muestra con un D similar.

**Límites:**
- Normales y ejes son un conjunto finito de candidatos; esto **no certifica** el mínimo global sobre las semirrectas.
- La definición operacional congelada de ρ_borde se mantiene. Lo que conviene precisar es su interpretación: «longitud mínima de una e-geodésica recta que llega a un **vértice** del casco» (lo que mide el nativo), frente al mínimo sobre todas las caras.
- Afecta en la misma medida a T2-A1 (updates 50–250, en su mayoría ya colapsados) y a D1–D6. No se reevalúan aquí.
