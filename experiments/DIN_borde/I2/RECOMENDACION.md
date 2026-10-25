# I5 · recomendación al responsable

Para estudios futuros cuyo objeto sea **todas las semirrectas naturales desde
P0**, propongo `rho_caras`. Es el objeto de la partición demostrada en I1 y
recupera los casos de caras masivas y el testigo Iris. Sigue siendo una cota
por longitudes de semirrectas, no la distancia geodésica al borde.

Conservar `rho_vert` por separado si interesa deliberadamente el ínfimo sobre
direcciones genéricas. No llamar ambos resultados indistintamente rho_borde:
la diferencia puede ser factor26 en un ejemplo conocido. v1 tampoco debe
renombrarse retrospectivamente como rho_vert sin auditar sus resultados: puede
perder conos o confundir transiciones tardías, como muestran los triángulos AG.

Declarar prospectivamente versión/SHA, objeto, tratamiento de duplicados y
casi colinealidad, presupuestos, tolerancias, validación independiente y regla
ante fallos. Conservar dirección racional, soporte completo, longitudes,
restos y diagnósticos. Si el ganador es un límite de cono, decirlo.

Esto es una recomendación exploratoria; el responsable decide. No modifica
DIN-C1, ninguna etapa cerrada ni sus conclusiones. Antes de transferencia,
conviene una validación independiente del optimizador por cono y de las
raíces, y un piloto separado que fije el desenlace antes de medir.
