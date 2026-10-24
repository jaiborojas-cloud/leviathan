# DIN-D2 · diseño congelado antes de código y mediciones

Exploratorio. Sólo D2/**. Base main con AH; PR68 de contexto aún separado.
Únicamente se leyeron plan/cierre D1 y escalares publicados de su resumen,
no estados ni otros datos T2. Ningún dato de entrenamiento entra al cálculo.
Fuentes autorizadas: rho_borde.py y geometry.py exactos, SHA en config.
Importar sin editar ni monkeypatch. Llamar **rho_borde(g)** con defaults
1440/800; no ejecutar su main, ni cargar sus listas/npz. Guarda propia que
bloquea todos los datos T2, baseline/comparators/cuarentena_X/predictors_locked,
todo .npz y todo archivo archivado salvo geometry.py. Se permite sólo el
fuente rho_borde.py de T2, como exige esta tarea.

## Preguntas y veredictos previstos

THEORY.md contiene las pruebas y condiciones, fijadas antes de medir.
Q1 PASS si la caracterización exacta de e_k se demuestra y sus testigos
independientes verifican a1e-8 relativo/1e-12 absoluto; FAIL si hay un
contraejemplo a esa caracterización. No exigir el piso incondicional: esa
versión es falsa cuando k pertenece a una cara con más de n/2 índices.
Q2 PASS con fórmula TV finita por puntos críticos y construcción explícita
con inf_vρ=0 (incluso v⊥1); FAIL si una identidad no se sostiene.
Q3 PASS con cotas PSD/condiciones suficientes y contraejemplo al piso
universal por rango o λmax; no se interpretará como afirmación de piso
positivo universal. Validar espectros/contrastes a1e-10 y punto a punto.
Q4 PASS_DESCRIPTIVE si se demuestra cota aguda y se construye saturación,
con comparación escalar correcta de unidades log/absolutas. Si la observación
D1 es compatible, NO se afirma explicación causal o concentración real.
Q5 PASS si TODOS los210 casos del instrumento congelado concuerdan con sus
referencias estables dentro atol1e-6+rtol1e-5*|ref|, tanto en mínimo conocido
como en longitud de la dirección reportada. FAIL si hay cualquier violación
estable o error/valor negativo/no finito del instrumento; si sólo faltan
referencias/tiempo y no hay violación conocida: INCONCLUSIVE. Si falla el
instrumento bajo prueba se conserva Q5 FAIL, NO se altera ese código ni se
invalida automáticamente la demostración. Los controles de la implementación
independiente sí deben pasar; si fallan, corrida INVALID y enmienda antes de
corregir. Sin afirmar que los mínimos no conocidos estén certificados.

## Paneles fijados, sin selección

Tres semillas PCG64 listadas × cuatro formas, n=27:12 paneles.
Gaussian: normal2D estandarizada por columna (ddof0).
Interior:6 puntos de hexágono radio1 con rotación .113(i+1),20 puntos
normales reescalados dentro del disco radio.3 y el centro exacto0 (índice26).
Near_collinear: el mismo gaussian transformado por diag(1,2^-12), conservando
rango afín2; pareja de carta para comparar un mismo problema analítico.
Mass_face:26 x=(j−13)/16, y=(i/8)x y un punto(0,−1). Todas las coordenadas
son dyádicas:26 puntos están EXACTAMENTE en una cara, no casi alineados.
No usar rotación flotante que destruya ese empate al infinito.

En gaussian/near elegir el menor índice vértice y el menor índice interior.
En interior elegir0 y26; en mass_face0,13,26. Geometría exacta se determina
con envolvente y signos racionales de floats (Fraction), antes del instrumento.
No reemplazar semillas ni casos inesperados. k_piso es el interior elegido,
o26 en mass_face, para el que el teorema da1/n.

Por panel:2 coordenadas (3 en mass_face); contraste entre dos interiores
(o10,13 en mass_face); vector constante; coordenada centrada normalizada;
I/n; dos mezclas nulas de constante/contraste con λmax=.5,.9; vector aleatorio
centrado normalizado con semilla+999; y8 perturbaciones (4ε×N constante oI/n)
de k_piso. Son207 casos. Añadir en cada mass_face el proyector sobre
(1,…,1,−26)^⊥ dividido por26 (λmax=1/26, ρ=0): total210.
Guardar todos M/f/parámetros/hashes sintéticos; matrices y perfiles fuera
Git, entradas mínimas reproducibles y resultados escalares dentro Git.

## Referencias independientes y controles

No invertir G para M singular: geometry.jac es suficiente.
Para e_k: a_k es unimodal; TV=1/m−1/n si k maximiza r, TV=1/n si se
extingue monótonamente; si primero crece, TV=2a_k(s*)−1/n.
Resolver μ(s*)=r_k por bisección MP80. Para contraste: si r_k=r_j, TV=0;
si el mayor de ambos es máximo global, TV=1/(m√2); si ambos se extinguen,
TV=2max|a_k−a_j|/√2, con raíz única de la derivada logarítmica.
Constante, coordenada centrada y mezcla nula son escalados de esas fórmulas.

Para I/n, perturbación isotrópica, vector general y proyector: norma directa
factorizada en MP80, independiente de einsum M del instrumento. Integrar por
gaps de logits: cortes1/δ,8/δ,32/δ; cota resto2Σ exp(−δU)/m≤1e-20.
En vector general añadir raíces detectadas en9 puntos por intervalo y
bisección MP; no se afirma aislamiento riguroso de todas las raíces.
GL16/32 en MP80 por intervalo; discrepancia>atol1e-12+rtol1e-8 vuelve
la referencia INCONCLUSIVE. La dirección reportada es cos/sin float deθ
promovidos exactamente; no convertir casi empates en empates. Los testigos
algebraicos de caras/contrastes se calculan por separado en MP/racionales.

Cotas globales: exactas en coordenadas, centradas, constante, contraste,
mezclas nulas, perturbación constante y proyector mass_face. Para los demás,
L_end(M,f) es cota inferior; una dirección algebraica prefijada, escogida
sin usar el resultado nativo, da cota superior numérica. Validar el valor
nativo contra ese intervalo y su testigo; no afirmar mínimo global exacto.

Controles de referencia: e_k en triángulo3 con cara2 (1/6), extinción1/3;
contraste constante/caso monótono/único pico frente a integral MP partida;
positividad/traza de M; J original frente a normas factorizadas y homogeneidad
puntual; casos de igualdad1/n y cara26; testigo PSD cero en .9 y1/26.
Homogeneidad del instrumento se contrasta con una llamada adicional4M en
el primer gaussian e_k. Es diagnóstico del instrumento, no filtro de estados.

Tres procesos numéricos, BLAS/OMP1,240s por caso mediante alarma externa a
la función congelada,14400s total. Conservar retornos, avisos, errores y
nan como desconocidos explícitos; no rellenar ni seleccionar supervivientes.
Una corrida y verificación desde archivos. Defecto del código D2 requiere
nueva enmienda congelada ANTES del código corregido, conservando original.
No entrenar, no leer T2 ni atribuir su mecanismo por espectro agregado.
