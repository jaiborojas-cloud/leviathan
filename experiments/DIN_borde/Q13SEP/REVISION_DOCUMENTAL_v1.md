# Q13-SEP · comprobaciones del borrador y puntos para auditoría

2026-11-02. Solo revisión documental y de aritmética del plan. **No se ejecutaron redes, M, rho, X, señal, simulaciones ni piloto.** No equivale a controles de instrumento aprobados: estos pertenecen al productor futuro.

## Coherencia que debe conservarse al implementar

| Caso de decisión | Resultado fijado |
|---|---|
| Calibración sin λ con E y C aptos | NO_IDENTIFICABLE, no entrenar validación |
| En validación E = 16/20 y C = 16/20, calidad y controles válidos | SEPARABILIDAD_LOGRADA |
| E = 15/20 o C = 15/20 | NO_IDENTIFICABLE, aunque el otro cumpla |
| Solo un contraste dentro del brazo por temperatura cumple | No rescata; NO_IDENTIFICABLE si faltan los principales |
| Margen exactamente 10 %, .15, .05 o factor 1.5 | Límite inclusivo, valores sin redondear |
| Un r falla una visita o temperatura requerida | Mantenerlo en el denominador de 5, con motivo |
| Acc_train final < .5 | Etiqueta NO_APRENDIO; no reescribir valores o estados MEDIDA anteriores |
| S no positiva, dominio inválido o dato ausente | No logaritmar ni imputar; conservar como fallo |
| 48/50 completos en cal; 95/100 en val | Límite de calidad admitido; por debajo detener fase |
| Control de copia T, SHA, reconstrucción o pareado falla | Corrida INVALIDA; sin interpretación física de no separación |

La igualdad de escala y su diferencia grande no pueden cumplirse en el mismo par/unidad/visita; los dos contrastes pueden ser distintos. La configuración evita exigir que el mismo par A0/LP a T fija satisfaga ambas preguntas. La fórmula exacta S(T) = S(1)/T predice que E no puede lograrse SOLO_TEMPERATURA con esta rejilla: 2 y 4 exceden 1.10. C sí podría lograrse solo por temperatura, pero no cuenta como separación entre brazos.

## Revisión aritmética y de fuentes

- Calibración: 10 × 5 × 5 = 250 entrenamientos, × 3 = 750 celdas, × 2 = 1.500 medidas M.
- Validación: 20 × 5 × 2 = 200 entrenamientos, 600 celdas, 1.200 medidas M.
- Total máximo: 450 entrenamientos, 1.350 celdas, 2.700 medidas M principales más tres reconstrucciones de control, máximo 2.703 llamadas M; cero llamadas rho.
- Prueba corta: 3 unidades × 5 brazos = 15 entrenamientos, 45 celdas, 90 medidas principales más tres reconstrucciones de control (93 llamadas M), todas dentro de calibración.
- Proxy temporal ideal: 450 × 33 / 12 = 1.237,5 s; no es una medición del piloto. Presupuesto orientativo 30–60 min y parada operacional si la proyección supera 90 min.
- Las nueve combinaciones principales de T, y σ±, tienen orden explícito para seleccionar en calibración, no se maximizan después con la validación. Se elige la menor dosis apta, no la de mejor D o confianza.
- Fuentes congeladas y snapshot de decisión por commit; cotejo estático de semillas con main y PR #132. No se afirma una prueba formal de independencia PRNG.

## Puntos para Claude antes de congelar

1. Auditar que 10 %/.15/.05/1.5 y el umbral 3/5 en 80 % de splits son adecuados como criterio operativo, sin cambiarlo tras medir. Se justifican como diferencias útiles, no como equivalencia estadística o potencia.
2. Confirmar la interpretación **factorial**: un contraste entre brazos a T distintas no aísla solo entrenamiento y un éxito no identifica al colapso como causa. La confianza y otras propiedades de M no quedan fijadas por emparejar c/S.
3. Revisar calidad conjunta en todos los brazos antes de calibrar: no eliminar selectivamente dosis por precisión o faltantes. Validar que la orientación fijada evita mezclar signos entre u10/u250.
4. Asegurar copias frescas de la cabeza completa, salir de no_grad antes de core, recomputar Gram/ridge/M y no reutilizar gradientes entre T. Comparar T1 y reconstrucciones sin ejecutar medidores heredados que calculan X/rho.
5. Antes de productor/plan congelado, cotejar de nuevo semillas publicadas y confirmar versiones, presupuestos, memoria y límites de la prueba corta. La decisión de congelar pertenece al responsable.
6. El siguiente experimento tendrá datos nuevos, analista robusto congelado y contraste pareado entre D auditado; familia de dos primarias con Holm α=.05. No se trata de comparar significaciones separadas por celda; una ausencia de efecto de escala exigiría margen de equivalencia y potencia prospectivos.

El analista A1 del PR #132 permanece BORRADOR; este piloto no lo ejecuta ni lo congela. Claude implementa solo después de la aprobación del diseño.
