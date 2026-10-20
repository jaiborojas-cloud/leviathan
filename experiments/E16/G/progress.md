# Registro E16-G

1. Rama sobre `fe92f26cdba0e62895e524972c0dad1ce13a150c` (E16-F, PR #20),
   conservando F tal como fue publicado. No se sobrescriben sus resultados.
2. Protocolo y configuración congelados en `7049807` antes de programar o medir G.
   Las dificultades de F eran conocidas: propósito diagnóstico explícito.
3. Primera corrida: 324/324 PASS_NUMERICAL, 216/216 pares validados y
   13 102/13 102 controles PASS. Resueltos bajo G los 85 casos inconclusos F;
   ninguno excluido o reemplazado. 21,99 s y 40,22 MiB, dentro de 180 s/512 MiB.
4. Código y primera evidencia conservados en `f59b952`. Sin ajustes al protocolo
   ni corridas fallidas ocultas. F conserva sus estados originales.
5. Reproducción: seis salidas científicas idénticas byte a byte, en 23,45 s.
   Hashes, diseño congelado, alcance, F y T2-A verificados sin cambios.
   Sintaxis, enlaces relativos y `git diff --check` comprobados.
6. Comparación conservada: discrepancia normalizada máxima F/G de 1,21e-20
   entre los 239 casos que F validó; 3,90e-7 entre los 85 antes inconclusos.
   Son diagnósticos posteriores, no criterios de aceptación nuevos.
