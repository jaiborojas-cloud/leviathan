# Potencia M2: aclaración del escenario antes de simular

Estado: preparación documental; no hay simulación, plan ni cohorte. El diseño y analista son BORRADORES, no congelados. La pregunta se remitió al responsable antes de escribir código de medición.

El encargo pide D(c) lineal con beta=.077 ajustada a los puntos publicados de Q13-DR. Se usan exclusivamente los seis D y c del resultado oficial JSON, sin abrir su tabla de cohorte ni recalcular D. Con pendiente fija, el intercepto por mínimos cuadrados es media(D)−.077·media(c):

`D(c) = -0.038434071244996953 + 0.077*c`.

Esto da D(.40)=−.0076340712449969525 y D(.438)=−.0047080712449969545. El método gaussiano Q13/C2/DR parametriza la amplitud como sqrt(d/(1−d)*.8*sigma²/var(X_residual)), que no admite d negativo. La potencia anterior de Q13-DR declaró expresamente max(0,D(c)) antes de convertirla en amplitud.

**Decisión pendiente:** conservar ese truncamiento y declarar que la curva generadora deja de ser lineal en esos extremos, o reformular el escenario. No se asume que el paso del tiempo sea una respuesta. Los objetivos pre y post truncamiento hipotético se publican en escenario_pendiente.json; los segundos no representan una decisión tomada.

El resto queda listo para aplicar la respuesta: N200,400 réplicas por rho como Q13-DR,11 niveles con un único A0,IC97.5 con cuantiles.0125/.9875,500 bootstrap,ρ∈{0,.3,.6,.615}, remuestreos compartidos LP/WD y potencia conjunta. Solo se usaría G3s=.8 como piloto. La preparación se contrastará con el SHA congelado futuro; si cambia el estimando se repetirá.
