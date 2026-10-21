# Errata de implementación v1: referencia redondeada

Primera corrida preservada en `1486ef1`, `results/run_v1` y copia exacta del
código `scripts/run_v1_snapshot.py`. Hubo cinco INCONCLUSIVE: cuatro de forma
y uno en C0/source_reference. No se alteran esas salidas.

L guarda `mp.nstr(x,40)`: 40 cifras significativas. v1 trató el decimal guardado
como exacto, sin su error de redondeo. Para números entre 1 y 10, la unidad de
última cifra es 1e-39, con incertidumbre de hasta 5e-40. El error normalizado
observado de C0, 1,55e-40, es compatible con esa incertidumbre y no demuestra
falta de precisión del control.

## Corrección fijada antes de modificar código o repetir

Sólo para la referencia archivada L32: interpretar el decimal como intervalo
[centro−q/2,centro+q/2], q=10^(floor(log10|centro|)+1−40).
Comparar la distancia del valor calculado a ese intervalo, normalizada por
max(1,|valor|,|centro|), con la misma tolerancia 1e-40. Registrar centro, q,
radio, valor calculado, error escalar y distancia al intervalo. No editar L.

No se cambia ninguna tolerancia ni comparación MP80/120, gradiente, primitiva,
SPD, dominio, grupo, solver, resolución o reinicio. Los cuatro incumplimientos
de forma no se rescatan. No se interpreta la tabla de 40 cifras como medición
exacta a una precisión que no conserva.

Controles del lector a 120 cifras: centro=1,25, q=1e-39; desplazamiento q/4
pertenece al intervalo (distancia cero); desplazamiento 2q queda fuera y debe
exceder 1e-40. Son controles matemáticos del lector, no nuevos datos científicos.

Guardar código corregido y resultados como run_v2, enlazando esta errata en la
procedencia; reproducir v2 exactamente. Conservar v1 sin reetiquetarlo. Todas
las corridas siguen siendo diagnósticos de los mismos datos, no muestras nuevas.
Esta corrección de lectura no cambia el diseño congelado ni estados históricos.
