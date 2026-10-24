# Auditoría: ¿afecta el FAIL de DIN-D2 Q5 a los estados reales de T2-A1? (2026-10-24)

**Motivo.** DIN-D2 (PR #71) encontró que `rho_borde.py`, congelado e intacto, falla en 33 de 210 casos sintéticos. Todos los fallos están en paneles **casi colineales** o con **una cara de 26 puntos**. En 1 caso devuelve una longitud **menor** que la cota de cuerda del mismo ángulo, es decir, subestima. En los paneles gaussianos e interiores (102 de 102) no falla.

**Naturaleza:** auditoría descriptiva hecha **después** del cierre de T2-A1. **No cambia** su veredicto ni reabre el análisis. Solo usa M, f y los ρ ya publicados. Se corrió en la VM del responsable.

## 1. Geometría de los paneles reales (160 splits, f del update 5; f es el mismo en todos los updates)
- **Puntos por cara de la envolvente:** **2 en los 160** (posición general). No hay ninguna cara con 3 puntos o más, ni duplicados.
- **Anisotropía** (σ₂/σ₁ de f centrado): mínimo 0.56, mediana 0.81. No hay paneles casi colineales en el sentido de D2.
- **Ángulo interior máximo del casco:** mediana 173.1°, percentil 99 179.88°, máximo 179.95°. Hay vértices **casi empatados**, que D2 señala como una situación en la que la búsqueda angular uniforme puede no encontrar casos aislados.
- **Consecuencia teórica (D2 Q1):** con caras de a lo sumo 2 puntos, ρ̃(e_k e_kᵀ) = 1/n **para todo k**. Esto explica el piso 1/27 observado en D1.

## 2. Cota de cuerda en los 3120 estados (updates 5, 50, 150 y 250)
- **Qué se comprueba:** si ρ_borde ≥ min_S √(Δ_Sᵀ M Δ_S), con Δ_S = 1_S/|S| − 1/n, sobre los vértices y aristas de la envolvente. Es una cota inferior válida para cualquier curva que llegue a la cara S, por la desigualdad triangular en la seminorma de M.
- **Violaciones: 0 de 3120.** El modo de fallo «longitud menor que la cuerda» de D2 no aparece en los estados reales.
- **ρ_borde/cuerda:** mínimo 1.000, mediana 1.046, percentil 99 2.05, máximo 3.64.

## 3. Lo que no se descarta
- **Sobreestimación por dirección perdida.** En paneles con vértices casi empatados, la búsqueda de ρ_borde podría no encontrar una dirección aislada de menor longitud y sobreestimar ρ_borde. La cuerda no lo detecta, porque solo acota por abajo.
- **Cómo se resolvería:** con las referencias MP de D2 (`references_v1.py`) aplicadas a una muestra de estados reales. Habría que priorizar los splits con ángulos > 179.8° y los estados con cociente ρ/cuerda > 2.
- **Efecto sobre T2-A1:** sería ruido en el desenlace, no un sesgo hacia NOT_MET que se pueda identificar. Se declara como limitación.
