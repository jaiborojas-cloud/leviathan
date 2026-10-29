# DIN-CIFAR F1 — borrador para auditoría

**Diseño y analista BORRADOR; ninguna cohorte F1 medida y ningún permiso de ejecución implícito.** [Diseño completo](../DISENO_CIFAR_F1_BORRADOR_v1.md), [esquema CSV/enlaces](ESQUEMA_TABLA_v1.md), [plan propuesto](plan_F1_BORRADOR_v1.json), [analista](analisis_F1_v1.py), [pruebas](pruebas_F1_v1.py), [reporte de pruebas](PRUEBAS_F1_v1.md).

## Propuesta fijada para revisar

-100 splits×5,500 IDs y2.000 filas por visita. Semillas F1:1.100.000/1.110.000/1.120.000, con +s/+5s+k; F2 reserva1.200.000/1.300.000/1.400.000 sin fijar N. Rangos nuevos respecto a F0/F0b/F0c. No se afirma independencia de imágenes entre particiones de un mismo CIFAR finito.
- Configuración vigente de v2, lr=.003 pasado explícitamente. El módulo sistema conserva el default=.001 para reproducir F0; no se modifica. f PCA por split fija, cabeza reducida perro y fuentes congeladas por SHA.
- Primaria sobre rho_caras: C1 exacto, centrado intra-split, grado3,10 bloques260010,5.000 permutaciones260001, sin cambiar semillas para este dataset. PASS_DESCRIPTIVO si D>0,p<.05,pendiente>0; no es confirmación.
- Sin filtrar por c ni precisión. Más25/500 faltantes, menos80 splits con≥3, variación insuficiente o integridad/ajuste fallidos: INCONCLUSIVE, nunca «ausencia de señal». Libro completo de causas por visita.
- Rho r3 con defaults explícitos60s de pared/4096 evaluaciones, watchdog externo120s propuesto, sin reintentos. Candidatos parciales o rho inválidos no se logaritman ni se imputan. El watchdog pertenece al futuro productor, no a este analista de CSV.
- X5/X30/R, c/q y precisiones/CE registradas sin redefinir la primaria. rho_vert, grado5, X5/X30, mitades y estratos c250(0,.4)/[.4,.8)/[.8,1] como secundarios sin p adicionales; los estratos no son intervenciones Q13-DR/M2 ni prueban causalidad.

## Código y contrato

`analisis_F1_v1.py` carga únicamente el código C1 SHA `8711f468…`; no su wrapper de cohortes, ni datos Wine, ni CIFAR, pesos o geometría. Usa numpy/scipy. Valida el plan contra el prototipo por SHA; al congelar, el mismo contenido científico con estado CONGELADO es aceptado. Cualquier otro cambio científico requiere una nueva versión auditada, no editar el prototipo silenciosamente.

La CLI exige estos argumentos:

```text
--tabla --tabla-sha --plan --plan-sha --resumen --compuerta --compuerta-sha --productor-sha --dataset-sha --out
```

Los SHA de productor y dataset vienen de la publicación previa del productor, no de inferirlos al mirar resultados. Tabla larga y resumen se definen en el esquema. La compuerta es el JSON original con9 checks y fuentes/versiones, no la transcripción F0/F0b. La CLI no admite cambiar5000 permutaciones. Plan BORRADOR solo admite tipo PRUEBA_SINTETICA; tipo real requiere CONGELADO. Salida exclusiva `RESULTADO_CIFAR_F1.json`, siempre modo DESCUBRIMIENTO, JSON estricto y registro de datos no usados/faltantes.

F1 se usa para proponer hipótesis y potencia conservadora de F2. No produce un tamaño F2, un productor, un resultado confirmatorio, ni justifica retocar clases/red/lr tras observar señal. La aprobación y congelación quedan pendientes del responsable y auditoría independiente.

## Pruebas y conservación

[Protocolo de pruebas previo al código](PROTOCOLO_PRUEBAS_SINTETICAS_v1.md), comprometido junto al borrador en `0b51b875`; analista/pruebas antes de ejecutarse en `09e5bfa1`. Solo sintéticos:54 controles PASS,20 tablas contra OLS independiente, C1 directo y CLI con5000. Sin imágenes, entrenamiento, geometría o cohortes reales. No se estimó tamaño nominal/potencia mediante Monte Carlo.

Desde una copia limpia anterior a resultados, con [requisitos](requirements.txt):

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python -I experiments/DIN_borde/CIFAR/F1/pruebas_F1_v1.py
```

Las salidas se crean en exclusiva. No borrar la corrida archivada para repetirla; una reproducción requiere ubicaciones vacías y una nueva versión/ruta declarada. Resultados crudos locales en `pruebas/results_v1/`, publicados sin cambios de bytes con nombres portables e índice en [pruebas/publicacion_v1](pruebas/publicacion_v1/). Se conserva una [enmienda de empaquetado](ENMIENDA_PUBLICACION_v1.md) para un nombre con dos puntos, sin cambiar el analista ni repetir pruebas. Fixtures y salidas CLI sintéticos fuera de Git por manifest.

## Fuentes y entrega

El [provenance](fuentes/provenance.json) fija main `77ff8376`, versiones/fuentes y el snapshot F0b de PR126 `679654e5`, pendiente al leerlo. No se altera su estado ni se inventa SHA del resumen original del responsable. Se leyeron solo informes/código, no estados de factibilidad.

[verification.json](verification.json), [manifest.csv](manifest.csv) y [manifest.sha256](manifest.sha256) verifican la entrega, no congelan el estudio. Las pruebas no prueban ausencia universal de defectos ni sustituyen la auditoría solicitada.
