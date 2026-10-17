# Leviathan / RIPG — E15-T1: diseño de topología local e inyectividad

**Estado: diseño separado; ejecución pendiente.** Se abre sólo al confirmar pérdida geométrica en E15-C1-A2. C1-A conserva su clasificación INCONCLUSIVE y su estimando D_0.02. Este diseño no autoriza cambiar retrospectivamente C1, excluir split 0, reducir áreas por estado ni tratar pares supervivientes como confirmación. C2 no se abre.

## Pregunta y observables nuevos

Estudiar por separado radio de inyectividad, primeros radios conjugados por dirección, colisiones del mapa exponencial, cut locus, topología de los frentes geodésicos y área de la familia embebida conectada al origen. No combinarlos en un score ni confundirlos con magnitud curvatural, concentración espacial o atribución por profundidad.

A2 aporta estimaciones de primeros conjugados y colisiones. No demuestra que el primer conjugado sea el primer punto de corte, ni determina el radio de inyectividad global. El objetivo prioritario de T1 es cerrar esa diferencia.

## Fase T1-0 — especificación previa a nuevos resultados

Conservar exactamente los diez estados split 0 de A2, checkpoints M/f y geometría RIPG. El piloto no introduce semillas ni reentrena. Antes de integrar nuevos radios se debe congelar un archivo versionado que defina: dominio computacional, máximos radios y criterios de censura, malla angular/radial, tolerancias, reglas de continuación de curvas, detección de colisiones, presupuestos, pruebas de independencia y tratamiento de excepciones. No fijar estas decisiones tras abrir los nuevos resultados.

La geometría fuera de las trayectorias ya auditadas puede perder resolución o cercanía al régimen regular; monitorizar SPD y la validez del dominio sin reemplazar corridas fallidas. No presumir completitud global. Distinguir límites por presupuesto de verdaderos límites geométricos.

## Fase T1-1 — cut locus frente a locus conjugado

1. Continuar el primer cero de Jacobi por ángulo, con mallas/fases y tolerancias independientes; reportar intervalos numéricos y direcciones no resueltas.
2. Buscar colisiones de geodésicas inicialmente distintas tanto de igual longitud como de distinta longitud, y comparar longitudes hasta los mismos puntos.
3. Verificar minimización de distancia con un instrumento independiente adecuado a la misma métrica, no sólo cruces de polígonos. Una colisión o un pliegue de un frente no identifica por sí solo todo el cut locus.
4. Obtener cotas superiores reproducibles de r_inj y, si el instrumento lo permite, cotas inferiores justificadas. Si no se dispone de certificado, etiquetar estimación/censura/INCONCLUSIVE; nunca sustituir la ausencia de eventos muestreados por una prueba global.
5. Separar cambios de rango local de exp, solapamiento global de imágenes, puntos de corte y singularidad de G. Guardar trayectorias, longitudes, residuos, multiplicidades y condiciones.

## Fase T1-2 — área y topología

Estimar A_embed como límite de la familia inicialmente embebida. Contrastar borde simple con inyectividad del interior; un borde simple aislado no prueba ausencia de plegamiento interno. Medir área intrínseca de la unión y área con multiplicidad por separado, además de las áreas de coordenadas. Registrar winding por región y número de giro del frente, con estabilidad frente a resolución/fase.

En controles censurados por R nominal, extender el radio sólo bajo el nuevo protocolo T1 congelado; esto no modifica sus discos C1. Guardar censura si se agota el presupuesto sin evento.

## Fase T1-3 — extensión jerárquica opcional

Sólo después de validar el instrumento y congelar su versión final, considerar los 80 estados Wine originales. No seleccionar sólo estados interesantes. Mantener pares y jerarquía split/inicialización; reportar fallos y censura explícitamente. Los nuevos observables requieren un plan de análisis propio fijado antes de abrir ese panel. Asociaciones con C_A, Lambda y R_eff son descriptivas salvo diseño causal independiente; los estados sin dominio C1 admisible no reciben estimandos espaciales fabricados.

## Cierre requerido

Entregar matrices de resolución/fase, mapas de colisiones y conjugados, cotas/estimaciones de r_inj, A_embed, comprobaciones de distancia, métricas SPD, excepciones, censura, costes, código y hashes. Una nueva tarea/arquitectura externa continúa aplazada. No se ejecuta C2 sobre una confirmación incompleta de C1-A.
