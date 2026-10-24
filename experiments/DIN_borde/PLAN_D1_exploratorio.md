# DIN-borde D1 — ¿cómo lleva el entrenamiento la geometría hacia el borde? (plan exploratorio, 2026-10-24)

**Naturaleza:** **exploratorio**. Se registra antes de calcular. Usa datos ya analizados en T2-A1: estados (M, f) de las 780 trayectorias confirmatorias en los updates 5, 50, 150 y 250, con su ρ_borde ya calculado. **Nada de aquí puede confirmar una hipótesis.** Confirmarla exigiría un prerregistro nuevo con una cohorte independiente. No reabre T2-A0 ni T2-A1.

## Pregunta
Entre el update 5 y el 250, ρ_borde baja; 248 de 780 trayectorias llegan a menos de r*. ¿Eso se debe a que **la escala** de M se contrae, o a que **su forma** cambia?

## Descomposición exacta
G = JᵀMJ es lineal en M, así que ρ_borde(cM) = √c·ρ_borde(M). Por lo tanto:
log ρ_borde = ½·log tr M + log ρ̃,  con ρ̃ = ρ_borde(M / tr M).
No requiere integrar nada nuevo: ρ̃ = ρ_borde/√(tr M).

## Medidas por estado (solo numpy, sin entrenar)
tr M; autovalores de M (λ_max/tr y razón de participación (Σλ)²/Σλ² como rango efectivo); ρ̃. También se lee el `f_sha` del panel, para confirmar que f no cambia entre updates.

## Descriptivos
1. Por update: medianas y cuartiles de log ρ, ½·log tr M y log ρ̃.
2. **Reparto del cambio** entre u5 y cada visita, por trayectoria: Δlog ρ = ½·Δlog tr M + Δlog ρ̃. Fracción de la varianza de Δlog ρ que corresponde a cada término, incluida la covarianza.
3. Lo mismo dentro del split (centrando por split) y entre splits.
4. Relación con la precisión en validación del update 5 (la nota exploratoria del cierre de T2-A1): Spearman dentro del split con Δ½log tr M y con Δlog ρ̃.

Sin umbrales ni veredictos. Salida: tabla por estado, resumen JSON y una nota de resultados.
