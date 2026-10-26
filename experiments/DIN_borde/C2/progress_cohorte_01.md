# DIN-C2: compuerta superada antes del entrenamiento

Plan 0e167f4 ya publicado antes del código df248d5. Tres modelos de control SIN
entrenar: M reconstruida desde pesos con error relativo 0 en los tres y f idéntica.
Semillas C2 disjuntas de G2/G3; controles también disjuntos.

No se ha entrenado ninguna trayectoria de C2; este commit conserva la compuerta.
El generador no contiene importaciones de análisis ni acceso al piloto. Se conservan
5,10,30,250 como visitas autorizadas. Quedan 1.000 entrenamientos / 4.000 estados.
No se ha ejecutado analisis_C2.py ni calculado asociaciones con C2.
