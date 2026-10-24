# Ejecución principal y corrección de instrumentación

343be81 congela fase0 antes de ba3bb43 (código). 4fbdaca/91cc1a2 congelan
principal antes de b6cbb89 (código). No geodésicas antes de congelación principal.
V1:VALID_EXPLORATORY,20 controles PASS,4 contrastes MP de rayos PASS,
30 bloques numéricos de índice0 y6 objetivos censurados. Q1/Q2/Q3 INCONCLUSIVE.
No conjugados ni cruces propios antes de censura; todos los rayos salen del
dominio. rdeg y Adeg UNKNOWN. r_safe=.66580874,A_safe=1.40366931.

Defecto del puente v1: fraction_at_fixed=.623046875 sólo incluyó cobertura
individual/Jacobi. No permite afirmar ausencia de colisiones con trayectorias
censuradas. Se conserva v1 íntegra y se congela reproceso v2 antes del código,
sin reintegrar rayos ni alterar reglas geométricas. También se añade primer
candidato de colisión por rayo, con incertidumbre de segmentos incidentes.
