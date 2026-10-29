# Pruebas sintéticas del borrador CIFAR F1 v1

**54/54 PASS**, sin fallos inesperados. No se ejecutaron imágenes, entrenamiento, geometría ni cohortes reales. Son pruebas del software, no resultados de F1 ni una validación nominal de potencia/tamaño.

- Analista SHA `f34a6506037de591fd70046c5f91d95ff00695e6582912dc83e834b4c2c952a0`.
- Pruebas SHA `993f897bb6b24b103c771e1752310e9310415a956ec05d2dd61294901e593cf9`.
-20 tablas independientes: error máximo de D `3.3306690738754696e-16`, p idéntico con las mismas permutaciones. Incluyen coeficientes negativos, cero y positivos; no se exige un veredicto inferencial a cada nulo aleatorio.
- Equivalencia exacta con llamada C1 por SHA y prueba CLI nominal con5000 permutaciones.
- Límites25/26 faltantes, X/L/Y constantes y saturación, c=1/panel erróneo sin filtro, fallos5 sin contaminación, presupuesto/timeout/auditoría rho, dominios múltiples sin log inválido, estrato pequeño, IDs/visitas/hash f, plan y metadatos.
- CLI: JSON estricto, salida inicial/final exclusiva, lecturas ausentes/directorio/SHA incorrecto/JSON inválido y bloqueo de tipo real mientras el plan es BORRADOR.

[Resumen](pruebas/publicacion_v1/summary.json), [índice de54 casos](pruebas/publicacion_v1/indice_casos.csv), [manifest externo](pruebas/publicacion_v1/external_manifest.csv). Las copias publicadas son byte a byte de los resultados crudos; [enmienda de empaquetado](ENMIENDA_PUBLICACION_v1.md) y mapeo conservan los nombres originales no portables. No se modifica ni repite una prueba para publicarla.
