# Marco matemático recuperable

Fuente primaria disponible: [Perspectivas.ipynb](../../Perspectivas.ipynb), con índices de celda desde cero.

- Celdas 26–38: dL′ = J⁻ᵀdL, g′ = J⁻ᵀgJ⁻¹ y v = −g⁻¹dL; el control busca v′ = Jv.
- Celda 41: la equivalencia discreta se plantea para una transformación lineal con J constante. No extenderla sin justificación a cambios no lineales.
- Celdas 65–79: Fisher se compara entre cartas y se regulariza mediante F + λG, transformando también G. Usar λI independientemente en cada carta no es la misma construcción covariante.
- Celdas 138–143: relevancias de scores por autodiferenciación y comparación angular mediante una métrica inversa regularizada.
- Celdas 153–159: Fisher categórica y comparación angular entre cartas con regularización transformada.

El contexto solicitado introduce ω_P = d_θS_P y B = d_Pω. Esta última derivada corresponde a la variación en perspectivas, diferente de d_θω_P. Falta la fuente para fijar dominios, suavidad, convenciones de índices y signo de B.

La construcción ideal con pseudoinversa y kernel de Fisher debe distinguirse de la implementación regularizada denominada G_rho en el contexto. No se ha recuperado una definición verificable de G_rho ni una equivalencia con F + λG del notebook. No identificar estas notaciones por intuición. Véase [admisibilidad](admissibility-axiom.md).
