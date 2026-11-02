# A1/A2 · primaria robusta DIN v1

**BORRADOR para auditoría de Claude**, conforme a la [especificación adoptada](../PRIMARIA_ROBUSTA_v1.md). Solo diseños nuevos; ningún estado previo cambia.

- **A1:** [analista genérico](analisis_robusta_v1.py), [contrato](DISENO_ANALISTA_BORRADOR_v1.md), [interfaz/CSV/CLI](INTERFAZ_v1.md) y [configuración](config_BORRADOR_v1.json).
- [Pruebas actuales v1.1](pruebas_robusta_v1_1.py): **58/58 PASS**, [reporte](PRUEBAS_v1_1.md), [verification.json](verification.json). NO_APRENDIO, L con |z| > 10, equivalencia exacta C1 sin recorte, influencia y cuatro veredictos. Sin simulación de tamaño o potencia.
- [Pruebas v1 conservadas](pruebas_robusta_v1.py): 56/57, fallo del fixture archivado; [enmienda previa](ENMIENDA_PRUEBAS_v1_1.md). El analista no cambió. Resultados comunes idénticos en las dos corridas.
- **A2:** [dos opciones breves](OPCIONES_SIGUIENTE_EXPERIMENTO.md), con pregunta, coste orientativo del PC, riesgos y aplicación de A1. Sin nueva cohorte ni elección por el agente.
- [Fuentes y SHA](fuentes/provenance.json), [reparto PR #130](fuentes/reparto_PR130.md), [progreso](progress.md), [manifest](manifest.sha256). PR #130 estaba pendiente de fusión al leerlo, snapshot de `f45e320a`.

## Reproducir pruebas y revisar

Python 3.12 y [requisitos](requirements.txt). Las salidas son exclusivas: usar una copia anterior a resultados o rutas vacías declaradas para una reproducción, sin borrar las corridas archivadas.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -I experiments/DIN_borde/primaria_robusta/pruebas_robusta_v1_1.py
```

Los fixtures, arrays y salidas CLI se conservan fuera de Git en `/workspace/work/din-robusta-pruebas-v1` y `/workspace/work/din-robusta-pruebas-v1_1`; cada corrida conserva su manifest externo. Se cargó solo código C1 por SHA, nunca sus datos o su wrapper de cohorte. La CLI del borrador bloquea datos reales; no se incluyen productores ni dependencias de red. Las pruebas se ejecutaron en Linux; no se promete validación nativa Windows.

Antes de congelar, Claude debe revisar las convenciones explícitas y los límites del [reporte](PRUEBAS_v1_1.md). El primer diseño nuevo deberá fijar universo, productores, compuerta y potencia, y congelar esta implementación tras la auditoría. Un PASS frente a esta base no prueba información condicional frente a cualquier función de L, causalidad ni robustez universal. La compuerta añade exactamente D_sin_max > 0, sin inventar otro umbral de fracción dominante.
