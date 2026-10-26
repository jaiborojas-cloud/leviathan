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
