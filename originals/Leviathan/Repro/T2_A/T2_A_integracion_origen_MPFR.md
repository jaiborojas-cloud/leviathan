# Integración MPFR desde el origen — ensayo aislado

Estado: **PAUSED_PARTIAL**. Pasos aceptados: 90; radio integrado: 0.073400762331533767; límite de búsqueda: 0.09. CPU: 1523.09 s; tiempo de integración: 1523.29 s. Este radio no es un radio nominal ni una escala de inyectividad.

Condiciones iniciales verificadas mediante SHA-256. Mismos 2048 rayos, DOP853, rtol=2e-10 y atol=2e-12; MPFR fijo169 bits. El archivo `origin_mpfr_step_000090.zip` contiene el estado del integrador y toda la salida densa; SHA-256: `de0f854646e9da24402b7adf5ce5ad055cea48230008d622bc0097d44244a987`. Reanudar con `python3 origin_mpfr_replay.py`, sin recalcular pasos guardados. La equivalencia de reanudación se verificó en el paso12→13: tiempo, estado y salida densa idénticos bit a bit.

La calibración completa requiere integrar el límite de búsqueda heredado, localizar el radio para área 0.02 con las 32 coronas y regla Dunavant original y superar la tolerancia de área. No se declara completa con un prefijo. Después quedan comparación de precisión y auditoría de Jacobi/topología. No se modificaron outcomes ni la trayectoria oficial: sigue en paso512, 1/8000 visitas completas.

## Cierre del lote

Reanudación comprobada por un paso real: restaurar el paso12 y repetir el13 produjo estado, tiempo y polinomio denso idénticos bit a bit a la ejecución continua.

Área diagnóstica del prefijo integrado: **0.0181330885**, equivalente a 90.67% del objetivo. No es A_embed certificado ni una calibración completa. El último paso avanzó 3.19489e-05 en radio; mediana de coste por paso: 13.89s.

El lote se detuvo de forma recuperable según el presupuesto operacional predefinido (900s o60 pasos nuevos; se termina el paso activo). La pausa no es FAIL, INCONCLUSIVE ni evidencia topológica. Para continuar, ejecutar el mismo script, que verifica y recupera el archivo origin_mpfr_step_000090.zip. No repetir el origen.

No hay procesos activos al cierre. Falta alcanzar el límite de búsqueda, completar la calibración y contrastarla a mayor precisión; no se puede declarar validada la calibración completa.

Reanudación de esta sesión: paso41 → paso90; 49 pasos nuevos. Tiempo adicional de integración: 721.94s. ZIP nuevos verificados: 13. Próximo paso pendiente: 91.
