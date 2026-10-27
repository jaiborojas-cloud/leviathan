# DIN-Q13 — cohorte bajo protocolo v2

**Pausa obligatoria para confirmar N=800 (12.000 trayectorias)** antes de crear
plan y entrenar. Ninguna trayectoria confirmatoria se ha iniciado; C2 intacta.

La calibración v2 tiene 900/900 ejecuciones válidas y cero errores. Dosis mínimas
elegibles: **LS ε=.005, WD λ=.2**; mediana c250=.609784 y .675014 respectivamente,
con precisión mediana .925926 igual a A0. Sólo se midieron c, q y precisión.

La potencia simulada recorre la rejilla congelada y selecciona 800 como primer
tamaño con ambos límites inferiores Wilson95 ≥.8. Se conservan las siete celdas,
400 réplicas por tamaño, 500 bootstrap por réplica y sus controles PASS. No es una
garantía universal de potencia para los manipuladores.

- [Calibración y tabla de dosis](RESULTADO_CALIBRACION_v2.md).
- [Potencia y motivo de la pausa](potencia_v2/RESULTADO_v1.md).
- [Procedimiento](PROCEDIMIENTO_v2.md) · [configuración](config_v2.json).
- [Verificación v2](verification_v2.json) · [publicación por SHA](PUBLICACION_v2.sha256).
- [Manifiesto de añadidos v2](manifest_v2.csv).

El [diseño v1 §6](../../DISENO_DIN_Q13_v1_CONGELADO.md), conservado en v2, exige
confirmación si N>400. Hasta recibirla no hay q13_plan.json, q13_cohorte.csv ni
RESUMEN_q13.json. Faltantes confirmatorios por brazo: no aplica, universo aún no
publicado. Todos los archivos v1 quedan intactos; las nuevas salidas son aditivas.
