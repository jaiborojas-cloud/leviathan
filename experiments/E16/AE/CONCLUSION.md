# Conclusión E16-AE

**Q1 INCONCLUSIVE · Q2 INCONCLUSIVE · Q3 INCONCLUSIVE.** Corrida numérica
VALID_EXPLORATORY,20/20 controles principales PASS,4/4 contrastes MP de rayos
PASS. Corrección derivada v2 con2/2 controles PASS. No se fuerza una conclusión
sobre conjugados o corte a partir de curvatura no nula.

## Familia y fase0

Se adaptó la familia exponencial E12-B/C a θ=h00 y panel P0 de E16, sin
entrenamiento ni datos externos. Rasgos: x1/x2 estandarizados poblacionalmente.
Métrica h=B(F+.01I)⁻¹Bᵀ; no la regularización relativa de E12.
Malla90 puntos SPD, K∈[−6.6438350978,+.0465519012],2 positivos y88 negativos,
contrastada MP50/80. Los9 candidatos de centro fueron negativos; la regla
congelada eligió P0=(0,0), K0=−.1325705172. No se cambió para obtener eventos.

## Exponencial y disco con censura

| Rayos | Conjugados observados | Cruces propios antes de censura | Primer censor de dominio | Último frente completo comprobado | r_deg | A(r_deg) |
|---:|---:|---:|---:|---:|---|---|
| 512 | 0 | 0 | 0.700851304963 | 0.6875 | UNKNOWN | UNKNOWN |
| 1024 | 0 | 0 | 0.700851304963 | 0.6875 | UNKNOWN | UNKNOWN |

Todos los1536 rayos salen del dominio antes del máximo4. No son1536 eventos
geométricos: son censuras. El radio de salida≈.7008513 no se renombra r_deg.
El detector de cruces sólo comprueba niveles radiales y polígonos entre rayos;
no excluye contactos tangentes o eventos entre muestras. El dato censurado
observacional llega hasta el frente muestreado.6875, sin certificado continuo.

A(r_safe)≈1.403669310497 en r_safe=.665808739714 para ambas resoluciones;
esto es área estimada antes de cobertura incompleta, no A(r_deg). El contraste
MP integra geodésica/Jacobi/área completo en cuatro rayos, no sólo K sobre una
curva float. Errores frente a DOP853 del orden1e-9 o menor, según mp_audits.csv.
La afirmación de disco embebido sigue condicionada a inyectividad, que los
frentes muestreados no certifican. K0<0 hace no aplicable la predicción local
positiva π/√K0; los dos puntos positivos de la malla no la sustituyen.

## Índice y corte

Dos rayos prefijados, extremos exploratorios.25,.5,.75; mallas16/32/64, ambas
resoluciones angulares.30/36 bloques normales con cobertura pasan cuadratura,
gradiente y testigo MP, todos con índice0. Seis objetivos están censurados.
No hay un conjugado observado que defina pares antes/después; no se ha
probado ni refutado el salto0→1. Se preservan bandas, espectros y nodos normales.
Los controles esfera sí detectan0→1 y los de hiperbólico/AD dan0.

Sin conjugado observado no se fabricó un extremo posterior: las cuatro
combinaciones resolución/rayo de búsqueda de corte quedan explícitamente
NO_OBSERVED_CONJUGATE. No se ejecutó shooting multiángulo en un objetivo
sustituto. El locus de corte, el minimizante global y el cambio de rama quedan
UNKNOWN, no inexistentes. La implementación conserva esa rama condicional
para objetivos elegibles, pero esos resultados no existen en esta corrida.

## Puente descriptivo con T2-A1 y defecto corregido

V1 conservada: fraction_at_fixed=.623046875 a r1 comprueba sólo cobertura
individual y Jacobi. No es supervivencia libre de cualquier evento geométrico.
El reproceso v2 lee los perfiles sin reintegrarlos y añade candidatos por rayo
y censura conjunta. Pasado.6875 faltan rayos para comprobar colisiones: al radio1
los512/1024 casos son censurados para ese desenlace conjunto,0 éxitos conocidos
y0 eventos conocidos; las cotas sin supuestos son[0,1]. No interpretar0 éxitos
conocidos como fracaso de todos: el desenlace es desconocido por censura.
El par(r_deg,A(r_deg)) es(UNKNOWN,UNKNOWN), acompañado por censor muestreado
y A(r_safe) como dato distinto. No se leyó ni ejecutó T2-A/T2-A1.

## Alcance y siguiente paso

La familia es no plana, pero no garantiza foco en esta región y centro. Hace
falta otro protocolo prospectivo si se desea estudiar una región positiva y
un horizonte que pueda contener conjugados; selección sólo con geometría previa,
sin reutilizar supervivientes como confirmación. Otra opción es ampliar dominio
con controles de rango/condición para reducir censura, sin cambiar esta corrida.
No se afirma certificado riguroso, radio de degeneración exacto, locus de corte
exacto o minimizante global. La síntesis S–AD conserva todos sus estados.

## Integridad y recursos

PASS_REPRODUCTION:22 salidas científicas idénticas byte a byte (3 fase0,
13 principal,6 puente), excluyendo recursos/tiempos. Principal inicial
324.810266s/174MiB; repetición324.168418s/
173.960938MiB, dentro del presupuesto2400s.
Las tres etapas conservan sus propios tiempos/entorno/hashes.
[Verificación](verification.json) · [Figura derivada](figures/geometry_and_censoring.svg).
Integridad aprobada no sustituye las tres respuestas INCONCLUSIVE.
