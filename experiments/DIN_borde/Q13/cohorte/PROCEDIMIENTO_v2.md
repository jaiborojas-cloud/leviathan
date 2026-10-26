# DIN-Q13 — ejecución de cohorte, protocolo v2

Rige el [diseño v2](../../DISENO_DIN_Q13_v2_CONGELADO.md), SHA
`1eda9d43e6425ca50934db8364607660a91ac6f3269d42f22ec97c644e42ae6f`,
y lo no cambiado del [v1](../../DISENO_DIN_Q13_v1_CONGELADO.md).
Main actualizado tras #97/#98; no se modifica ningún archivo v1 ni diseño.

La receta de scripts/recipe_v1.py se copia **byte por byte** a scripts_v2/.
Calibrate sólo cambia la importación del soporte y la carpeta de salida.
Support sólo cambia configuración, rutas de código a verificar y manifiesto v2.
Config fija LS={.001,.002,.005,.01}, WD={.2,.5,1,2}, con split=741000+s,
init=742000+5s+k y lote=743000+5s+k. A0 se mide de nuevo como referencia, sin
compuerta de régimen en calibración. No se cambia entrenamiento ni instrumento.

900 ejecuciones: nueve condiciones, 20 splits por cinco inicializaciones. Sólo
c250, q250 y acc_panel250; nada de X ni rho. Dosis mínima con mediana c en
[.55,.70] y diferencia absoluta de mediana acc frente a A0 <.05. Sin elegibles,
descartar el brazo; ambos descartados, cerrar «manipulación no lograda con dos
rejillas», conservando todos los resultados. No sustituir fallos.

Orden con commit y push previos a cada paso: código → calibración/dosis →
potencia simulada → plan → compuerta → cohorte → publicación. Si procede, la
potencia usa sólo G3 s=.8, nunca C2 ni calibraciones como datos de señal. Ningún
tamaño elegible, no entrenar. Si N>400, detenerse y solicitar confirmación del
responsable en el PR antes de entrenar. No se ejecuta el analista contra datos reales.

Semillas de cohorte sin cambios: 711000+s, 721000+5s+k, 731000+5s+k; no usadas
en calibración. Datos/pesos/lotes pareados entre brazos. Archivos nuevos y arrays
externos exclusivos: /workspace/work/din-q13-cohorte-v2-arrays/. Se mantienen los
fallos y versiones anteriores. Toda corrección de un defecto exige enmienda previa.
