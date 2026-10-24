# Síntesis documental E16 · AC–AF

Consulta hasta AF, a partir de los cierres oficiales enlazados. Esta síntesis
no ejecuta geometría, no reabre etapas y no cambia estados, conclusiones ni
resultados. Complementa el [cierre S–AD](SINTESIS_S_AD.md).

## Etapas de un vistazo

| Etapa y fuente oficial | Pregunta | Estado oficial | Lo establecido | Lo NO establecido |
|---|---|---|---|---|
| [AC · Índice de Morse por campos de Jacobi](AC/CONCLUSION.md) | ¿Las negativas discretas corresponden a conjugados de la geodésica continua? | **INCONCLUSIVE**; v2 VALID_EXPLORATORY, v1 INVALID conservada | 12/12 shooting convergentes, 12 índices numéricos 0 estables y 8/8 controles PASS; las ocho curvas cuadráticas corresponden a una geodésica de longitud ≈0.506971938975 | No se midieron los bloques normales ni la tangencialidad de los testigos de Z/AB; el índice 0 no satisface por sí solo H2 ni certifica un mínimo global |
| [AD · Bloques discretos y carta normal](AD/CONCLUSION.md) | ¿Son planas suma, producto y cuadrática, y desaparecen las negativas al restringir a desplazamientos normales? | **INCONCLUSIVE** | K≡0 analíticamente en la región regular SPD de las tres composiciones; bloques normales positivos y cociente sin negativas admisibles; 12/12 controles PASS, incluida esfera con índice 1 | Los tres LIBRE cuadráticos no cumplen la ruta de estacionariedad; no se establecen H2/H1 por regla, causa única de las negativas históricas ni equivalencia global del cociente |
| [AE · Familia no plana tipo E12](AE/CONCLUSION.md) | ¿Se observan conjugados, salto de índice y cambio de minimizante al cambiar la familia perspectival? | **Q1 INCONCLUSIVE · Q2 INCONCLUSIVE · Q3 INCONCLUSIVE**; corrida VALID_EXPLORATORY | Malla SPD con K∈[−6.6438350978,+0.0465519012], 88/90 puntos negativos; ningún conjugado ni cruce observado antes de censura; 20/20 controles principales PASS | No se obtuvo r_deg ni A(r_deg), no se validó el salto 0→1 y no se ejecutó shooting multiángulo sin extremo elegible; locus de corte y minimizante global UNKNOWN |
| [AF · Réplica sintética de la familia geométrica T2](AF/CONCLUSION.md) | ¿Se miden de forma estable degeneración, índice y asociación predictiva, y reduce desconocidos usar radio con censura en vez de área objetivo? | **Q1 PASS · Q2 INCONCLUSIVE · Q3 PASS · Q4 FAIL**; corrida válida exploratoria | 40 estados sintéticos, estabilidad entre 512/1024 rayos; cinco eventos conjugado+colisión operacional, 35/40 censurados; asociación exploratoria negativa y 20/20 controles PASS | Rayo θ=0 sin conjugado en 40/40: 0 elegibles para Morse; no hubo escapes en la rejilla ni reducción de desconocidos; no se establece transferencia a T2 |

## Cadena de lectura

**AC → AD: cierre de la sublínea plana.** En el sintético 2→2→1, suma,
producto y cuadrática son localmente planas: K≡0 en su región regular SPD.
AC encontró índice continuo 0 sin los comparandos discretos archivados; AD
midió bloques normales positivos y ausencia de negativas admisibles en el
cociente, con controles de esfera que sí detectan el índice 1 geométrico.
La lectura de las «sillas» numéricas de T–AB es, por tanto, de discretización:
**H2 respaldada en sustancia y no establecida por regla**, debido a la falta de
estacionariedad LIBRE. Se conserva el INCONCLUSIVE oficial de AC y AD, sin
atribuir causa única a todos los modos históricos. Véase [S–AD](SINTESIS_S_AD.md).
La planitud local no resuelve fenómenos globales, singularidades o incompletitud.

**AE: no planitud con censura.** La familia tipo E12 es casi toda de curvatura
negativa en la malla fijada; el centro elegido tiene K0≈−0.1325705172.
Todos los 1536 rayos salen del dominio antes del radio máximo 4. Son censuras,
no eventos de degeneración: el último frente completo comprobado llega a
r=0.6875 y el par (r_deg,A(r_deg)) permanece (UNKNOWN,UNKNOWN).
A(r_safe)≈1.403669310497 es otro dato, no A(r_deg). Los bloques elegibles
medidos tienen índice 0; sin conjugado observado no hay contraste antes/después.
La corrección derivada v2 del puente conserva v1 y la censura conjunta; no
convierte la falta de éxitos conocidos en fracasos geométricos.

**AF: eventos estables sin reproducir la patología motivadora de T2-A.** Se
usa su familia geométrica softmax, con 27 componentes y estados nuevos: no
son estados de T2 ni una ejecución de la red 2→2→1. Los cinco eventos se
registran como conjugado+colisión dentro del empate operacional del 2%, sin
afirmar simultaneidad exacta. Q1 confirma la estabilidad numérica fijada.
Q3 PASS es exploratorio: diez semillas por cuatro escalas emparejadas y una
calibración conjunta de la métrica inducen parte de la asociación; no hay
p-valores de 40 réplicas independientes ni transferencia a T2.

Q4 FAIL significa que la fracción de «?» no bajó: ya es 0/40 tanto para el
disco de área objetivo 0.02 como para el radio con censura. **No significa que
todos los discos sean construibles:** 3/40 no alcanzan el área objetivo antes
del evento. A_emb sigue desconocida en los 35 censurados, aunque el área
observada hasta Rmax permita decidir la construibilidad. No hubo escapes en
la rejilla hasta Rmax=0.2; el control independiente de escape conocido sí pasó.
El rayo θ=0 prefijado no tiene conjugado y no se reemplaza por uno favorable:
Q2 sigue pendiente. No se afirma certificado riguroso ni locus de corte exacto.

## Preguntas abiertas

1. **Validación discreta del índice de Morse en una geometría con conjugados
   (Q2):** contrastar prospectivamente el salto de negativas normales 0→1 al
   cruzar un conjugado; los controles de esfera no sustituyen esa validación
   en la familia sintética.
2. **Sintéticos que reproduzcan escapes y arrastre del integrador:** AF no
   observó escapes en sus 40 estados ni reprodujo la patología motivadora.
   Falta un protocolo nuevo que los estudie con reglas prospectivas, sin
   modificar AF ni tomar sus casos seleccionados como confirmación.
