# DIN-borde D3 — ¿sobre qué colapsa M? (plan exploratorio, 2026-10-24)

**Naturaleza:** **exploratorio**. Se registra antes de calcular. Usa los mismos 3120 estados (M, f) de D1. No confirma nada. Corre en paralelo con DIN-D2, la parte teórica del otro agente.

## Motivación
D1 mostró que M colapsa a rango ≈ 1 y que ρ̃ cae a ≈ 1/n. La derivación de D2 sugiere que el piso 1/n exige que el vector dominante v de M esté **concentrado en un solo ejemplo** del panel. Si v está repartido, ρ̃ puede quedar por debajo de 1/n.

## Medidas por estado (solo numpy y scipy; sin entrenar)
- v₁, el autovector dominante de M. **Concentración:** c = max_k v₁,k², con su índice k*, y la razón de participación 1/Σ v₁,k⁴.
- M_kk/tr M máximo, con su índice.
- Si k* es **vértice de la envolvente convexa** de f (scipy ConvexHull).
- **Estabilidad de k*:** si es el mismo entre los updates 50, 150 y 250 de una trayectoria, y cuántos k* distintos hay entre las 5 trayectorias de un split, que comparten f.

## Descriptivos
1. Distribución de c y de la razón de participación por update.
2. Relación de log ρ̃ con c y con λ_max/tr: Spearman global y por update.
3. Fracción de estados con k* en un vértice de la envolvente, frente a la fracción de puntos del panel que son vértices.
4. ¿Los estados que quedan claramente por encima del piso (log ρ̃ > log(1/n) + 0.05) tienen menor c?

Sin umbrales ni veredictos. Salida: tabla por estado, resumen JSON y una nota.
