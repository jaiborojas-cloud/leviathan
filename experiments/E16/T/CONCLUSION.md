# Conclusión de E16-T

Las comprobaciones diagnósticas pasan en los doce caminos. Los cuatro
cuadráticos finos tienen curvatura negativa numéricamente resuelta, contrastada
por MP, en direcciones casi enteramente tangenciales. Los cuatro gruesos tienen
su mínimo en la banda casi nula. Los bloques normales son positivos al umbral,
pero no eliminan el efecto del acoplamiento ni prueban estabilidad completa.

El control recto reproduce el Hessiano analítico y sus modos tangenciales
nulos. Los diminutos negativos de C0 son compatibles con redondeo y no se
interpretan como inestabilidad real.

S conserva PASS_NUMERICAL para su protocolo de primer orden. T no cambia ese
resultado: muestra por qué no debe interpretarse como mínimo certificado.
El estado global sobre propiedades de mínimo permanece INCONCLUSIVE. No se
atribuye causalidad exclusiva a parametrización o redistribución de nodos.

Un próximo protocolo podría contrastar descensos finitos factibles sobre las
direcciones negativas y comprobar si cambian longitud e imagen geométrica,
frente a desplazamientos tangenciales de control. Necesitaría pasos y reglas
congelados antes de medir; no se ejecuta como parte de T.
