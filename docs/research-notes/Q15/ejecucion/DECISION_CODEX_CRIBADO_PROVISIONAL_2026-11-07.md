# Decisión del responsable: Codex criba de forma provisional

**2026-11-07, hora de México.** Decide: el responsable.

## Contexto
- El piloto de cribado con modelos abiertos terminó **NO APTO** ([registro](cribado_llm/REGISTRO_EJECUCION.md)): el cribado de las 2 998 obras pendientes no se hace con un modelo abierto.
- Argon, que criba desde el lote 02, no tiene cuota hasta el 2026-11-12.

## Decisión
- Mientras Argon no tenga cuota, **Codex criba lotes de 100 obras** con las mismas reglas que Argon:
  - razón propia por obra, citando el resumen, sin plantillas;
  - los dos criterios del responsable: [CONTEXTO y lotes](DECISION_CRITERIO_CONTEXTO_Y_LOTES_2026-11-05.md) y [medidas de dificultad, opción B](DECISION_CRITERIO_MEDIDAS_DIFICULTAD_2026-11-05.md);
  - identificadores reunidos de todas las posiciones elegibles y un solo ID de arXiv sin versión por obra;
  - conteos calculados con código, con la salida pegada en el informe;
  - lotes fijados por `obra_id` antes de leer.
- Claude audita cada lote antes del siguiente. **Si un lote no pasa la auditoría, Codex se detiene** y el cribado espera a Argon.
- Cuando Argon tenga cuota, retoma desde el primer lote pendiente.
- Las decisiones del piloto con modelos abiertos **no** se usan ni se muestran al lector.

## Lote 04
Las 100 obras siguientes en `PENDIENTE_CRIBADO` por `obra_id`, después de los lotes 02 y 03 de Argon, fijadas antes de leer:

```
W00381 W00382 W00384 W00385 W00386 W00387 W00388 W00389 W00390 W00391
W00392 W00393 W00394 W00395 W00397 W00403 W00413 W00421 W00424 W00434
W00435 W00438 W00439 W00441 W00442 W00444 W00445 W00446 W00447 W00448
W00449 W00450 W00451 W00452 W00453 W00455 W00456 W00457 W00458 W00459
W00460 W00461 W00462 W00463 W00464 W00465 W00466 W00467 W00468 W00469
W00470 W00472 W00474 W00475 W00482 W00484 W00485 W00487 W00488 W00489
W00490 W00493 W00494 W00498 W00499 W00500 W00501 W00502 W00503 W00504
W00505 W00506 W00507 W00508 W00509 W00510 W00511 W00512 W00514 W00515
W00516 W00517 W00518 W00519 W00520 W00521 W00522 W00523 W00524 W00525
W00526 W00527 W00530 W00531 W00533 W00543 W00544 W00545 W00546 W00547
```

Quedan 2 998 obras pendientes antes de este lote.
