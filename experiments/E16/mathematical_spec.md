# E16 — Especificación matemática

## Convenciones y dominio

Línea independiente: E16, sin reutilizar E15 ni T2. Se conserva la convención del
[axioma](../../docs/archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md).
M=R^d, P=R^m (o abiertos declarados), S:M×P→R suave C³.
θ es columna d×1; p columna m×1; ω_i=∂S/∂θ^i, columna d×1.
B_ai=∂²S/(∂p^a∂θ^i), matriz m×d. En dθ se fija p; en dp se fija θ.
C^{ij} es una cométrica explícita, simétrica positiva definida sobre el dual
identificable. h_ab=B_ai C^{ij} B_bj, h=BCBᵀ (m×m).
En los controles SPD: g=diag(1/2,1/3), C=g⁻¹=diag(2,3), fijo en θ y p.
No se afirma que g sea Fisher de una red. La familia base es
S=θ¹p¹+θ²p², ω=p, B=I₂, h=diag(2,3).

h puede ser semidefinida: ker h=ker Bᵀ cuando C es SPD; sólo es métrica
riemanniana en P si B tiene rango fila completo. Para llamarla métrica sobre
P/ker h se requiere distribución regular e integrable y descenso; el rango
puntual por sí solo no garantiza un cociente global.

## A. Cambio de carta y B. subfamilia

Sea p=φ(q), J_ai=∂p^a/∂q^i, J de forma m×n, independiente de θ.
ω_q(θ,q)=ω(θ,φ(q)); B_q=Jᵀ B_p y

h_q=Jᵀ h_p J.

Si n=m y φ es difeomorfismo local, es cambio de carta: el rango y las longitudes
se conservan, aunque los autovalores de la matriz no tienen por qué conservarse.
Si n<m y φ es inmersión, es pullback a una subfamilia, no cambio de carta.
Para C SPD: rank h_q=rank(B_pᵀ J)=rank h_p −
dim(im B_pᵀ / im(B_pᵀ J)); equivalentemente se conserva el rango r si
im(B_pᵀ J)=im B_pᵀ. Siempre rank h_q≤min(n,r).
No debe compararse sólo la dimensión de las coordenadas.
La fórmula presupone θ fijo y φ independiente de θ; mapas dependientes de θ
introducirían términos adicionales.

## C. Agregación y descenso

q=π(p) es una submersión suave sobreyectiva con fibras conectadas en los ejemplos.
Un tensor covariante h desciende como h=π* hbar si es horizontal
h(v,·)=0 para todo v∈ker Dπ y sus valores sobre levantamientos son independientes
del representante de cada fibra (tensor básico). En coordenadas producto esto
exige bloques verticales nulos y bloque horizontal independiente de la fibra.
Bajo estas hipótesis la definición hbar_q(u,w)=h_p(ũ,ŵ) es independiente del
levantamiento y representante. Es SPD si ker h=ker Dπ. Si π es submersión,
rank π*hbar=rank hbar: perder coordenadas redundantes no reduce ese rango.
No toda agregación tiene ese descenso. Un cociente riemanniano por minimización
de energía es otra construcción, que exige elegir horizontales y verificar
independencia del representante; no se presume aquí.

Ejemplo válido: p=(x,y), π=x+y, S=θ¹(x+y), C=diag(2,3).
ω=(x+y,0), B=[[1,0],[1,0]], h=2[[1,1],[1,1]]=π*(2 dq²).
El rango es 1 antes y después, vertical (1,−1) nula.
Ejemplo inválido: familia base S=θ¹x+θ²y y π=x. h(∂y,∂y)=3≠0:
no existe hbar con π*hbar=h. Elegir sección y=0 produce 2 dx², pero y=x
produce 5 dx²: se ha añadido una elección, no definido el descenso.
Otro impedimento independiente: S=θ¹xy, π=x, θ fijo. h=2(y dx+x dy)²;
a x=1 los levantamientos ∂x en y=1,2 tienen valores 2 y 8.

Agregación de variables y nuevo funcional no son automáticamente pushforward
de h. Si primero se define S(θ,p)=Sbar(θ,π(p)), entonces B=Dπᵀ Bbar y el
descenso anterior está garantizado, con la misma C y θ fijo. La afirmación
«toda agregación reduce estrictamente rango» queda refutada por el ejemplo válido.

## D. Composición escalar

S_macro=Ψ(S₁(θ,p),…,S_k(θ,p)), Ψ:R^k→R C² sin dependencia explícita adicional.
Escribiendo Ψ_l=∂Ψ/∂s_l, Ψ_lr=∂²Ψ/(∂s_l∂s_r):

ω_macro,i=Σ_l Ψ_l ω_l,i,
B_macro,ai=Σ_l Ψ_l B_l,ai + Σ_l,r Ψ_lr (∂_a S_r) ω_l,i.

El segundo sumando incluye la dependencia en θ de los coeficientes al derivar
primero dp S_macro; en la derivación alternativa d_p ω_macro incluye su
dependencia en p. La igualdad de derivadas mixtas conecta ambas rutas.
No tratar Ψ_l como constantes. Si Ψ tiene dependencia explícita en θ,p hay
además términos explícitos y mixtos: esos casos quedan fuera de este experimento.
Con Ψ afín de coeficientes constantes, B_macro=Σ_l c_l B_l; cancelación puede
reducir rango. Con Ψ no lineal no hay ley de monotonicidad frente al rango de
cada componente; siempre rank h_macro≤min(m,d).

Control: S₁=θ¹p¹, S₂=θ²p², Ψ=s₁s₂. S_macro=θ¹θ²p¹p²,
B_macro=[[θ²p²,θ¹p²],[θ²p¹,θ¹p¹]], rango 1 para θ,p no nulos;
Σ Ψ_l B_l omite los términos fuera de diagonal.
Contraejemplo a monotonía respecto de la suma: S₁=θ¹p¹+θ²p², S₂=−S₁+θ¹.
La suma tiene B=0. Ψ=(s₁²+s₂²)/2 tiene, en θ=(1,2), p=(1,1),
B=[[11,3],[6,7]], determinante 59, rango 2; la no linealidad restaura variación.
No es una comparación con el tensor de la familia conjunta apilada ni prueba de emergencia.

## Caso degenerado y cambio de coordenadas del modelo

F=diag(2,0), K=span(e₂), S=θ¹p¹. ω=(p¹,0) y BK=0.
El cociente TθM/K es 1D con métrica 2, cométrica 1/2 y h=1/2.
Si θ=Aη, Fη=AᵀFA, ωη=Aᵀω, Bη=B A.
En SPD Cη=A⁻¹ C A⁻ᵀ, por lo que h no cambia.
Para F singular no se afirma (AᵀFA)⁺=A⁻¹F⁺A⁻ᵀ. En el cociente, con
rango constante y covectores admisibles, la contracción por soluciones Fx=β
es intrínseca: dos soluciones difieren en K y α(K)=0. Moore–Penrose sólo
elige un representante; αᵀF⁺β da esa contracción en cada carta si α,β∈K°.
Control A=[[1,1],[0,1]]; los pseudoinversos como matrices difieren, pero las
contracciones admisibles coinciden. Para S_bad=θ²p¹ se viola el axioma:
h ingenua pasa de 0 a 1/8 con esa carta. Se registra como contraejemplo esperado,
no como fallo del marco ni geometría válida.
