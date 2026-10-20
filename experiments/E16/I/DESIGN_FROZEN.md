# E16-I — Caminos quebrados acotados: diseño previo

## Pregunta y alcance

¿Se encuentra un camino de dos tramos más corto que el segmento recto entre
los mismos extremos, con las métricas declaradas? Exploratorio, no prueba
confirmatoria: se reutilizan H h00/h01/h02 (los tres primeros por orden), P0,
los tres pares 0→1,1→2,2→0 y suma/producto/cuadrática: 27 casos, sin entrenamiento.
No se escogen por resultados geométricos ni se modifica evidencia A–H o T2-A.
No se resuelve una ecuación geodésica ni se prueba un mínimo global.

## Familia de caminos y búsqueda

Sean a,b los extremos, v=b−a y Rv=(−v_y,v_x), en la carta original H.
m(s)=(a+b)/2+s Rv, con s∈[-1/4,1/4]. Camino: a→m(s)→b, suma de longitudes
de sus dos tramos. Incluye el segmento recto cuando s=0. Los extremos permanecen
fijos; se permite una esquina, por lo que una mejora no implica geodésica suave.
La familia se fija en esta carta y se transporta completa bajo otras cartas;
no se redefine una normal euclídea después de cambiar coordenadas.

Calcular primero coeficientes de la métrica con derivadas analíticas D a 120 cifras;
convertirlos a float64 para buscar con scipy.optimize.minimize_scalar, bounded,
intervalo completo, xatol=1e-8, maxiter=100. Usar integral cerrada de sqrt(q)
en float64 para el objetivo. Para suma usar longitud en métrica constante.
q=a t²+b t+c: si no es constante y a≤0 o δ=c−b²/(4a)≤0, devolver infinito
y registrar la evaluación inválida, sin recortar ni añadir pisos.

Candidatos del primer ajuste: s=0, ambos extremos y el s devuelto por el optimizador.
Elegir el menor objetivo finito (desempate por orden de evaluación). Si la mejora
respecto a s=0 no supera 1e-10 max(1,L0), conservar s=0 para evitar selección
por ruido de float64. Si el candidato elegido no pasa después la validación de
positividad, queda INCONCLUSIVE: no reemplazarlo retrospectivamente.

Repetir la búsqueda desde el intervalo completo con xatol=1e-9 y mismos límites;
seleccionar con la misma regla, sólo para estabilidad, sin sustituir el resultado
principal por el mejor de los dos. Guardar ambas salidas, éxito, mensajes,
parámetros y todas las evaluaciones. No se hacen más reintentos según resultados.
El fracaso del optimizador queda INCONCLUSIVE, aunque haya un candidato más corto.

## Validación de candidatos y controles

Usar sin modificar funciones y umbrales G, con hashes fijados, para comprobar:
- Segmento recto y ambos tramos del candidato principal: integral cerrada,
  cuadratura localizada 16/32/64 y reparametrización t=u² a 80/120 cifras.
  Tolerancias gruesa 1e-12, fina 1e-24 y precisión 1e-40, como G.
- Positividad global numérica de H00 y det H en cada tramo por Bernstein G,
  margen 1e-30, profundidad 20 y 8191 nodos; sin intervalos dirigidos.
- Representación polinómica frente a B directo en cinco puntos por tramo.
- Transporte de rapidez por las tres cartas G, sin cambiar el camino.
- El camino s=0 tiene la longitud del segmento recto, error ≤1e-40.
- Los dos tramos del candidato de estabilidad: primitiva a 120 cifras y las
  mismas cotas SPD; comparar su longitud total con la principal a 1e-8.
- Longitud validada principal no peor que recta, error normalizado ≤1e-12.
- Suma: s=0 y longitud igual a recta a 1e-12, por desigualdad triangular.
- Control euclídeo: a=(0,0), b=(1,0); s=0 da L=1, s=±1/4 da sqrt(5)/2>1.
  El mismo procedimiento de búsqueda debe conservar s=0 en ambas resoluciones.

## Decisión y reporte

FAIL si falla una identidad, un control esperado o no-empeoramiento validado;
INCONCLUSIVE si falla optimización, estabilidad, precisión, integración o SPD;
PASS_NUMERICAL sólo si todo pasa. Distinguir éxito instrumental de mejora:
ganancia=(L_recta−L_candidato)/L_recta; mejora detectada si ganancia>1e-8 y
caso PASS_NUMERICAL. Sin mejora detectada no implica que recta sea óptima.
Reportar fracción de casos mejorados con denominador, ganancias, s, límites
activos a distancia≤1e-6, estado de cada tramo y controles, sin ocultar inconclusos.
Si s alcanza frontera, no ampliar dominio: la solución está limitada por la familia.
No se evalúan curvatura ni capacidad predictiva. No comparar ganancias entre
métricas como si sus escalas funcionales fueran una ventaja predictiva.

Guardar tablas de resultados, trazas de búsqueda, validación de tramos, controles,
resumen, procedencia, recursos y manifests. Repetir exactamente una vez para
reproducción; comparar salidas científicas byte a byte, tiempo separado.
Presupuesto por corrida 180 s/512 MiB, un hilo. Preservar fallos sin ajustes.
Congelar diseño/configuración en Git antes de programar y medir.
