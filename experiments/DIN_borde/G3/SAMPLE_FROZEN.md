# DIN-G3 · tamaño de cohorte congelado antes de entrenar

Diseño7bce1dc → código potencia3f01bc7 → simulación/controles → ESTE commit.
No se generó ni entrenó ninguna cohorte G3. La tabla G2 se usó sólo como piloto.

**N=100 splits por nivel;500 trayectorias por nivel;1500 entrenamientos y10500 visitas.**
Se aplica el PRIMER tamaño válido de la secuencia congelada, sin entrenamiento piloto nuevo.

| s | potencia .015 | potencia .020 | potencia .026 | límite inferior95% .026 | falsos PASS nulo |
|---:|---:|---:|---:|---:|---:|
|0.25|0.6975|0.8050|0.9050|0.8723|0.0300|
|0.5|0.6400|0.8025|0.8925|0.8583|0.0175|
|0.8|0.6700|0.7925|0.8900|0.8555|0.0250|

400 réplicas por nivel/efecto,1999 permutaciones cada una; cuatro soportes
bootstrap del piloto. Todos los límites inferiores para.026≥.8 y los
superiores Wilson del nulo≤.10. No se probaron tamaños mayores.
Control de cuatro tablas FWL vs fuente C1: PASS, p idéntica yD≤1e-10.
Potencia condicional al ruido Gaussiano y soporte piloto; no garantiza
potencia real ni ausencia de efectos menores. D_obj es oráculo; elD CV
medio finito se publica por separado en power_table.csv.

Semillas nuevas: datos511000..511099; pesos521000..521499;
lotes531000..531499. Ninguna coincide con las de G2.

SHA config.json: b5042380a1c6c56adf84820ff07504412583480d322d7ec8e11418e621c31637
[Diseño](DESIGN_FROZEN.md) · [potencia completa](results/power_v1/summary.json) ·
[tabla potencia](results/power_v1/power_table.csv) · [controles](results/power_v1/controls.json).
