# Pruebas de CIFAR F1 · revisión v2

2026-10-29, hora de México. **71/71 PASS:** se repitieron los 54 casos anteriores contra el analista v2 y se añadieron 17 controles prospectivos. Sin imágenes, entrenamiento, geometría ni cohortes reales. No se repitió Monte Carlo de tamaño o potencia.

- Analista SHA: `0c4d03b539fce2c115580c2928c6f5b9470e8b4b121c45c13b054a3934b9eb27`.
- Pruebas SHA: `6b8a7f127b5f04da7f59ed29fc1c39c3f048e943c5708276ffad3097bf0e868b`.
- Plan v2 SHA: `a2e8c01d5bc9207a1e06a845b80dc643f41fcd0460f0dfbaebdccf3000446bb8`.
- Las 20 tablas independientes conservan exactamente la primaria y el veredicto de v1; frente al cálculo independiente, error máximo de D = `3.3306690738754696e-16` y p idéntico. También se reprodujeron C1 directo y la CLI con 5.000 permutaciones.
- AST: primaria, inclusión, validador rho, integridad, CLI y semillas sin cambios. Solo se añadió el agrupamiento por split, se sustituyó el secundario de estratos y se actualizaron las referencias de versión y plantilla.

## Cambios comprobados

| Caso | Resultado |
|---|---|
| c individuales atraviesan .4 y .8 | Cada split conserva sus cinco trayectorias; 33/34/33 splits y 165/170/165 trayectorias en bajo/intermedio/alto. Asignación igual a un cálculo independiente por split; sin IDs repetidos o perdidos. |
| Medianas exactamente .4 y .8; c = 1 | Empates hacia el estrato superior; se reportan también el estrato vacío y sus conteos. |
| Splits con 3 o 4 elegibles | Medianas solo entre elegibles; la mediana par usa los dos centrales. Un split con 2 elegibles queda fuera de la primaria y de los estratos, y se identifica explícitamente. |
| 19 frente a 20 splits | NO_DEFINIDO frente a DESCRIPTIVO, conservando número e IDs de splits y trayectorias. La primaria no cambia. |
| Quad_error nulo, vacío, NaN, infinito o negativo | Rechazo en ambos ganadores sin imputar cero; mismos resultados primarios que v1 ante esos datos inválidos. |
| Tolerancias por longitud del ganador | Se acepta el límite relativo y se rechaza el exceso de una ULP; el error de caras usa ρ_caras y el de vértices usa ρ_vert, también si difieren por un factor 10. |

[Resumen](pruebas/summary.json), [índice de los 71 casos](pruebas/indice_casos.csv), [log](pruebas/console.log), [manifest externo](pruebas/external_manifest.csv) y [verificación](verification.json). Todos los resultados nuevos están separados de v1, cuyos 75 miembros y manifiestos permanecen intactos. Los nombres nuevos son portables en Windows; estas pruebas se ejecutaron en Linux, no se afirma validación nativa de Windows.

El watchdog externo de 120 s es un requisito del productor futuro. El analista y estas pruebas solo verifican el tiempo declarado y el tratamiento de timeout como falta de medida. No se implementó ni probó aquí una interrupción real de rho. Ninguna prueba autoriza congelar o entrenar F1.
