# E16-C — Precisión de rango: especificación

Se conserva la familia y los 81 puntos de [E16-B](../B/mathematical_spec.md).
Este reanálisis instrumental es posterior al diagnóstico FD de B, no una muestra
nueva para confirmar hipótesis de aprendizaje. El INCONCLUSIVE de B es inmutable.
θ∈R⁹, p=(x,y)∈R², S: R⁹×R²→R; ω_i=∂θⁱS, columna 9×1 con p fijo;
B_ai=∂pᵃω_i, forma 2×9 con θ fijo. F(θ) es Fisher del panel fijo;
g=F+0.01I, C=g⁻¹, h=BCBᵀ, L=chol(C) inferior, C=L Lᵀ.
Por tanto U=B L y h=U Uᵀ, rango h=rango U=rango B porque C es SPD.
No se usa pseudoinversa ni se afirma equivalencia con el cociente ideal Fisher.

## Referencia analítica explícita, independiente de autodiff

Para neurona j=1,2: a_j=tanh(W_j·z+b_j), f=v₁a₁+v₂a₂+c,
σ=1/(1+exp(−f)), ℓ=y_n f−log(1+exp f).
En el orden de parámetros de B:

r=dθf=(v₁(1−a₁²)z₁,v₁(1−a₁²)z₂,
v₂(1−a₂²)z₁,v₂(1−a₂²)z₂,
v₁(1−a₁²),v₂(1−a₂²),a₁,a₂,1)ᵀ,
dθℓ=(y_n−σ)r.

Los cuatro pesos por muestra son (1,z₁,z₂,z₁z₂); sus promedios ponderados
de ℓ dan c=(A,B,D,E), y de dθℓ dan J_c (4×9).
S₁=xA+yB, S₂=xD+yE. Escribiendo c_l=(A,B) o (D,E),
v_l=dθS_l=pᵀJ_l (fila), J_l=d_p dθS_l (2×9):

- Suma: B_macro=J₁+J₂.
- Producto: B_macro=S₂J₁+S₁J₂+c₂ v₁+c₁ v₂.
- Cuadrática: B_macro=S₁J₁+S₂J₂+c₁ v₁+c₂ v₂.

Los productos c_l v_r son exteriores, 2×9. Son la regla completa
Σ_l Ψ_l B_l+Σ_lr Ψ_lr(d_p S_r)ω_lᵀ. Se incluyen dependencias en θ de
los coeficientes Ψ_l. F=N⁻¹Σσ(1−σ)rrᵀ se construye con el mismo r explícito.
Se evalúa a 80 y 120 dígitos decimales con mpmath. Los literales de config.json
se interpretan como decimales exactos de entrada; la diferencia frente a float64
incluye también su representación binaria. No se atribuye todo a autodiff.

## Diferencias finitas independientes

D_t^(4)f=[f(t−2δ)−8f(t−δ)+8f(t+δ)−f(t+2δ)]/(12δ).
Se aplica D_p^(4) D_θ^(4) directamente al escalar S, sin alimentar gradientes
analíticos ni autodiff. Error de truncamiento O(δ⁴) para funciones suaves.
En p las composiciones son polinomios de grado ≤2, por lo que no hay error de
truncamiento en esa dirección. Se permite cachear evaluaciones escalares del
forward por θ desplazado y panel, nunca derivadas. δ=0.002 y 0.001, a 80 dígitos;
no se elige un paso posterior mirando el resultado.

## Error transportado y separación espectral

Sea referencia U*=B_120 L_120. Para otra pareja computada (Bhat,Lhat):

Uhat−U*=(Bhat−B*)L*+Bhat(Lhat−L*),
||Uhat−U*||₂≤||Uhat−U*||F≤
|| (Bhat−B*)L* ||F + || Bhat(Lhat−L*) ||F =: e_triangle.

La última expresión es una cota algebraica entre las matrices computadas;
Weyl da |σ_i(Uhat)−σ_i(U*)|≤||Uhat−U*||₂. Para FD se usa L_120 y queda
sólo el primer término. Para autodiff se calculan F,g,C,L float64 por esa ruta
y se incluyen tanto el error en B como en L. No se compara error de B crudo
con un umbral de U, deficiencia operacional identificada en B.

La concordancia entre 80/120 dígitos es diagnóstico de precisión, no una cota
certificada de error respecto de la solución exacta. Los intervalos σ_i(U*)±e
que se reporten son márgenes operacionales entre métodos, no intervalos
validados ni certificados globales de rango. No se hace aritmética intervalar.
Una validación numérica fuerte puede pasar sin demostrar un teorema sobre un abierto.

## Controles

S_dup=(x+y)A: B_dup tiene filas dθAᵀ iguales, rango esperado 1 si dθA≠0.
S_const=A: B_const=0, rango 0. Se evalúan por panel/estado, p=(1,1).
Se comparan tres métodos también en esos controles.
Para producto/cuadrática se omite deliberadamente el sumando mixto en una
matriz defectuosa B_trunc; el control debe detectar la discrepancia transportada.
El rango de esa matriz podría coincidir: se detecta error de derivada, sin
confundir rango igual con implementación correcta.
