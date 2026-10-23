# Norma consistente y nuevas variables de refinamiento

Y compara dos espacios de desplazamientos sobre la misma poligonal base,
sin reoptimizarla. La imagen y la longitud se conservan por subdivisión exacta;
la estacionariedad respecto de todas las variables nuevas no se conserva por
esa identidad.

## Masa P1 sobre un parámetro de referencia

Para cada fuente se normaliza su longitud de arco euclídea en (t,s), con
pesos δj=‖zj+1−zj‖/Σ‖Δz‖. La masa consistente de un desplazamiento lineal
por arista tiene bloque local, por componente,

$$M_j=\frac{\delta_j}{6}\begin{pmatrix}2&1\\1&2\end{pmatrix}.$$

Los extremos están fijos. Al insertar puntos medios, cada peso se divide en
dos. Para el transporte lineal S se tiene Mf y Mc compatibles:

$$S^TM_fS=M_c.$$

Por tanto, la norma de un desplazamiento transportado no aumenta sólo porque
hay más nodos. Esta masa es una norma de referencia de desplazamientos, no
Fisher ni longitud de arco intrínseca. Cada fuente tiene su propio parámetro;
la comparación emparejada es coarse/fine de esa fuente.

## Problema generalizado restringido

Se resuelve

$$\mu_1=\min_{v^TMv=1,\;g^Tv=0}v^THv.$$

Si B genera g⊥, corresponde al problema generalizado de (BᵀHB,BᵀMB).
Su estacionariedad satisface Hv−μMv=αg; se valida el residuo proyectado.
Los números no son directamente comparables con los de X, que usaba vᵀv=1.
Para gradiente por debajo del umbral se conserva el espacio completo.

La identidad de longitud Lf(Sz)=Lc(z) implica en aritmética exacta

$$S^Tg_f=g_c,\qquad S^TH_fS=H_c.$$

Esto no implica gf≈0 si gc≈0: el gradiente fino puede ser grande en direcciones
que no son transporte de variables gruesas. Y mide sus componentes nuevas
por diferencias finitas MP, sin reutilizar el gradiente grueso como si fuera fino.

Con gradientes exactos y masas compatibles, los transportes de direcciones
gc⊥ pertenecen a gf⊥ y el mínimo fino no puede ser mayor que el grueso.
Y contrasta esa desigualdad con tolerancia; no exige que los mínimos estén
cerca ni deduce convergencia de una sola subdivisión.

## Auditoría direccional y dos umbrales

La dirección mínima generalizada se limpia en MP del pequeño residuo de
restricción float. Para evaluar la referencia se escala a máximo desplazamiento
nodal uno. La curvatura central se divide entre su masa vᵀMv para reconstruir
el Rayleigh generalizado. No se confunde esta amplitud con norma de masa uno.

La banda espectral depende de max|μ| del espectro. Puede ensancharse al refinar,
y contener autovalores negativos de baja magnitud o positivos débiles.
Por separado se informa un testigo MP direccional negativo con umbral propio,
tras pasar sus auditorías. Esa evidencia direccional no certifica el error
de todos los autovalores ni cambia sus clases espectrales guardadas.

En C0, el espacio tangencial recto sigue siendo nulo en aritmética real.
La masa puede amplificar el redondeo del Hessiano y del eigensolver. Un pequeño
mínimo float negativo no basta para atribuir inestabilidad si la curvatura MP
correspondiente es casi nula. Los controles y umbrales se conservan sin ajuste.

## Qué queda abierto

Añadir variables a un candidato no equivale a producir un nuevo candidato fino
estacionario. Curvatura fina negativa en un punto con gradiente nuevo importante
no certifica silla exacta ni permite afirmar estabilidad de mínimos optimizados.
No hay nuevos datos de confirmación, convergencia continua o mínimos probados.
