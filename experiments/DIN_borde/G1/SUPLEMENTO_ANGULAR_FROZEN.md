# Suplemento angular · diseño diagnóstico posterior al diseño principal

Este documento se compromete ANTES de escribir/ejecutar su código. No cambia
DESIGN_FROZEN, semillas, resolución, controles o reglas H1–H5 del protocolo
principal, que sigue corriendo. No sustituye ningún rho ni reentrena redes.

Motivo observado: P60_s02_k0_u010 tiene diferencia720/400 frente a1440/800
de1.0592%, auditada como fallo según el umbral original1%. El retorno1440/800
da rho≈3.26098 y rho_min_gl≈2.19203. Eso sólo sugiere un problema de búsqueda:
la cuadratura GL podría ser inexacta. No se declara todavía un defecto probado
en ese dato. D2 ya documentó problemas en caras; no se reabre esa etapa.

Selección AD HOC Y EXPLÍCITA: ese estado motivante, más los tres centinelas
R27/P60/W27_s00_k0_u010. Son4 estados G1 ya previstos; no se estima prevalencia
ni se infiere significación de una selección motivada por una discrepancia.

Después de completar el protocolo principal, integrar sólo los cuatro rayos
AXIALES EXACTOS u=(1,0),(-1,0),(0,1),(0,-1) en cada estado, con M/f archivados.
Se usa integrando original de rho_borde.py/Geometry.jac intactos, sin llamar
rayos de T2 ni alterar senos/cosenos o globals. Las direcciones exactas evitan
que sin(pi)≈1e-16 convierta un empate de cara en una transición a tiempos enormes.
Cuadratura quad epsrel1e-10/epsabs1e-11, cortes0,1/gap,8/gap,32/gap para
todas las brechas positivas de f·u. No se optimizan ángulos ni se reemplaza
el resultado original. Tiempo máximo adicional300s; conservar errores.

En el corte final S, comprobar que la brecha media estimada del softmax es
menor que la mínima positiva. Después todas las probabilidades no máximas
decrecen; la variación total restante en norma1 es≤2 sum exp(-gap S)/m,
m=número de máximos. Cota flotante de cola métrica:
2 sqrt(lambda_max(M)) sum exp(-gap S)/m. Registrar hipótesis PSD/monotonicidad,
errores de quad y cola; no se llama a esto certificado de intervalos.

«TESTIGO_NUMÉRICO» si alguna longitud axial más error estimado y cola está
por debajo de rho nativo por margen relativo>1e-4. Eso indica que el retorno
no es el mínimo numérico entre esas curvas concretas; no determina el mínimo
global verdadero. «SIN_TESTIGO» si no ocurre y todos los controles son válidos;
«INCONCLUSIVE» ante fallo. No es una nueva decisión H1–H5.

La entrega distinguirá veredictos operacionales congelados y esta advertencia
sobre interpretar rho como mínimo matemático. Fuentes y todos los retornos
previos se conservan byte por byte; no se modifica ningún instrumento.
