# Ejecución v1 y defecto identificado

Diseño6238a9f → código735ac0d → corrida results/run_v1. Doce shootings
convergentes, índices numéricos0 y perfiles conservados; corrida INVALID porque
hyperbolic_10 falla el contraste MP. No interpretar sus éxitos individuales
como resultados de una corrida válida.

El control tiene K=−1 y j=sinh(s). DOP853 tiene error relativo5.29e-15,
pero RK4 con512 pasos sobre L10 introduce error de truncamiento acumulado
aproximadamente L*(L/512)^4/120≈1.21e-8, que supera1e-8. El campo error de
controls.csv v1 sólo guardó el error DOP853, no el del contraste MP: defecto
de instrumentación adicional. El FAIL se conserva; no se cambia su estado.

Corrección prospectiva v2:2048 pasos sólo para controles sintéticos MP, mismo
umbral1e-8 y mismas mallas MP científicas256/512. Registrar error MP explícito,
estados de shooting y eventos.csv vacío con cabecera si no hay conjugados.
Congelar en commit antes de código v2. Código v1 y resultados v1 no se tocan.
