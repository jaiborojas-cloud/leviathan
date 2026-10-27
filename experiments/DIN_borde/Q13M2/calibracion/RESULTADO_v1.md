# DIN-Q13-M2 — calibración v1

**7000/7000 ejecuciones medidas; 0 fallidas.** Solo c250, q250, acc_panel250. No se seleccionan dosis confirmatorias.

| Brazo | Dosis | Mediana c250 | IC95 mediana c | Mediana q250 | Mediana acc_panel250 | Fracción c≤.70 | medidas/fallos |
|---|---:|---:|---|---:|---:|---:|---:|
| A0 | 0 | 0.863802 | [0.820919, 0.912983] | 0.000099 | 0.925926 | 0.306000 | 500/0 |
| LP | 0.0001 | 0.687607 | [0.640756, 0.742880] | 0.000157 | 0.925926 | 0.520000 | 500/0 |
| LP | 0.0003 | 0.620666 | [0.579502, 0.677469] | 0.000192 | 0.925926 | 0.590000 | 500/0 |
| LP | 0.001 | 0.540733 | [0.489463, 0.588227] | 0.000238 | 0.925926 | 0.704000 | 500/0 |
| LP | 0.003 | 0.467836 | [0.434954, 0.501101] | 0.000293 | 0.925926 | 0.824000 | 500/0 |
| LP | 0.01 | 0.374794 | [0.340142, 0.393950] | 0.000385 | 0.888889 | 0.948000 | 500/0 |
| LP | 0.03 | 0.257156 | [0.239044, 0.275205] | 0.000517 | 0.888889 | 0.996000 | 500/0 |
| LP | 0.1 | 0.153233 | [0.144151, 0.161080] | 0.000830 | 0.888889 | 1.000000 | 500/0 |
| LP | 0.3 | 0.086499 | [0.084503, 0.088900] | 0.001292 | 0.888889 | 1.000000 | 500/0 |
| WD | 0.2 | 0.761418 | [0.709369, 0.821121] | 0.000138 | 0.925926 | 0.424000 | 500/0 |
| WD | 0.5 | 0.713577 | [0.658414, 0.770102] | 0.000165 | 0.925926 | 0.486000 | 500/0 |
| WD | 1 | 0.666695 | [0.606401, 0.742663] | 0.000210 | 0.925926 | 0.536000 | 500/0 |
| WD | 2 | 0.578280 | [0.530374, 0.642322] | 0.000323 | 0.925926 | 0.646000 | 500/0 |
| WD | 4 | 0.437884 | [0.401011, 0.492626] | 0.000578 | 0.925926 | 0.840000 | 500/0 |

## Criterios exactos del §5

| Manipulador | C1 monotonía | C2 rango y precisión | C3 precisión si c≥.55 | Resultado |
|---|---|---|---|---|
| LP | cumple | cumple | cumple | ELEGIBLE |
| WD | cumple | cumple | cumple | ELEGIBLE |

LP: inversiones adyacentes=[]; dosis que testimonian C2=[0.01, 0.03, 0.1, 0.3]; violaciones C3=[].

WD: inversiones adyacentes=[]; dosis que testimonian C2=[4.0]; violaciones C3=[].

Bootstrap percentil de 2000 remuestreos de 100 splits completos con sus cinco k, semilla 904001. Draws compartidos entre condiciones. No son intervalos entre trayectorias independientes ni pruebas confirmatorias de monotonía. Comparaciones exactas con valores sin redondear; las cifras de esta tabla solo se redondean para leer.

Tiempo total de medición y resumen: 1000.161s; dos procesos de un hilo. Código publicado antes de medir en 16139f48. Fuente de protocolo SHA: 08551c5810d0c9d65c20e6adf193fed04c195def5cacedd44b9144731f3f7a15.

Las dosis testigo de C2 son evidencia de un criterio, no elecciones para el confirmatorio. La regla de interpolación y cualquier selección corresponden al diseño posterior y al responsable. No se interpoló, amplió rejilla ni calcularon asociaciones. Las dos calibraciones Q13 anteriores permanecen intactas.

[Tabla completa](results_v1/calibracion.csv) · [resumen íntegro](results_v1/summary.json) · [controles](results_v1/controls.json) · [pareado](results_v1/pairing.json) · [verificación](verification.json) · [arrays por SHA](external_manifest.csv).
