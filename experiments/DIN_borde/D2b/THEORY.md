# DIN-D2b · demostraciones y alcance

Este texto deriva identidades; las mediciones sintéticas se informan aparte.
N=n=27 aquí, aunque se distingue N del tamaño n para exhibir el Fisher medio.
p_n tiene tres componentes estrictamente positivos. Se usa el logit reducido
z_n=(z0-z2,z1-z2), con Jacobiano A_n de tamaño2×d, exactamente como core.

## Q6 · factor residual e identidad Fisher condicional

Sea t_nc=(1[c=0]-p_n0,1[c=1]-p_n1), C_n=diag(p_red)-p_red p_redᵀ.
Las definiciones del instrumento implican exactamente

    r_n=A_nᵀ t_n,y,  F=(1/N) sum A_nᵀ C_n A_n,
    gamma=1e-4 max(lambda_max(F),1e-14),  K=F+gamma I,
    M_nm=r_nᵀ K⁻¹r_m.

Con delta_n=1-p_n,y y q_n la distribución condicional de clases incorrectas,
t_n,y=delta_n b_n, donde b es la reducción de e_y-q_n. Por tanto

    M_nm=delta_n delta_m h_nᵀK⁻¹h_m, h_n=A_nᵀb_n,
    M_nn=delta_n² ||K⁻¹/²h_n||²,
    tr M=sum delta_n² ||K⁻¹/²h_n||².

Ésta es identidad, no un modelo de regresión. La correlación entre filas es
el coseno de gradientes blanqueados por K. Un par duplicado con igual etiqueta
tiene r_n=r_m: M_nm=M_nn, incluso con ridge. Ni diagonalidad ni dominancia del
ejemplo de menor confianza son universales. Los residuos y K cambian juntos.

**Rango interpolante.** Apilar A de tamaño2N×d y W=blockdiag(C_n)/N.
Si rango(A)=2N, B=W¹/²A tiene rango completo de filas. Sea E de tamañoN×2N,
con t_n,yᵀ en el bloque n: R=EA. Usando B(BᵀB)^+Bᵀ=I,

    M0=R F^+ Rᵀ=E W⁻¹Eᵀ=N diag(t_n,yᵀ C_n⁻¹ t_n,y)
      =N diag((1-p_n,y)/p_n,y).

La última igualdad es la identidad de Pearson de una observación categórica;
también sale por Sherman–Morrison de C. En este límite sí se fuerza la
diagonalidad y el máximo coincide con la menor confianza, sin necesidad de
gradientes ortogonales. Varias probabilidades comparables no dan colapso.

Para ridge real, R está en el rango de F. Si lambda_+ es su menor autovalor
positivo, por cálculo espectral

    M0/(1+gamma/lambda_+) <= M_gamma <= M0.

En rango interpolante, con D=M0 y eta=gamma/(lambda_++gamma),
0<=D-M_gamma<=eta D. De Cauchy–Schwarz,
|M_gamma,nm|<=eta sqrt(D_nn D_mm) para n!=m. El argmax se conserva si,
por ejemplo, D_kk/(1+gamma/lambda_+) > max_m!=k D_mm. Sin control de condición
o sin rango completo no se puede inferir ese mecanismo desde p sola.

**Escalamiento.** Para A acotado y fijo, delta_n=epsilon c_n y proporciones
incorrectas fijas, R=O(epsilon), F=O(epsilon). Antes del piso absoluto del ridge,
gamma=O(epsilon), de modo que M=O(epsilon) en los modos relevantes y
rho=O(sqrt(epsilon)), cuando el término dominante no se anula. No es una ley
universal M~delta² con denominador fijo. Con piso gamma=1e-18 activo y F<<gamma,
M~RRᵀ/gamma=O(epsilon²)/gamma. Normas/Jacobianos que cambian con epsilon
pueden modificar estos órdenes. Escalar TODOS los Jacobianos por c deja M
invariante si el piso no interviene, pues F y gamma escalan como c².

Si sólo un delta_k permanece positivo y los demás se anulan, con Jacobianos
acotados y Fisher no nulo del ejemplo difícil, gamma queda separado de cero:
M converge a una matriz coordenada. No se deduce que toda trayectoria de
entrenamiento llegue a ese régimen ni que el difícil sea siempre el mismo.

## Q7 · puente con D2

Para cualquier d>0, M=dS implica rho(M,f)=sqrt(d) rho(S,f), exactamente.
Si M=d_k e_k e_kᵀ y el panel tiene rango afín2, [D2](../D2/THEORY.md) da

    rho=sqrt(d_k) min(1/n,1/m_k-1/n).

En posición general n=27, las caras tienen a lo sumo2 puntos, luego
rho=sqrt(d_k)/n, también para k interior. Combinando con el límite Fisher,

    log rho ≈ (1/2)log N-log n+(1/2)log(1-p_k)-(1/2)log p_k.

Esto requiere AMBOS supuestos: colapso coordenado y ridge despreciable en los
modos Fisher relevantes. La pendiente local respecto a log(1-p_k) es1/(2p_k),
no necesariamente1/2. Si esos supuestos fallan, la expresión segura es
log rho=.5 log Mkk+log rho(M/Mkk,f): queda un factor de forma que depende
de todos los gradientes, de sus alineaciones, Fisher/ridge y el panel f.

Si M=d_k e_k e_kᵀ+E, E PSD, la monotonía Loewner y la desigualdad triangular
dan sqrt(d_k)/n <= rho <= sqrt(d_k)/n+L_E(u_ext), usando un rayo de extinción
monótona para k. Para error indefinido Delta, cada longitud cambia a lo sumo
sqrt(||Delta||) integral||a'|| ds <=2n sqrt(||Delta||): cada a_i(s) es unimodal.
Es una cota gruesa, no supone perturbaciones arbitrarias PSD.
La cota de cuerda sobre TODAS las caras es válida aun sin separar E:
rho>=min_S sqrt((1_S/|S|-1/n)ᵀM(1_S/|S|-1/n)).

## Q8 · el campo completo tampoco identifica X

La red lookup de diseño realiza H=aI+eta 11ᵀ en su segunda capa; W3=0.
Sólo el bloque de salida contribuye a R/U y A consta de vectores
z_n=[H_n,1] en cada uno de los dos logits. Sus productos tienen autovalor
a² en1⊥ y s_c=(a+n eta)²+n sobre c=1/sqrt(n).
Todas las probabilidades son la misma p, con y=0. C es su covarianza reducida
y t=(1-p0,-p1). El Fisher separa en esos modos, con

    gamma=alpha lambda_max(C) s_c/n,
    d_perp=n tᵀ[C+alpha lambda_max(C) s_c/a² I]⁻¹t,
    d_const=n tᵀ[C+alpha lambda_max(C) I]⁻¹t,
    M=d_perp(I-ccᵀ)+d_const ccᵀ.

Como 1ᵀJ=0, G=d_perp JᵀJ para TODO P, no sólo cerca de0. Variar a
a p fija cambia d_perp y rho sin cambiar X. Variar p0 y elegir a para
igualar d_perp produce mismo G y mismo rho EXACTOS con X diferentes.
En ambas situaciones hay muchos Mnn comparables; no hace falta colapso.
La raíz se fija con esta fórmula, no buscando resultados de rho.
El embedding con unidades inactivas conserva exactamente R/F/M en WineMLP.

La existencia de esos pares refuta redundancia algebraica universal; no estima
la dispersión condicional en la familia empírica. Conocer L10 no determina
X10 en general, pero su relación puede ser casi determinista en una cohorte
concreta. La construcción estática no contiene una ecuación de evolución de
M10 a M250: puede haber información predictiva temporal adicional, sin que
quede probada por este contraejemplo.

**Control del estadístico.** Para L=(0,.01,.02,.03,1), X=L-2 y Y=-L²,
el MCO con intercepto produce residuos con rangos(1,2,4,5,3). Entonces
Spearman(X,e)=1-6(6)/(5(25-1))=.7, aunque X es función AFÍN de L.
Pearson(X,e)=0 por ortogonalidad. Si se residualiza X también, su residuo
es0 y la correlación no se identifica. Una tendencia Y=g(L) no lineal puede
quedar en los rangos de e pese a que X no añade información condicionada a L.
La permutación no elimina una especificación incorrecta del nulo condicional.
Este ejemplo NO refuta por sí solo un contraste bajo un nulo lineal correcto,
ni diagnostica la causa del .218 de D6. Error de medida en L, empates y
selección exploratoria son otras hipótesis, no explicaciones demostradas.

## Q10 · decisión que permanece abierta

La asociación posterior al colapso puede estar muy constreñida por construcción;
el predictor temprano no es universalmente redundante. Pero un W_adj obtenido
residualizando sólo Y linealmente y luego correlacionando por rangos no prueba
por sí mismo información adicional respecto a L en sentido condicional general.
La recomendación final distinguirá esos dos estimandos y no congelará DIN-C1.
