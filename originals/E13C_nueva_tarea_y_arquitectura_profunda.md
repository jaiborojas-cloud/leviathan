# E13-C — nueva tarea y arquitectura de dos capas ocultas

**Estado:** completado; E13-D permanece cerrado.  
**Fecha:** 23 de septiembre de 2026.  
**Prerregistro:** E13-A.

## Objetivo

E13-C construye la réplica externa necesaria para E13-D sin calcular todavía curvatura ni abrir el contraste primario. La etapa debía demostrar cuatro cosas:

1. que la nueva arquitectura 13–64–32–3 puede aprender etiquetas verdaderas y memorizar etiquetas permutadas;
2. que cada par `true/random` comparte exactamente inicialización, partición y secuencia de minibatches;
3. que la familia de perspectivas conserva rango dos y admisibilidad en una red con dos capas ocultas;
4. que la geometría regularizada está numéricamente definida antes de medir (K) o (C_A).

## Diseño congelado

- Datos: `sklearn.datasets.load_wine`, 178 ejemplos, 13 variables y 3 clases.
- Particiones: semillas 1000–1007.
- Tamaños por partición: 124 entrenamiento, 27 validación y 27 prueba, todos estratificados.
- Estandarización: media y desviación calculadas sólo con entrenamiento.
- Inicializaciones: semillas 2000–2004.
- Arquitectura: dos capas ocultas ReLU de 64 y 32 unidades, salida softmax de tres clases.
- Etiquetas `random`: permutación del entrenamiento con semilla (3000+10s+j).
- Minibatches emparejados: semilla (4000+10s+j).
- Optimizador: Adam, tasa 0.006, lote 64, máximo 20 000 pasos.
- Criterio de capacidad: accuracy sobre la etiqueta objetivo (ge99\%), comprobada cada 25 pasos.
- Panel geométrico: validación, nunca usado para actualizar parámetros.
- Perspectiva: familia exponencial normalizada de E12-B sobre las variables Wine 0 y 1, estandarizadas con entrenamiento.
- Geometría: (H=I), (ho=10^{-4}), malla de auditoría (7\times7) en ([-0.6,0.6]^2).

La prueba queda reservada para medir generalización verdadera y no participa en entrenamiento ni en la geometría.

## Resultado de entrenamiento

| Régimen | Estados | Pasos mín.–med.–máx. | Accuracy objetivo mínima | Mediana accuracy verdadera train | Mediana validación | Mediana prueba |
|---|---:|---:|---:|---:|---:|---:|
| True | 40 | 25–25–25 | 0.99194 | 1.0000 | 1.0000 | **0.96296** |
| Random | 40 | 75–100–125 | 0.99194 | 0.34677 | 0.31481 | **0.29630** |

Los 80 estados alcanzaron el umbral. La rama `random` no es una red subentrenada: memoriza su objetivo permutado casi perfectamente, pero su desempeño frente a las etiquetas verdaderas permanece cerca del azar de tres clases. La manipulación aprendizaje–memorización queda, por tanto, lograda.

El rango de accuracy verdadera en prueba fue:

- `true`: 0.92593–1.00000;
- `random`: 0.14815–0.55556.

## Emparejamiento

Los hashes SHA-256 de los parámetros iniciales coincidieron en **40/40 pares**. Dentro de cada par también permanecieron fijos:

- partición y estandarización;
- semilla de inicialización;
- secuencia de minibatches;
- arquitectura y presupuesto;
- panel geométrico.

Sólo cambia la asignación de etiquetas del entrenamiento. No hubo reintentos ni sustitución de semillas.

## Extensión geométrica a dos capas ocultas

Para la geometría Fisher se utilizó la parametrización de logits reducidos con dimensión total 3042:

| Bloque | Dimensión |
|---|---:|
| Capa oculta 1: (W_1,b_1) | 896 |
| Capa oculta 2: (W_2,b_2) | 2080 |
| Salida reducida: (W_3,b_3) | 66 |
| Total | 3042 |

Esta partición habilita en E13-E una atribución por profundidad mediante complementos de Schur. Se identificaron además 96 tangentes exactas de reescala ReLU: 64 de la primera capa y 32 de la segunda.

## Compuerta de admisibilidad y positividad

La auditoría cubrió los 80 estados finales y 49 puntos por estado: **3920 evaluaciones**.

| Control | Resultado extremo |
|---|---:|
| Rango mínimo de (B) | **2** |
| (lambda_{\min}(BB^T)) mínima | (2.74\times10^{-5}) |
| (lambda_{\min}(G_ho)) mínima | (2.91\times10^{-4}) |
| (det G_ho) mínimo | (2.10\times10^{-6}) |
| Condición métrica máxima | 3159.1 |
| Residuo máximo (omega)–simetrías | (8.60\times10^{-17}) |
| Residuo máximo (B)–simetrías | (1.05\times10^{-16}) |
| Residuo máximo Fisher–simetrías | 0 |
| Residuo máximo del solucionador | (5.00\times10^{-8}) |

No hubo pérdidas de rango ni métricas indefinidas. La condición máxima es elevada y deberá conservarse en la auditoría de E13-D, pero el solucionador alcanzó la tolerancia fijada en todos los casos.

## Autoprueba del nuevo retropropagador

Se probaron cuatro estados extremos mediante diferencias finitas y simetría del operador:

| Control | Error máximo |
|---|---:|
| Derivada direccional de (S_P) | (2.39\times10^{-10}) |
| (B=d_P\omega) | (1.77\times10^{-10}) |
| Autoadjunción de Fisher | (9.46\times10^{-15}) |

Esto valida la extensión analítica del aparato RIPG desde una a dos capas ocultas antes de calcular curvatura.

## Estado de E13-D

E13-C no calculó (K), (C_A), holonomía ni diferencias `true-random`. El archivo de configuración registra explícitamente:

```text
curvature_computed = false
primary_E13D_outcome_opened = false
```

Para mantener comparabilidad con E13-B, E13-D heredará el jet métrico analítico de segundo orden en (P_0), las áreas (0.01,0.02,0.04), la malla principal y el refinamiento duplicado. Como auditoría secundaria previamente fijada, se evaluará la curvatura analítica exacta en ocho direcciones de la frontera primaria para cada estado incluido. Esta auditoría no sustituirá el estimando primario ni se usará para seleccionar casos.

## Alcance y cautelas

- Wine es una tercera tarea natural y la arquitectura es genuinamente más profunda.
- Las ocho particiones son remuestreos del mismo conjunto de 178 observaciones; son unidades de partición prerregistradas, no ocho datasets poblacionalmente independientes.
- La alta accuracy `random` sólo demuestra capacidad de memorización, no equivalencia dinámica entre regímenes.
- La positividad regularizada de (G_ho) no anticipa el signo o magnitud de la curvatura.
- No se infiere todavía confirmación o refutación de la hipótesis primaria.

## Cierre

E13-C cumple su función: entrega 40 pares completos, una manipulación de memorización efectiva, una geometría admisible de rango dos y una implementación profunda validada numéricamente. No hay exclusiones antes de abrir E13-D.
