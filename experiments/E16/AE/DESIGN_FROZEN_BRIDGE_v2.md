# Enmienda prospectiva v2 · puente descriptivo y colisiones por rayo

Defecto de instrumentación, no selección de centro/radio ni nuevo experimento
geométrico: v1 midió correctamente rayos, Jacobi, área y bloques, pero su
fraction_at_fixed sólo comprobó cobertura individual y ausencia de conjugado.
No incorporó censura de colisiones: tras salir un rayo ya no se puede excluir
su colisión con otros sin conocer su trayectoria exterior. También faltaba
una columna explícita de primer candidato de colisión por rayo. No cambiar v1.

Esta versión derivada lee únicamente perfiles y tablas v1 congeladas por hash.
No reintegrar geodésicas, cambiar métricas, centro, región, n o veredictos.
Rehacer TODAS las intersecciones propias de segmentos no adyacentes por cada
frente radial archivado con cobertura completa. Un cruce de segmentos se
asigna a los cuatro rayos extremos incidentes como candidato angular, no como
igualdad exacta de dos rayos discretos. Conservar primer intervalo radial por
rayo y parejas; pasos129 niveles y margen.05 son los de v1.

Cobertura de colisiones: último nivel radial efectivamente comprobado mientras
todos los rayos existen. No prolongarla hasta el primer censor de dominio si
ese valor no es un nivel comprobado. Censura conjunta por rayo=min(cobertura
individual, cobertura de colisiones). Primer evento: conjugado exacto observado
o intervalo candidato de colisión; guardar ambos y su naturaleza separada.

En r_fijo1: conocido sin evento sólo si cobertura conjunta alcanza1 y ningún
evento/intervalo ambiguo llega antes; evento conocido si su extremo superior≤1;
resto censurado/desconocido. Fracción de supervivencia sin modelo en
[conocidos_sin_evento/n,1−eventos_conocidos/n]. Todos n en denominador.
La fracción individual sin conjugado de v1 se conserva y renombra descriptor.
No tratar censura de dominio como fallo geométrico. Sin eventos observados,
rdeg y A(rdeg) UNKNOWN; r_censura es dato distinto y tampoco certificado
continuo entre ángulos o niveles. Mantener A(r_safe) como estimación muestreada.

Controles del reproceso: polígono cruzado detectado, círculo no cruzado.
Guardar rayos v2, todos los cruces, resumen y puente. Cualquier fallo de estos
controles → derivación inválida. Reproducción determinista desde los mismos
archivos; luego repetir v1 una vez según diseño original y comparar v2 derivada.
No sobrescribir datos/código previos; todos los fallos y estados se conservan.
