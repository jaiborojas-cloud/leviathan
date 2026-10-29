# DIN-CIFAR F1 · revisión v2 para auditoría

**BORRADOR, sin congelar.** Esta revisión responde a los tres cambios solicitados tras la auditoría del PR #127. La v1 y sus 54 salidas quedan intactas.

- [Diseño v2](../../DISENO_CIFAR_F1_BORRADOR_v2.md): espacios revisados, estratos por mediana del split y definición explícita de longitud y `quad_error = None`.
- [Plan v2](../plan_F1_BORRADOR_v2.json): mismo universo, semillas, primaria y opciones rho; regla de estratos explícita.
- [Protocolo de revisión](PROTOCOLO_REVISION_v2.md): comprometido antes del código y las nuevas pruebas.

La mediana de c250 se calcula entre las trayectorias elegibles de cada split usado por la primaria. Los cortes son .4 y .8, y se conservan juntas todas las trayectorias elegibles. Se reportan los splits de cada estrato, incluidos los que no llegan al mínimo de 20 splits para calcular D. El límite de 120 s queda como requisito del futuro productor.

Analista, pruebas y sus salidas se publicarán en esta misma revisión, conservando las de v1. No se crea productor ni se usa ninguna cohorte real.
