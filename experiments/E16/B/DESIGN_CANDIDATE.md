# E16-B — Protocolo candidato v0, NO congelado ni ejecutado

Falta resolver la elección de red con el usuario. Este documento concreta la
alternativa de una red nueva sin entrenamiento; no cambia retrospectivamente
el diseño congelado de E16. Una vez resuelta la elección, copiar la versión
aceptada a DESIGN_FROZEN.md, registrar hash y commit, y sólo entonces programar
y ejecutar los controles. No hay resultados de red abiertos.

## Red y estados propuestos

Arquitectura y orden de θ: [mathematical_spec.md](mathematical_spec.md).
Se proponen tres estados fijos, sin pseudoaleatoriedad ni entrenamiento:

- n0: [0.3,−0.2,0.1,0.4,0.05,−0.1,0.7,−0.6,0.02].
- n1: [−0.25,0.35,0.45,0.15,−0.08,0.12,−0.5,0.8,−0.04].
- n2: [0.6,0.1,−0.3,0.5,0.1,0.03,0.4,0.9,0.06].

Son controles fabricados para instrumentación, no redes entrenadas ni muestras
independientes de una población de modelos. Versionar estos vectores como JSON
legible, no como checkpoints binarios. Los parámetros tienen origen nuevo y
no comparten procedencia con T1/E15/T2-A. Los resultados no describirán aprendizaje.

## Datos y perspectivas propuestos

Panel completo: ocho entradas y etiquetas definidas en mathematical_spec.md,
en el orden indicado. Paneles secundarios fijados por índice (base cero):
P0=(0,1,2,3,4,5,6,7), P1=(0,2,5,7), P2=(1,3,4,6).
No se ajustan tras observar Fisher o los rangos.
Para cada panel usar L_n=log probabilidad de la etiqueta sintética.
A=media L_n; B=media z₁L_n; D=media z₂L_n; E=media z₁z₂L_n.
Los pesos con signo son contrastes declarados, no distribuciones de probabilidad.
En S₁=xA+yB, S₂=xD+yE, evaluar p=(1,1),(0.5,−0.25),(−0.75,0.5).
Composiciones: suma Ψ=s₁+s₂, producto Ψ=s₁s₂,
cuadrática Ψ=(s₁²+s₂²)/2. No se fuerza cancelación ni se elige el punto según rango.

F y los funcionales se calculan con el mismo panel en cada configuración.
Estimando SPD regularizado: ρ=0.01, H=I₉, g=F+ρH, C=g⁻¹.
Los paneles secundarios evalúan sensibilidad determinista, no intervalos de
confianza ni incertidumbre poblacional. No simular independencia de paneles.

## Controles propuestos

1. Autodiff directo de S_macro frente a cadena completa; medir ω y B.
2. Diferencias centrales de S respecto a θ y mixtas θ,p con δ=0.002 y 0.001,
   usando evaluación NumPy independiente del grafo autodiff; medir ω,B,h.
3. Carta perspectival p=Jq, J=[[1,1/2],[0,1]], rango invariante y pullback.
4. Carta del modelo θ=Tη, T identidad salvo T₀₁=1/2 y T₂₂=2;
   transportar F y H. No recalcular H=I en la carta nueva. Comparar h y normas.
5. Restricción p=(t,2t), t=0.25: comparar derivada directa con pullback.
6. Agregación válida S_ag=(x+y)A: descenso y norma vertical cero; registrar rango.
7. Negativo π=x para S₁: h_yy positivo indica obstrucción al descenso. Si no
   supera umbral, INCONCLUSIVE, conservar estado y no sustituirlo.
8. Descomponer B_macro=B_lineal+B_mixto; comparar normas, rango de cada
   composición frente a suma y sensibilidad a panel. Descriptivo exploratorio.

## Decisiones numéricas propuestas

float64, CPU, una hebra BLAS; matrices ≤9×9. Presupuesto por corrida 120 s,
memoria objetivo 512 MiB; sin GPU, optimizador, entrenamiento ni geodésicas.
Autodiff propuesto: autograd (dependencia pequeña), frente a NumPy independiente.
Versiones exactas se fijan en la congelación, tras comprobar disponibilidad sin
calcular observables científicos.

Errores: norma máxima por entrada; absoluto y relativo con denominador
max|referencia|, relativo vacío si referencia cero. Autodiff/cadena y cartas:
abs≤1e−10+1e−9 max|ref|; FD: abs≤2e−5+2e−4 max|ref| en ambos pasos.
Justificación: mezcla de tanh/logsigmoid C∞, pesos/entradas O(1), δ²≤4e−6,
redondeo ε/δ²≤2.3e−10, inversión con autovalor mínimo g≥0.01 en carta inicial.
Condición de g>1e5 implica INCONCLUSIVE de estabilidad instrumental, sin
regularización adaptativa. Dos pasos contrastan estabilidad; no exigir factor
cuatro cuando redondeo domina o el error esperado se anula.

Rango de h: evaluar SVD de B L con C=L Lᵀ, corte τ=1e−8 max(1,s_max).
Valor singular en [τ/10,10τ] => rango INCONCLUSIVE; conservar espectro.
Comparar rango sólo si no ambiguo y la discrepancia FD de B no supera τ/10;
si lo supera, la estimación de rango sólo se reporta como rango autodiff, con
estabilidad FD INCONCLUSIVE. No aumentar τ para obtener concordancia.
La incertidumbre de panel se registra como rango mínimo/máximo entre P0/P1/P2,
con etiqueta SENSITIVE si discrepan, sin calificar eso como error del código.

Admisibilidad puntual: R de filas r_nᵀ, ker F=ker R exacto por definición.
Residual ||ωᵀK||∞, ||BK||∞ en base de kernel obtenida por SVD de R con
corte 1e−10 max(1,s_max). Si valores próximos al corte, INCONCLUSIVE del
kernel numérico. Reportar gap espectral. No concluir rango constante de Fisher
ni equivalencia con F⁺. Métrica operativa sigue siendo regularizada.

PASS por configuración si las identidades obligatorias cumplen tolerancias.
FAIL si una identidad o derivada excede tolerancia. INCONCLUSIVE si falta
artefacto, dependencia, presupuesto, estabilidad o diagnóstico de rango.
Distinguir estado de identidad, rango y sensibilidad; un rango ambiguo no
invalida automáticamente una identidad que sí pasó. No excluir configuraciones.

## Alcance y entrega

Los cambios de rango entre composiciones son descripción de estos tres estados,
no contraste confirmatorio de una hipótesis de aprendizaje. La siguiente etapa
sobre una red entrenada seguiría pendiente incluso si estos controles pasan.
Guardar diseño, fórmulas, scripts, configuración de datos/pesos, entorno,
checks.csv, spectra.csv, panel_sensitivity.csv, diagnósticos y manifest.
Actualizar progress tras cada grupo; ante fallo, conservar versión y salida.
Publicar en rama propia/PR dependiente de E16; no fusionar automáticamente.
