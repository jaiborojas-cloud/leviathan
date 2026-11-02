# Respuesta a la auditoría de Q13-SEP v1 · revisión v2

2026-11-02. **Borrador documental, sin piloto ni mediciones.** La v1 y todos sus archivos/manifiestos se conservan. Esta revisión no cambia receta, instrumento, semillas, tamaños de fases o prohibición de X/rho/D.

| Hallazgo de Claude | Cambio v2 |
|---|---|
| Bloqueante: exigir E y C en u10 y u250 con el mismo par | Principal solo u250. u10 descriptivo, con su propio T* o mínimo por visita, sin seleccionar dosis o vetar la principal. Calidad principal usa u250; las tres reconstrucciones oficiales pasan a u250. |
| Importante: rejilla gruesa hace que misma escala dependa de razones ≈1/2/4 | E ancla A0/T1, transforma LP con T*=S_LP/S_A0 por unidad/visita y verifica igualdad relativa de S a 1e−12; sin proyectar T* a rejilla. |
| C necesita aproximar c con una rejilla fina | LP T=2^(j/8), j=−16..16; argmin de |Δc| con empate (|j|,j). Después se exige factor de escala 1.5. No escoger por S ni pasar al segundo mejor. |
| Coste y prueba corta | M máximas 20.703, entrenamientos 450. Prefijo 15 entrenamientos: 825 llamadas M máximas. Proyección separa train/M/IO y se confirma en el PC antes de continuar. |
| Error 0 de reconstrucción frente al 1e−12 de rutas | 0 corresponde a mismos bytes float64 y misma ruta/versiones/hilos. 1e−12 compara rutas algebraicamente equivalentes que pueden redondear distinto. No relajar después del resultado ni llamarlo certificado. |
| Temperatura cambia el estimando de señal | §9 explicita que cambian X10/L/Y y exige recomputarlos por celda. Prohíbe usar T_C250 para reconstruir u10 y seguir llamándolo temprano sin declarar la información futura. |

## Casos documentales de decisión

- E/C pasan en u250, pero no hay separación o faltan medidas puntuales en u10: el descriptor no veta la principal, si calidad y controles oficiales son válidos.
- T* es distinta en u10 y u250: previsto, no falla por ese hecho. No se fuerza a compartir temperatura.
- El GRID más cercano en c falla el factor 1.5 de escala, pero otro GRID lo pasa: C **falla**; no se elige ese segundo punto.
- Rejilla parcial en u250: C no definido y unidad incompleta; no se asigna infinito al punto faltante.
- Diferencia de c empatada entre j: preferir menor |j| y luego menor j, sin redondear.
- T* fuera de [.25,4] pero finita/positiva: E se mide a T*, sin clipping; la rejilla es solo de C.
- Una dosis solo cumple u10: no es apta. Otra dosis solo cumple C por temperatura dentro del mismo brazo: no rescata E entre brazos.
- Sin dosis apta en cal o E/C insuficientes en val: NO_IDENTIFICABLE y parada de esta vía, sin ampliar rejilla o umbrales tras medir.

Estos son chequeos del contrato, no pruebas ejecutadas sobre estados sintéticos ni implementación del analista de separabilidad. El productor será de Claude después de auditar/congelar.

## Aritmética revisada

A0: dos medidas por entrenamiento; LP: dos visitas × (33 GRID + 1 E_MATCH) = 68 medidas. C referencia el GRID ganador, sin otra llamada. Cal: 50·2 + 200·68 = 13.700. Val: 100·2 + 100·68 = 7.000. Total 20.700 + 3 reconstrucciones = 20.703. Todas las medidas actuales de este agente siguen siendo **cero**.

Prueba corta: 3 A0·2 + 12 LP·68 = 822 + 3 controles = 825; los mismos primeros 15 entrenamientos, dentro del universo. El máximo principal u250 es 10.350; el resto es u10 descriptivo. La comprobación del coste es aritmética con supuestos, no un benchmark: con t_train=33s y eficiencia .8, t_M=.1/.5/1s da 29.4/43.8/61.7 min sin IO. Presupuesto inicial 30–75 min; detener si proyección >90 min y consultar la decisión operacional del responsable.

## Puntos que siguen para auditoría

Confirmar que el emparejamiento adaptativo de validación valida la **regla**, no un par de temperaturas constante; que no se usa S para elegir j_C; y que se distingue defecto global de implementación de un u10 descriptivo no disponible. Revisar la cobertura limitada de la rejilla C, la calidad conjunta sin eliminación selectiva de dosis, la definición del control exacto y la separación entre temperatura métrica y causalidad. No hay resultados de separabilidad, dosis elegida ni potencia de señal; la primaria robusta permanece BORRADOR.
