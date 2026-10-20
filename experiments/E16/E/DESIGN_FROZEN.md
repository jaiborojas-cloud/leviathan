# E16-E — Diseño previo: distancias y anisotropía relativa

Análisis exploratorio de los mismos 12 estados, tres paneles y tres puntos de
[E16-D](../D/README.md). No constituye réplica independiente ni confirmación de
una hipótesis descubierta aquí. No se entrenan redes ni se seleccionan casos.
Los hashes de configuración y método D quedan fijados en config.json.

Pregunta: conservándose rango 2, ¿cómo cambian tamaño y forma de la métrica del
producto y cuadrática respecto a la suma? Se calculan las 216 comparaciones,
sin predicción de dirección, magnitud o significación estadística.

## Estimandos

Para cada estado/panel/punto, G=h_suma y H=h_composición, construidos mediante
las derivadas analíticas de D y su cométrica regularizada C=(F+0.01 I)^(-1).
Si G=L Lᵀ, los autovalores positivos λ de L^(-1) H L^(-T) son los del par (H,G).
No se usa la condición espectral de H aislada, dependiente de coordenadas.

- ℓ_i=log λ_i, μ=(ℓ_1+ℓ_2)/2.
- Distancia afín invariante entre tensores SPD: d=sqrt(ℓ_1²+ℓ_2²).
- Escala métrica: exp μ; escala isotrópica de longitudes: exp(μ/2).
- Distancia de forma: s=sqrt(Σ(ℓ_i−μ)²); d²=2μ²+s².
- Anisotropía relativa: κ=λ_max/λ_min; s=log κ/sqrt(2).
- Razones extremas de longitud tangente: sqrt λ_min, sqrt λ_max.
- Razón de elemento de área: sqrt(det H/det G)=exp μ.

Estas son distancias entre métricas en un punto, no geodésicas entre perspectivas.
Las cotas de longitud son locales; no certifican distancias finitas ni curvatura.
La escala depende de las unidades y de la elección de los escalares S1/S2.
Incluso la forma se interpreta respecto a esta familia y cométrica declaradas.

## Controles y decisión numérica

Calcular todo a 80 y 120 cifras; comparar cada observable con error relativo
|a−b|/max(1,|a|,|b|)≤1e-40. En cada comparación comprobar las identidades anteriores
y las tres congruencias simultáneas (G,H)→(JᵀGJ,JᵀHJ), con J en config.json.
Control G=[[2,1],[1,3]]: identidad; H=4G (s=0,d=sqrt(2)log4); y H=L diag(4,1/4)Lᵀ
(μ=0,s=sqrt(2)log4). Negativo: usar sólo autovalores ordinarios en H=diag(1,4),
G=I y J=diag(2,1); su condición cambia de 4 a 1 mientras κ relativa sigue 4.

No corregir matrices, añadir piso espectral ni omitir casos. SPD fallida:
INCONCLUSIVE y conservar caso; control o identidad fallida: FAIL; todo satisfecho:
PASS_NUMERICAL. Precisión múltiple es evidencia numérica, no certificado intervalar.

## Salidas y límites

CSV por caso con autovalores, distancias, escalas, anisotropía y cotas tangentes;
JSON con mínimo/mediana/máximo por composición y panel, sin pruebas de significación.
Contar s>1e-8 y d>1e-8 sólo como separación numérica, no efecto científico mínimo.
Guardar controles, procedencia, recursos y manifest. Repetir y comparar salidas
científicas byte a byte; recursos separados. Presupuesto 120 s y 512 MiB por corrida.
No ampliar muestra ni cambiar umbrales según los resultados. Congelar este documento
y config antes de escribir el programa o calcular observables.
