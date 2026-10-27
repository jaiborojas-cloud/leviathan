# Cierre de mediciones de auditoría

Diseño7ef4d67 antes de códigobededc3 y de cualquier medición. Casos v1 preservados;
extensión v2 y confirmación N200 congeladas antes de sus respectivos scripts y
ejecuciones. No se cambió el motor/configuración Monte Carlo durante sus1.400
réplicas. No hubo fallos del motor, redibujos ni exclusiones.

Defectos de objetivo reproducidos: L degenerada en bootstrap (crash), población
c observada distinta de la de bootstrap (incluido IC NaN con compuerta válida),
plan sin validar eps/esquema, Spearman con empates y clasificación de crashes por
substring en las pruebas. Se conserva la etiqueta CLI heurística inicial del
auditor; la extensión v2 identifica el traceback real y no reescribe resultados.

La comparación de la revisión nueva78a7d2e confirma analista/diseño/referentes
idénticos; sólo cambia un float en repr del generador de pruebas. Tasas nominales
completas y artefactos conservados. La evidencia no muestra inflación global de
falsos MODULA en los dos nulos principales, pero NO_MODULA no ocurre en400 réplicas
por tamaño. No extrapolar a otras dependencias; el responsable decide los cambios.

Sólo datos sintéticos, sin Wine/C2/Q13 reales, sin entrenamiento ni geometría.
Código original, diseño, estados y resultados de otras etapas sin modificaciones.
Entrega final: fuentes por SHA, casos, tasas globales/condicionadas y extremos,
defectos/correcciones propuestas, verificación, arrays externos y PR separado.
