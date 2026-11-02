# Formalización en Lean: posibilidad y alcance (propuesta, 2026-11-02)

**Estado:** propuesta, a pedido del responsable («añade la posibilidad de uso de Lean»). Nada está instalado ni probado todavía. No cambia ningún protocolo, resultado ni veredicto.

## Para qué sirve y para qué no
- **Sirve** para **certificar el esqueleto matemático** de la línea DIN: identidades algebraicas, invariancias, dominios y desigualdades que el código da por supuestas. Una prueba en Lean 4 con Mathlib es un certificado riguroso de que el enunciado vale en los números reales.
- **No sirve** para certificar resultados numéricos (D, p, ρ). El código calcula en punto flotante y Lean razona sobre ℝ. Según AGENTS.md, hay que **separar las estimaciones numéricas de los certificados rigurosos**: un teorema en Lean nunca se presenta como una verificación de una corrida.
- **No sustituye** a las pruebas sintéticas ni a la compuerta de equivalencia; las complementa.

## Enunciados candidatos
Van ordenados por dificultad estimada. La dificultad es una estimación previa, no medida.

| id | enunciado (sobre ℝ) | dónde se usa | dificultad |
|---|---|---|---|
| L1 | X = logsumexp_{c≠y} z − logsumexp z ≤ 0, y R ≤ X cuando X es el máximo sobre el panel | dominios del analista de F1 | baja |
| L2 | ρ_caras ≤ ρ_vert cuando ρ_caras = mín(ρ_vert, ρ_aristas), es decir, un mínimo sobre un conjunto que contiene al de ρ_vert | aceptación de ρ | baja |
| L3 | Para M semidefinida positiva con tr M > 0: c = máx diag M / tr M ∈ (0, 1], y q ∈ [0, 1] | dominios de c y q | baja–media |
| L4 | Parametrización reducida: restar la misma fila a W y la misma constante a b deja el softmax invariante | `make_geom_state` y control de la compuerta | baja–media |
| L5 | Identidad de Woodbury: para γ > 0, R(UUᵀ + γI)⁻¹Rᵀ = (1/γ)[RRᵀ − RU(UᵀU + γI)⁻¹UᵀRᵀ] | `subset_M` | media (Mathlib tiene resultados de complemento de Schur; falta comprobar el nombre exacto del lema) |
| L6 | Los valores ajustados por mínimos cuadrados dependen solo del espacio columna, así que la base cúbica centrada es invariante a cambios afines no degenerados de L | justificación de la base de C1 y de la primaria robusta | media |
| L7 | La base recortada coincide con la de C1 cuando las z de prueba están dentro del rango de entrenamiento | equivalencia de la [primaria robusta](../../experiments/DIN_borde/PRIMARIA_ROBUSTA_v1.md) | baja |
| L8 | Validez del p de permutación: bajo intercambiabilidad dentro del split, P(p ≤ α) ≤ α con p = (1 + #)/(B + 1) | inferencia de C1 y C2 | alta (teoría de la probabilidad en Mathlib) |

## Cómo se organizaría
- **Carpeta:** `lean/`, con un proyecto Lake y **Mathlib fijada por commit** (y `lean-toolchain` fijado), para que cada prueba se pueda reproducir.
- **Cada teorema** enlaza el archivo y la función de Python que respalda, y el SHA de ese archivo.
- **Primer piloto:** L1, L2, L4 y L7, que son de baja dificultad y sirven para validar la cadena (instalación, Mathlib y CI opcional). Después, L3, L5 y L6. L8 solo si hay interés en publicar.
- **Riesgo práctico:** Mathlib pesa varios GB y su caché se descarga de servidores externos. Hay que comprobar que el contenedor o tu PC puedan instalarla antes de comprometer trabajo.

## Reparto
Lo hace **Claude**, en paralelo con el trabajo del otro agente: ver [reparto](reparto-2026-11-02.md).
