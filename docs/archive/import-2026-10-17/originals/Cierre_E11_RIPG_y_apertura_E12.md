# RIPG — cierre de E11 y punto de partida de E12

**Fecha de cierre:** 23 de septiembre de 2026  
**Decisión:** E11 queda cerrado. E12 se continuará en otro chat.

## Resultado central de E11

La teoría conserva una base geométrica consistente, pero pierde la interpretación de una única distancia como marcador universal de generalización. La cantidad operativa vigente es

\[
G_{\rho,\mathcal U}
=B_{\mathcal U}
\left(F_{\mathcal U}+\rho\,\lambda_{\max}(F_{\mathcal U},H_{\mathcal U})H_{\mathcal U}\right)^{-1}
B_{\mathcal U}^{T},
\]

donde deben declararse el funcional de perspectiva (S_P), la referencia tensorial (H), la escala (ho), el panel Fisher y el alcance tangente \(\mathcal U\). La expresión es covariante cuando (H) se transporta correctamente, pero esas elecciones todavía impiden llamarla canónica.

El corte de autovalores de la matriz Fisher cruda queda descartado como procedimiento intrínseco: puede cambiar bajo reparametrizaciones no ortogonales. La regularización suave de E11-J evita saltos de rango, pero define una geometría condicionada por (H) y (ho).

## Qué establecieron los controles E11-A–O

- La variabilidad dentro de un mismo estado debida al panel puede superar la deriva temporal; se requieren paneles independientes y suficientemente grandes.
- La distancia true/random depende del observable (S_P), el tratamiento espectral, la carta o referencia y el alcance tangente.
- La réplica externa de Wisconsin reprodujo (D_{\mathrm{random}}<D_{\mathrm{true}}) en promedio, aunque con dispersión entre semillas.
- Cambiar el alcance tangente invirtió el signo del contraste en el control sintético: salida (-1.779), últimas dos capas (+2.823), red completa (+3.549).
- La descomposición de Schur a escala común permitió atribuir contribuciones de bloques manteniendo
  \[
  G_{E\cup U}=G_E+\Delta G_{U\mid E},\qquad \Delta G_{U\mid E}\succeq0.
  \]
- En Digits, el contraste oculto fue positivo en 20/20 semillas; en Wisconsin fue positivo en 12/20 y mostró heterogeneidad entre particiones. La distancia temporal oculta tampoco es universal.

## Hipótesis prioritaria que pasa a E12

La participación oculta normalizada

\[
\boxed{\eta=\frac12\operatorname{tr}\!\left(G_{\mathrm{full}}^{-1}\Delta G_{\mathrm{hidden}\mid\mathrm{output}}\right)}\in[0,1]
\]

es invariante bajo cambios de coordenadas de perspectiva por congruencia. En los paneles completos:

| Datos | Inicial | True | Random | Resultado |
|---|---:|---:|---:|---|
| Digits | 0.289 | 0.349 | 0.786 | random > true, 20/20 |
| Wisconsin | 0.360 | 0.480 | 0.860 | random > true, 20/20 |

En subpaneles se mantuvo en 40/40 comparaciones agregadas entre ambas tareas. Este resultado justifica priorizar \(\eta\), pero sólo se han usado dos conjuntos naturales; no constituye todavía una ley de generalización.

## Hipótesis cerradas o debilitadas

1. No hay evidencia para tratar (D_G) como escalar universal de generalización.
2. No hay un signo universal del contraste true/random de las trayectorias.
3. No apareció un predictor temprano robusto ni una firma general del optimizador.
4. No se estableció causalidad.
5. La magnitud de la deformación no equivale a su organización o coherencia.

## Curvatura y holonomía

La curvatura queda **abierta**, no descartada. Que \(\omega_P=dS_P\) sea exacta sólo da \(d\omega_P=0\); no fuerza \(\nabla\omega_P=0\), curvatura nula ni holonomía trivial.

La holonomía deja de ser un frente independiente: en E12 debe usarse como validación derivada de la curvatura. El control histórico de E6 —ángulo (-4.907906\times10^{-5}\) rad frente a integral (-4.908089\times10^{-5}\), discrepancia (1.82\times10^{-9}\)— es consistente, pero precede a la formulación final de admisibilidad, cociente y regularización. No valida por sí solo la teoría vigente.

## Camino natural para E12

1. **E12-A:** prueba de canonicidad y robustez de \(\eta\) frente a (\rho), (H), observables y particiones.
2. **E12-B:** construir un campo no lineal admisible (P\mapsto S_P\) y verificar (BK=0) localmente.
3. **E12-C:** calcular conexión de Levi-Civita y curvatura del campo (P\mapsto G(P;\theta)).
4. **E12-D:** comparar la evolución de la curvatura bajo true/random con controles de panel y semilla.
5. **E12-E:** verificar holonomía como consecuencia local, \(\mathrm{Hol}(\gamma)\approx\int_\Sigma K\,dA\), para lazos pequeños.

## Texto de reanudación para el próximo chat

> Continuar RIPG desde E12-A. E11 está cerrado. Mantener el axioma \(\omega_P\in K^\circ\) y (BK=0); usar el estimando regularizado covariante con (S_P,H,\rho\), panel y alcance tangente declarados. No reabrir (D_G) como escalar universal. La hipótesis empírica prioritaria es la participación oculta normalizada \(\eta\). Primero probar su canonicidad; después construir el campo (P\mapsto G(P;\theta)), calcular curvatura y usar holonomía sólo como control derivado.
