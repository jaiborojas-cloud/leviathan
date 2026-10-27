# Defectos y ambigüedades reproducibles

Fuentes auditadas, sin cambios, en [sources/provenance.json](sources/provenance.json). Los fragmentos siguientes usan el snapshot del analista; B=39 y NB=64 bastan para estos controles de flujo, no para estimar tamaño nominal. El Monte Carlo usa los presupuestos nominales completos.

## F01 — Alta: un fallo puntual exclusivo invalida al manipulador sano

**Defecto demostrado.** En [analizar, líneas 155–160](sources/target/Q13M2/analisis_Q13M2.py#L155), una sola captura de excepciones rodea todos los niveles activos. Si WD3 tiene Y constante, `A.primaria` lanza `FloatingPointError: SSE_base = 0`; se retorna `INCONCLUSIVE` global con `por_manipulador={}`. El diseño §4 prescribe `INCONCLUSIVE_PARCIAL` cuando un manipulador queda inconcluso y reportar ambos veredictos.

Caso mínimo, desde la raíz del repo, usando Python con NumPy/SciPy del [entorno](requirements.txt):

```python
import sys
sys.path.insert(0, 'experiments/DIN_borde/Q13M2/auditoria/scripts')
from support import target, fixture, execute
m = target()
rows = fixture(20)
baseline = execute(m, rows, 20)
for r in rows:
    if r['nivel'] == 'WD3':
        r['rho_caras_250'] = 1.0
observado = execute(m, rows, 20)
print(baseline['por_manipulador']['LP']['veredicto'])  # MODULA
print(observado['veredicto_conjunto'])                # INCONCLUSIVE
print(observado['por_manipulador'])                   # {}
```

Todas las filas siguen válidas, no hay faltantes, las compuertas pasan y las seis estadísticas puntuales de LP/A0 son **exactamente idénticas** antes y después. No se necesita modificar el analista. La alteración simétrica de LP3 borra WD. Salidas: [baseline](results/cases/baseline.json), [WD3](results/cases/WD3_Y_constant.json), [LP3](results/cases/LP3_Y_constant.json); comparación verificada en [verification.json](verification.json).

**Corrección propuesta:** capturar el fallo por nivel y marcar inconclusos solo los manipuladores que lo usan; si falla A0, ambos. Continuar el brazo sano y derivar `INCONCLUSIVE_PARCIAL`. Conservar nivel, excepción y todos los fallos. Agregar regresiones en ambos sentidos, sin alterar las restricciones globales declaradas de faltantes y comunes.

**Ambigüedad asociada, no disfrazada de discrepancia con el propio docstring:** [líneas 137–145](sources/target/Q13M2/analisis_Q13M2.py#L137) hacen global cualquier X/L constante, incluso en un nivel exclusivo. El docstring del analista declara explícitamente esa excepción global; entra en tensión con la independencia solicitada y la tabla general del diseño. Los casos [X constante](results/cases/WD3_X_constant.json) y [L constante](results/cases/WD3_L_constant.json) también borran LP. Aclarar antes de congelar si esa excepción es intencionada; si se exige independencia salvo A0, localizarla por manipulador y alinear el texto. No cambiar silenciosamente la regla de población común de los 11 niveles.

El [control WD con compuerta fallida](results/cases/WD_bad_gate.json) sí conserva LP MODULA y devuelve `INCONCLUSIVE_PARCIAL`: delimita el defecto al tramo anterior al bootstrap, no a toda la implementación.

## F02 — Media operacional: la CLI destruye una salida anterior

[main, línea 246](sources/target/Q13M2/analisis_Q13M2.py#L246) usa `write_text` sin exclusión. El caso [output_collision](results/validation/output_collision.json) crea una tabla sintética N=1, plan/resumen enlazados y la referencia LS autorizada; deja un marcador en `RESULTADO_Q13M2.json` y ejecuta la CLI original. Resultado: código 0, JSON estricto y `output_marker_preserved=false`.

Receta completa en [validation_v1.py](scripts/validation_v1.py), función `cli`; inputs, stdout/stderr y salida externa están inventariados por SHA en [external_manifest.csv](external_manifest.csv), bajo `cli/output_collision/`. No se destruyó ningún resultado real ni se demuestra un error estadístico con este caso; se demuestra pérdida de trazabilidad ante reejecución o error de ruta.

**Corrección propuesta:** creación exclusiva de la salida y rechazo controlado de colisiones, o directorio de versión nuevo explícito; conservar parciales. Agregar una prueba que deje intacto el marcador y no termine con éxito silencioso.

## F03 — Media documental: pruebas archivadas de otros SHA

El [informe del autor](sources/target/Q13M2/PRUEBAS_Q13M2_2026-10-27.md) y su [JSON](sources/target/Q13M2/pruebas_Q13M2.json) registran analista `15ca7b42…`, pruebas `c195ec50…`, 16 reglas puras y un caso de tope N=219. Los archivos auditados son `2e69516e…` y `063c15e4…`; ahora contienen aceptación de 320 y rechazo de 321 y 17 reglas puras. Reproducción mínima: comparar los campos `analisis_sha256`/`pruebas_sha256` del JSON con [provenance.json](sources/provenance.json).

**Qué demuestra:** la evidencia archivada no autentica estos archivos. No demuestra que el autor nunca haya ejecutado las pruebas actuales ni que el cambio de N_MAX haya alterado el estimando.

**Corrección propuesta:** después de resolver los defectos, ejecutar las pruebas contra los SHA finales y publicar un informe/JSON nuevos conservando esta evidencia previa. La auditoría independiente no sustituye esa vinculación documental.

## F04 — Baja numérica: «exactamente» β_LS depende del redondeo

Sobre la única tabla LS permitida y verificada por SHA, la función `referencia_ls` devuelve **0.07692466151365296**, no el literal **0.07692466151365258** exigido por diseño/pruebas. Diferencia absoluta: **3.7470027081099033×10⁻¹⁶**. Se conservan [resultado y bootstrap](results/reference_LS/reference.json).

El [contraste adicional](results/reference_LS/numeric_comparison.json) calcula los seis D mediante `Q.D_punto` y mediante la primaria original C1; ambos vectores son idénticos y producen la misma β observada. El p de ese contraste no se interpreta. No se fuerza el valor a coincidir y no se atribuye sin prueba a una plataforma concreta.

**Corrección propuesta:** reemplazar la igualdad literal por una tolerancia numérica explícita, por ejemplo absoluta 10⁻¹², antes de congelar, registrando entorno y SHA. Esto cambia la prueba de reproducción, no el umbral científico. No modifica β, IC ni estado oficiales de Q13-DR.

## Límites de API y recomendaciones opcionales

- [LS puntual degenerada](results/cases/LS_point_degenerate_API.json): un diccionario LS sintético con L constante da `LinAlgError` antes del bloque que recoge fallos bootstrap. No es un crash CLI demostrado con la tabla de SHA fijo, que es válida. Validación adicional sería endurecimiento opcional.
- [Vectores LS/M2 de longitud distinta](results/api_edges/results.json): `compatibilidad` lanza `ValueError` por broadcasting. La CLI fija ambos en 2000: no es un defecto alcanzable por una tabla admitida bajo el SHA actual. Validar tamaños haría más clara la API.
- El mismo archivo adicional verifica que una réplica de seis niveles con c=.1 constante se rechaza con `FloatingPointError`, conservando la protección de Q13-DR.
- Conservar las réplicas β/D/c y los remuestreos fuera de Git por SHA simplificaría auditorías futuras. Esta auditoría los archiva sin cambiar el productor oficial.

Ninguna de estas recomendaciones se implementó en el analista o diseño ajenos.
