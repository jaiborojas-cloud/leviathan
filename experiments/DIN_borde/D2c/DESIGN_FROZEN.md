# DIN-D2c · diseño congelado de la auditoría v1

Exploratoria, independiente, sin entrenamiento. Fecha de usuario2026-10-25.
Base main de1cb4edcae812b7e3f7ff53d65ae5bb994ac9c4. Sujeto EXACTO de auditoría:
árbol6b17d25216381238f5a0f38f8eb9e7eb87f0a4da de claude/din-confirmatorio-diseno.
No se sigue una rama móvil ni se modifica C1. Sólo se escribe en D2c.
Este documento se compromete ANTES del código de auditoría y las mediciones.

## Fase0 y acceso

Se leyó AGENTS raíz, diseño v2 completo, analisis_C1_v1.py línea por línea,
c1_cohorte.py v2 y recomendación D2b. No hay AGENTS subordinados.
Se inspeccionaron sólo cabeceras de los dos CSV autorizados, sin estadísticas.
No se ejecutó ningún script ni control del sujeto. Los únicos datos empíricos
que se abrirán son d1/d1_estados.csv y d6/PROGRESO_d6.csv, de MAIN fijado.
Se unirán por trajectory/split: X=log1p(-p_min_val) y L=log(rho_borde) de
u10 en d6; Y=log(rho) de u250 en d1; rho30 de d6 sólo para secundarias.
Todos los splits12–167, sin escoger por resultado. Duplicados, ausencias y
valores inválidos se registran, nunca se sustituyen. Datos gastados:
ningún p de esta tabla es confirmatorio.

Se copiarán bytes de las tres fuentes del sujeto, con SHA, después del commit
de diseño. No se ejecutará c1_cohorte, core, geometry, entrenamiento ni rho.
El original de análisis se ejecutará como caja negra en un proceso aislado;
la referencia propia NO importa ni llama a ese código. La separación es
comprobable en sus módulos. Una guarda bloquea T2, estados y checkpoints.
La función cuerda podrá extraerse por AST para un control geométrico algebraico
sintético; ninguna medición de geodésicas ni ejecución de una etapa cerrada.

## A1 · contrato y revisión estática

Tabla requisito→líneas→OK/AMBIGÜEDAD/DEFECTO, distinguiendo:
1. Variables/logsumexp, centrado, z global (de poblacional), potencias centradas,
   10 folds por splits ordenados, default_rng260010, OLS sin intercepto tras
   centrado, D fuera de muestra, pendiente completa, permutación X intra-split
   (260001,5000), regla conjunta p<.05 y pendiente>0.
2. Compuerta, denominadores planificados156×5, faltantes, mínimo3 por split,
   empates, variación de X, inputs positivos/finitos, tablas vacías, trazabilidad.
3. Secundarias y auditoría/cuerda de cohorte. No se audita entrenamiento.

Hallazgos estáticos a probar, NO veredictos todavía: cohorte omite filas con
error y análisis cuenta faltantes sobre filas recibidas; validación ocurre
después de primaria; np.allclose(Xc,0) introduce tolerancia no documentada;
p usa D-1e-15 aunque el texto usa D. Se distinguirá del problema estadístico
de intercambiabilidad de X condicionado a L.

## A2 · referencia independiente y comparación

Propia referencia: centrado matricial por grupos, construcción independiente
de potencias, SVD/QR y predicciones por fold; sin copiar helpers del sujeto.
Misma asignación de folds y flujo RNG de permutaciones (orden por np.unique).
D debe coincidir a1e-10 absoluto en tablas no degeneradas; pendiente a1e-8
relativo/absoluto. Se reporta p literal >=D y también con la holgura numérica
1e-15 del sujeto; p operativo debe coincidir exactamente o quedar marcado.
Las diferencias del literal por empates numéricos se registran por separado.

Comparaciones: descubrimiento con5000 permutaciones y31 tablas sintéticas
con199: siete controles propios del autor aplicados a la tabla gastada y
24 tablas (12 escenarios×2 semillas260201/260202). Menor B se declara;
no equivale a ejecutar la decisión confirmatoria a5000 en esas31 tablas.
En toda tabla se ejecuta primaria del sujeto y referencia independiente.
Además se contrasta la versión por lotes acelerada de la referencia, usada
en Monte Carlo, contra su versión explícita y el sujeto.

## A3 · controles y adversarios fijados

Siete controles exactos de aplicar_control del sujeto: X=L, cúbica de L,
Y_g_L con X afín, X constante, L_con_error, incremento_real r=.3, ruido;
la referencia reconstruye sus fórmulas sin importar el sujeto.

12 escenarios sintéticos,156 splits×5 salvo n3/n4:
L=mu_split+N(0,1), mu_split=N(0,.7); todos los ruidos indicados independientes.
No se ajustan generadores para obtener un resultado.

- ruido: X normal, Y=.7L-.2L²+.05L³+normal.
- incremento: Y anterior+normal latente T, X=.3T+sqrt(1-.3²)normal.
- heterosplit: X y errorY normales escalados por sigma_s=exp(linspace(-2,2,156));
  Y conserva base cúbica; no relación entre innovaciones X/Y.
- n3 y n4: misma construcción de ruido;3 o4 observaciones por split.
- outlier_L: ruido, pero primer L se desplaza40 desviaciones y Y se recalcula.
- empates_X: X=0 en80% esperado, -1 en20% (Bernoulli); Y cúbica+normal.
- escalon: X=1[L>0], Y=2X+.2normal.
- log: X=logaddexp(0,L), Y=2X+.05normal.
- sin: X=sin(3L), Y=X+.2normal.
- entre_splits: X=mu_split constante dentro del split, Y cúbica+normal.
- nulo_condicional: X=.9L+.1normal, Y cúbica+.5normal.

Escalón/log/sin tienen X función de L. Un PASS puede ser incremento REAL
frente a una BASE CÚBICA LIMITADA, sin información condicional nueva. No se
confundirá esto automáticamente con un defecto del código. Se distinguirá
de un falso positivo bajo un nulo de intercambiabilidad válido.

Pruebas de CLI original, con tabla/compuerta totalmente sintéticas y SHA,
B5000/BW20000 SIN parchear script: compuerta verdadera/falsa/ausente;
156×5 completa con señal fuerte;47 filas ausentes frente a47 filas con error;
40 splits omitidos; exactamente39 faltantes (5%) y40 (>5%);
X constante; X sólo entre splits; L constante; Y constante; rho=0 y rho<0;
tabla vacía; todos splits con2 trayectorias; duplicación de filas/IDs.
Se conservan retornos, stdout/stderr, exceptions y timeouts, aun si el código
no alcanza INCONCLUSIVE. Presupuesto por CLI300s y total14400s; no sustitución.

Se añade un control de cuerda del sujeto en27 puntos:26 colineales en una cara
y uno fuera, M=e0e0ᵀ+1e-12 I. Una dirección normal llega a toda la cara;
se compara la cuerda devuelta con una curva monótona de longitud acotable
analíticamente. No se deduce que ese caso ocurra en Wine.

## A4 · tamaño y potencia independientes

Remuestrear156 splits completos con reemplazo del descubrimiento; asignar
IDs nuevos y mantener5 filas. Semilla maestra260400 y subsemillas por réplica.
400 réplicas POR escenario nulo y400 POR r=.10,.15. B=199 por réplica,
semilla de permutación260001 y folds260010 como en el script. Arrays de
permutación reutilizables cuando la estructura de tamaños es idéntica;
no se reutilizan datos sintéticos entre réplicas.

Tres nulos: (N0) X normal independiente, L/Y de bootstrap; (N1) X=.9z+.1ruido,
Y=.7z-.2z²+.05z³+ruido, sin incremento real con base correcta;
(N2) X y errorY heterocedásticos por split sigma=exp(linspace(-2,2)),
independientes, Y base cúbica. Misma regla conjunta p<.05 y betaX>0.
Se informa Wilson95%, numerador/denominador y resolución p=1/200.
N0/N2 son nulos intercambiables; N1 no tiene intercambiabilidad X|L garantizada.
Con signo añadido a un D bilateral, bajo simetría cabe esperar tamaño cercano
a.025 (y algo menor por discreción), no necesariamente.05.

Potencia: en cada bootstrap, e=residuo intra-split de Y sobre cúbica,
X=r e/std(e)+sqrt(1-r²)normal, como definición del autor. r es parámetro
generador, no correlación muestral exactamente fijada. Se informa también
correlación realizada. Es potencia de este generador retrospectivo, no
garantía para un predictor temprano prospectivo. Comparación con §6:
4/96 de nulo, aproximadamente22/32 para r=.10 y32/32 para r=.15;
usar intervalos binomiales, no exigir igualdad de porcentajes redondeados.

Reglas A4: inflación demostrada si límite inferior Wilson de PASS>.05 en
un nulo válido; ausencia de inflación al alcance medido si límite superior
≤.075; otro caso INCONCLUSIVE. Compatibilidad de potencia con §6 si intervalos
95% se solapan, etiquetada como tal;400 y199 no certifican tamaño5000 exacto.
Se ejecutarán además las réplicas0..4 de N0 y cada r con5000 para comprobar
sensibilidad a B, con referencia validada. No se seleccionan por outcome.

## Veredictos y entrega

A1 PASS si concordancia sin defectos; FAIL si defecto reproducible; dudas
sin resolución INCONCLUSIVE. A2 PASS si todas las comparaciones no degeneradas
cumplen tolerancias/p operativo; FAIL si discrepancia resuelta; errores propios
INCONCLUSIVE hasta enmienda versionada. A3 PASS si controles cumplen su
contrato y no hay PASS sin incremento bajo nulo válido; FAIL ante contraejemplo
demostrado del contrato; patrones/modelo limitado se describen sin forzarlos.
A4 reglas anteriores, distinguiendo tamaño y potencia. A5 PASS_DESCRIPTIVE si
lista cambios necesarios/ opcionales con evidencia, sin decidir por responsable.

Conservar todas las versiones, fallos, entorno, tiempos, hashes y arrays fuera
de Git (/workspace/work/din-d2c-v1-arrays). Dos procesos numéricos, BLAS1.
Defecto propio → enmienda comprometida ANTES de corregir, archivos nuevos,
sin sobrescritura. JSON convierte escalares NumPy antes de crear el archivo.
Guarda exige código comprometido antes de ejecutar; éxito del commit se
comprobará en llamada independiente. PR en BORRADOR, no fusionar.
