# E16-O — Estimador local y refinamiento adaptativo

Protocolo exploratorio congelado antes de implementar o medir. Mismos datos
sintéticos, sin entrenamiento. No es confirmación independiente.

## Fuente y geometría

Se mantienen Q0, Q1 y C0 de N128, con todos sus resultados. La etapa inicial
se lee sin reoptimización y su longitud se verifica con el intervalo de redondeo
archivado de 40 cifras. Dominio, extremos, corredor |s|≤0,25, métrica h,
objetivo, optimizador y tolerancias de N se mantienen. Nuevas mallas conservan
todos los nodos previos y bisecan sólo segmentos marcados; la interpolación
conserva exactamente el polígono antes de optimizar. Cada linaje adapta su
propia malla. No se mezclan candidatos ni se añaden reinicios globales.

## Indicador local, sin garantía de error global

Para cada segmento se inserta su punto medio longitudinal. Con sus dos extremos
fijos, minimizar la longitud de las dos mitades respecto al nuevo s en
[-0,25;0,25], mediante bounded, xatol=1e-10 y máximo 100 iteraciones.
Comparar el candidato devuelto, ambos límites y el punto medio original;
conservar el menor (desempate por ese orden). Si la mejora respecto al original
es ≤1e-12·max(1,longitud del segmento), elegir el original para evitar movimiento
por redondeo. Registrar también la mejora cruda. No se garantiza el mínimo
unidimensional global. La falla del optimizador local queda registrada y hace
inconclusa la corrida; no se excluye su segmento del registro ni del marcado.

Registrar desplazamiento eta_s=|s_nuevo-s_original| y ganancia eta_L≥0.
El indicador de marcado es E=max(eta_s/1e-3,sqrt(eta_L/1e-8)). Verificar
la longitud seleccionada contra la primitiva de 80 cifras (error normalizado
≤1e-10); preservar fallos como inconclusos, sin cambiar candidatos a posteriori.

Ordenar E² descendente, desempate por índice del segmento, y marcar el prefijo
mínimo que acumule al menos 50 % de la suma; truncar a 32 bisecciones por ronda
y al espacio restante hasta 256 segmentos. Registrar fracción capturada real:
no afirmar 50 % si el límite impide alcanzarlo. Insertar los nuevos nodos con
el s interpolado ORIGINAL, no con el valor explorado por el indicador; así se
conserva el polígono al empezar cada optimización global.

Máximo cuatro rondas posteriores a N128. Parar antes sólo cuando todos los
E≤1 y los últimos dos refinamientos pasen longitud, forma y Hausdorff junto
con validación de caminos; o si E² suma exactamente cero o no quedan recursos.
E=0 sin dos refinamientos no demuestra estabilidad del caso cuadrático.
C0 puede pasar sin refinar si todos los indicadores son cero, además de pasar
su identidad recta y validación. Los presupuestos no se amplían para pasar.

## Medidas del extremo y evaluación

Guardar por segmento la pendiente ds/dt, velocidad euclídea normalizada
sqrt(1+(ds/dt)²), velocidad de h en ambos extremos y punto medio (dividida
por delta t), longitud y fracción de longitud en t≥0,75/0,9/0,95.
Las porciones de longitud se evalúan con la misma primitiva en el punto de corte.
Informar si el máximo de velocidad crece al refinar; no inferir singularidad
ni existencia de una curva límite de este descriptor.

Comparar cada transición en la unión de nodos: sup|delta s|≤1e-3; cambio de
longitud normalizado≤1e-3; Hausdorff euclídea en (t,s) con cota superior≤1e-3
y brecha≤1e-5. Usar sin modificar el estimador Hausdorff de N, con sus controles
y límites. Es numérico en float64, no distancia intrínseca de h ni certificado.
Heredar precisión 80/120, cuadraturas, reparametrización, SPD Bernstein,
gradiente AD/FD local multiprecisión, KKT, límites y presupuestos de N.
Q0/Q1 se comparan en cada ronda como descriptor, aunque sus mallas difieran;
la coincidencia mutua no sustituye el refinamiento. Registrar además los cambios
locales de forma y su masa de cola usando la regla heredada de M/N.

Para un linaje cuadrático, PASS_NUMERICAL requiere todos los caminos válidos,
ningún probe fallido y, al terminar, E≤1 y dos últimas transiciones PASS.
Las transiciones tempranas inconclusas siguen registradas, aunque después se
cumpla el criterio terminal. Cualquier fallo de identidad produce FAIL;
resto no resuelto o presupuesto agotado produce INCONCLUSIVE global.
Conservar la primera corrida completa, incluidas contradicciones y fallos.
Reproducir salidas científicas byte por byte; tiempos y memoria aparte.
