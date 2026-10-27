# DIN-Q13-M2: potencia en preparación

La preparación apunta al PR#114,commit525c7455 y analista SHA15ca7b42…. No son archivos congelados. Los snapshots preservan la lectura exacta y no modifican el PR de diseño.

Antes de simular hace falta [aclarar el escenario](ESCENARIO_PENDIENTE.md): su recta tiene objetivos negativos y el método anterior usa una raíz cuadrada de d/(1−d). Se preguntó si se conserva el truncamiento a cero,que cambiaría la linealidad en los extremos. [Valores auditables](escenario_pendiente.json).

No se generó código de medición,simulación,plan o cohorte. No se recalculó D de ninguna cohorte real. Solo se leyeron los seis puntos del resultado oficial ya publicado y fuentes de código. [Procedencia por SHA](sources/provenance.json).
