# Conclusión de E16-S

El protocolo prospectivo obtiene PASS_NUMERICAL: ocho candidatos cuadráticos
satisfacen tres auditorías MP consecutivas de KKT físico y validación final;
cuatro controles rectos terminan naturalmente. Pasan los seis refinamientos.
No se sustituyen los estados nativos del solver ni los resultados de R.

El escalado termina en menos iteraciones que la referencia en los cuatro
pares cuadráticos observados. No se infiere una superioridad general ni un
ahorro temporal: la auditoría añade coste considerable y la caché procede de R.
La trayectoria fina parte del candidato grueso propio de cada método.

Persisten límites: problema sintético pequeño, dos fuentes cuadráticas
relacionadas, un control constante, dos discretizaciones y observaciones
correlacionadas. No hay datos de confirmación nuevos ni certificado riguroso
de errores, mínimo o unicidad. La positividad métrica y la coincidencia entre
discretizaciones son comprobaciones numéricas necesarias, no pruebas globales.

Un siguiente protocolo podría examinar curvatura de segundo orden en estos
candidatos, separando modos casi nulos de redistribución de nodos y direcciones
geométricas. Requeriría congelación propia; no se ejecuta ni se anticipa su
resultado en S.
