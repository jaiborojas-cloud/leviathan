# DIN-G3 · estimando, potencia condicional e interpretación

## Estadístico C1 y aceleración de planificación

Sea B la base cúbica centrada intra-split, y un fold que deja splits completos
fuera. El modelo ampliado añade x=Xc. Si r=x_train−B_train B_train^+x_train,
la pendiente parcial es t=rᵀY_train/(rᵀr), por Frisch–Waugh–Lovell. Fuera del
fold el predictor ampliado es

    B_test beta_base + (x_test−B_test B_train^+x_train) t.

Su SSE es SSE_base−2t<e_base,z_test>+t²||z_test||². Ésta es identidad de MCO,
no una aproximación de potencia ni un cambio del estimando. Permite evaluar
los1999 X permutados y100 ruidos de cada panel sin miles de regresiones
separadas. Se contrastó con el código C1 original antes de planificar.

La potencia simulada usa sigma² residual del piloto G2 con grados n−splits−3,
no la varianza de Y sin ajustar. Al centrar cinco ruidos iid, la varianza
media pasa a.8 sigma². Inyectar beta*rX con beta² mean(rX²)=D_obj/(1−D_obj)
*.8 sigma² fija un incremento oráculo; la validación cruzada finita tiene
coste de estimación y no se obliga a que su media sea exactamente D_obj.

La calibración modela ruido Gaussiano y soporte de covariables remuestreado
del piloto. No prueba que la nueva cohorte tenga esa distribución de errores.
Wilson cuantifica Monte Carlo sobre esa simulación, no incertidumbre de todo
el modelo generador. Una potencia simulada alta no es una prueba de equivalencia
ni convierte NOT_MET en ausencia universal de cualquier efecto.

## Identidades de M y hallazgos que siguen siendo empíricos

La construcción core intacta da M=R_grad(F+gamma I)⁻¹R_gradᵀ y cada gradiente
lleva un factor1−p_y. D2b demuestra aproximación n·diag(odds) sólo con rango
interpolante y ridge despreciable. No fuerza dominancia de una sola fila,
el momento del colapso o una relación predictiva entre updates10 y250.

Tras colapso coordenado y caras pequeñas, log rho≈.5log Mkk−log n. R250
está entonces relacionado con Y250 casi por construcción, pero leverage,+condicionamiento y forma de M pueden variar. D_X|R usa una covariable medida
al tiempo final, y no es mediación causal ni una herramienta disponible en10.
La razón1−Dcond/D compara bases y SSE diferentes; no es partición literal
de la varianza y puede ser negativa o mayor que1.

## Variación continua, clasificación y legado

V_cont media varianzas poblacionales de los cinco R250 de cada split.
Puede variar aun con Mal constante: clasificar bien/mal no fija la confianza.
El índice dominante también puede cambiar entre inicializaciones; por ello
V_cont mide un desenlace operacional de cada red, no el mismo individuo
preseleccionado. La frecuencia modal de k* se informa como contexto.

Sólo hay tres niveles elegidos mirando G2, con ruido/pesos/lotes emparejados.
Una tendencia D–V_cont es descriptiva, sin contraste de dependencia ni causalidad.
El criterio de colapso se aplica a niveles sin filtrar individuos retrospectivamente.

W_adj legado residualiza Y linealmente sobre L y correlaciona rangos con X.
El contraejemplo D2b muestra que puede reflejar no linealidad residual aun
cuando X sea función de L. Se publica porque fue solicitado, pero no sustituye
la primaria cúbica ni rescata un nivel NOT_MET. D positivo sólo mejora a ESA
base cúbica; no demuestra información nueva sobre toda función de L.
