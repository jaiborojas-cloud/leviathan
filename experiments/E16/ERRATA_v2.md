# Fe de erratas de referencia — posterior a run_v2

El diseño original permanece intacto, commit de congelación `7db497d`.
`run_v1` se interrumpió por un error de ruta. `run_v2` completó 121 controles:
120 PASS, 1 FAIL (`B_cuadratica_manual`). No se descarta ni sobrescribe.

Causa: error aritmético en la referencia manual congelada de la composición
cuadrática, no desacuerdo de las derivadas independientes. Para f=θ¹p¹+θ²p²,
S_macro=f²−θ¹f+(θ¹)²/2. Entonces

ω₁=(2f−θ¹)p¹−f+θ¹, ω₂=(2f−θ¹)p²,
B₁₁=2θ¹p¹+2f−2θ¹,
B₁₂=2θ¹p²,
B₂₁=2θ²p¹−θ²,
B₂₂=2θ²p²+2f−θ¹.

En θ=(1,2), p=(1,1): B=[[6,2],[2,9]], det=50, rango 2.
La referencia congelada [[11,3],[6,7]], det=59, era incorrecta.
La igualdad entre B₁₂ y B₂₁ en este punto es accidental; B no es una Hessiana
sobre un único espacio y no se presupone simétrica.

La regla de cadena completa, la diferenciación simbólica directa y las
 diferencias mixtas sobre S coinciden. Corrección v3: sustituir sólo la matriz
manual esperada. No cambian S, puntos, tolerancias, observables ni la predicción
cualitativa de rango 0→2 respecto a la suma. Se añade control exacto explícito
de ω_macro=Σ Ψ_l ω_l y memoria/tiempo de ejecución como diagnósticos.
`mathematical_spec.md` se corrige enlazando esta fe de erratas; el diseño se
conserva con su error original para auditar la secuencia.
