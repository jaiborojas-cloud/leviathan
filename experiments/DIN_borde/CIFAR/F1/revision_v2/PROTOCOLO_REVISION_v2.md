# Revisión prospectiva de CIFAR F1 v2

2026-10-29, hora de México. Respuesta a la auditoría del PR #127 transmitida por el responsable. **El diseño sigue BORRADOR.** Se registra esta revisión antes del código v2 y de las pruebas; no se modifican ni sobrescriben v1, sus salidas ni sus manifests.

## Cambios solicitados

1. Estratos según la mediana de c250 de cada split usado por la primaria, calculada entre sus trayectorias elegibles. Cortes .4 y .8; empates hacia el estrato superior. Todas las trayectorias elegibles del split permanecen juntas. Reportar número e IDs de splits, IDs de trayectorias y medianas por split. Mantener el mínimo de 20 splits con ≥ 3 elegibles y el carácter secundario.
2. «Longitud» en las tolerancias de auditoría significa el valor de ρ del ganador correspondiente. `quad_error = None` es inválido; no equivale a cero. Esta era ya la validación de v1: la aclaración no cambia sus umbrales ni el validador.
3. Corregir espacios y legibilidad en todo el documento v2. Se conserva la v1 histórica sin retocarla.
4. El watchdog de 120 s es un requisito del futuro productor, no una interrupción implementada por el analista de CSV.

La primaria, las semillas, las opciones rho, los estados, la inclusión, el esquema de columnas y F2 no cambian. El plan v2 añade la regla explícita `c_strata_assignment = split_median_c250_primary_eligible`; el resto solo cambia el identificador de versión. Se crearán `analisis_F1_v2.py` y `pruebas_F1_v2.py`, sin editar los originales.

## Pruebas fijadas antes del código

- Repetir los 54 casos sintéticos de v1 contra v2, con las mismas semillas, 20 tablas independientes, C1 directo y una CLI de 5.000 permutaciones. Primaria idéntica a v1 en las mismas filas y planes propios.
- Split con c individuales que atraviesan ambos cortes: sus cinco trayectorias deben quedarse en el estrato de su mediana. Comparar con un agrupamiento independiente por split y confirmar que cada split aparece una sola vez y se mantienen todos los IDs elegibles.
- Medianas exactamente .4 y .8, c = 1 y medianas de 3 o 4 elegibles con c inválidas o rho fallida fuera de ese conjunto. La mediana par usa el promedio de los dos centrales. No contaminar la primaria ni imputar.
- Estratos con 19 frente a 20 splits, con conteos y listas explícitas aun si son NO_DEFINIDO. Un split con menos de 3 elegibles no se asigna a estratos; debe reportarse fuera del conjunto de primaria.
- `quad_error = None`, vacío, NaN, infinito o negativo en cada ganador: inválidos. Cada error se compara con la longitud de su propio ganador. Umbrales relativos exactos de 1e−6, tanto cuadratura como prefijo y cola, con ejemplos que diferencien ρ_caras de ρ_vert.
- Comparación AST del analista v1/v2: solo cambian versión, plantilla del plan, asignación y reporte de los estratos. Las funciones de primaria, validación rho, integridad, preparación, CLI y semillas deben permanecer idénticas salvo referencias explícitas de versión.
- Conservar todas las salidas nuevas por separado y publicar manifest por SHA. Pruebas, fixtures y exportación usarán nuevas rutas; nombres de resultados portables en Windows desde el inicio, sin renombrar los casos originales ni tocar v1.

Sin imágenes, descargas, entrenamiento, geometría ni análisis de cohortes reales. No se repite Monte Carlo de tamaño o potencia. Un fallo inesperado se conserva; cualquier corrección se documenta y compromete antes de nuevo código y una nueva corrida.
