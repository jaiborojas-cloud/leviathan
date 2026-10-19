# Enmienda E1 al preregistro T2-A0 — BORRADOR (no vigente, no congelado)

**Estado:** borrador para revisión del responsable del protocolo. No tiene efecto hasta que se congele con hash.
**Advertencia de procedimiento:** esta enmienda se redacta **después** de observar un caso (split8_j5_true, update 25, paso 139). El preregistro exige enmienda versionada antes de estados nuevos y prohíbe corregir el contrato retrospectivamente tras resultados. Por eso se registra como **desviación documentada**: se declara qué se observó, cuándo, y qué no se modifica.
Los puntos marcados **[DECIDIR]** son decisiones del responsable del protocolo, no del borrador.

## 1. Hechos que motivan la enmienda

1. Visita split8_j5_true, régimen true, update 25 (integración MPFR; el paso aceptado 139 no es un update). Radio integrado r₁₃₉ = 0.07447265825972331. El radio nominal de esa visita no está determinado.
2. En los rayos 1775 y 1776 las coordenadas originales P divergen (velocidad en coordenadas de 7.3×10⁴ a 2.89×10⁷ entre los pasos 94 y 139) mientras la rapidez intrínseca permanece ≈ 1 (vᵀGv = 0.99999999766). La condición de G alcanza 3.32×10¹¹ y 2.50×10¹¹. Las aceleraciones coinciden con referencias de 80 y 120 dígitos en 14 rayos.
3. Los datos son compatibles con una frontera de la familia softmax a distancia intrínseca finita (mezcla donde solo permanecen los componentes 6 y 13), fuera del dominio original. Radio de llegada local mínimo ≈ 0.07447421007, entre los rayos 1775 y 1776. Certificación global: **INCONCLUSIVE** (falta integración con error acotado y cobertura del continuo angular).
4. El área diagnóstica del prefijo hasta el paso 139 es ≈ 0.0187 (< 0.02) y **no** es A_embed certificado.
5. No se ha demostrado punto conjugado ni pérdida de inyectividad.
6. Reproducción exploratoria, en doble precisión, desde las semillas del manifiesto tras pasar la compuerta del update 5 (sondeo_update25.py, estado state_025_regen.npz, R_ref = 0.0797751845662646 = radio nominal basal): max cond(G) = 95.8 a 0.80·R_ref, 256 a 0.85·R_ref y 1.05×10⁵ a 0.90·R_ref; la integración se atasca a 0.95·R_ref. split8_j6_true update 25 no presenta señales de borde hasta 0.95·R_ref. Es evidencia exploratoria, no certificación.
7. La función de integración heredada (`rays`) no impone límite de pasos ni de tiempo; ante esta frontera la integración se arrastra con pasos cada vez menores en vez de lanzar una excepción. El disparador heredado «excepción/inconsistencia» no se activa.

## 2. Lo que NO cambia

Predictor X y r* = 0.05697156262709151; predictores y comparadores sellados; cola 10 %; elegibilidad basal; definición de Y; criterios íntegros T1-A/C1-A2 para GEOMETRIC_NONINJECTIVITY; jerarquía de refinamiento; calibración heredada del radio nominal A = 0.02, **sin reducirlo para rescatar un caso**; horizonte 250 y visitas 25, 50, …, 250; bootstrap de splits completos (20000, semilla 220020); criterios 1–6 de PASS_PROSPECTIVE_PILOT. Las visitas ya clasificadas no se reclasifican.

## 3. Nueva disposición de visita: NOMINAL_DOMAIN_EXIT (nombre provisional)

**Definición.** Una visita es NOMINAL_DOMAIN_EXIT si el disco geodésico de área intrínseca 0.02 no existe dentro del dominio de la familia, es decir, si existen r₀ < R_nom y al menos un rayo de la familia inicial que alcanza la frontera de la familia a un radio ≤ r₀.

**Evidencia exigida (ambas):**
- (a) Cota superior certificada r₀ del radio de llegada de al menos un rayo a la frontera (aritmética exacta o integración con error acotado; no basta convergencia numérica entre precisiones).
- (b) Cota superior certificada del área barrida hasta r₀, calculada como **área inmersa** (integral del elemento de área sobre el disco de radio r₀), que acota por arriba el área embebida, con valor < 0.02.

Si falta (a) o (b), la visita **no** es NOMINAL_DOMAIN_EXIT: permanece INCONCLUSIVE con la regla heredada (y mantiene la compuerta técnica global INCONCLUSIVE).

NOMINAL_DOMAIN_EXIT certificada **no** es una auditoría fallida, **no** es un cero y **no** implica GEOMETRIC_NONINJECTIVITY. Se reporta con su evidencia íntegra.

## 4. Tratamiento en Y y en el análisis primario

- Y = 1 y Y = 0 conservan su definición. Una trayectoria con NOMINAL_DOMAIN_EXIT y sin Y = 1 confirmado queda con **Y no determinado** (Y_ND). No es negativa.
- **Análisis primario con cotas [DECIDIR; opción A]:** precision@upper10 %, tasa base, lift, IC95 % y la sensibilidad leave-one-split-out se calculan en dos escenarios extremos: (i) todo Y_ND → 0; (ii) todo Y_ND → 1. Se re-aplica la regla de cola en cada remuestreo, sin optimizar q. PASS o FAIL solo si ambos escenarios coinciden; si no, **INCONCLUSIVE por censura informativa**.
- El criterio 3 (≥ 30 trayectorias con evento en ≥ 10 splits) se evalúa con Y = 1 confirmado únicamente.
- Se reporta, como descriptivo y sin declaración confirmatoria: número de visitas y trayectorias con NOMINAL_DOMAIN_EXIT por update, por split y con su evidencia.
- *Alternativas no adoptadas:* (B) redefinir Y como «pérdida de inyectividad o salida del dominio» cambia el desenlace primario y constituiría otro protocolo, no una enmienda; (C) mantener el tratamiento heredado hace que cualquier salida de dominio deje el ensayo en INCONCLUSIVE.

## 5. Detección operativa

Disparadores declarados de antemano que **solo inician** el procedimiento de certificación de la sección 3 y no clasifican por sí mismos **[DECIDIR umbrales]**:
- condición de G > [1e8] en algún rayo antes de R_nom, o
- tamaño de paso del integrador < [ε] durante [N] pasos consecutivos, o
- tiempo de pared por radio > [T].

La integración se detiene al activarse un disparador; no se continúa «hasta que acabe».

## 6. Aplicación y registro

- La enmienda aplica a las visitas aún no clasificadas **[DECIDIR: ¿se aplica también a split8_j5_true update 25?]**. Si se aplica, se reporta además el resultado bajo la regla heredada (INCONCLUSIVE) y se identifica que la regla nueva se redactó tras observar ese caso.
- No se usa para elegir, excluir ni reemplazar trayectorias, ni para modificar X, comparadores, umbrales, cola o Y.
- El mecanismo exploratorio asociado a la escala de la métrica (cociente de Rayleigh ρ_min) **no forma parte** de la enmienda ni del contrato.
- Los análisis exploratorios sobre estados de update 25 de split8_j5_true y split8_j6_true se registran como exploratorios: copias regeneradas desde semillas, que no sustituyen ninguna corrida confirmada. Verificación del prefijo de 5 updates exigida por A0 (parámetros ≤ 1e−12): reportada para j5 (max|Δθ| = 6.9×10⁻¹⁶); **pendiente para j6** (solo se reportó max|ΔM| = 2.1×10⁻¹¹).

## 7. Qué no se afirma

No se afirma que la salida del dominio sea un evento geométrico intrínseco, ni que ocurrirá con frecuencia, ni que prediga o evite la pérdida de inyectividad. No se afirma que el primer borde global esté certificado.

## 8. Registro de integridad (completar al congelar)

Hash de esta enmienda: [ ]. Fecha y hora de congelado: [ ]. Referencias de soporte (expediente): state_025_regen.npz `845c2251…4776`; state_025_regen_j6.npz `0e3fbfd3…6cac`; snapshot de referencia state.npz `6713246b…e19c`; sondeo_j5_u25.csv `38B5D4BE…1F3B`; sondeo_j6_u25.csv `4522E8C6…EEE2`.
