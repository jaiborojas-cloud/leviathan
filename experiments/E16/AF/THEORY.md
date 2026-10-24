# AF · convenciones y calibración sintética

Se leyeron exclusivamente geometry.py y audit.py autorizados, sin ejecutar
main/load/boundary/jacobi/rk ni abrir datos de T2. geometry.py se importa tras
verificar SHA256 b4d1e0e413170a337411af82231b3e072565f515521e98b2f33e8bdb44e0bdf3.
La carta es P∈R², a=softmax(fP), J_ni=a_n(f_ni−μ_i),
H_nij=a_n[(f_ni−μ_i)(f_nj−μ_j)−Cov_ij], g=JᵀMJ.
jet devuelve g,g⁻¹,H,<J,H>_M,Γ; eval devuelve √detg,K por Gauss de componentes
normales H−JΓ. M es constante SPD, no Fisher aprendido ni un estado de T2.

rays usa velocidad chol(g0)⁻ᵀ(cosθ,sinθ), de norma métrica1; su tolerancia
por defecto2e-10 no es la solicitada para etapa2. jacsolve de audit integra
p,v,j,j' a2e-10/2e-12 con orden(6,n), usando j''+Kj=0,j0=0,j'0=1.
AF llama ese jacsolve intacto sólo para predictores cortos y contrasta después
el integrador propio DOP8531e-12. No se modifica código archivado. area7 integra
√detg en triángulos de la carta con regla Dunavant7; triangles crea anillos
radiales y usa origen0. Antes del primer evento es área aproximada del disco,
condicionada a inyectividad; los controles/meshes no son intervalos rigurosos.

## Por qué escalar sólo f no basta

Para f_s=s f y M fijo, g_s(P)=s²g(sP): cambio de carta, K_s(0)=K(0).
AF conserva M=QQᵀ/27+εI pero escala también su amplitud. Primero fija una base
por semilla, mide κ=K_base(0) sin geodésicas, y usa α=max(|κ|,1e-6)/T,
Q_s=√α Q_base,ε_s=α*.1,f_s=.0004√T f_base para T=1,10,1000,10000.
Entonces M_s=αM_base y K_s(0)=κ/α≈sign(κ)T. No se cambia signo ni se
seleccionan semillas; una κ casi nula se conserva como calibración inconclusa.

La base es gaussiana estandarizada por columna(ddof0). Q tiene una primera
columna3u, donde u es la componente de f1²+f2² ortogonal a(1,f1,f2), normalizada
a norma√27; las otras26 columnas son gaussianas de desviación.1. ε_base=.1.
Este sesgo radial de familia se declara ANTES de K/geodésicas; no es M isotrópica
pura ni una estimación tomada de T2. Persigue curvatura central visible sin
seleccionar supervivientes. Ningún signo ni evento se garantiza por construcción.

Las40 filas están emparejadas por10 semillas y4 escalas, no son40 réplicas
independientes. Parte de las asociaciones de curvatura/radio provendrá de la
calibración métrica; no se interpretará como ley causal, validación externa o
transferencia predictiva a T2. No se entrenan redes ni se leen sus estados.

## Eventos y censura

Conjugado: cero interior de j. Colisión: primer frente poligonal no simple,
con intervalo radial refinado; no es certificado del locus de corte.
Escape: ||P||∞=150, caras±P1/±P2; se guarda también norma euclidiana.
Es un evento operacional de carta de AF, no prueba de singularidad de la métrica.
Fracciones de a, Neff y tendencia radial describen aproximación observada al
borde del simplex; el límite asintótico sigue UNKNOWN.
Un fallo numérico antes de evento no se rellena con escape ni censura enRmax.
Rmax sin evento es censura por la derecha. Tipos simultáneos a tolerancia se
conservan múltiples. A_emb es límite muestreado desde antes del primer evento,
convergencia angular/radial y contraste MP local, no integral MP completa.
