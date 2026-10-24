# Diccionario de salidas AF

`stage1_v1/predictors.csv` y `predictors_sha256.json` están cerrados en commit
e798206, antes del primer código de desenlaces. `synthetic_states.json` contiene
únicamente entradas nuevas de AF: semillas, bases y los40 M/f. No datos T2.

En `outcomes.csv`, **status** es el estado de terminación de la integración:
RIGHT_CENSORED_RMAX significa que la integración llegó al máximo sin escape,
pero puede haber observado un conjugado o colisión antes. El desenlace de disco
se identifica por **censored**, **r_deg** y **type**, no por status aislado.
Un evento observado tiene censored=False; sin evento tiene censored=True y
r_deg vacío. Un fallo numérico es distinto de ambos y no se rellena con Rmax.

`r_conj`/`r_col` son primeros eventos detectados antes de detener el conjunto;
si el primer escape detuvo los demás rayos, sus posibles eventos posteriores
quedan censurados a ese radio, no inexistentes. `ray_events.csv` conserva esa
censura por rayo. `selected_ray.csv` registra la extensión independienteθ0
para Morse, que puede seguir después del primer evento global del disco.
`type` conserva eventos a distancia relativa≤2% como coincidencia operacional
(por ejemplo COLLISION+CONJUGATE), no simultaneidad exacta ni causalidad.

`A32/A64` usan area7 y32/64 anillos, sobre radio justo anterior al evento o
Rmax si no hubo evento. `A_emb` sólo se llena con evento observado. Para
censura, A_at_limit es área hasta Rmax y no el área de una degeneración futura.
Los intervalos entre resoluciones/anillos se guardan en state_assessments.csv.
`area_answer` es construibilidad operacional en el dominio/radio observados;
no una afirmación geométrica global independiente de la carta de escape.

`normal_bands.csv` permite reconstruir bloques normales de longitud discreta
sin recalcular Hessianas. `normal_spectra.csv` conserva todos los autovalores,
con tau. `normal_vectors.csv` guarda modos negativos resueltos. Las variables
son desplazamientos métricos normales, no nodos tangenciales libres. En v1 no
hay estados elegibles en el rayo θ0: estas cuatro tablas normal_* no se crean,
las 240 filas de morse.csv explican la ausencia y no contienen índices medidos.

`arrays.csv` indexa las matrices float64 completas de257 radios, forma(6,n,257),
con orden[p1,p2,v1,v2,j,jprime]; los radios son uniformes0..r_end. SHA por archivo.
Sus archivos .npy AF permanecen fuera de Git en el directorio declarado en
resources.json. No son .npz ni contienen estados de T2. En Git se guardan todas
las fronteras, eventos por rayo y perfiles axiales/críticos, además de los hashes.
Los tiempos y ubicación física de arrays quedan excluidos de igualdad exacta.

Las tablas por escala usan40 como denominador global y10 por escala. La mediana
observada de r_deg/A_emb no sustituye una mediana poblacional cuando hay censura;
se acompaña por número de eventos/áreas y censurados. Las taus son descriptivas,
con censurados en rango mayor que Rmax y sin p-valores de40 independientes.
