# E12-E — holonomía como control derivado y cierre de E12

## Objetivo

E12-E verifica que la conexión y la curvatura calculadas en E12-C satisfacen, para lazos decrecientes,

\[
\operatorname{Hol}(\gamma)
\approx
\int_{\Sigma_\gamma}K\,dA.
\]

La holonomía no se trata como una hipótesis independiente. Su función es comprobar mediante transporte paralelo la consistencia del campo métrico, la conexión de Levi-Civita y la curvatura ya obtenidos.

## Protocolo

Se seleccionaron cuatro regiones de los atlas de E12-C:

1. `digits-true`, \(P=(0,0)\): curvatura negativa fuerte;
2. `digits-random`, \(P=(0,0)\): curvatura cercana a cero;
3. Wisconsin `true`, \(P=(0.4,0.4)\): región positiva;
4. Wisconsin `true`, \(P=(-0.4,-0.4)\): región negativa.

Alrededor de cada centro se construyeron cuadrados antihorarios de lado

\[
L\in\{0.20,0.10,0.05\}.
\]

El vector se transportó resolviendo

\[
\frac{dv^k}{dt}
+\Gamma^k_{ij}(P(t))\dot P^i v^j=0.
\]

Cada arista se dividió en dos segmentos y cada actualización usó

\[
v_{m+1}=\exp(-A_m)v_m,
\qquad
(A_m)^k{}_j
=\Gamma^k_{ij}(P_{m+1/2})\Delta P^i.
\]

El ángulo final se midió en la métrica del punto base. De forma independiente, el flujo se aproximó con cuadratura de Gauss \(2\times2\):

\[
\Phi_K=\int_{\Sigma_\gamma}K(P)\sqrt{\det G(P)}\,dP^1dP^2.
\]

## Resultado completo

### Digits — aprendizaje verdadero, curvatura negativa fuerte

| Lado | Ángulo de holonomía | Flujo de curvatura | Error relativo |
|---:|---:|---:|---:|
| 0.20 | −0.031699 | −0.031772 | 0.231 % |
| 0.10 | −0.007942 | −0.007947 | 0.0603 % |
| 0.05 | −0.001987 | −0.001987 | **0.0152 %** |

El error se reduce 15.2 veces entre el lazo mayor y el menor.

### Digits — memorización aleatoria, campo casi plano

| Lado | Ángulo de holonomía | Flujo de curvatura | Error relativo |
|---:|---:|---:|---:|
| 0.20 | −0.026488 | −0.026503 | 0.0558 % |
| 0.10 | −0.006664 | −0.006664 | 0.0146 % |
| 0.05 | −0.001668 | −0.001669 | **0.0037 %** |

El error se reduce 15.0 veces.

Aunque \(K\approx-0.0076\) es pequeño, \(\det G\) es grande en este atlas. Por eso el área intrínseca de un cuadrado de tamaño coordenado fijo es mucho mayor y el flujo \(K\,dA\) no tiene que ser pequeño. La holonomía depende del producto entre curvatura y área intrínseca, no de \(K\) aislado.

### Wisconsin true — región positiva

| Lado | Ángulo de holonomía | Flujo de curvatura | Error relativo |
|---:|---:|---:|---:|
| 0.20 | +0.008852 | +0.008881 | 0.328 % |
| 0.10 | +0.002171 | +0.002169 | 0.0740 % |
| 0.05 | +0.000539 | +0.000539 | **0.0337 %** |

El error se reduce 9.7 veces. El signo positivo de la curvatura se reproduce en el sentido de rotación del vector transportado.

### Wisconsin true — región negativa

| Lado | Ángulo de holonomía | Flujo de curvatura | Error relativo |
|---:|---:|---:|---:|
| 0.20 | −0.001478 | −0.001477 | 0.0585 % |
| 0.10 | −0.000369 | −0.000369 | 0.0287 % |
| 0.05 | −0.000092 | −0.000092 | **0.0081 %** |

El error se reduce 7.2 veces y la orientación cambia respecto a la región positiva del mismo atlas.

## Controles

| Control | Resultado |
|---|---:|
| Casos | 4 |
| Lazos | 12 |
| Error máximo del solucionador | \(5.00\times10^{-8}\) |
| Error relativo máximo de norma transportada | 0.120 % |
| Error máximo en esfera unitaria | 0.139 % |
| Error decreciente al contraer el lazo | 4/4 casos |

La autoprueba de esfera usa la conexión exacta de

\[
ds^2=d\vartheta^2+\sin^2\vartheta\,d\varphi^2,
\qquad K=1,
\]

y reproduce el flujo de área con el mismo integrador. Su error también decrece aproximadamente de segundo orden.

## Interpretación geométrica

El control confirma tres hechos:

1. la conexión calculada en E12-C transporta vectores de forma consistente con la curvatura de Riemann;
2. el signo de \(K\) determina la orientación local de la holonomía para lazos pequeños;
3. la cantidad integrada es \(K\,dA\), por lo que comparar holonomías de lazos con el mismo tamaño coordenado puede confundir curvatura con expansión del área métrica.

Para comparaciones futuras entre regímenes conviene fijar **área intrínseca**, no sólo lados en coordenadas de perspectiva.

## Estado de la holonomía

La holonomía no fue descartada. Queda validada en la formulación vigente como consecuencia derivada de la curvatura:

\[
\boxed{
\theta_{\mathrm{hol}}(\gamma)
=\int_{\Sigma_\gamma}K\,dA+o(\operatorname{Area})
}

para lazos decrecientes y con la convención de orientación adoptada.

No aporta por sí misma una nueva variable independiente de generalización. Sí constituye un control geométrico fuerte del campo RIPG.

## Cierre de E12

E12 completa la cadena:

\[
P\mapsto S_P
\mapsto \omega_P=d_\theta S_P
\mapsto B(P)=d_P\omega_P
\mapsto G(P;\theta)
\mapsto \Gamma
\mapsto R,K
\mapsto \operatorname{Hol}(\gamma).
\]

Los resultados consolidados son:

1. **Canonicidad condicionada:** \(\eta\) es robusta en las familias examinadas, pero no independiente de \(H\) ni \(\rho\).
2. **Campo admisible:** la familia exponencial de perspectivas satisface \(BK=0\) en todo el vecindario y mantiene rango dos.
3. **Curvatura intrínseca:** los campos son no planos, con signo y magnitud dependientes de tarea y régimen.
4. **Aprendizaje:** `random` produce gran participación oculta y expansión métrica, pero curvatura cercana a cero; `true` conserva o genera mayor \(|K|\) en 36/40 pares.
5. **Holonomía:** el transporte alrededor de lazos reproduce el flujo de curvatura con error decreciente.

La lectura más precisa al cierre es:

> La memorización aleatoria puede producir una geometría extensa y dominada por capas ocultas, pero intrínsecamente casi plana. El aprendizaje verdadero tiende a mantener una organización curvada más rica, aunque su signo y evolución dependen de la tarea.

Esto es evidencia exploratoria condicionada al funcional de perspectiva, referencia, regularización, arquitectura y panel. No constituye todavía una ley universal ni una explicación causal.

## Siguiente frontera

E12 deja lista una geometría diferencial completa. El paso posterior no debería añadir otra cantidad geométrica local sin una pregunta nueva. Las opciones científicas naturales son:

1. réplica preregistrada de \(|K_{true}|>|K_{random}|\) en nuevas tareas y arquitecturas profundas;
2. estudiar si energía de curvatura o heterogeneidad espacial predicen generalización fuera de muestra;
3. fijar lazos de igual área intrínseca para comparar holonomía entre regímenes;
4. investigar la relación entre la participación oculta \(\eta\), expansión de área y aplanamiento de curvatura.

## Reproducción

El paquete incluye transporte paralelo, integración de flujo, resultados por lazo, control de esfera, auditoría y las dependencias analíticas de E12-C.
