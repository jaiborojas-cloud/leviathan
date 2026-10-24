# E16-AD · diseño prospectivo antes de código y mediciones

Parte A se ejecutará completa antes de B. No reabrir S–AC. Fuentes con hashes
en config. Q0/Q1 comparten extremos, métrica y una rama AC; tomar la primera
fuente Q0/reference/132, parámetros shooting rtol1e-12 archivados, sin seleccionar
por resultado. Evaluar esa solución por IVP, no volver a hacer shooting AC.
Doce casos B: cuadrática y C0 ×132/264/528 ×LIBRE/COCIENTE. Sin caminos producto.

## A: curvatura

Malla fijada81 puntos z: t0..1 en9, s−.25...25 en9, p=A+t(B−A)+sR(B−A).
Suma, producto, cuadrática: U=B(p)chol(C), h=UUᵀ con derivadas exactas D.
Usar Gauss de AC sobre U lineal; producto también usa U(p)=p1ux+p2uy,
pero coeficientes de analytic_B(product), no los de cuadrática. Guardar SPD y
excluir sólo puntos no regulares con estado explícito. Contraste MP80/120
(tolerancia1e-60), float/MP≤1e-7. Reportar rangos sin redondear a cero.
SymPy verifica identidad de K para métrica cónica diag(1,R²w(φ)²) y para
métrica constante. Deducción: Ψ=∇θcomposición chol(C); producto y cuadrática
son homogéneos de grado2, por lo que la imagen regular es cónica; suma es lineal.
El cálculo simbólico universal, no una sustitución racional de pesos, decide
planitud analítica si se comprueban esas premisas. Si no se verifica, UNKNOWN;
no deducir K≡0 sólo de una malla. Producto no plano: proponer AE, no ejecutar.

## B: discretización y estacionarización

Reintegrar el IVP con parámetros AC y rtol1e-12, DOP853; muestrear a s=Lj/m,
mallas132/264/528. Fijar extremos exactos A,B. C0 recta muestreada igual.
Objetivo LIBRE: primitiva exacta de longitud por segmento recto de P, mismas
coordenadas z y cajas t[0,1],s[−.25,.25]. COCIENTE: x=x0+N0q, cada columna
N0 normal métrica unitaria inicial y fija por nodo; una coordenada por nodo.
Cotas q: intersección exacta de cajas físicas para esa recta normal. Esto es una
carta normal lineal local, no construcción de todo el cociente global. Eliminar
variaciones tangenciales permitidas no significa que la Hessiana ambiental cambie.

L-BFGS-B físico, maxiter2400,maxfun60000,maxls40,ftol1e-14,gtol1e-9.
KKT=||y−clip(y−g,Cy)||∞/max(1,|L|) en variables admisibles y. En LIBRE y=x;
en COCIENTE y=q, gq=N0ᵀgx, unidad de q es desplazamiento métrico. Registrar
además KKT físico completo en x, sin llamarlo KKT restringido ni exigir igualdad.
Auditoría MP80 completa inicial y final: FD locales1e-18/1e-22 por cada t,s,
proyectar después a q. AD/MP≤1e-6, pasos≤1e-20. Monitor cada200 aceptadas;
AD>2e-5 reinicia racha sin MP; de otro modo MP. Tres muestras consecutivas
verificadas KKT≤1e-5 interrumpen en ese punto, status99 nativo conservado.
Éxito nativo necesita auditoría final; límite sin éxito/racha INCONCLUSIVE.
No sustituir, reiniciar o seleccionar mejor estado anterior. Fallos conservados.
C0 también se ejecuta y valida; no éxito ficticio por omitir solver.

## B: instrumento de segundo orden

En cada final evaluable, aun inconcluso (sólo descriptivo), H=Hessiana AD física.
Marco nodal métrico ortonormal E=[T,N] basado en cuerda centrada final y h:
TᵀGT=NᵀGN=I,TᵀGN=0. G=JᵀhJ en z. No confundirlo con normal euclidiana de T.
Archivar espectros de H físico, EᵀHE completo, bloques TT,NN y Hessiana admisible
(COCIENTE N0ᵀHN0; LIBRE EᵀHE para decisión métrica). Son normas nodales,
no masa P1 de Y ni índice continuo. Umbral por bloque tau=max(1e-8,
1e-8 max|λ|), conservador frente a redondeo y escalas; no cero exacto.
Archivar para cada modo negativo completo métrico y normal y admisible su
vector en coordenadas z y coeficientes tangente/normal, λ, tau y fracción
ΣaT²/(ΣaT²+ΣaN²). La decisión usa **mínimo** de fracciones, aunque PR pide
máximo: guardar ambos y cada valor. Sin negativos, fracciones UNKNOWN.

Testigo MP80/120 del mínimo completo métrico y del mínimo admisible: pasos
1e-10/1e-12, Rayleigh vs AD relativo≤1e-5 y pasos≤1e-7, precisión≤1e-30.
Conservar pendientes distintas de cero, no proyectar a g⊥ ni ocultarlas.
Guardar Hessiana física completa en bandas de bloques2×2 (localidad por arista),
bloques TT/NN/TN en tres bandas y admisible en bandas; comprobar resto≤1e-10
relativo. Permite reconstrucción exacta dentro de tolerancia sin arrays densos.

## Controles e interpretación

C0 en todas mallas y ambas cartas: NN sin negativos; negativos ambientales,
si existen, fracción tangencial≥.9. Esfera unidad: misma longitud de polígono
por integración de la métrica a lo largo de segmentos **rectos en coordenadas**,
Gauss-Legendre32 contrastado con64 (H relativo≤1e-9), no distancia gran círculo.
Ecuador lat0,lon0..L; L=.75pi y1.5pi, cada malla132/264/528. Normal latitud,
tangente longitud; NN debe tener respectivamente0 y exactamente1 negativos.
Contrastar con FEM esperado: por arista NN=stiffness/Δlon−Δlon/6[[2,1],[1,2]],
error relativo≤1e-9. Cualquier control falla → corrida INVALID. No producto B.

H2 sólo si las seis cuadráticas pasan estacionariedad y controles, cada NN no
negativo, cada modo negativo LIBRE tiene fracción≥.9, y en COCIENTE el espectro
admisible no tiene negativos. Guardia adicional contra atribución vacía: exigir
al menos un modo negativo LIBRE por malla; sin él, INCONCLUSIVE sobre el origen
de negativas históricas. Ningún fallo se excluye. NN negativo en tres mallas:
H1 candidato **posible defecto del instrumento primero**, no contradecir K0
como hecho probado. Otros patrones INCONCLUSIVE. No certificados, mínimo
global, causa única ni confirmación independiente. No reinterpretar S–AC.

Presupuesto total2400s/corrida; restantes UNKNOWN si excede. Una corrida y una
reproducción exacta excluyendo tiempos. Guardar todas versiones; defecto requiere
nueva enmienda congelada y nuevo código/resultados sin sobrescribir. Sólo AD/**.
