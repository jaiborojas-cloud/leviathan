# DIN-G2 · registro prospectivo

## Fase0 · lectura antes del diseño

AGENTS raíz leído y main actualizado a552da0d. Sólo documentación agregada
C1/D7 y G1, teoría D2b y código autorizado: core, geometry, I2 r3 y funciones
matemáticas C1_v2. No se abrieron tablas, checkpoints ni estados Wine/T2/C1,
ni arrays de Iris G1. No hubo piloto ni entrenamiento ni medición antes
de congelar. Se verificó únicamente disponibilidad/versiones del entorno:
venv leviathan, TorchCPU2.9.1, NumPy2.3.5, SciPy1.17.0, CPU cuota2.

C1 usa centrado intra-split y z global con base cúbica; D7 añade Rc lineal
a esa base. Importarlos no requiere su CLI ni archivos de cohorte. core
define load_wine, pero no lo invoca al importar: se impedirán lecturas de
datasets y llamadas a load_split. Red13→64→32→3 sin adaptación de logits.

Se fijan seis niveles de ruido analíticamente por separación de medias,
emparejados por epsilon, pesos y lotes;600 entrenamientos,4200 visitas.
No se presupone éxito en producir variación: falta de manipulación →
INDETERMINADO. I2 r3 es primario rho_caras y secundario rho_vert, intacto.

El diseño se compromete antes de crear código de generación/medición.

## Código v1 antes de ejecutar
Generación emparejada, fuentes importadas sin cambios, IO exclusivo, guarda,
funciones C1 originales y reimplementación independiente para controles.
El commit del código debe preceder a controles y cualquier entrenamiento.

## Controles y ejecución
Prepare bajo7e6c715: PASS triángulo,face26,r3,generador y reproducción
independiente de D/p originales C1 en cuatro tablas sintéticas/999 permutaciones.
Cohorte completa:600 entrenamientos,4200 visitas, cero errores/invalidaciones;
1114.62s de pared,CPU2/BLAS1. Se mantuvieron pesos y lotes emparejados entre
niveles. Las tres reconstrucciones prefijadas de M dan error relativo0 y f
idéntica, sin reentrenamiento ni repetir rho.

## Análisis final sin cambiar reglas
Primario rho_caras,secundario rho_vert; todas las compuertas100/100 y20/20.
H-var CONTRADICE_DESCRIPTIVAMENTE: Spearman(D,V)=−.6375356;V máximo.104 en
s=.5 con D=−.032711. En s=2/4,V0 y D=.044534/.032361. Los p999 .055/.072
son exploratorios; no se usan como criterio confirmatorio. D_X|R=.023340
y.043676 respectivamente; la fracción no se recorta ni interpreta causalmente.
La concentración mediana c=.324/.254 allí limita una lectura condicionada a
colapso; no se selecciona a posteriori un subgrupo para cambiar el resultado.

## Integridad, archivo y figuras
verification PASS:4200 estados,600 trayectorias,12740 archivos externos conSHA,
100 grupos de pesos iniciales y700 de lotes emparejados; fuentes intactas.
Archivo JSONL reversible4200/4200 bit a bit, sin borrar originales; agrupación
para que el PR sea consultable. No es una modificación científica ni selección.
La figura PNG/SVG se inspeccionó; Fontconfig emitió un aviso no fatal de caché
sin afectar la salida. Consolas y todos los resultados se conservan.

## Entrega autorizada
Sólo G2. El usuario autoriza explícitamente push y PR borrador, sin fusión.
La fase científica concluye sin alterar instrumentos ni etapas anteriores.
