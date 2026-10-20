# Registro E16-I

1. Base `7ed3e35` (main con G/H integrados), rama independiente I, mismo checkout.
2. Diseño y configuración congelados en `acab94e` antes de programar y medir.
   Tres primeros estados H, P0 y tres caminos, sin selección por resultados.
3. Primera corrida: 27 casos PASS_NUMERICAL, 5533 controles PASS; 18 mejoras
   no lineales y nueve controles de suma sin mejora. Un candidato en frontera.
   28,64 s, 67,79 MiB, dentro de 180 s/512 MiB, un hilo.
4. Código y primera evidencia conservados en `b5c1709`. No se ajustaron criterios,
   dominio, resolución ni muestra tras medir. No se ejecutaron fases anteriores.
5. Reproducción: siete salidas científicas idénticas byte a byte; 29,63 s dentro
   del presupuesto. Hashes, congelación, fuentes, alcance y evidencia previa
   verificados. Sintaxis, enlaces relativos y `git diff --check` sin errores.
