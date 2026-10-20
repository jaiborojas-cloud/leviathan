# Registro E16-E

1. Base `47f0eff`: E16-D ya integrado en main. Rama independiente
   `research/e16-e-distancias-anisotropia`.
2. Diseño, umbrales, muestra, hashes fuente y salidas congelados en `f9a1b58`
   antes de crear el script y ejecutar observables nuevos.
3. Corrida v1: 216 comparaciones; 10 176 controles PASS; sin casos omitidos,
   fallidos ni inconclusos. 3,50 s y 37,75 MiB, un hilo. No hubo cambios al
   protocolo ni estados fallidos que corregir.
4. Verificador: cuatro salidas científicas reproducidas byte a byte, hashes y
   diseño congelado comprobados, alcance limitado a E y tres índices. La
   repetición consumió 3,01 s. `git diff --check` limpio. T2-A sin cambios.

Los tiempos son observaciones de estas corridas, no garantías de rendimiento.
El estado PASS_NUMERICAL valida los controles instrumentales especificados;
la interpretación científica sigue siendo exploratoria.
