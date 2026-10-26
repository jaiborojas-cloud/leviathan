# DIN-D9g: mediciones archivadas antes del análisis

Diseño0896fe4 → código43b1202 → controles9a99718 → evaluación forward.
1.500 trayectorias / 7.500 checkpoints; todos MEASURED y reproducción OK.
Tiempo de evaluación: 17.656463 s. No se entrenó ni se midió rho.
Controles estadísticos: cuatro tablas, todos los D de 2.000 permutaciones
comparados con OLS directo; p idéntica; errorD máximo1.11e-15. Guarda C2 PASS.

Se conservan 1.500 originales en tres shards JSONL reversibles bit por bit, con
SHA por registro. El análisis usará exactamente los once candidatos aprobados,
con p<0.05/12. Todavía no se interpretaron asociaciones D9g. No se accedió a C2.
