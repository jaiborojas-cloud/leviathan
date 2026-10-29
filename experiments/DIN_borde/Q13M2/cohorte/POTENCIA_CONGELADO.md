# Correspondencia de potencia N320 con el analista congelado

Se conserva la potencia de [N320_v1](../potencia_preparacion/N320_v1/RESULTADO_v1.md), publicada antes de la congelación. Se verificó el analista de potencia `2e69516e…` frente al congelado `190e3e87…` **sin importar ni ejecutar los analistas**. [Resultado AST](power_frozen_equivalence.json), [diff completo](fuentes/analista_potencia_congelado.diff), [verificador comprometido antes de ejecutarse](validacion/verify_power_ast_v1.py).

Las siete funciones auxiliares, constantes, dependencias por SHA, llamada primaria y bloque de bootstrap/clasificación son idénticos por AST. Los cambios del programa completo incluyen localización de degeneración por brazo, manejo de errores LS/compatibilidad y escritura exclusiva; no son solo comentarios. El cambio final v2→v2.1 agrega la conservación de motivos múltiples. Ninguno altera el estimando de la ruta no degenerada simulada en N320.

**No se repite la potencia:** se demuestra equivalencia de esa ruta, no identidad de todos los comportamientos del programa ni garantía de potencia ante fallos operacionales de la cohorte. La simulación ya conservaba los controles inconclusos en su denominador. Se mantienen todas sus hipótesis y limitaciones, incluida compuerta operacional válida y c esperadas fijas.

Con ρ=0, criterio que decide: LP398/400, Wilson95 inferior0.981955; WD393/400, inferior0.964323. Ambos superan0.8. Conjunta contada directamente391/400,97.75 %, solo descriptiva. Son resultados ya archivados, no nuevos cálculos sobre datos reales. Sensibilidades y modelo están en el informe original.

No se leyó ni analizó ninguna cohorte M2, C2, Wine, T2 o DIN-C1. El diseño y analista congelados permanecen intactos. El productor no importa el analista: únicamente verificará su SHA como archivo.
