# Cierre basal: extensión operacional de 8 a 9 auditorías

Se ejecutan las nueve trayectorias pendientes en orden de cohorte, en lotes 4+4+1, mediante final_nine_baselines.py. Únicos cambios respecto de bounded_session.py: límite y aserción del número pendiente (8→9), y descripción. Se conservan exactamente las funciones científicas, cuatro trabajadores como máximo, guardado individual y verificación tras cada lote. Ningún cambio numérico ni de selección científica. No se abre seguimiento futuro ni se sella automáticamente el predictor.
