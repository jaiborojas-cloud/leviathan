# DIN-Q13 — procedimiento del agente de cohorte

Se aplica sin cambios el [diseño congelado](../../DISENO_DIN_Q13_v1_CONGELADO.md),
SHA `81d8ad9e41b029f3342691bbb0e4d8e248778a7f226a077fd80b007e64656077`.
Sólo se añaden archivos de cohorte. No se analiza una cohorte Q13 ni se accede a
la cohorte C2. El analista conserva la ejecución única de su script congelado.

Orden, con commit y push antes del paso siguiente: implementación → calibración
completa y dosis → potencia simulada → plan → compuerta → cohorte → publicación.
Si la calibración descarta ambos manipuladores, terminar sin potencia ni cohorte.
Si ningún N cumple potencia, terminar sin cohorte. Si N>400, pedir confirmación
en el PR y detenerse antes de entrenar la cohorte, como exige §6 del diseño.

La receta numérica se copia de G3/C2: red double 13→64→32→3, ReLU, generador de
117 ejemplos (90 train, 27 panel), tres centros en las dos primeras variables,
ruido normal de escala .8 y StandardScaler ajustado sólo sobre train. Inicializar
como G3 después de cargar core (dtype float64 global). Adam lr .006 sin decay en
A0/LS; LS cambia sólo label_smoothing; WD cambia sólo a AdamW con el decay fijado.
Los lotes, datos y pesos iniciales son idénticos entre brazos pareados.

Calibración: 20×5 por cada una de nueve condiciones. Concretar «base 701000» como
split=701000+split, init=702000+5split+k, lote=703000+5split+k; tres flujos disjuntos.
Medir sólo c250, q250 y acc_panel250, con core intacto. No calcular X, rho ni
asociaciones en el piloto. Conservar pesos/M/f y fallos fuera de Git; publicar
las 900 filas operacionales. Un fallo impide seleccionar dosis con datos incompletos.
Seleccionar la menor dosis con mediana c en [.55,.70] y diferencia absoluta de
mediana acc respecto a A0 <.05, como pide el encargo. No ajustar la rejilla.

Semillas de cohorte: split=711000+split, init=721000+5split+k y lote=731000+5split+k.
Se comprueba disjunción contra configuraciones G2/G3/C2, sin leer datos C2.
La potencia, si procede, usa sólo el piloto G3 y datos simulados; las funciones
del analista sólo pueden ejecutarse en esa simulación, nunca contra Q13 real.

Escrituras exclusivas; no reemplazar fallos ni salidas. Cualquier defecto requiere
enmienda congelada antes de corregir. Arrays/checkpoints permanecen fuera de Git.
Se verifica SHA del instrumento rho r3 `2ac015a2…`, core y geometry `b4d1e0e4…`.
