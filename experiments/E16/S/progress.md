# Avances E16-S

- Diseño congelado en 3b04bbc, antes de implementar o medir; implementación
  científica en 0310ab7. Las fuentes y escalas quedan fijadas por hashes.
- Se incorpora main a la rama dependiente de R, conservando T2-A sin cambios.
  No se fusionan PR en main.
- Primera medición archivada en ccb0655: PASS_NUMERICAL, doce caminos,
  105 auditorías, cero UNVERIFIED y 31.409 comprobaciones aprobadas.
- Figura generada sólo desde CSV archivados y revisada visualmente.
- Reproducción integral PASS_REPRODUCTION: dieciséis salidas científicas
  idénticas byte por byte; segunda corrida 486,203 s, dentro del presupuesto.
- Durante la validación, R fue fusionado externamente en main (766b8cf).
  Historial integrado sin cambios de fuentes, protocolo ni resultados.
