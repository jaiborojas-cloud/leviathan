# Q13-SEP · esquema y decisión · BORRADOR v2

[Diseño v2](../DISENO_DIN_Q13SEP_BORRADOR_v2.md). No hay productor ni datos en esta entrega. La v1 queda archivada sin alteraciones.

## Tabla de medidas por visita y rol

`q13sep_medidas_v2.csv`, UTF-8/LF; una fila por medida planificada, con columnas propuestas exactas:

```text
phase,measure_id,trajectory,condition,lambda,split,k,update,temperature_role,j,T,c,q,tr_M,S_panel,S_train,conf_media_verdadera_panel,conf_media_maxima_panel,acc_train,acc_panel,estado_medida,error,no_aprendio_final,checkpoint_original_sha256,checkpoint_T_sha256,M_sha256,f_sha256,dataset_sha256,batches_sha256,cpu_seconds,wall_seconds,M_seconds,memory_peak_mb
```

Entrenamientos e IDs de fase/split/k/condición conservan los de v1; visitas 10/250. Roles:

- **A0_ANCHOR:** solo A0, T=1, j vacío; una medida por visita.
- **GRID:** solo LP, j entero −16..16, T=2^(j/8). j=0 es la referencia LP sin temperatura. Medir las 33 filas.
- **E_MATCH:** solo LP, j vacío y T*=S_LP(1)/S_A0(1) de esa unidad/visita. Es una medida adicional planificada, aunque coincida con GRID; no un reintento. Si no se puede calcular T*, conservar fila FALLIDA con T vacío y motivo.

Clave de medida: ID de entrenamiento + update + rol + j (solo GRID); no se incluye un T adaptativo desconocido en el ID. Así se publica el universo antes de medir. C no genera otra fila de medida: referencia el GRID ganador. Los tres controles tienen su propio JSON y no duplican filas principales.

Máximo de filas: **13.700 cal + 7.000 val = 20.700**, mitad u250 principal y mitad u10 descriptiva, más tres reconstrucciones M separadas. No son los 1.350 pares de visitas de la v1. Filas fallidas o ausentes se conservan, nunca se rellenan con cero o se reemplazan.

`estado_medida` = MEDIDA/FALLIDA; `no_aprendio_final` = true/false/unknown con precisión train de u250/T1. La etiqueta final no reescribe estados o valores anteriores. Los parámetros originales y transformados, datos, escalador, lotes, RNG/Adam y M completos van fuera de Git con hashes. Los tiempos por fila corresponden a la medida, no a toda la trayectoria; el registro de entrenamiento separa train, medidas/IO y latencia individual sin cola. El elapsed global incluye spawn y es el que informa rendimiento con 12 procesos.

## Tabla derivada de emparejamientos

`q13sep_emparejamientos_v2.csv` tendrá una fila por (fase, LP, split,k,visita,pregunta E/C). Referencia el ID del ancla A0 y la fila LP elegida, sin calcular X/rho/D. Incluye:

- regla/versión, estado, motivo; j_C y empates, o T* y log T*; SHA del conjunto GRID completo;
- escalas y c de ambas filas, log ratio de S, diferencia de c, error relativo de igualdad S para E;
- orientación oficial de calibración cuando exista, pasa/falla y **uso=PRINCIPAL_u250 o DESCRIPTIVO_u10**;
- etiqueta de procedencia entre brazos (T=1 o T emparejada); datos faltantes sin inferir un mínimo de rejilla parcial.

C se selecciona por **(|Δc|, |j|, j)** exclusivamente, **antes** de comprobar separación de S. No elegir el segundo mejor si el primero falla el factor 1.5; no omitir GRID fallidos como si no existieran. La positividad/validez de S se verifica antes de los logs. E usa su T* exacta representable, no la rejilla ni la banda ±10 % de v1.

## Dosis, orientaciones y momento de decisión

Calibración: usar solo las filas de emparejamiento **u250** para E/C, orientaciones +1 antes de −1. Un split pasa con ≥3/5 unidades planificadas y una orientación es apta con ≥8/10 splits. Elegir la menor λ con E y C aptos. No usar u10 para escoger o favorecer dosis. No hace falta que u10 y u250 seleccionen el mismo j o T*.

Publicar `DOSIS_Y_REGLAS_Q13SEP_v2.json` por SHA antes de entrenar validación: diseño/plan/productor/tablas/controles por SHA, dosis, σ_E/σ_C, fórmulas de temperatura, ancla, rejilla, desempate y conteos. Se fijan **algoritmos**, no temperaturas iguales para todas las unidades. La validación vuelve a calcular T* y argmin con su propia geometría, sin alterar esos algoritmos, dosis, márgenes u orientaciones.

Calidad principal solo u250: todos los brazos y puntos requeridos válidos y sin NO_APRENDIO; ≥48/50 r comunes en cal y ≥95/100 en val, además de ≥8/10 y ≥16/20 splits con ≥3 completos. Los fallos de u10 se informan con sus propios denominadores y **no se convierten en veto**. Si falta la rejilla u250, la unidad no es completa. Un defecto global o un control oficial fallido sí invalida toda la corrida.

| Resultado principal u250 | Decisión |
|---|---|
| Calidad válida; E y C cada uno en ≥16/20 splits | SEPARABILIDAD_LOGRADA |
| E o C no alcanza el criterio, aunque u10 o SOLO_TEMPERATURA pasen | NO_IDENTIFICABLE |
| Sin dosis apta en calibración | NO_IDENTIFICABLE; no entrenar validación |
| Calidad insuficiente o controles oficiales inválidos | NO_IDENTIFICABLE operativo, sin conclusión física; INVALIDA si falla control |

Se tabulan los candidatos por dosis/orientación y todos los GRID; no solo los ganadores. SOLO_TEMPERATURA compara LP(T1) con cada GRID T≠1 descriptivamente y no rescata. u10 se reporta con las orientaciones principales congeladas, sin aprender otras con esa visita. No hay p-valores o certificados de equivalencia; los umbrales son operacionales.

Resúmenes y decisiones enlazan `tabla_sha256`, `plan_sha256`, `script_sha256`, diseño, controles y versión de reglas. Nunca etiquetar el piloto como estudio de señal ni calcular esas asociaciones para verificarlo.
