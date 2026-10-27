# Hallazgos nuevos, limitados al diff v1→v2

Se revisó únicamente el [diff congelado](sources/analista_v1_v2.diff) y sus interacciones. No se reabrió una auditoría estadística general ni se modificaron archivos ajenos.

## N01 — Media de trazabilidad: solo queda registrado el primer nivel fallido del brazo

**Demostrado; sin cambio de veredicto demostrado.** La localización introducida en [líneas157–160](sources/v2/Q13M2/analisis_Q13M2.py#L157) y [líneas167–172](sources/v2/Q13M2/analisis_Q13M2.py#L167) condiciona tanto cambiar el estado como agregar el motivo a `estado[m] is None`. Tras el primer fallo, los motivos siguientes desaparecen de la salida. Para X/L, la v1 recorría todos los niveles y conservaba los motivos globales; la v2 pierde esa exhaustividad al localizarlos.

Caso mínimo reproducible, desde la raíz del repo, con los [requisitos](requirements.txt):

```python
import sys
sys.path.insert(0, 'experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts')
from support import target, fixture, execute
m = target()
rows = fixture(20)
for r in rows:
    if r['nivel'] == 'WD2':
        r['X10'] = -2.0
    if r['nivel'] == 'WD3':
        r['rho_caras_10'] = 1.0
out = execute(m, rows, 20)
print(out['motivos_inconclusive'])
# ['WD: WD2: X sin variacion intra-split']
# Falta WD3: L sin variacion.
```

Todos los datos siguen válidos y no hay faltantes. La salida [two_malo_levels_WD.json](results/changed_cases/two_malo_levels_WD.json) conserva `LP=MODULA`, `WD=INCONCLUSIVE` y conjunto `INCONCLUSIVE_PARCIAL`: el aislamiento científico de F01 funciona. El defecto es perder evidencia de un fallo presente.

Segundo caso: fijar `rho_caras_250=1` en WD2 y WD3. La nueva primaria por nivel intenta ambos, pero solo registra el `SSE_base=0` de WD2. Salida: [two_primary_failures_WD.json](results/changed_cases/two_primary_failures_WD.json). El código continúa iterando los niveles de `usar`; el filtro de estado suprime el segundo mensaje. No se afirma que la v1 evaluase todos esos fallos de primaria: antes retornaba globalmente al primero.

**Corrección propuesta:** separar la transición de estado del registro de errores. Guardar todos los `malo[nv]` y las excepciones puntuales por nivel, aunque el manipulador ya esté inconcluso; cambiar el estado solo cuando corresponda. A0 puede seguir invalidando ambos. Agregar regresiones con dos niveles inválidos del mismo brazo. No se necesita cambiar semillas, estimando, compuertas ni bootstrap.

## N02 — Baja documental: dos frases siguen exigiendo igualdad exacta

La cabecera del [borrador v2](sources/v2/DISENO_DIN_Q13M2_BORRADOR_v2.md) resuelve F04 mediante tolerancia10⁻¹² y las pruebas la implementan. Sin embargo, sus [líneas84](sources/v2/DISENO_DIN_Q13M2_BORRADOR_v2.md#L84) y [106](sources/v2/DISENO_DIN_Q13M2_BORRADOR_v2.md#L106) todavía dicen «reproduce exactamente 0.07692466151365258».

**Interpretación:** la modificación explícita de v2 y su prueba numérica son claras; no se demuestra un error del analista ni se rechaza la reproducción por esa redacción antigua. Se recomienda sustituir esas dos frases por la tolerancia ya aprobada antes de congelar. No cambia ningún umbral científico.

## Nuevas rutas comprobadas sin defecto de veredicto

- F02 crea en exclusiva y conserva un marcador ante colisión inicial y carrera posterior. Directorio y enlace colgante también se conservan. La prueba de carrera usa una inyección en memoria, declarada en su salida; no altera la fuente del analista.
- `ls={error:…}` suprime la compatibilidad y preserva las primarias y LP−WD. En `main`, una excepción LS inyectada queda como nota sin crash ni pérdida de la primaria.
- `compatibilidad` rechaza explícitamente63 o1 réplicas LS frente a64 de M2, sin broadcasting;64/64 mantiene los IC. El error al proporcionar longitudes distintas directamente a `analizar` es un límite de API, no un crash demostrado de la CLI que fija ambos tamaños en2000.
- Arrays vacíos o matrices de réplicas no son el contrato de la CLI. El caso vacío lanza `IndexError`; matrices de igual forma se aplanan en el cuantil. Este comportamiento de `q`/NumPy ya existía; no se presenta como defecto introducido por el diff.
- Si hay compuerta fallida y un dato constante del mismo brazo, prevalece la compuerta de manipulación. El brazo sano permanece intacto. No se cambia esa precedencia después de observar el caso.

Resultados íntegros: [new_findings.json](new_findings.json), [changed_cases](results/changed_cases/summary.json) y [CLI](results/cli/summary.json). No se implementó ninguna corrección en el analista o diseño auditados.
