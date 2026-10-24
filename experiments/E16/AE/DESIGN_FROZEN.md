# Congelación inicial AE · fase0 y separación de etapas

Este protocolo se congela antes de cualquier código/medición AE. La petición
exige verificar la geometría antes de congelar centro/radio del estudio; se
resuelve mediante dos congelaciones: esta fase0 y DESIGN_FROZEN_MAIN.md luego,
antes de código de geodésicas. No sobrescribir esta congelación ni sus datos.

Lecturas: E12-B/C originales archivados; E16 D scores/Fisher, AC Gauss/Jacobi,
AD interpretación y estados. Sin acceso a datos externos ni T2-A/T2-A1.
Familia:12 observaciones P0, θ=h00 fijo sin entrenamiento. Rasgos f_n=(x1,x2)
estandarizados por media/desvío poblacional del panel; no aprender rasgos.
a_n(P)=softmax(P·f_n), r_n=(y_n−sigmoid(logit_n))∇θlogit_n.
ω=Σa_nr_n, B_i=Σa_n(f_ni−μ_i)r_n, h=B(F+.01I)⁻¹Bᵀ.
F de Bernoulli uniforme sobre panel; usar chol del cométrico de E16, no
la regularización relativa1e-4 de E12. m=2, θ/C constantes en P.

Inmersión X(P)=Σa_n r_n chol(C). J_i=Σa_n d_i R_n,
X_ij=Σa_n(d_i d_j−Cov_ij)R_n. Calcular Γ por proyección tangencial de X_ij
y K por Gauss de segunda forma fundamental, sin diferencias ruidosas.
Contraste MP50/80 de h,Γ,K. Malla81 puntos [-2,2]^2 fijada más9 candidatos
P∈{−.5,0,.5}²; guardar SPD/rango/condición y signos/rango de K. No filtrar
puntos difíciles: fallo explícito. Acuerdo float/MP≤1e-7 normalizado max1,
MP50/80≤1e-35, no planitud si max|K|>1e-6 estable. Falla → fase principal
INCONCLUSIVE/NO_EJECUTADA, sin buscar otra familia o pesos.

Elegir centro por regla previa a geodésicas: entre9 candidatos regulares con
condición≤1e10, máximo K (desempate lexicográfico). Si todos K≤0, elegir(0,0)
y registrar que no hay predicción positiva aplicable; no seleccionar otra red.
Región principal fijada[-4,4]^2; salida censura, no prueba de degeneración.
SPD muestreada no es certificado sobre toda región: comprobar en cada RHS.
No se ejecutan geodésicas en esta fase. Centro y escala de radio se materializan
en la congelación principal a partir sólo de esta malla geométrica.

La síntesis S–AD es documental y conserva todos los estados. No leer, modificar
ni ejecutar instrumentos T2; el puente será sólo comparación de objetos.
Versionar fase0, entorno, tiempos, hashes y fallos. Cualquier defecto exige
nueva versión documentada, sin sobrescribir. Sólo AE/** y SINTESIS_S_AD.md.
