# AE · geometría softmax y objetos distintos

E12-B/C proporcionan la forma de la familia, no resultados transferibles a E16.
Con observaciones y θ fijos, rasgos estandarizados f∈R², scores r_n de Bernoulli,
a_n(P)=exp(P·f_n)/Σexp(P·f_l), μ=Σa_nf_n y C=(F+.01I)⁻¹,

$$X(P)=\sum_n a_n(P)r_n\,\mathrm{chol}(C),\quad
U_i=\partial_iX=\sum_n a_n(f_{ni}-\mu_i)R_n,\quad h=UU^T.$$

R_n=r_n chol(C). Su segunda derivada es

$$S_{ij}=\sum_n a_n[(f_{ni}-\mu_i)(f_{nj}-\mu_j)-\mathrm{Cov}_{ij}]R_n.$$

Γᵏᵢⱼ=hᵏˡ<U_l,S_ij>. La parte normal II_ij=S_ij−ΓᵏᵢⱼU_k da

$$K=(\langle II_{00},II_{11}\rangle-\|II_{01}\|^2)/\det h.$$

La inmersión de pesos softmax no es homogénea de grado2: no aplica la prueba
cónica de AD. La regularización es la absoluta de E16, no la relativa de E12.
La geometría depende de rasgos, panel, θ y C fijados; no se afirma canonicidad.
Los scores anulan kernel Fisher por la construcción de E12; eso no convierte
la inversa regularizada en la inversa no regularizada ni elimina sus condiciones.

## Exponencial, Jacobi y área

La velocidad inicial v=chol(h0)⁻ᵀ(cosθ,sinθ) tiene norma métrica1. El tiempo
s de p̈ⁱ=−Γⁱⱼₖṗʲṗᵏ es longitud de arco. Jacobi normal cumple
j''+K(p(s))j=0,j(0)=0,j'(0)=1. Ceros interiores son conjugados en la rama
regular. K positiva en un punto no garantiza un cero a π/√K(P0): para controlar
foco hacen falta condiciones a lo largo de la curva. La escala local es heurística.

Antes de degeneración e inyectividad, el jacobiano polar es j y

$$A(r)=\int_0^{2\pi}\int_0^r j(s,θ)\,ds\,dθ.$$

Se integra I'=j con la geodésica, no se identifica área con área euclidiana del
polígono del frente. Tras conjugados no se usa la integral firmada como área
embebida. Ausencia de cruces propios en frentes muestreados no certifica
inyectividad entre rayos/radios, ni detecta por sí sola contactos tangentes.

Un primer conjugado, un cruce del frente entre segmentos no adyacentes, una
salida del dominio y un cambio de candidato más corto son cantidades distintas.
Un cruce poligonal es un candidato con intervalo radial/ángulos inciertos;
no se presenta automáticamente como locus de corte. Una salida regional es
censura aunque la métrica siga existiendo fuera: no es degeneración física.

## Índice normal y corte

Los puntos de la geodésica se muestrean sin reoptimizar. La carta normal fija
p_j+q_j n_j usa normales métricas unitarias. La Hessiana normal se obtiene por
AD de longitud integrada en segmentos rectos, contrastada entre cuadraturas;
no se sustituye por el operador de Jacobi para obtener el salto esperado.
Su gradiente residual se guarda y controla; aproximación estacionaria no es
estacionariedad exacta ni certificado de inercia continua. Se archivan bandas,
espectros y componentes negativas cuando existen.

Sin conjugado observado no se inventan objetivos antes/después de él. Los
extremos exploratorios fijos pueden tener índice0 sin probar la predicción de
salto0→1. Shooting multiángulo enumera candidatos en el conjunto de arranques
fijado, no todas las ramas; el más corto encontrado no es un mínimo global.

## MP, censura y puente descriptivo

MP50/80 verifica geometría en la fase0 y cuatro rayos completos mediante RK4
512/1024: endpoint, Jacobi e integral de área, con tolerancia1e-5. La trayectoria
MP no usa interpolación de la trayectoria float. No cubre todos los rayos ni
es aritmética de intervalos. Los testigos de índice usan diferencias MP80 de
la longitud con cuadratura, no sólo diferencias float.

El puente con T2-A1 reporta objetos de supervivencia/censura sin leer o ejecutar
sus instrumentos. r_deg,A(r_deg) permanecen UNKNOWN cuando el evento no se
observa. A(r_safe) y una cota radial muestreada no se renombran A(r_deg).
La fracción de cobertura individual sin conjugado no basta para afirmar ausencia
de colisión con otros rayos cuya trayectoria ya quedó censurada. Ese defecto
de resumen v1 requiere corrección versionada, conservando v1 íntegra.
