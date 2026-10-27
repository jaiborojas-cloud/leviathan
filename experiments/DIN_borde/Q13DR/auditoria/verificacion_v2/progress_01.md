# Cierre de la verificación contra245d735f

Diseño68959d0 antes de código2006631 y de cualquier ejecución. Casos antiguos se
reprodujeron contra los snapshots v2, sin tocar v1. Se añadieron casos previstos
de dominio y reglas con código comprometido antes de ejecutarlos.

Monte Carlo r1 falló por la importación Path ausente en el verificador. Se
conserva completo; enmienda de60ef5 precede al driver r2 de3be3953. Ningún parámetro
ni seed cambió y no se tomó ninguna réplica incompleta para tasas. R2 completó
1000/1000 con datos y álgebra idénticos por bytes a v1; no descartó ni redibujó.

Resultados F01–F06 y ambigüedades en la matriz. Las correcciones principales se
confirman, pero N01–N05 documentan casos residuales/nuevos antes de congelar.
Especialmente, c constante decimal puede dar β8/IC[-8,8] y un rango común no
ordenado da un margen negativo. No se aplica ninguna corrección al original.

Se conservan logs, snapshots, tablas de tasas, fallos y dos versiones del driver.
Arrays nuevos fuera de Git; arrays sintéticos v1 sólo leídos y verificados contra
su manifiesto original. Sin datos Wine/C2/Q13 reales, entrenamiento ni geometría.
