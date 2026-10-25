# DIN-G1 · generalización exploratoria fuera de Wine

Iris,3 clases: referencia27, panel60 y arquitectura más ancha.
20 splits×5 inicializaciones por familia, diseño previo a código/mediciones.

- [Diseño congelado](DESIGN_FROZEN.md)
- [Configuración](config.json)
- [Fuentes y contexto autorizados](freeze_manifest.csv)
- [Progreso](progress.md)
- [Conclusión por H y familia](CONCLUSION.md)
- [Tabla de veredictos](results/run_v1/hypotheses.csv)
- [Descriptivos por visita](results/run_v1/by_update.csv)
- [Figura exportable](figures/trayectorias.svg)
- [Teoría e interpretación algebraica](THEORY.md)
- [Diagnóstico angular separado](SUPLEMENTO_ANGULAR_FROZEN.md)
- [Ejecución](progress_run.md), [diccionario](DATA_DICTIONARY.md),
  [manifest](manifest.csv) y [verificación](verification.json)

No se accede a datos Wine, T2 o DIN-C1. Instrumentos originales sin cambios.

H1 APARECE en W27; R27/P60 INDETERMINADO. H2 APARECE en los colapsados de las
tres familias. H3 APARECE en R27/W27 y queda indeterminado en P60 por auditoría.
H4 APARECE sólo en P60; H5 NO_APARECE en R27 e INDETERMINADO en las otras dos.
El suplemento encontró un retorno rho mayor que la longitud de un rayo concreto;
los veredictos operacionales se conservan, sin certificar mínimos geométricos.
