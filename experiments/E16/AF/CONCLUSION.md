# E16-AF · conclusión exploratoria v1

Corrida válida: **Q1 PASS; Q2 INCONCLUSIVE; Q3 PASS; Q4 FAIL** según las reglas
congeladas, sin cambios de estados previos. Se conservaron los 40 estados y sus
80 resoluciones, sin fallos numéricos ni sustituciones. Los 20 controles pasaron.

## Desenlaces por escala

K(P0) es positivo y coincide numéricamente con el objetivo de cada fila; las
variaciones relativas son menores de 1e-7. Las medianas siguientes incluyen
**sólo eventos observados**, no imputan los radios censurados ni sus A_emb.

| K0 ≈ | Estados | Censurados a Rmax=.2 | Eventos | Mediana r_deg observada | Mediana A_emb observada | A_emb<.02 / estados |
|---:|---:|---:|---|---:|---:|---:|
| 1 | 10 | 10/10 | ninguno observado | — | — | 0/10 |
| 10 | 10 | 10/10 | ninguno observado | — | — | 0/10 |
| 1000 | 10 | 9/10 | 1 conjugado+colisión | .1175455426 | .0363072770 | 0/10 |
| 10000 | 10 | 6/10 | 4 conjugados+colisiones | .0770340968 | .0129577530 | 3/10 |

La censura domina en las cuatro escalas: 35/40 (87.5%). Los cinco eventos
observados tienen ambos tipos dentro del empate operacional del 2%; esto no
establece simultaneidad exacta. No hubo escapes en los 40 estados hasta Rmax;
el control sintético independiente sí reproduce el escape conocido.

## Preguntas y límites

**Q1 PASS:** 40/40 estados cumplen estabilidad entre 512 y 1024 rayos, entre
32 y 64 anillos y contraste MP80 local de K y densidad. Véanse los errores por
estado en [state_assessments.csv](results/stage2_v1/state_assessments.csv).
No es un certificado de inyectividad entre frentes muestreados ni una integral
de área enteramente en multiprecisión. El área de evento se evalúa desde el
interior, a (1−1e-6)r_deg. A(Rmax) de los censurados no es A_emb.

**Q2 INCONCLUSIVE:** el rayo θ=0 prefijado llega a Rmax sin conjugado en los
40 estados, incluidos los cinco con conjugados en otros rayos. Hay 0 estados
elegibles para el contraste antes/después; las 240 filas por malla/objetivo
quedan INCONCLUSIVE. No se midieron Hessianas de estos candidatos ni se validó
el salto de índice en la familia sintética. El instrumento discreto pasa los
controles esfera, hiperbólico y cuadrática plana en las tres mallas, lo cual no
sustituye la validación sintética que faltó. Se archivaron los perfiles del rayo
prefijado y las razones de no elegibilidad; no se escogió otro rayo a posteriori.

**Q3 PASS exploratorio:** Kendall tau-b, con censurados empatados por encima de
Rmax, da −.36902210 para |K0|, −.42383099 para max|K| del disco pequeño y
−.42909597 para X. Son idénticos en ambas resoluciones angulares. No hay
p-valores: son diez bloques de semilla por cuatro escalas emparejadas, y la
calibración conjunta de M induce parte de la asociación. El PASS corresponde
exclusivamente a la regla descriptiva congelada; no acredita transferencia a T2.

**Q4 FAIL:** 3/40 (7.5%) no permiten construir el disco de área objetivo .02
antes del evento, todos en K0≈10000 y con tipo conjugado+colisión. Los otros
37/40 superan el área objetivo antes del evento o del límite observado. La
fracción de «?» es 0/40 tanto para área como para radio con censura: no bajó,
y el empate es FAIL por diseño. Un radio censurado conocido no es un evento
observado; A_emb continúa desconocida en los 35 censurados.

## Controles, trazabilidad y siguiente paso

20/20 PASS: Jacobi en esfera (π), hiperbólico y plano; áreas planas en ambas
resoluciones; K de la cuadrática AD; bloques normales esfera corta/larga,
hiperbólico y AD en mallas 32/64/128, con GL8/16; escape sintético n=4 en
r=0.07444251681165903 hacia +P1, contrastado analíticamente y en MP80.

Diseño 46470bd → código etapa1 1698ff8 → predictores y SHA e798206 → código
etapa2 12cf59c → resultados. Sólo se importaron los dos fuentes geométricos
autorizados, verificando sus SHA; las guardas no registraron accesos prohibidos
en ninguna corrida científica. [Manifest de arrays](results/stage2_v1/arrays.csv)
y [política de archivo](ARCHIVE_POLICY.md) documentan los diagnósticos completos
fuera de Git. Entorno y tiempos están junto a cada versión de resultados.

Siguiente propuesta: un protocolo nuevo, congelado sin reutilizar AF como
confirmación, que cubra direcciones de Morse con una rejilla angular prefijada
y familias sintéticas con escapes dentro del horizonte. Puede usar estos
resultados para diseñarse, pero necesita estados nuevos para una validación
prospectiva. No se ejecuta aquí. Permanecen abiertos el salto de índice en la
familia, la generalidad de la asociación y la comparación de desenlaces cuando
sí existe incertidumbre de área. No se afirma mínimo global, locus de corte
exacto, certificado riguroso ni transferencia a datos T2.

La única reproducción prevista pasó con igualdad bit a bit de ambas etapas
(excluidos recursos variables) y de los 120 hashes de arrays. El contraste
independiente de segunda variación MP frente a diferencias finitas MP dio
error 1.36e-17. Errores máximos entre resoluciones: radio 0.011491%, área
0.017264%; en los 170 contrastes locales MP, error de K ≤1.88e-14 y de
densidad ≤1.32e-19. [Registro de verificación](verification.json).

## Amplitud de los predictores pequeños

Los intervalos siguientes son rangos **entre semillas del máximo muestreado**
de |K| y de X; no cotas continuas de toda la región. K0 por escala es la
primera columna de la tabla de desenlaces.

| K0 ≈ | Rango de máximo de curvatura absoluta | Rango de X |
|---:|---:|---:|
| 1 | [1.00001699, 1.00036735] | [1.00000016667, 1.00000016673] |
| 10 | [10.0005102, 10.0113351] | [1.00000166675, 1.00000166854] |
| 1000 | [1000.14081, 1008.90961] | [1.00016667972, 1.00016812292] |
| 10000 | [10001.4145, 10229.2467] | [1.00166466905, 1.00170576466] |
