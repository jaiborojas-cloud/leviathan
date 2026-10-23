# E16-V — Refinamiento con transporte y nodos insertados fijos

Protocolo exploratorio prospectivo. Doce caminos de S, incluidos todos C0,
dirección full_min de T/U, tres pasos y ambos signos sin selección por outcomes.
Mismo problema sintético; sin entrenamiento, optimización ni nuevos candidatos
oficiales. S/T/U y T2-A intactos.

## Pregunta y cinco familias

Recuperar full_min mediante Hessiano original y eigensolver/canonización de T;
comprobar hash archivado. No repetir su auditoría de curvatura ni recalcular
Hessianos refinados. h=1e-5,1e-4,1e-3, signos ±, desde el original siempre.
Insertar un punto por arista, en fracción α=1/2 o α=1/4 desde su inicio.
Ambas variantes conservan exactamente la imagen original en aritmética real,
aunque distribuyen los nodos de modo diferente. 132→264 y 264→528 segmentos;
no confundir esos polígonos con los optimizados de S con el mismo número.

Cinco familias, sin fallback:
- original: mismo ensayo full_min de U.
- transported_half/quarter: insertar sobre cada arista YA perturbada.
  Es la misma curva perturbada con otra representación.
- pinned_half/quarter: insertar sobre la arista ORIGINAL y fijar esos puntos;
  mover sólo los vértices originales por ±hv. Cambia la familia de curvas.

Mismo h y mismo desplazamiento de vértices originales en todas las familias.
No renormalizar los vectores refinados: sus normas euclídeas pueden diferir;
registrarlas y no comparar Rayleigh como si fueran direcciones unitarias iguales.
Máximo 12×5×3×2=360 ensayos y 180 parejas; conservar todos los inviables.

## Identidades y mediciones

Construir inserciones y perturbaciones directamente en MP, sin redondearlas
de vuelta a float para longitud. L con primitiva heredada MP80/MP120, acuerdo
≤1e-35. Comprobar original contra U (longitud, delta y estado), base contra S,
y longitud transportada contra original, a ≤1e-35 normalizado por max(1,|L|).
Verificar por identidad de puntos que las inserciones transportadas son la
interpolación afín de extremos perturbados, misma tolerancia. Es un control
algebraico, no evidencia independiente de estabilidad en mallas nuevas.

Factibilidad de cajas MP sin clipping; aristas no nulas; primitivas válidas;
positividad métrica numérica por Bernstein de h00 y det MP120 en cada arista.
Guardar INFEASIBLE/INVALID/INCONCLUSIVE sin sustituir. No ampliar pasos.

Δ±=(L±−L0)/max(1,|L0|), E=(Δ++Δ−)/2 y O=(Δ+−Δ−)/2. Banda de signo ±1e-20,
sin ajustar. Registrar signos de cada ensayo, E/O y comparación de signo E
con original: SAME/CHANGED/UNRESOLVED cuando alguna pareja no es válida.
Un SAME con banda casi nula es coincidencia al umbral, no invariancia exacta.
Registrar diferencias E entre pinned y transported sin regla de aceptación
retrospectiva. Descenso unilateral no se atribuye sólo al Hessiano.

## Geometría

Reutilizar cotas numéricas de U en float64 sobre proyecciones MP: inferior
simétrica por vértices/puntos medios contra todos los segmentos destino,
superior por máximo desplazamiento de vértices correspondientes, colchón fijo
1e-12 y proyección por coordenada ≤1e-15. No intervalos rigurosos.
Comparar cada ensayo con su base y con su transported correspondiente.
Original se compara consigo mismo para la segunda comparación.
CHANGED si inferior>1e-8, WITHIN_TOLERANCE si superior≤1e-8; si no,
UNRESOLVED. No refinar selectivamente muestras. Cota superior holgada
no acredita imagen distinta; cota inferior pequeña no acredita igualdad.

## Estados, controles y límites

Controles de subdivisión: cada inserción es afín; L base refinada=original;
L transportada=original perturbada. La conservación de imagen en transported
es identidad de construcción. Para pinned, ningún signo se anticipa: guardar
resultados positivos, negativos y casi nulos; diferencias entre α son evidencia
descriptiva de dependencia de la familia de perturbaciones, no causa única.

Diagnóstico PASS/INCONCLUSIVE separado del estado exploratorio. Mínimos UNKNOWN,
ningún certificado de geodésica o convergencia continua. No seleccionar punto
mejor ni presentar subdivisión exacta como nueva confirmación de U.
900 s/512 MiB por corrida; exceder preserva parcial INCONCLUSIVE. Repetir una
vez para comparar nueve salidas científicas (siete CSV y dos JSON), excluyendo
recursos. Versionar escalares, código y hashes; no matrices, vectores densos
ni polígonos intermedios.
