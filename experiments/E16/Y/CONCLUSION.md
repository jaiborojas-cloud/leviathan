# Conclusión de E16-Y

Las 559 comprobaciones pasan en 24 problemas. La misma imagen y longitud
admiten un gradiente fino mayor cuando se añaden variables. Los mínimos de
masa refinados cuadráticos son fuertemente negativos y contrastados con MP;
no conservan la magnitud del nivel original. C0 no aporta testigos negativos.

Las identidades de transporte de masa, gradiente y Hessiano pasan. Eso
explica la compatibilidad entre un gradiente coarse pequeño y uno fine grande:
la restricción sólo observa los desplazamientos del espacio original.
No se identifica una causa única de las nuevas direcciones negativas.

La persistencia de signo negativo y la disminución del mínimo no equivalen
a estabilidad de mínimos estacionarios frente a malla. Los refinados no se
han reoptimizado y no son aproximadamente estacionarios en sus nuevas variables.
La conclusión es exploratoria, mínimos UNKNOWN; no invalida S o X.

El siguiente protocolo podría reestacionarizar las poligonales subdivididas
con una regla física congelada antes de comparar sus espectros de masa.
Necesitaría fuentes, presupuesto, parada y validación propios. No se ejecuta
dentro de Y; tampoco se afirma convergencia con esta única subdivisión.
