# Progreso Q13-SEP v2 · 2026-11-02

Se recibió la auditoría de Claude transmitida por el responsable: corregir visita principal y emparejamiento de temperatura antes de congelar. Se leyeron AGENTS.md, configuración/esquema v1 y estado del PR #134. V1 se conserva íntegra con sus fuentes y manifiestos.

El diseño v2 se comprometió en 1e57f768: principal u250, u10 descriptivo, T* de escala aplicado a LP y rejilla C de 33 temperaturas con argmin de c independiente de S. Se mantienen dosis candidatas, fases, receta y semillas; no se ejecuta modelo o PRNG. Se actualizan cuentas a 20.703 llamadas M máximas, incluida la prueba corta de 825. Costes solo aritméticos a confirmar en el PC.

Se aclaran el control exacto y el tolerante, y que temperatura redefine las variables de una futura primaria de señal, con cuidado explícito de no usar u250 para fabricar un predictor temprano. El analista robusto continúa BORRADOR; no se modifica ni se ejecuta. La familia futura de dos contrastes/Holm sigue siendo una propuesta para el diseño posterior, sin potencia estimada aquí.

La comprobación de esta entrega cubre solo coherencia documental, aritmética, hashes y enlaces. Cero entrenamientos, llamadas M/rho o estadísticas. Claude revisará esta v2 antes de que el responsable la congele; el productor sigue pendiente.
