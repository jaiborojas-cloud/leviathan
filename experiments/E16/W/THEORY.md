# Primer orden nulo en una dirección proyectada

Sea g el gradiente MP archivado del candidato original, v la dirección mínima
unitaria recuperada de T y H el Hessiano de longitud en coordenadas (t,s).
Para ‖g‖ por encima del umbral congelado se usa

$$q=v-g\frac{g^Tv}{g^Tg},\qquad w=\frac{q}{\|q\|}.$$

Es una proyección ortogonal euclídea sobre g⊥. En aritmética exacta gᵀw=0,
si q no es nulo. No se usa una proyección Fisher ni se modifica el punto base.
La normalización se hace en MP antes de construir las perturbaciones.

Si ‖g‖≤1e-25 se evita dividir por un gradiente pequeño y se normaliza v,
ruta SMALL_GRADIENT. Esto no equivale a afirmar que g sea exactamente cero.
Si ‖q‖≤1e-8 se conserva DEGENERATE sin dirección sustituta. El signo canónico
sólo fija representación; se evalúan ambos sentidos de cada dirección.

## Una proyección no resuelve el problema espectral restringido

Aunque v sea un autovector mínimo de H, w en general no minimiza

$$\min_{\|u\|=1,\;g^Tu=0}u^THu.$$

Proyectar v y diagonalizar H restringido a g⊥ son operaciones distintas.
Una curvatura positiva de w no demuestra que todo el subespacio sea positivo.
Si la curvatura cambiara al proyectar, tampoco invalidaría el autovalor original.
El punto, el Hessiano y la dirección están cumpliendo papeles diferentes.

Una componente pequeña añadida o sustraída puede elevar mucho un Rayleigh
cuando H tiene direcciones rígidas. Un ángulo pequeño entre v y w no impone
que sus curvaturas sean próximas sin controlar también la norma de H.

## Comprobación separada de pendiente y curvatura

Las columnas MP archivadas de S definen la proyección. W contrasta su pendiente
contra diferencias finitas centrales de la longitud, con pasos 1e-10/1e-12 en
MP80/MP120, sin repetir la auditoría de cada componente del gradiente de S.
Se exige pendiente proyectada ≤1e-18 normalizada, además de la ortogonalidad
al gradiente archivado. No se declara un cero exacto ni una cota rigurosa.

La curvatura central se contrasta con wᵀHw, calculado por AD usando la
proyección float del vector sólo para ese diagnóstico. Las longitudes usan
los vectores MP sin esa conversión. Dos pasos y dos precisiones verifican
consistencia, no una garantía de error por intervalos.

## Perturbaciones finitas

Para c=max(1,|L(x)|) y la dirección w se registran

$$\Delta_\pm=\frac{L(x\pm hw)-L(x)}c,\quad
E=\frac{\Delta_++\Delta_-}2,\quad O=\frac{\Delta_+-\Delta_-}2.$$

Si la pendiente fuera exactamente cero y L suave, E empieza con
h²wᵀHw/(2c), mientras O puede contener términos cúbicos. Anular primer orden
no fuerza simetría exacta ni descenso a paso finito. W registra los dos signos,
la derivada auditada, las predicciones y los residuos, sin reajustar pasos.

Las cotas geométricas de U siguen siendo numéricas euclídeas en la carta.
El control de cajas y positividad métrica corresponde a los nuevos ensayos,
sin cambiar resultados de S/T/U/V. Son los mismos datos exploratorios; no hay
confirmación independiente, mínimo certificado o prueba de silla exacta.
