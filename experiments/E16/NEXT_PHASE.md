# Fase posterior — diseño candidato, no ejecutado ni preregistro confirmatorio

La fase analítica sólo justifica probar instrumentación en una red pequeña;
no justifica prometer poder predictivo ni entrenar automáticamente.
Antes de ejecutarla debe congelarse un protocolo nuevo con los siguientes pasos:

1. Red ya disponible con procedencia y permiso fuera de T2-A; usar conjunto
   nuevo y estados que no sean los T1/E15 usados para descubrir hipótesis.
   No reutilizar checkpoints, protocolos ni outcomes T2-A. Si no existe un
   artefacto independiente autorizado, detener esa fase y declarar el faltante.
2. Fijar panel Fisher, funcionales, cartas y una referencia SPD transportada;
   verificar convergencia de derivadas con autodiff frente a diferencias finitas.
   Si se usa Fisher degenerada, certificar rango constante y admisibilidad sobre
   el dominio, o declarar explícitamente la regularización como estimando distinto.
3. Controles: carta invertible; mezcla afín; producto/cuadrática con términos
   mixtos; π con descenso analítico garantizado y π sin descenso como negativo.
   Las secciones elegidas deben reportarse como restricciones.
4. Observable primario instrumental: residual entre B directo y cadena completa;
   secundario: rango con incertidumbre respecto al panel y separación espectral.
   No extrapolar espectros entre cartas. Determinar tolerancias antes de mirar
   contrastes de tareas, según precisión, acondicionamiento y error de panel.
5. Hipótesis nueva candidata, aún no validada: en una familia y distribución
   fijadas, términos mixtos no nulos pueden dar rango distinto al de la mezcla
   afín; cuantificar su frecuencia con incertidumbre en estados independientes.
   Algebraicamente es posible, ya lo muestran los controles; que ocurra de forma
   estable en redes y resulte informativo es lo que queda abierto.
6. No atribuir emergencia a rango menor. Una eventual pregunta predictiva exige
   target, baseline simple, partición externa, pérdidas, presupuesto, criterios
   de faltantes y tamaño muestral definidos en otro prerregistro. Curvatura y
   geodésicas sólo después de validar campo, dominio y estabilidad instrumental.
