# DIN-D9g-c: ridge y el componente fuera del diccionario

Sean Z los21términos baratos transformados sólo con entrenamiento, y c,Y centrados
por grupo. La base resuelve:

\[
\hat b_\lambda=\arg\min_b n^{-1}\|Y-Zb\|^2+\lambda\|b\|^2.
\]

λ se escoge con CV interna en el entrenamiento exterior. Todos los21coeficientes
están penalizados; no hay intercepto tras centrar. La escala por n evita cambiar
la interpretación de λ entre bloques, mitades y agregado.

Añadir c cruda sin penalizar puede mejorar una ridge aun si c=Za, porque deja a
esa dirección eludir la penalización. El responsable escogió el siguiente estimando:

\[
\hat a=Z_{tr}^{+}c_{tr},\quad
r_{tr}=c_{tr}-Z_{tr}\hat a,\quad r_{te}=c_{te}-Z_{te}\hat a,\qquad
\hat\gamma=\frac{r_{tr}^{\!T}(Y_{tr}-Z_{tr}\hat b_\lambda)}{r_{tr}^{\!T}r_{tr}}.
\]

La predicción completa es Z_te b_λ + r_te γ. Como Z_trᵀr_tr=0, es equivalente al
ajuste conjunto que penaliza los coeficientes de Z y deja r sin penalizar. La
base ridge no cambia al añadir r; el coeficiente γ depende del componente OLS
fuera del diccionario. Que γ completo coincida con el OLS parcial de21términos
es consecuencia de esa ortogonalidad, no evidencia de una nueva medición.

Si c pertenece al espacio de Z, r_train es cero: se registra alias y no existe
un coeficiente adicional identificable. La tolerancia relativa1e-10 se fijó antes
del código. El control negativo q0²/producto confirma ese caso de construcción;
no certifica calibración para cualquier dependencia o misspecificación.

D=1−SSE_completo/SSE_base y D_base=1−SSE_base/SSE_0, sobre10bloques externos.
Se elige BR si D_base(BR)≥D_base(B1)−.005, antes de mirar el incremento de c.
La elección se repite con cada permutación junto a λ/proyección/ajuste. Como la
base no usa c, los scores internos y λ son invariantes a la permutación de c;
cachear su SVD conserva exactamente el problema. Cada repetición sí vuelve a
calcular scores y argmin; el control sin caché reajusta todo desde cero.

Un D negativo no es prueba de independencia o de efecto exactamente cero. La
regla REDUNDANTE es predictiva y exploratoria. El residuo OLS de c se estima
con muestras finitas y puede generalizar con variabilidad, aun con Y regularizada.
El test grande continúa siendo finito y ya gastado para descubrir. La decisión
sobre confirmatorio/Q13 sigue siendo del responsable; esta etapa no usa C2.
