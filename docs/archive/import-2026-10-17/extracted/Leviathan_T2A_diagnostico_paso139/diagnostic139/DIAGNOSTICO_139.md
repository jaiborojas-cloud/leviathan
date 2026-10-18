# RIPG — diagnóstico aislado del paso 139 (2026-10-15)

## Estado e integridad
Entrada RIPG_RESULTADOS_PC.zip SHA-256 f082f89bd76f94e5bd8060021939008363228aabd0f377d0cd4cfa6eb1ca555b.
17 hashes del manifest válidos, 13 segmentos ZIP con CRC válido, pasos 91–139 contiguos. Último estado PAUSED, r=0.07447265825972331, siguiente paso oficial del replay 140. No se modificaron checkpoints ni se añadieron pasos a la cadena. El estado oficial antiguo float64 continúa separado de este replay MPFR. No se abrieron nuevas visitas ni se calcularon outcomes.

## Localización
Se reconstruyó el estimador DOP853 desde K guardado y su escala atol+rtol*max(abs(y_old),abs(y)). Norma de error aceptada: 0.40524556341654594 (<1). Las contribuciones indicadas son fracciones de la suma cuadrática del término E5 normalizado, no una descomposición aditiva del estimador completo E5/E3.

Índices desde cero, 2048 rayos:
- 1775: 79.1051839 % de E5; condición métrica en alta precisión 3.323811966e11.
- 1776: 20.8761103 % de E5; condición métrica 2.496840013e11.
- Ambos: 99.9812942 % de E5.
- Los cinco primeros: 99.999999438 %.

La condición aquí es de G en la carta utilizada, NO kappa(Dexp), ni un diagnóstico de conjugados.

## Crecimiento de coordenadas
Rayo 1775, paso94: norma(P)=106.8965, norma(v)=73044.81.
Paso118: norma(P)=212.6079, norma(v)=346052.85.
Paso130: norma(P)=341.0646, norma(v)=4059284.08.
Paso139: norma(P)=440.3738, norma(v)=28937627.88.
En139 P=(267.57010087,-349.76468209); v=(17406963.12,-23116745.93).
Autovalores de la parte simétrica de G: aproximadamente 1.19418122e-15 y 3.96923384e-4; positivos en el punto evaluado.
v^T G v=0.9999999976597301: el crecimiento en coordenadas coexiste con rapidez intrínseca prácticamente unitaria.
Rango de logits=1698.55; peso softmax mínimo aproximadamente1.9962e-738 (no representable como float64 positivo).
Esto hace plausible una aproximación a una frontera de la inmersión/escape en coordenadas, pero NO prueba límite a radio finito, incompletitud geométrica, cut locus ni singularidad intrínseca.

## Contraste de precisión
14 rayos preseleccionados por E5 (10 mayores) y controles angulares0,512,1024,1536.
Referencias independientes mpmath80/120 dígitos usando la matriz M y f originales. Se contrastan aceleraciones en los mismos estados float64 guardados.
En todos los puntos, MPFR169 y referencias80/120 producen la misma aceleración después de redondear a float64. Esto no implica error matemático exactamente cero ni verifica toda la trayectoria.
La implementación geométrica original float64 difiere de referencia120 en aceleración relativa máxima por componente: 2.2748e-4 en1775; 5.4891e-5 en1776. No se atribuye toda esa diferencia exclusivamente al underflow: intervienen también cancelación y acondicionamiento.

Comprobación adicional en COPIAS de los rayos1775 y1776, intervalo fijo [0.07447265825972331,0.07447309083990389], DOP853, rtol2e-10/atol2e-12 sin cambios. RHS MPFR169 frente a implementación independiente120 dígitos: ambos exitosos, mismas evaluaciones (70 y43 respectivamente), diferencia escalada en513 puntos=0 tras redondeo. El integrador/estado sigue siendo float64 en ambos; esta prueba no valida un integrador de estado completo en alta precisión. Son sondas diagnósticas y NO pasos confirmados140 ni nuevos outcomes.

## Conclusión y siguiente intervención
Hay evidencia directa de que un sector angular muy pequeño obliga a reducir el paso, con fuerte crecimiento de coordenadas, métrica mal condicionada en esa carta y rapidez intrínseca conservada. La falta de precisión de la aceleración MPFR169 no aparece como explicación del atasco en los puntos/intervalos probados. Aumentar sólo precisión o velocidad de CPU no está justificado como solución por estos datos.
Mantener pausa139. Investigar la aproximación a la frontera mediante representación de la inmersión y, si corresponde, una carta alternativa equivalente, con validación de solapamiento antes de usarla en producción. Un cambio de coordenadas debe conservar exactamente geometría, radios, observables y criterios; no debe completar o extender el dominio silenciosamente. Si hay una frontera intrínseca real, documentar la imposibilidad de continuación en vez de imponer cruce artificial. No descartar rayos ni aflojar tolerancias.

## Reproducción
Scripts diagnose.py y local_check.py; fuente exacta en el paquete Windows CP90. numpy/scipy/gmpy2 según paquete; referencia mpmath. Ejecutar desde la raíz que contiene Windows_RIPG_T2A_CP90 y upload/RIPG_RESULTADOS_PC.zip. Datos all_rays.csv, history.json, precision_checks.json, local_checks.json, results.json. Hashes en manifest.json. La cadena de producción y el protocolo no se modificaron.
