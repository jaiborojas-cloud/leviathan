# Registro de ejecución

46470bd congela diseño completo antes de1698ff8 (código etapa1). Etapa1
completa:40/40 predictores PASS, todos los estados preservados, K0 positivos
aproximadamente1,10,1000,10000 por calibración conjunta declarada. No se
calcularon desenlaces largos ni se escribió código etapa2 antes de este commit.
La tabla predictors.csv y los estados sintéticos quedan congelados con su SHA.
El guard runtime no registró lecturas bloqueadas ni acceso a datos T2.

Etapa2 v1 completada en 705.307792 s con dos procesos y BLAS/OMP=1.
20/20 controles PASS, 40/40 Q1 PASS, 35/40 censurados y cinco eventos
conjugado+colisión; ningún escape ni fallo numérico en la rejilla. Q2 conserva
las 240 filas INCONCLUSIVE: θ0 no tiene conjugado en ninguno de los 40 estados.
Q3 PASS exploratorio; Q4 FAIL por empate de desconocidos (0/40 frente a 0/40).
No se adaptaron semillas, rayos ni tolerancias. Se inicia la única reproducción
prevista por el diseño, con directorios temporales separados de los originales.

Reproducción finalizada: igualdad bit a bit de todas las salidas de ambas
etapas salvo resources.json (tiempos, RSS y directorio físico), incluidos los
120 hashes de arrays diagnósticos. Verificación independiente de la segunda
variación MP frente a diferencias finitas MP: error 1.3565432461e-17.
La prueba de la guarda usa una ruta ficticia mediante llamada directa, sin
abrir archivos T2. Recursos de reproducción y hashes: verification.json.
No hubo correcciones ni versiones sustituidas.
