# Conclusión de E16-U

Los cambios finitos conservan la señal local de T: en los cuatro cuadráticos
finos, full_min y tangent_min tienen cambio par negativo para los tres pasos.
La dirección full_min da un descenso unilateral en cada pareja, mientras el
otro sentido aumenta. El gradiente residual sigue contribuyendo: el descenso
unilateral no se atribuye exclusivamente al Hessiano.

En los descensos full_min finos, los pasos 1e-4 y 1e-3 producen cambio de imagen
numéricamente detectado; 1e-5 queda sin resolver al umbral geométrico congelado.
Una dirección casi tangencial puede deformar el polígono. No se construye
un cociente exacto por reparametrizaciones ni se identifica una causa única.

Los efectos de longitud son pequeños. No se selecciona un candidato mejor,
no se reinicia optimización y no se cambia el PASS de primer orden de S ni el
INCONCLUSIVE sobre mínimos de T. U es exploratorio y mantiene mínimos UNKNOWN.

Persisten límites: mismos datos sintéticos y candidatos, direcciones dependientes
de T, tres pasos, dos mallas, sin control riguroso de redondeo o truncación y
cotas geométricas holgadas con 78 ensayos válidos sin resolver. Los diez ensayos
inviables de C0 y sus estados desconocidos se preservan.

Un protocolo posterior podría comprobar estabilidad del efecto al refinar la
poligonal y controlar la redistribución de nodos. Requeriría fijar de antemano
fuentes, amplitudes, controles y criterio geométrico; no se ejecuta dentro de U.
