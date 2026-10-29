# Progreso de la revisión v2

2026-10-29, hora de México. Leídos AGENTS.md, el diseño, el analista y las pruebas v1, y la petición de la auditoría del PR #127. No se usaron imágenes ni estados de F0/F0b o F1.

La revisión prospectiva, el diseño legible con espacios y el plan v2 se comprometieron en `ec32a7de`, antes del analista y sus pruebas (`17030c89`). Se conservan todos los archivos y resultados de v1. Se ejecutaron 71 pruebas sintéticas: 54 heredadas y 17 nuevas, sin fallos inesperados. Las 20 comparaciones conservaron exactamente la primaria de v1; los cambios de estratos no afectan a la inclusión ni al estimando global.

Se separó la clasificación por mediana elegible del split de los perfiles operacionales por c individual. Se publican todos los conteos e IDs de estratos aunque D sea NO_DEFINIDO. «Longitud» se aclaró como ρ del ganador, y None se rechaza en los errores de cuadratura sin modificar el validador. El watchdog de 120 s continúa reservado al productor como requisito.

El diseño y el analista permanecen BORRADOR para revisión; no se congela F1, no se crea productor ni se elige N de F2. No se entrenó ni se midió ninguna cohorte real.
