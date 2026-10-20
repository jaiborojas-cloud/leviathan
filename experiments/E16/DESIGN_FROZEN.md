# E16 — Diseño congelado antes de ejecutar

Fecha de diseño: 2026-10-19. Versión 1. No hay resultados abiertos en esta línea.
Las [fórmulas](mathematical_spec.md) preceden al código. El commit de congelación
se registra en progress.md; no cambiar este diseño tras observar controles.

## Configuración

Python, NumPy float64, SymPy racional exacto. Sin aleatoriedad ni semillas.
θ=(1,2), p=(1,1); para cartas q=(0.25,−0.5), η=(0.5,−0.25).
Matrices ≤3×3; presupuesto por ejecución 60 s, 1 CPU, sin redes, entrenamiento,
checkpoints ni integración de geodésicas. Memoria objetivo <256 MiB.
No buscar umbrales en datos. Sólo se escriben artefactos en E16.

## Controles y observables congelados

1. **A/SPD:** base de la especificación; carta perspectival
   φ(q)=(q¹+2q², q²+(q¹)²/2), J=[[1,2],[q¹,1]], det=1−2q¹;
   dominio q¹<1/2 (inversa q¹−(q¹)²=p¹−2p² con rama q¹<1/2).
   Comprobar B y h por derivación directa y pullback, rango 2, igualdad de
   norma de v=(1,−2). Carta del modelo θ=Aη con A=[[1,1],[0,1]], transportar g,C.
2. **B/restricción:** base en φ(t)=(t,2t), t=0.25: h_t=14, rango 2→1.
   Familia redundante S=θ¹p¹, φ(t)=(t,0): h_t=2, rango 1→1.
3. **C/agregación:** π=x+y, S=θ¹(x+y): hbar=2, rango 1→1,
   residuo h−DπᵀhbarDπ=0 y h(1,−1)=0.
   Contraejemplos π=x con familia base: norma vertical 3 y secciones 2 frente a 5;
   S=θ¹xy: valores horizontales 2 frente a 8 en misma fibra x=1.
4. **D/composición:** producto de la especificación: B=[[2,1],[2,1]], rango 1;
   referencia exacta, cadena completa y truncada. La truncada debe dar error >0.1.
   S₁=θ·p, S₂=−S₁+θ¹: suma rango 0, composición cuadrática B=[[11,3],[6,7]],
   rango 2. Medir espectros sólo en cartas declaradas; no llamarlos invariantes.
5. **Degenerado:** F=diag(2,0), A del control 1; verificar admisibilidad, h=1/2
   en dos cartas, diferencia de matrices pseudoinversas >0.1 y discrepancia
   inadmisible 1/8. No usar pseudoinversa para el primer control SPD.
6. **Derivadas independientes:** diferenciación simbólica exacta de S para ω,B;
   diferencias centrales sobre S para ω y diferencias mixtas sobre S para B,
   pasos δ=1e−3 y 5e−4. Cubrir base, ambas cartas, restricciones, agregación,
   ambos contraejemplos de descenso, producto, suma, composición cuadrática y
   familia degenerada. Registrar errores en B y h; error relativo sólo si
   referencia no nula. Para referencia cero, escribir vacío en relativo.

## Reglas de decisión

Identidades simbólicas: igualdad exacta de cada entrada. Controles float64:
error absoluto máximo ≤1e−11 + 1e−11 max|referencia|. Diferencias finitas:
≤2e−6 + 2e−6 max|referencia| para ω,B,h en ambos pasos.
Error mixto esperado O(δ²)+O(ε/δ²); ε≈2.22e−16, δ≥5e−4 da escala de
cancelación ≈9e−10 multiplicada por valores O(10); tolerancia conservadora
2e−6, sin datos mal acondicionados ni singularidades próximas. No exigimos
cociente 4 entre errores en polinomios cuyos errores de truncamiento se anulan.
Rango numérico: SVD con corte absoluto 1e−10; valor singular entre 1e−12 y
1e−8 activa INCONCLUSIVE (salvo cero simbólico conocido). Registrar espectro,
rango exacto y condición sobre modos no nulos. No confundir condicionamiento
infinito por kernel exacto con mala estimación de modos positivos.

PASS por control si todas sus identidades/contrastes esperados y derivadas
aplican y pasan. FAIL si contradice referencia o tolerancia. INCONCLUSIVE por
rango ambiguo sin referencia exacta, dependencia ausente o presupuesto excedido.
Un contraejemplo correcto es PASS del control, no aprobación de la afirmación
refutada. Conservar cualquier salida fallida; corregir en versión nueva y
anotar causa sin reescribir resultados anteriores. Actualizar progress.md después
de cada grupo completo. Las réplicas se guardan en directorios nuevos.

## Interpretación preestablecida

Identidades: pullback, cadena, rango Gram y descenso bajo hipótesis.
Controles esperados: concordancia float64/analítica y refutaciones diseñadas.
Exploratorio: sólo descriptores de estos ejemplos; no inferencia poblacional.
Hipótesis futura candidata: fuera de cambios de carta, composiciones no lineales
podrían reorganizar el rango por los términos mixtos, sin relación monótona con
la suma. La posibilidad ya tiene ejemplos algebraicos: su frecuencia y utilidad
en redes reales siguen sin validar. Este experimento no mide predicción,
curvatura, conjugados ni emergencia.
