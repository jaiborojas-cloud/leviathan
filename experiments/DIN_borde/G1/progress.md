# Progreso G1 · fase0

AGENTS raíz leído, sin instrucciones subordinadas. Checkout existente,
main actualizado aa532c3c; rama nueva research/din-g1-generalizacion.
Lectura: informes publicados D1/D3/D4/D5/D6 y conclusiones D2/D2b/D2c.
No se abrieron sus tablas/estados ni datos de C1. No se ejecuta código C1.

Fuentes científicas leídas y SHA fijados: core.py, geometry.py, rho_borde.py.
make_geom_state hardcodea2 capas ReLU y3 logits reducidos: se elige Iris3
clases y una arquitectura más ANCHA, sin adaptar ese forward.
Core define un cargador Wine que no se llama. No se usa train_branch por
su parada temprana; el aprendizaje mantiene Adam/lr/lote y continúa250.

Entorno revisado con habilidad cloud-environment-runtime:2 CPU de cuota,
3 afinidad, ~10GB RAM. torch2.9.1+cpu disponible fuera de Git. Aún no se
cargó Iris, no se entrenó ninguna red ni se ejecutó rho.
Se fija720/400 con120 auditorías1440/800 previas para completar20×5 en cada
familia con este presupuesto. No es una adaptación a resultados geométricos.
