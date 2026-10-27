# DIN-Q13 v2 — avance y pausa por tamaño

Main actualizado tras #97/#98. Diseños y manifiestos SHA íntegros.
f865be3 (receta/configuración v2) publicado antes de calibrar; 218ad79 conserva
900 calibraciones y dosis LS=.005/WD=.2, publicado antes de potencia; 3a56b59
publica código y especificación operativa de potencia antes de simular.

Todas las calibraciones válidas; datos/pesos iniciales/lotes pareados. Sin X/rho
ni asociaciones en calibración. Receta v1 copiada byte por byte y no modificada.
La potencia sólo usa el piloto G3 permitido, fuentes estadísticas por SHA y datos
simulados; nunca estados/cohorte C2 ni una cohorte Q13. Controles numéricos PASS.

El primer tamaño elegible es 800. Los otros seis no cumplen la condición completa.
§6 del diseño exige confirmación si supera 400: publicar y solicitarla en el PR,
deteniéndose antes de plan/compuerta/cohorte. Serían 12.000 trayectorias en tres
brazos. No se entrenó ninguna; semillas de cohorte aún sin usar.

Sin fallos ni enmiendas de implementación. Se conservan todos los resultados y
arrays externos. Diseños, calibración v1, instrumentos y otras etapas intactos.
