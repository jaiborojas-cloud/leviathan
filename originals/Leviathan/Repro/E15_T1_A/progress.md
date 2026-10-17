# E15-T1-A — progreso recuperable

Completados: 80/80. Pendientes: 0.

C1-A permanece INCONCLUSIVE. Clasificaciones T1-A: {"INJECTIVE_AT_NOMINAL_RADIUS": 78, "GEOMETRIC_NONINJECTIVITY": 2, "NUMERICAL_FAILURE": 0, "INCONCLUSIVE": 0}.

Integridad: C1 1925/1925; checkpoints80/80; A2 581/581; CRC ambos PASS. Reconstrucción M/f80/80 PASS. SHA ZIP en input_integrity.json.

Protocolo: protocol_T1_A_frozen.json SHA256 6081c1e2517ddf2ff02457b361894bd508889aec13e8fd37b0a9e9a45a02fc6c. P0=(0,0), rho=1e-4, área0.02, radios C1 intactos, DOP853 rtol2e-10 atol2e-12. Compuertas y presupuestos congelados antes del nuevo screening.

Última tarea completamente terminada: split7_j4_true.

Reanudar: materializar estos archivos y ZIP por estado en la misma carpeta; extraer cada ZIP para obtener states/<id>. Recuperar fuentes de los ZIP C1/A2 verificados, ejecutar setup.py sólo si faltan insumos y reconstruct.py si faltan comprobaciones. Ejecutar python3 run_map.py; los result.json válidos se omiten. No regenerar un resultado confirmado. Los pendientes no cuentan como INCONCLUSIVE completado. Las identidades/versiones se conservan en persistence_receipts.json local; si nueva sesión, recuperar identidades actuales por búsqueda antes de guardar.

Pendientes:


Completados:
split0_j0_random, split0_j0_true, split0_j1_random, split0_j1_true, split0_j2_random, split0_j2_true, split0_j3_random, split0_j3_true, split0_j4_random, split0_j4_true, split1_j0_random, split1_j0_true, split1_j1_random, split1_j1_true, split1_j2_random, split1_j2_true, split1_j3_random, split1_j3_true, split1_j4_random, split1_j4_true, split2_j0_random, split2_j0_true, split2_j1_random, split2_j1_true, split2_j2_random, split2_j2_true, split2_j3_random, split2_j3_true, split2_j4_random, split2_j4_true, split3_j0_random, split3_j0_true, split3_j1_random, split3_j1_true, split3_j2_random, split3_j2_true, split3_j3_random, split3_j3_true, split3_j4_random, split3_j4_true, split4_j0_random, split4_j0_true, split4_j1_random, split4_j1_true, split4_j2_random, split4_j2_true, split4_j3_random, split4_j3_true, split4_j4_random, split4_j4_true, split5_j0_random, split5_j0_true, split5_j1_random, split5_j1_true, split5_j2_random, split5_j2_true, split5_j3_random, split5_j3_true, split5_j4_random, split5_j4_true, split6_j0_random, split6_j0_true, split6_j1_random, split6_j1_true, split6_j2_random, split6_j2_true, split6_j3_random, split6_j3_true, split6_j4_random, split6_j4_true, split7_j0_random, split7_j0_true, split7_j1_random, split7_j1_true, split7_j2_random, split7_j2_true, split7_j3_random, split7_j3_true, split7_j4_random, split7_j4_true

PASS de integridad y reconstrucción; FAIL de estas compuertas:0. Compuerta poblacional: 80 clasificados; revisar cierre y persistencia final.

## Cierre confirmado

T1-A PASS como mapa observacional:80/80, 0 pendientes;78 INJECTIVE_AT_NOMINAL_RADIUS,2 GEOMETRIC_NONINJECTIVITY,0 NUMERICAL_FAILURE,0 INCONCLUSIVE. True38/2; random40/0.

Última tarea completamente terminada: auditoría final80 checkpoints,80 ZIP de estados persistidos y780 arrays finales PASS. Se corrigió únicamente selección de temporales del postprocesador en tres estados, sin cambiar tareas ni integrar otra vez. Ver postprocess_recovery.json y resultados anteriores retenidos.

T1-B poblacional no abierto: sólo los dos positivos A2 conocidos. Serie específica propuesta; aún no ejecutada. C1-A permanece INCONCLUSIVE. C2 no abierto.

Ningún estado necesita recalcularse. Los scripts y resultados completos acompañan este cierre. Las asociaciones son descriptivas; censura en38 true y40 random al área nominal0.02. No existe certificado global de inyectividad.
