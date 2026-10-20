# v1 — Interrupción de implementación

El grupo A guardó checks.csv, spectra.csv y timing.json, pero se interrumpió al
anotar progress.md: ValueError en args.output.relative_to(ROOT), porque la ruta
de salida era relativa y ROOT absoluta. No se completaron los demás grupos.
No es un fallo geométrico. Corrección v2: resolver args.output antes de usarla.
La implementación v1 se conserva en el commit que incorpora este diagnóstico.
No hay summary.json; esta corrida global queda INCONCLUSIVE por interrupción.
