# E16-B — Formalización instrumental candidata

Extiende la instrumentación de E16, sin confirmación empírica del aprendizaje.
No reutiliza estados, datos, predictores ni protocolos T1/E15/T2-A.
El usuario eligió la construcción nueva sin entrenamiento. El [inventario](results/artifact_inventory.json)
conserva el faltante inicial, que no se presenta como un resultado experimental.

## Modelo mínimo nuevo sin entrenamiento (alternativa propuesta)

θ∈R⁹, orden: W₁₁,W₁₂,W₂₁,W₂₂,b₁,b₂,v₁,v₂,c.
Para entrada z∈R²: a=tanh(Wz+b)∈R², fθ(z)=vᵀa+c,
Pθ(Y=1|z)=sigmoid(fθ(z)). No optimizador ni pasos de entrenamiento.
Panel sintético de evaluación fijado antes de medir, con ocho entradas:
(−1,−1),(−1,0),(−1,1),(0,−1),(0,1),(1,−1),(1,0),(1,1).
Etiquetas y=1 si z₁+z₂>0 y 0 en otro caso, definidas por regla sintética,
sin interpretación de generalización. Pesos exactos y estados fijados en config.json y DESIGN_FROZEN.md antes de medir.

Relevancias de los escalares de evaluación:
L_n(θ)=y_n log σ(f_n)+(1−y_n)log(1−σ(f_n)).
Sea p=(x,y)∈R² el parámetro de perspectivas (distinto de entrada z o etiqueta y_n).
Se fijan dos funcionales suaves de la forma
S₁(θ,p)=x A(θ)+y B(θ), S₂(θ,p)=x D(θ)+y E(θ),
donde A,B,D,E son promedios ponderados de L_n con pesos fijos y normalizados.
Pesos fijados: A=media L, B=media z₁L, D=media z₂L, E=media z₁z₂L, por panel.

ω_l=dθ S_l, columna 9×1 con p fijo; B_l=d_pω_l, forma 2×9 con θ fijo.
Para Ψ afín, producto o cuadrática:
ω_macro=Σ_l Ψ_l ω_l,
B_macro=Σ_l Ψ_l B_l+Σ_lr Ψ_lr (d_p S_r)ω_lᵀ.
El segundo sumando no se omite. Autodiff directo sobre S_macro se contrastará
con ensamblado de esta fórmula y diferencias mixtas centrales sobre S_macro.

## Métrica declarada

F(θ)=N⁻¹Σ_n σ(f_n)(1−σ(f_n)) r_nr_nᵀ,
r_n=dθ fθ(z_n), matriz 9×9 semidefinida. Se declara como estimando instrumental
regularizado g=F+ρH, H=I₉ en esta carta, ρ fijo antes de medir.
C=g⁻¹ SPD; h=B C Bᵀ, forma 2×2. Esto no se identifica con F⁺ ni con el cociente
ideal. No se eligen cortes espectrales de F para fabricar una métrica intrínseca.
La condición de g y sus autovalores se reportarán con cada panel.

Todo L_n tiene dθL_n=(y_n−σ(f_n))r_n. Si las probabilidades son estrictamente
interiores y el panel es el mismo, ker F=ker R, con R de filas r_nᵀ.
Por tanto ω_l y las filas de B_l anulan ker F. Las composiciones con coeficientes
escalares conservan esta admisibilidad puntual. Se verificará residual sobre
el kernel numérico sin afirmar rango constante de F en un dominio abierto.
La métrica operativa sigue siendo la regularizada g, aun si la admisibilidad pasa.

## Cartas, restricciones y descenso

Carta θ=Tη, T constante invertible, gη=TᵀgT, Cη=T⁻¹CT⁻ᵀ,
Bη=BθT. Comparar h con misma familia y mismo punto físico, sin reiniciar H=I.
Carta p=Jq con J 2×2 invertible: B_q=JᵀB_p, h_q=Jᵀh_pJ.
Restricción p=(t,2t): h_t=(1,2)h_p(1,2)ᵀ; no se llama coarse-graining.

Agregación válida π(p)=x+y, S_ag=(x+y)A(θ):
B_ag tiene ambas filas dθAᵀ, h_ag=γ[[1,1],[1,1]], γ=dθAᵀ C dθA;
hbar=γ y h_ag=DπᵀhbarDπ, kernel contiene (1,−1).
Agregación negativa π(p)=x para S₁: si h_yy>tolerancia, no hay descenso
como tensor covariante. Si h_yy≈0, clasificar INCONCLUSIVE para ese contraejemplo,
sin cambiar la familia ni eliminar el estado.

## Observables

Primario instrumental: error de B directo frente a cadena completa, y frente
al escalar evaluado por método numérico independiente. Secundarios: rango de
B C^(1/2), espectro de h en carta fijada, condición, transporte de métricas,
y sensibilidad a paneles fijados de antemano. Rango no es utilidad predictiva.
No inferir pérdida de rango de la mera no invertibilidad de π.
