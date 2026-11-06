# Comparación algebraica para Q15: M y la métrica inducida

Fecha: 2026-11-02. **Deducción documental del revisor, no experimento ni conclusión de novedad.**

Para un estado fijo, sean r_n los scores y H = F + γI, con γ > 0. Definiendo φ_n = H⁻¹ᐟ²r_n y Φ como la matriz cuyas columnas son φ_n,

\[
M_{nm}=r_n^\top H^{-1}r_m=\phi_n^\top\phi_m,
\qquad M=\Phi^\top\Phi.
\]

La forma de scores y Fisher inversa tiene el antecedente del [Fisher kernel de Jaakkola–Haussler](https://proceedings.neurips.cc/paper/1998/hash/db1915052d15f7815c8b88e879465a1e-Abstract.html) [leído: fragmentos, §4, ecuación 6]. DIN fija una variante: scores condicionales de etiquetas observadas, una Fisher construida sobre un panel, selección de parámetros y un ridge. No se afirma equivalencia de todas esas decisiones con el modelo generativo original.

Para a(P) = softmax(fP), defínase la combinación ponderada μ(P) = Φa(P). Como Φ no cambia al recorrer P dentro de ese estado,

\[
\mathrm d\mu=\Phi J(P)\,\mathrm dP,
\qquad \|\mathrm d\mu\|_2^2
=\mathrm dP^\top J(P)^\top M J(P)\,\mathrm dP.
\]

Así, G es exactamente la métrica inducida por ese mapa de combinaciones de features en un espacio euclídeo. Si el diferencial pierde rango, es una semimétrica; la geometría riemanniana exige restringirse a la región regular. Esta reexpresión se obtiene por multiplicación matricial, sin evaluar estados ni ρ.

Consecuencias para la búsqueda, no veredictos:

1. M no debe presentarse como una familia de kernels inventada por DIN. La contribución residual, si existe, tiene que especificar construcción, campo, funcional al borde o evidencia empírica.
2. Que una métrica sea un pullback es una operación general. No demuestra por sí solo que ya se haya estudiado el mismo mapa μ ni ρ_ray; esa equivalencia bibliográfica sigue pendiente.
3. La longitud de la curva μ(su) sigue siendo longitud de una curva concreta; minimizar solo en u no la convierte en distancia geodésica al borde.
4. La invariancia de un Fisher kernel ideal bajo reparametrización no se transfiere automáticamente a añadir γI en unas coordenadas particulares. La elección de referencia y regularización debe permanecer en la comparación.

En el código archivado [core.py](../../../archive/import-2026-10-17/extracted/j7_update25_execution_sources/core.py), `make_geom_state` usa pesos p_c/N para las columnas de U, mientras R contiene scores de las etiquetas del panel. En la terminología discutida por [Kunstner–Balles–Hennig](https://arxiv.org/abs/1905.12558v3) [leído: fragmentos, §3.2 y apéndice A.2], esto obliga a separar la distribución empírica de entradas de la sustitución de etiquetas por observadas. No se importó ni ejecutó el módulo: fue lectura de código.

La expresión como combinación de features sugiere comprobar también literatura sobre embeddings de distribuciones con kernels. Esta es una **ruta candidata para una eventual enmienda**, no una consulta añadida ni ejecutada silenciosamente al protocolo vigente.
