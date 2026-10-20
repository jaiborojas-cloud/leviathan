# Registro E16-J

1. Base main `0687654` con I integrado; rama independiente y mismo checkout.
2. Protocolo y configuración congelados en `c2cd4a8` antes de implementar.
3. Primera corrida: 27 casos, 81 resoluciones; 24 casos PASS_NUMERICAL y tres
   INCONCLUSIVE, cero FAIL. 5907 controles PASS y seis INCONCLUSIVE.
   14,60 s y 70,38 MiB dentro de 300 s/512 MiB, un hilo.
4. Código y primera evidencia preservados en `d1a342a`, antes de interpretar
   las causas. No hubo ampliación de dominio, reinicios o criterios retrospectivos.
5. SciPy emitió `OptimizeWarning: Unknown solver options: method`: `options`
   contiene una clave redundante del manifiesto. El método efectivo se fija
   mediante el argumento explícito `method='L-BFGS-B'`; las otras opciones
   pasan sus valores congelados. Se conserva el código ejecutado y la advertencia;
   no se cambió implementación ni se repitió con otro optimizador.
6. Diagnóstico posterior: tres casos por refinamiento, dispersión entre
   inicializaciones o diferencias de gradiente; todos los tramos evaluados
   pasaron las cotas de positividad. Dos casos son limitados por frontera.
7. Reproducción: ocho salidas científicas idénticas byte a byte, 14,43 s dentro
   del presupuesto. Hashes, congelación, fuentes y alcance verificados; el estado
   científico global sigue INCONCLUSIVE. No se cuentan réplicas estadísticas.
8. Sintaxis, enlaces relativos, manifests finales y `git diff --check` comprobados.
   T2-A y evidencia A–I sin cambios propios.
