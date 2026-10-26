# DIN-R1 etapa 2 — los estados de T2-A1 y DIN-borde con ρ_borde v2 (plan, 2026-10-25)

**Naturaleza:** reevaluación posterior y declarada. Se registra antes de calcular. **Ningún veredicto congelado cambia.**

## Estados (splits 12–167, 780 trayectorias)
- update 5: `T2_A1\rho_u5\estados_u5\<t>.npz`
- updates 10, 20, 30 y 40: `T2_A1\DIN_borde\d6\estados\<t>\u<k>.npz`
- updates 50, 150 y 250: `T2_A1\fase2\visitas\<t>\u<k>\states\<t>\state.npz`

Son 6240 estados. Se calculan con `r1_etapa2.py` y ρ_borde v2 r3 (`2ac015a2…`) con las opciones por defecto, simetrizando M. Los fallos se reportan y no se sustituyen.

## Reanálisis (contenedor, exploratorio; ninguno sustituye un cierre)
1. **T2-A1:** el mismo análisis congelado (`analisis_T2A1.py`: W, W_adj, Δ y secundarios) con Y_c = min de ρ_caras en 50, 150 y 250, y L5 = log ρ_caras(5). Se reporta junto al NOT_MET original.
2. **D6:** la curva W(t) de log ρ_caras(t) frente a log ρ_caras(250), y el W_adj de la confianza sobre ρ_caras(t).
3. **D4:** la relación de log ρ_caras(250) con log(1 − p(y_k*)).
4. **D1:** ρ̃ = ρ_caras/√tr M y el piso 1/27.
