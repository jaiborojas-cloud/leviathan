# Fase0 · antes del código/medición

AGENTS raíz leído. Checkout existente limpio, main actualizado a32536da;
rama research/din-i2-rho-v2. Sólo I2 se modifica. Se leyeron fuentes/teoría y
tablas sintéticas D2/AG/AH y el testigo Iris G1. No se ejecutó geometry ni
v1 ni se cargó un estado M en un cálculo de longitud.

No se abrió el informe C1/sensibilidad_aristas ni Wine/T2/C1. El68% citado
por el usuario se mantiene como contexto aportado, no resultado verificado.
Los40 AF se tomarán únicamente de su copia sintética archivada EN AG.

Se constató en fuentes que AG ya separaba normales exactas de casi empates;
su rho archivada no es necesariamente la llamada literal al v1 d8ec69f8.
El benchmark contemporáneo se ejecutará sobre la fuente congelada y se
distinguirá del dato histórico. AH estudia caminos quebrados: no se usa su
longitud como cota superior de la mejor semirrecta desde0.

Hallazgo teórico previo: rho_vert=2 rho_caras en los triángulos AG. Se fija
por ello el criterio literal de compatibilidad y su posible FAIL esperado,
sin confundir cambio de estimando con defecto numérico. Miembros de caras
se decidirán racionalmente, sin fusionar casi empates por conveniencia.
Entorno revisado con cloud-environment-runtime; no red para datasets.

## Código v1, antes de ejecutar
Se implementan topología racional, conos completos, límites laterales, cuadratura
logarítmica con restos, referencias independientes MP y cohorte fijada de302 casos.
La primera ejecución sólo podrá empezar después del commit de estos archivos.

## Primer fallo conservado
Controles PASS archivados; falla sólo su impresión por numpy.bool_.
Enmienda v2 congelada antes de corregir. No se sobrescriben salidas ni código v1.

## Cúspides · r2 prospectiva
La enmienda33a9b43 precede al código r2. Se archiva el instrumento r1 bit a bit;
se subdivide en ceros antes de optimizar/contrastar casi rango uno. Se repetirán
los302 casos y24 sensibilidades, sin cambiar umbrales y conservando r1.

## Cierre r1
302/302 salidas; I2 FAIL por seis comprobaciones en gaussian/near_collinear
random_rank1 (sensibilidad y contraste MP). I1/I3 PASS; I4/I5 PASS_DESCRIPTIVE.
No se borran ni sustituyen los fallos. Ejecutó run_v2 bajo fb84731, con el
instrumento r1 a105dbe cargado antes de las ediciones posteriores.

## Cierre r2
Enmienda33a9b43 → código35aebfd → medición run_r2.302 salidas, seis FAILED
por brackets vectorizados/escalares inconsistentes; I2/I3/I4 INCONCLUSIVE.
Controles PASS. Fuentes, tiempos y trazas se preservan.

## Cierre r3
Enmiendaf7996f8 → código76ecd66 → controles y cohorte run_r3.
302/302 completos;884 comprobaciones PASS,24 sensibilidades,4 contrastesMP80,
1693 soportes completos verificados; ninguna selección de estados.
I1/I2/I3 PASS, I4/I5 PASS_DESCRIPTIVE. I3 sólo66 casos D2 elegibles:
el v1 literal no acertó en ninguno de los40 triángulos AG; no se confunde
el escáner propio de AG con v1 d8ec69f8. AF se describe sin mínimo certificado.
Mediana de coste102 pares:.26354s frente a4.46347s; ratio mediano.06067.
Comparadores v1 reutilizados en r2/r3, misma sesión/recursos. No hay transferencia
a Wine/T2/C1. verification.json PASS, arrays externos con SHA, fuentes intactas.

## Decisión de entrega
Se conserva el instrumento público r3 y copias exactas r1/r2. El manifest
cubre documentos, código y salidas; los arrays permanecen fuera de Git.
Push y PR borrador están autorizados explícitamente por la petición del usuario;
no se solicita fusión ni se modifica ningún archivo fuera de I2.
