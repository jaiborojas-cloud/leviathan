# Auditoría independiente DIN-Q13-DR

**Recomendación: no congelar este analista todavía.** Corregir primero los
defectos reproducibles de bootstrap, población del estadístico y validación del
plan; resolver las ambigüedades del diseño. No se cambió ningún archivo original.

El diseño/analista revisados siguen vigentes en PR #103, revisión78a7d2e; el
analista es idéntico al snapshot iniciale7dfc435, SHA c9159325…. La comparación
de revisiones está archivada. Este dictamen no cambia ningún estado científico.

Hallazgos necesarios antes de congelar:

1. **ALTA:** observado y bootstrap usan poblaciones distintas para c cuando hay
   faltantes. A N200, con4.8% por nivel, la compuerta pasa pero β bootstrap queda
   singular y el resultado incluye IC con NaN.
2. **ALTA:** L puede ser variable observado y constante en un remuestreo: crash
   LinAlgError no capturado. Reproducido también a N200.
3. **ALTA/MEDIA:** planes con seis eps=0 o sin eps se aceptan; N no entero se
   trunca; N0 y claves faltantes provocan excepciones sin control.
4. **MEDIA:** Spearman con empates es incorrecto: publica−1 con los seis D iguales.
5. **Diseño:** ±.02 en β no equivale a un cambio de D<.006: con rango .5 permite .010.
6. **Pruebas:** buscar ABORTA por substring puede ocultar un KeyError del CLI.

Sí se verificaron emparejamiento de los seis niveles, folds originales y
recálculo de D/c/β; no se encontró el supuesto error de fijar β en bootstrap.
Empates exactos de c, faltantes5%/exceso, IDs y constancia observada se comportan
como el contrato. PERSISTE tiene correctamente prioridad sobre DESAPARECE.

**Tasas nominales,1.400 réplicas sintéticas:** no se observó exceso global de5%
de falsos MODULA:2.00% en N200 y2.50% en N400 bajo D constante=.02, con IC95
Wilson superiores3.90% y4.54%. Sin embargo, **NO_MODULA fue0/400 en ambos**
(límite superior .95%): la potencia de equivalencia es muy baja bajo ruido
independiente. En alternativas fuera de banda, falsos NO_MODULA0/200 por caso.
Las tasas son específicas de los generadores; no certifican calibración universal.

Proponer al responsable: corregir F01–F06, aclarar precisión L4/L5, mínimo común,
dominio, tolerancias y tendencia versus monotonía; probar después la versión
corregida sin sobrescribir ésta. Justificar la dependencia entre niveles en la
potencia prospectiva antes de dimensionar una cohorte. No se decide su protocolo,
no se entrena ni se usa ningún dato real.

[Defectos, severidad y correcciones](DEFECTOS.md) · [tasas y límites](TASAS.md) ·
[revisión vigente](REVISION_OBJETIVO.md) · [verificación](verification.json).
