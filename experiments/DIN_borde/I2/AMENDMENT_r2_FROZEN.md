# Enmienda congelada r2 · cúspides de velocidad casi de rango uno

Antes de corregir el instrumento y las referencias. La corrida inicial permanece
íntegra en results/run_v1. No cambian estados previos, datos, umbrales ni veredictos
congelados. La corrección del ejecutor v2 fue sólo de impresión; ésta es r2 del
instrumento numérico.

Defecto localizado: en D2/near_collinear/2026102600/random_rank1, GL32 y GL64 MP
sin dividir en ceros difieren 2.998343262e-6. El mínimo por GL12 y la sensibilidad
GL24 difieren 1.607008020e-6, mayor que la tolerancia fijada. La velocidad de rango
uno contiene un valor absoluto: integrar y optimizar una cuadratura fija sobre
sus cúspides crea irregularidades espurias. Es un defecto del esquema numérico,
no evidencia sobre geometría. Los contrastes fallidos se reportarán, sin borrarlos.

Corrección prospectiva fijada:
- Preservar BIT A BIT el instrumento original en versions/r1/rho_borde_v2.py,
  y la referencia original en scripts/references_v1.py. Versionar el instrumento
  corregido en el archivo público rho_borde_v2.py (identificador r2).
- Cuando el principal autovalor del contraste contenga ≥1−1e-10 de la traza
  positiva, la búsqueda rápida usa la variación total del modo principal:
  extremos y ceros de su derivada. Buscar cambios de signo en log s con paso
  ≤.25 (sensibilidad≤.125), brentq xtol1e-12. Conservar los modos restantes
  para la longitud final; se informa su cota conservadora 2g sqrt(lambda_res).
  No se etiqueta esa aproximación rápida como longitud de M exacta.
- En las validaciones quad de M completo, subdividir además en esos ceros.
  Ningún cambio de tolerancia, presupuesto o topología.
- Referencia MP r2 independiente: eigsy MP80 original, sin factor double;
  en el mismo criterio de dominancia, localizar ceros del modo principal por
  malla logarítmica≤.125 y bisección MP hasta1e-35; dividir GL32 y GL64 allí.
  Aplicarlo a los CUATRO casos MP predesignados, sin seleccionar supervivientes.
- Repetir controles, TODOS los302 estados y24 sensibilidades en results/run_r2,
  con arrays fuera de Git en /workspace/work/din-i2-r2-arrays. Reutilizar los102
  comparadores v1 intactos ya medidos en la misma sesión/recursos; registrar
  explícitamente esa reutilización y separar sus tiempos de MP y sensibilidad.
- Conservar código/mediciones r1, resumen de sus fallos y trazas de ejecución.
  Código r2 y su commit precederán las mediciones r2. Si persiste la discrepancia,
  se reportará FAIL/INCONCLUSIVE con la regla original; no se relaja el umbral.

La búsqueda acotada sigue sin certificar mínimo global. La detección por cambios
de signo tampoco certifica encontrar todas las raíces; esa limitación se declara.
