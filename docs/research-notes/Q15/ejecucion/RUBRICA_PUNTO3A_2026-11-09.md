# Rúbrica de cercanía para el punto 3a (decisión del responsable, 2026-11-09, 19:58, hora de México)

**Estado:** VIGENTE desde el lote siguiente a esta decisión. Claude la propuso en la auditoría del lote 16 y de A1-01/A1-02 ([comentario 6756777882, PR #138](https://github.com/jaiborojas-cloud/leviathan/pull/138#issuecomment-6756777882)). **Solo afecta la cercanía**, que ordena la lectura de texto completo. No cambia ninguna decisión de inclusión o exclusión, ni las rúbricas de los puntos 2 y 4.

| cercanía 3a | criterio | ejemplos |
|---|---|---|
| **ALTA** | Estudia la Fisher, la NTK o la Gauss-Newton como **objeto geométrico** de la red: espectro o rango efectivo, relación Fisher–NTK, límites de la Fisher empírica, *pullback* por Jacobiano o softmax, métrica inducida en el espacio de datos o funciones, singularidades o degeneración | *Neural Tangent Kernels and Fisher Information Matrices*; *Limitations of the empirical Fisher approximation*; *Reducing the Adaptation Gap Through Reachable Fisher Geometry*; *Geometry of Learning in Multilayer Perceptrons* |
| **MEDIA** | **Aproximación o precondicionador** basado en la Fisher o la GN para optimizar, sin un resultado sobre la geometría misma | K-FAC y variantes, Shampoo, M-FAC, TNT, Natural GaLore, *trust-region* de Gauss-Newton |
| **BAJA** | Aplicación que usa la Fisher como **componente**: regularizador contra el olvido, poda, cuantización, RL o adaptación | EWC y variantes, poda con Fisher diagonal |

**Lotes anteriores:** la cercanía 3a de los lotes 05–16 y de A1-01/A1-02 se asignó con el criterio previo. Se revisará en el **repaso consolidado** anterior a la lectura de texto completo, junto con el del punto 2. No se corrige lote por lote.
