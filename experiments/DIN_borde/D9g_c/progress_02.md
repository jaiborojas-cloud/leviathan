# DIN-D9g-c: cierre exploratorio

Diseño d5e694a → código db6687d → controles 6d2852d → mediciones → documentación
18be491 → archivo final y publicación. Se preservan diseño, fuentes y código.
No hubo fallos de implementación ni enmiendas; no se sobrescribieron salidas.

Los 1.500 registros previstos están completos. En s=.8, D_base(B1)=.07512570 y
D_base(BR)=.07164647: diferencia .00347923 < .005, BR decide. Con el candidato
residualizado elegido antes del diseño, D_BR=−.00495214, p=.653 y pendientes
negativas en ambas mitades; lectura REDUNDANTE_EXPLORATORIO. Se propone Q13 al
responsable sin ejecutarlo. El agregado recae en B1 y no rescata la primaria.

Verificación PASS: fuentes por SHA, cronología, B1 reproducida, 999 permutaciones,
10.000 selecciones externas por conjunto, nueve arrays externos conservados.
Controles negativos D_BR=0; positivos grande y pequeño detectados. Una realización
positiva pequeña no prueba potencia suficiente. Contrastado el pipeline vectorizado
con cálculo directo y selección sin caché. No se cambió la regla de adecuación.

Sólo se añaden archivos en D9g_c. No se leyeron datos de C2, T2, DIN-C1, Wine o
Iris; no se generó ni reevaluó test ni se entrenó. Las copias de D9g/D9g-b son
fuentes archivadas, no modificaciones de etapas previas. Logs, tiempos, entorno,
estimaciones, figura, manifiestos y verificación quedan disponibles para revisión.
