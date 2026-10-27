# Revisión del objetivo durante la auditoría

El snapshot inicial es e7dfc435ab97cdc8d24bba5d525b193af274f35f. Durante el trabajo,
PR #103 avanzó a **78a7d2e1e19091546ebcb0725549a417eeb8121e**. Se revisó el diff:
el único cambio en los archivos solicitados es envolver en float un valor antes
de repr en el generador sintético de pruebas. Corrige su representación NumPy.

**Diseño v1, analista, Q13 y C1 siguen byte por byte idénticos.** Analista SHA
c9159325c7f22c6e5ded2977f6d208e0282558094fd34ab6f96fb68c00843b10. Por tanto,
casos y tasas siguen aplicándose a ese analista vigente. La heurística de ABORTA
de las pruebas tampoco cambió. No se repitió innecesariamente ningún cálculo.

Se conserva el snapshot anterior, el [diff](revision_78a7d2e/delta.diff), la nueva
fuente de pruebas como texto y la [comparación de SHA](revision_78a7d2e/verification.json).
La suite original no se ejecutó en ninguna revisión, ni se leyó su fixture C2.
