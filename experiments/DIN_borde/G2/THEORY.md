# DIN-G2 · identidad, estimando e hipótesis empírica

## Manipulación del solapamiento

Para X|y=c~N(mu_c,s²I13), con prior uniforme y medias de distancia
2sqrt(3), la frontera Bayes entre dos clases es el bisector euclídeo.
La probabilidad de cruzar ese bisector desde una clase es
Phi(−sqrt(3)/s). No es el error multicategoría exacto (las dos regiones
de error se solapan), pero establece la escala de separación sin entrenar.
El escalado afín invertible ajustado en train no altera la información
Bayes del problema; sí cambia las entradas y el condicionamiento de la red.

La muestra base epsilon se mantiene a través de s. No se ha intervenido
aisladamente sobre Mal: s modifica simultáneamente la dificultad, la Fisher,
los gradientes y la dinámica de entrenamiento. Una asociación entre V y D
no identifica un efecto causal de la variación de resolución.

## La parte algebraica de D2b

Con los instrumentos originales,

    M_nm = r_nᵀ(F+gamma I)⁻¹r_m,
    r_n = (1−p_y,n) h_n.

Esto fuerza un factor residual en cada fila/columna, pero h_n, F y gamma
también dependen de la red. Sólo bajo rango interpolante y ridge despreciable
se aproxima M≈n diag((1−p_y)/p_y). Tampoco esa aproximación obliga a que las
odds se concentren en un único índice o predice la evolución10→250.

Para una forma estrictamente coordenada M=m e_k e_kᵀ y caras pequeñas,
rho_caras=sqrt(m)/n; con una cara masiva puede disminuir, como mostró D2.
La homogeneidad rho(cM)=sqrt(c)rho(M) es exacta; colapso y dinamismo no lo son.
R250 y Y250 pueden quedar ligados casi algebraicamente después del colapso.
Por eso D_X|R es una descomposición descriptiva con una covariable del tiempo
final, no una validación de un mediador causal ni un predictor disponible en10.

## Qué se está prediciendo

El algoritmo C1 original centra Y y X dentro de cada split, normaliza L
globalmente y centra sus tres potencias dentro del split. Los diez bloques
separan splits completos y comparan SSE con y sin X. Se reutilizan exactamente
esas operaciones y semillas, sin ejecutar su CLI o leer su cohorte.
Este estimando describe diferencias entre inicializaciones de splits completos;
el centrado de Y usa las medias de esos grupos, y no constituye por sí solo
un sistema operativo que conozca la media futura de un nuevo split.

Un D positivo sólo mejora a ESA base cúbica de log rho10. No prueba información
nueva respecto a toda función de L, no elimina error de medida de rho ni evita
toda especificación incorrecta. Las permutaciones de X dentro del split son
las del estimando heredado y aquí sus p se etiquetan exclusivamente exploratorios.

## Variancia con cinco inicios y regla H-var

Si m de cinco inicios terminan con el dominante mal clasificado,

    p_s=m/5; var_s=m(5−m)/25 ∈ {0,.16,.24};
    V=sum_s m_s(5−m_s)/500.

Se computa V con ese numerador entero para respetar exactamente los cortes
racionales .04 y .08, sin ambigüedad de redondeo al sumar Bernoulli.
El dominante final puede ser un ejemplo diferente en cada inicialización:
V cuantifica el indicador operacional pedido, no la resolución de un
individuo común fijado antes de entrenar. Se reporta la frecuencia modal
de su identidad para hacer visible esa distinción.

No hay teorema que obligue a D a seguir V. H-var es la predicción empírica
congelada: máximo interior, alineación con la mayor V y asociación positiva
entre seis niveles. Esos seis puntos no son seis pruebas independientes:
comparten20 réplicas y pesos/lotes emparejados. Los umbrales de apoyo/contradicción
son descriptivos y no se ajustan después de observar el patrón.
