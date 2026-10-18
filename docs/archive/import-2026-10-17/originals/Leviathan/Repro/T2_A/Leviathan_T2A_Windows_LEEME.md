# Leviathan / RIPG — Windows, reanudación desde el paso 91

Paquete para Windows x64, Ryzen 9 3900X y 64 GB de RAM. **No necesita GPU, CUDA, PyTorch ni acceso a ChatGPT durante el cálculo.** La instalación sí necesita internet.

## Qué continúa

Únicamente el ensayo aislado MPFR de `split8_j5_true / update25`, desde el **checkpoint 90**, radio **0.07340076233153377**. El archivo original permanece intacto. No es el paquete para ejecutar las 800 trayectorias ni las 8000 visitas.

La trayectoria científica oficial sigue en el paso512; hay1/8000 visitas completas. Este ensayo todavía no ha validado la calibración completa. El área diagnóstica del prefijo previo,0.01813308845, no es área embebida certificada.

## Instalación y ejecución

1. Extrae **todo** el ZIP en una carpeta, por ejemplo `C:\RIPG\Windows_RIPG_T2A_CP90`. No ejecutes los archivos dentro del ZIP.
2. Necesitas **Python3.12 de64 bits**, incluido el launcher `py`. Si falta, usa el instalador oficial: https://www.python.org/downloads/release/python-31210/ (Windows installer64-bit). También se admite otro parche3.12 x64; el entorno real se registra y debe superar la prueba. No uses Python3.13/3.14 con este paquete.
3. Haz doble clic en **01_INSTALAR.cmd**. Crea un entorno `.venv` e instala las versiones fijadas. No requiere instalación global de los paquetes científicos.
4. Ejecuta **02_PROBAR.cmd**. Compara dos repeticiones aisladas del paso90→91 con la referencia. Puede tardar varios minutos. Debe terminar en **PASS**. Guarda los tiempos en `output/equivalence.json`. Esta prueba no cuenta como avance de la integración.
5. Si pasa, ejecuta **03_CONTINUAR.cmd**. Retoma desde el91 y corre hasta alcanzar el límite de búsqueda0.09, una pausa o un fallo. No inicia entrenamiento ni abre estados nuevos. Para limitar el tiempo, usa **07_LOTE_15_MIN.cmd** en lugar de03.
6. Para detenerlo de forma ordenada, ejecuta **04_PAUSAR.cmd** desde otra ventana. Espera a que termine el paso activo y aparezca `GUARDADO`. También puedes pulsar Ctrl+C una vez en la ventana del cálculo. No cierres esa ventana antes del guardado.
7. Para reanudar, vuelve a ejecutar **03_CONTINUAR.cmd**. No repitas01 ni02 si no cambió el entorno. `06_ESTADO.cmd` muestra el último estado confirmado; úsalo cuando no esté corriendo otra orden.
8. Al pausar o terminar, ejecuta **05_EXPORTAR.cmd**. Crea `RIPG_RESULTADOS_PC.zip`, que puedes adjuntar en el chat. El ZIP contiene los segmentos nuevos y sus hashes, sin volver a incluir el checkpoint90 que ya tenemos.

Si se creó `output/STOP` cuando no había cálculo activo,03 avisará y no iniciará: borra únicamente ese archivo para retirar la solicitud de pausa. No borres checkpoints, índices ni archivos de errores para forzar continuación.

## Qué comprueba la prueba

Se verifican SHA-256 de los archivos del paquete, versiones de dependencias y arquitectura64 bits. Después se ejecuta el paso90→91 dos veces, desde el mismo estado, con el mismo RHS MPFR169 bits, DOP853,2048 rayos, rtol2e−10 y atol2e−12.

La prueba exige el mismo tiempo aceptado y número de evaluaciones que la referencia. Compara el estado final y513 puntos de salida densa con la escala `2e-12 + 2e-10*abs(referencia)` y límite1. No busca ni ajusta parámetros. Un fallo bloquea03; comparte `output/equivalence.json` y el mensaje. No omitas esta compuerta.

El tiempo medido es el de ese paso concreto. No extrapoles directamente a una visita o a toda la cohorte. La GPU no se usa y el código no paraleliza automáticamente los12 núcleos. La ventaja inmediata es poder ejecutar de forma continua.

## Guardado y recuperación

Se guarda cada cuatro pasos aceptados y al pausar. El checkpoint90 es inmutable; cada segmento nuevo también. `output/index.json` se actualiza de forma atómica **después** de guardar y verificar el segmento. Es la autoridad para determinar qué está confirmado. Ante un cierre abrupto, solo se reejecutan pasos posteriores al último segmento confirmado.

Conserva la carpeta completa. El historial se guarda por segmentos para no copiar los90 pasos iniciales en cada guardado. La salida densa ocupa espacio creciente; mantén margen de disco. El programa pausa si quedan menos de512 MiB libres antes de otro paso. No borra resultados automáticamente. Si Windows suspende el equipo, el cálculo deja de avanzar mientras esté suspendido.

## Qué significa terminar

Al alcanzar0.09 se ejecuta la calibración heredada:32 coronas, Dunavant7, objetivo0.02, Brent con xtol1e−13 y tolerancia relativa de área1e−6.

- Si encuentra el área, guarda `calibration.json` y `boundary_calibration.npz`. El estado será **CALIBRATION_COMPUTED_NOT_PRECISION_VALIDATED**, no una validación geométrica final.
- Si el bracket0.09 no alcanza0.02, registra **BRACKET_EXPANSION_PENDING** y el siguiente límite heredado0.1125. Comparte el paquete de resultados para continuar esa compuerta; no disminuyas el área ni cambies el radio manualmente.
- Si falla el integrador, se conserva el último estado aceptado, se registra `failure.json` y se bloquean nuevos intentos hasta revisión. No se clasifica por ello el estado como NUMERICAL_FAILURE o GEOMETRIC_NONINJECTIVITY.

Después siguen pendientes la comparación de mayor precisión y la auditoría de Jacobi/topología. Este paquete no decide outcomes, no sella hipótesis nuevas y no modifica T2-A0.

## Entorno fijado

Python3.12 x64; NumPy2.3.5; SciPy1.17.0; gmpy2 2.3.2; Shapely2.1.2. La referencia se generó en Linux con esas versiones. **No se ha ejecutado Windows aquí**: la prueba02 verifica la compatibilidad numérica en tu máquina antes de habilitar continuación.

Las fuentes geométricas y el campo están copiados sin modificaciones y con hashes. `provenance/` conserva el protocolo, el plan y el código de origen. `portability_plan.json` fija las compuertas de este traslado.

## Pruebas previas del paquete

En Linux pasaron las dos repeticiones de referencia91, el bloqueo sin prueba, la continuación90→91, la reanudación91→92 con igualdad bit a bit, la pausa previa y dos exportaciones verificadas. La evidencia se conserva en provenance/package_qa.json y provenance/linux_qa_results.zip. Esos archivos son evidencia de prueba: no son el estado de ejecución de tu PC. La carpeta output se creará vacía y deberás ejecutar02 allí.
