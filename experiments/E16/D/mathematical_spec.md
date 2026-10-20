# E16-D — Réplica instrumental en configuraciones nuevas

Se usa la familia operacional de [E16-B](../B/mathematical_spec.md), con método
de precisión de [E16-C en commit fijo](https://github.com/jaiborojas-cloud/leviathan/blob/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C/mathematical_spec.md).
Los pesos, entradas y tres puntos principales son nuevos; no se reutilizan
checkpoints T1/E15/T2-A. C no se reejecuta ni se importa como etapa histórica.
El código del método se reutilizará con procedencia explícita para la réplica.

## Modelo y espacios

M=R⁹, θ=(W₁₁,W₁₂,W₂₁,W₂₂,b₁,b₂,v₁,v₂,c); P=R², p=(x,y).
Para entrada z∈R²: a_j=tanh(W_j·z+b_j), f=v₁a₁+v₂a₂+c,
σ(f)=1/(1+exp(−f)), ℓ_n=y_n f_n−log(1+exp f_n).
Etiquetas sintéticas y_n=1 si z₁+z₂>0, 0 en otro caso. No hay entrenamiento.
Los coeficientes (A,B,D,E) son medias por panel de ℓ_n con pesos
(1,z₁,z₂,z₁z₂), respectivamente. S₁=xA+yB, S₂=xD+yE.

ω_i=∂θⁱS (columna 9×1), B_ai=∂pᵃ∂θⁱS (2×9). En dθ se fija p,
y en dp se fija θ y el panel. Se evalúan Ψ=s₁+s₂, s₁s₂ y (s₁²+s₂²)/2.

ω_macro=Σ_l Ψ_l ω_l,
B_macro=Σ_l Ψ_l B_l+Σ_lr Ψ_lr (d_pS_r)ω_lᵀ.

La referencia explícita usa
r=dθf=(v₁(1−a₁²)z₁,v₁(1−a₁²)z₂,v₂(1−a₂²)z₁,v₂(1−a₂²)z₂,
v₁(1−a₁²),v₂(1−a₂²),a₁,a₂,1)ᵀ y dθℓ=(y−σ)r.
F=N⁻¹Σσ(1−σ)rrᵀ, g=F+0.01I, C=g⁻¹ SPD, h=BCBᵀ.
Se declara regularización fija; no se identifica con F⁺ ni con un cociente ideal.
Las relevancias de estos scores anulan el kernel Fisher del mismo panel por
construcción; D no pretende certificar rango constante de F en un abierto.

## Tres métodos y error

1. Autodiff float64 deriva directamente el escalar compuesto y los logits para F.
2. Referencia explícita de ℓ y r a 80 y 120 dígitos, sin autodiff ni FD.
3. FD central de cuarto orden en θ y p, sobre el escalar forward a 80 dígitos.
   Stencil [f(t−2δ)−8f(t−δ)+8f(t+δ)−f(t+2δ)]/(12δ).
   Cachear sólo valores forward; no alimentar derivadas analíticas al FD.

C=L Lᵀ, U=B L, h=U Uᵀ. Entre matrices computadas:
Û−U=(B̂−B)L+B̂(L̂−L),
||Û−U||₂≤||(B̂−B)L||F+||B̂(L̂−L)||F.
Para FD se usa L de referencia y sólo queda el primer término.
Los valores singulares y los márgenes se comparan en U, no en B cruda.
La desigualdad de normas es matemática; la referencia finita no da una cota
certificada frente a la solución exacta. 80/120 dps es diagnóstico de precisión.

## Controles y unidades de análisis

S_const=A: B=0, rango 0. S_dup=(x+y)A: filas iguales dθAᵀ, rango 1 si dθA≠0.
Controles por estado/panel en p=(1,1), conservando deliberadamente ese punto de
control para comparar el método. En las composiciones no lineales, omitir el
sumando mixto debe producir una discrepancia transportada detectable.

Los 12 estados comparten entradas y paneles; cada estado comparte tres puntos
y tres composiciones. No son 396 réplicas estadísticas independientes. Comparar
rangos entre suma/producto/cuadrática describe esta familia; menor rango no
prueba emergencia y términos mixtos no nulos no implican cambio de rango.
