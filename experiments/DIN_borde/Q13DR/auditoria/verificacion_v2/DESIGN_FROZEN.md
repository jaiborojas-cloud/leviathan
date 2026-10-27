# Verificación independiente Q13DR v2 — protocolo antes del código

Objetivo fijo: commit245d735ffae59fa28e6458d1cb8a9bd21387d278, analista SHA
afb807aad20830e0402c5fdb8f946f783b2a0835f497855e12364bf1fae356e6,
pruebas SHA7e16fa29737586044feb943d103fd9f5b04cd72420d6e97afaf42b524dba16b9.
Leer diseño/pruebas/informe de pruebas v2 y auditoría7ed54353. Guardar snapshots
sin modificar el diseño ni el analista. Sólo adiciones en verificacion_v2/ y PR
aparte desde main; los resultados v1 siguen intactos en #104 y sus arrays.

## Regresiones por hallazgo

Reejecutar los casos de cases_v1, la extensión y los casos N200 anteriores contra
el nuevo analista. Una parada nueva por dominio/80% puede impedir llegar a otro
fallo: registrarla y añadir un caso válido que ejercite la corrección directamente.
F01: caso adicional N20, sólo L5 pierde tres filas del split0 (95% comunes),
c=C_l+(-1)^l·.002·s. Trazar c de punto frente a las medianas comunes.
Trazar bootstrap completo con mismos draws/folds/recálculo D/c/β, sin cambiar
valores. Casos reducidos B39/NB16 como en v1; CLI válido usa nominales completos.

F03/F06: repetir planes inválidos y confirmar código3, prefijo ABORTA y ausencia
de traceback; F04: rangos medios y null para constantes; F05: texto/fórmula de
rango y coexistencia de MODULA con equivalencia secundaria. Verificar todas las
ambigüedades previas según las decisiones del diseño v2, sin imponer tolerancias.
La suite del autor sólo se lee, no se ejecuta porque abre un fixture bajo C2.

## Defectos nuevos: casos prospectivos

- Pendiente con c constante decimal (.1,.2,.3,.4,.7,.9), frente a .5 binaria:
  debe ser no identificada incluso si restar la media deja residuos de redondeo.
- N200: exactamente160 splits comunes (40..199), c común por inicialización
  [.04,.04,.1,.9,.9] igual en seis niveles. Distribuir los40 splits excluidos
  en grupos7,7,7,7,6,6 por nivel; invalidar k<3 en el grupo de ese nivel. Fuera
  de comunes fijar alturas [.9,.7,.61,.54,.42,.04]. Compensa el gate operacional
  pero deja c común constante. No forzar ningún veredicto si no aparece defecto.
- Mismo patrón de pérdidas, c común por k=[.04,.04,m_l,.95,.95], con m_l creciente
  [.3,.35,.4,.45,.5,.6]. Contrastar rango declarado con max(c)−min(c), no sólo
  primer−último; comprobar signo del margen de variación reportado.
- eps entero10**400, planes/tabla ausentes o directorio, JSON mal formado,
  límites bool/entero400/401, niveles/tipos, dominios finitos y no finitos.
- Fuente con L variable sólo por split0: NB300 para comprobar cuántos fallos se
  generan, cuántos índices/errores se retienen y que no se redibuja ninguna réplica.
- JSON estricto, nulos explícitos y resultados/campos de secundarias. Ninguna
  alteración del analista ni de los archivos de entrada congelados.

## Monte Carlo repetido, semillas idénticas

Mismo generador y kernel independiente por bytes/SHA que la auditoría v1.
Regenerar X/L/Y, no reutilizar resultados como observaciones. Comparar sus bytes
con arrays sintéticos v1 como control de identidad de semillas, sin escribirlos.

| Celda | Índice original de seed | N | Réplicas |
|---|---:|---:|---:|
|null_N200, d=.02 constante|0|200|400|
|null_N400, d=.02 constante|1|400|400|
|positive_N400, β=+.03,d central=.02|3|400|200|

SeedSequence([910300,índice_original,réplica]); caso910100 y controles910200.
Permutaciones5000, seed260001; bootstrap2000, seed860001; folds260010. Ruido
independiente entre niveles como en v1; c fija por nivel, compuerta válida.
Contrastar punto/p/bootstrap con funciones v2 antes de usar el motor. Reportar
primaria MODULA/NO_CONCLUYENTE, NO_MODULA secundaria e INCONCLUSIVE por compuerta,
con denominadores globales y condicionados y Wilson95. No confundir equivalencia
con un veredicto primario ni redefinirla para repetir las tasas antiguas.

Dos procesos/un hilo BLAS, sin redes ni geometría. Guardar todos los fallos y
versiones; si hay un defecto del verificador, enmienda previa a corregir. No
datos Wine/C2/Q13 reales. No recalibrar reglas, dosis, semillas o tamaños tras ver
resultados. No afirmar calibración universal ni aprobar la congelación en nombre
del responsable. Manifest y verificación final, arrays fuera de Git.
