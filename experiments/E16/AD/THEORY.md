# E16-AD · curvatura y variaciones normales

## A: por qué el producto también es plano

Con θ fijo y C=(F+ρI)⁻¹ fijo, definir Ψ(p)=∇θ f(p)chol(C). D/analytic_B es
DₚΨ antes del factor chol(C); por ello h=DΨ DΨᵀ. Para suma f=s1+s2 es
lineal en p. Para producto f=s1s2 y cuadrática f=(s1²+s2²)/2 son homogéneas
de grado2. En ambos casos Ψ(rp)=r²Ψ(p), imagen cónica sobre regiones de rango2.

Escribir Ψ=ρ a(φ), ρ=r². La métrica inducida es
|a|²dρ²+2ρ(a·a')dρdφ+ρ²|a'|²dφ². Con R=ρ|a| se vuelve

$$dR^2+R^2w(φ)^2dφ^2,\quad
w^2=|a'|^2/|a|^2-(a\cdot a')^2/|a|^4.$$

La condición SPD implica w²>0 localmente. Cambiar ángulo por integral de w
produce métrica polar plana. SymPy calcula Gauss de esta métrica universal y
da0 sin sustituir pesos aproximados por racionales. Otra prueba: Euler implica
D²Ψ[p,u]=DΨ[u], tangente; la segunda forma fundamental anula la dirección
radial y cada determinante de forma se anula en la ecuación de Gauss.
El vértice singular y regiones sin SPD quedan fuera del argumento.

En suma h es constante. La malla MP es un contraste numérico de la fórmula,
no la prueba de K≡0. Los rangos residuales MP120 no se sustituyen por cero.
No es correcto proponer conjugados regulares del producto como si fuera no plano
en este modelo fijo; curvatura global/singularidad/corte requieren otra pregunta.

## B: coordenadas, norma y restricciones

En p=A+Jz, el tensor es Gz=JᵀhJ. Por nodo se normaliza la cuerda centrada t
con Gz; se toma n perpendicular a Gz t en sentido euclidiano y se normaliza
con Gz. Entonces tᵀGt=nᵀGn=1 y tᵀGn=0. E=[T,N] es una base métrica,
no euclidiana. La Hessiana nodal H transforma por congruencia EᵀHE; sus
autovalores usan norma métrica nodal, no masa consistente P1.

Para v=Ta+Nb, la fracción tangencial es ||a||²/(||a||²+||b||²), equivalente
a la suma de normas métricas de componentes. Se conserva cada modo negativo
resuelto y se registran mínimo y máximo de las fracciones. El máximo solo no
permite afirmar que todas las negativas sean tangenciales. Se conservan también
los espectros físicos para evitar confundir normas y escalas.

COCIENTE usa la carta fija x=x0+N0q. Su gradiente es N0ᵀgx y su Hessiana
N0ᵀHN0, sin un término de curvatura de carta porque es lineal. Su KKT no es
el KKT completo en x. Es una restricción local a direcciones normales iniciales,
no una parametrización global del espacio cociente. El espectro ambiental puede
seguir teniendo negativas aunque no haya negativas admisibles. Esto se registra.

En un punto sólo aproximadamente estacionario la Hessiana depende de la carta;
no se identifica sin más su inercia con el índice de Morse continuo. Las pruebas
MP conservan pendientes; no se proyectan artificialmente a g⊥ para anularlas.
Los umbrales relativos distinguen negativas resueltas de valores casi nulos.
Un mínimo crudo negativo por encima de −tau no se reclasifica retrospectivamente.

## Controles y archivo

En esfera se integra longitud sobre segmentos rectos de latitud/longitud,
igual concepto de polígono de coordenadas que en S. En el ecuador, el bloque
normal discreto es rigidez−masa de Jacobi: por arista de longitud Δ,
1/Δ[[1,−1],[−1,1]]−Δ/6[[2,1],[1,2]]. Se contrasta Hessiana AD de cuadratura
32/64 y fórmula FEM. Debe contar0 negativas en0.75π y1 en1.5π en cada malla.
No se sustituye por distancia de gran círculo entre vértices.

La dependencia de longitud por aristas hace H bloque tridiagonal. Se guardan
todas sus entradas en banda (incluidos ceros internos), y las bandas TT/NN/TN;
las demás son cero dentro del control de localidad. El bloque completo métrico
se reconstruye como [[TT,TN],[TNᵀ,NN]]. Se guardan autovectores negativos en
coordenadas físicas z y sus coeficientes métricos. Nada exige volver a calcular
la Hessiana para inspeccionarlos. Los modos esféricos se reconstruyen de sus
bloques archivados como operación de archivo, sin repetir la medición AD.

Las guardias de estacionariedad y presencia de negativas LIBRE fijadas antes de
medir evitan atribuir el origen de negativas históricas a partir de supervivientes
o de una condición universal vacía. Exploratorio, sin certificado riguroso,
mínimo global, causa única o prueba de equivalencia global del cociente.
