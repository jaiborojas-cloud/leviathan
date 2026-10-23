# Registro de E16-AA

- Base integrada de main: 2db0bed; incluye Z y trabajo externo T2_A1 intacto.
- b88ee52 congela diseño/configuración antes de implementar o medir.
- 0862a9e congela scripts/run.py antes de la primera corrida.
- Una comprobación textual auxiliar buscó la subcadena `yp` y falló porque
  aparece dentro de `type`; no era un fallo del código científico. Se revisaron
  las referencias de fuente y el código compiló. No se modificó la implementación
  congelada ni se reinició la corrida.
- Primeros puntos se conservan aunque alcancen maxiter sin KKT1e-7.
- Corrida completa: 251.705298s / 202.664062MiB. 12 casos; 4 primer orden PASS, 8 INCONCLUSIVE; 12 espectros PASS. Sin cambios de diseño.
- PASS_REPRODUCTION: once salidas idénticas;255.124747s. Todos los controles de integridad pasaron; no se repitió más.
- Alcance final29 archivos, sólo AA y tres índices; enlaces relativos comprobados y figura inspeccionada. Z, T2_A/T2_A1 y .gitattributes intactos.
