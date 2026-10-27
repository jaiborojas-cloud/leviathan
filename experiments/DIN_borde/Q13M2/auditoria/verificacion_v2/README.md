# DIN-Q13-M2: verificación independiente v2

[Conclusión](CONCLUSION.md), [matriz](MATRIZ_VERIFICACION.md), [hallazgos nuevos](HALLAZGOS_NUEVOS.md). F01–F04 funcionalmente resueltos; N01 pide conservar los motivos de todos los niveles fallidos y N02 armonizar dos frases del diseño. No se demostró cambio incorrecto de veredicto en los casos probados.

## Fuentes y conservación

- [DESIGN_FROZEN.md](DESIGN_FROZEN.md): diseño de esta verificación, no congelación del confirmatorio.
- [sources/provenance.json](sources/provenance.json): objetivo `ac63574f`, analista `512737dd…`, pruebas `6e7b836c…`, base y SHA de todos los snapshots.
- [sources/analista_v1_v2.diff](sources/analista_v1_v2.diff): diff exacto revisado.
- [sources/auditoria_v1/CONCLUSION.md](sources/auditoria_v1/CONCLUSION.md): copia por SHA de la referencia #117; sus enlaces internos corresponden a la entrega original.
- [regression_matrix.json](regression_matrix.json): comparación de los23 casos originales,19 iguales y4 correcciones esperadas.
- [verification.json](verification.json):63 comprobaciones, `PASS_VERIFICATION_WITH_FINDINGS`; no es autorización para congelar.
- [verification_publicacion.json](verification_publicacion.json), [manifest.csv](manifest.csv), [manifest.sha256](manifest.sha256): integridad de la entrega.
- [external_manifest.csv](external_manifest.csv): array de referencia y fixtures CLI fuera de Git, incluidos enlaces simbólicos por SHA de su destino textual.

Solo se añaden archivos en esta subcarpeta. La auditoría #117 permanece en el commit `8115a912` y su rama. Se incluyen sus fuentes/salidas seleccionadas como snapshots para que este PR sea independiente de su fusión. No se incorporan ni reejecutan sus800 simulaciones.

## Ejecución reproducible

Python3.12.14, [dependencias](requirements.txt), [entorno registrado](environment.json), un hilo BLAS. Semillas y presupuestos en [config.json](config.json); los campos Monte Carlo heredados del config anterior son solo contexto, no se ejecutan.

```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
python experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts/static_v1.py
python experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts/cases_v1.py
python experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts/changed_cases_v1.py
python experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts/reference_LS_v1.py
python experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts/cli_v1.py
python experiments/DIN_borde/Q13M2/auditoria/verificacion_v2/scripts/verify_v1.py
```

Los scripts escriben en exclusiva. Para una reproducción, partir de una copia limpia de la implementación anterior a resultados con una ubicación externa vacía; no borrar ni sobrescribir esta entrega. Cualquier ajuste de rutas se registra como réplica nueva conservando semillas y criterios. La guarda exige código comprometido y fuentes por SHA. Los arrays no implican almacenamiento remoto permanente: se regeneran con el código y se cotejan por SHA en un entorno idéntico.

`cases_v1.py` y `reference_LS_v1.py` son copias byte a byte de #117, usando soporte con rutas y objetivo v2. B39/NB64 son controles de flujo, NB32 traza, NB300 fallos bootstrap; la referencia LS usa2000. La CLI con marcador/directorio ejecuta directamente el analista original. Los otros tres casos CLI usan [inyección en memoria](scripts/cli_injection_v1.py), presupuestos B39/NB64 y una excepción LS explícita; lo declaran en su JSON. No modifican la fuente ni se confunden con un fallo de la tabla LS real.

## Orden comprometido

1. `cbcbef1f`: diseño y snapshots antes de código/medición.
2. `47d6186b`: casos y controles antes de ejecutarlos.
3. `a09ea035`: integración/verificación antes de ejecutarla.
4. Informes, logs, manifests y publicación en PR aparte, borrador sin fusión.

Sin entrenamiento, cohortes restringidas ni datos reales nuevos; única referencia real, LS publicada de Q13-DR autorizada. Sin cambios de diseños/analistas/cierres previos. La aprobación pertenece al responsable.
