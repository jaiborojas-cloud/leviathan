# Formulación de segundo orden en E16-T

Sean x=(t₁,s₁,…,tₘ₋₁,sₘ₋₁), extremos fijos y L la longitud discreta
heredada de P/S. El Hessiano físico es H=∇²L(x). En un punto interior exacto
con ∇L=0, H semidefinido positivo es condición necesaria de mínimo local;
positivo definido es suficiente bajo suavidad. T tiene candidatos con KKT
aproximado, no estacionariedad exacta ni prueba rigurosa del signo espectral.

## Marco local y bloques

En cada nodo interior j se define el acorde cⱼ=zⱼ₊₁−zⱼ₋₁, τⱼ=cⱼ/‖cⱼ‖ y
νⱼ=(−τⱼ,₂,τⱼ,₁). Sus inserciones por nodo forman matrices T,N con

$$T^TT=N^TN=I,\qquad T^TN=0,\qquad TT^T+NN^T=I.$$

La representación ortogonal del Hessiano es

$$\begin{pmatrix}T^THT&T^THN\\N^THT&N^THN\end{pmatrix}.$$

Los espectros de los bloques diagonales no son una partición del espectro
completo. Los acoplamientos importan. Si Hnn es positivo definido, el criterio
algebraico involucra el complemento de Schur Htt−Htn Hnn⁻¹ Hnt; T no lo
calcula ni lo sustituye por Htt. Tampoco elimina T como si fuera un gauge exacto.

Para un vector mínimo unitario u se informa ‖Tᵀu‖² y su complemento normal.
En caso de degeneración, la participación puede depender de la base elegida
por el eigensolver. No se presenta u como dirección física única.

## Rayleigh y umbral

Cada bloque tiene umbral propio ε=1e-8 max(1,max|λ|). Los negativos por debajo
de −ε son resueltos al umbral numérico, los comprendidos en ±ε son casi nulos.
No es una cota demostrada del error de diagonalización. Se comprueba simetría
del Hessiano AD antes de usar (H+Hᵀ)/2.

Para cinco direcciones unitarias v predefinidas, se contrasta

$$v^THv\quad\text{con}\quad
\frac{L(x+hv)-2L(x)+L(x-hv)}{h^2}.$$

Se usan dos pasos y dos precisiones, perturbando directamente puntos MP.
Los autovectores proceden de AD: MP ofrece otro procedimiento de evaluación
de su curvatura, no una selección independiente de direcciones ni datos nuevos.
El signo concuerda numéricamente, sin aritmética de intervalos o garantía exacta.

Curvatura negativa en un punto con gradiente no exactamente cero no se
convierte por sí sola en prueba de punto silla. Tampoco se ensaya aquí una
búsqueda de descenso de longitud a un paso finito. Una perturbación bilateral
factible a los pasos medidos respalda el diagnóstico local dentro de la caja.

## Control constante recto

Sea M=JᵀhJ, J=[b−a,R(b−a)], y una arista recta (Δt,0), Δt>0.
Para f(q)=√(qᵀMq),

$$\nabla^2 f(q)=\frac{M}{\sqrt{q^TMq}}-
\frac{(Mq)(Mq)^T}{(q^TMq)^{3/2}}.$$

En la recta, sólo queda el coeficiente transversal

$$w=\frac{M_{ss}-M_{ts}^2/M_{tt}}{\sqrt{M_{tt}}\,\Delta t}.$$

El Hessiano global se ensambla como Laplaciano ponderado sobre las variables s,
con extremos fijos, y cero sobre las variables t. Por eso los m−1 modos
tangenciales son exactamente nulos en aritmética real, mientras no cambie el
orden de los nodos. El cálculo AD y la diagonalización introducen redondeo.

En una poligonal curva, desplazar un vértice sobre el acorde de sus vecinos
puede cambiar los segmentos y la curva. No existe razón para que ese modo sea
exactamente nulo. Una teoría del cociente por reparametrizaciones requeriría
un tratamiento adicional, compatible con la discretización y sus acoplamientos.
