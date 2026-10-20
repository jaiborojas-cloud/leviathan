# Reconstrucción y decisiones

Lectura de AGENTS.md, README, fundamentos, research-status, roadmap,
research-directions e índices antes de formalizar. Checkout inicial 12e849e,
rama inicial `work`, árbol limpio. E16 libre en los índices y búsqueda textual
de documentos actuales/históricos; elegido siguiendo la secuencia E<n>.
Rama propia `research/e16-composicionalidad`; sin worktree.

## Procedencia

1. Fuente histórica primaria de la propuesta: [DOCX mapa de rutas](../../docs/archive/import-2026-10-17/originals/RIPG_mapa_rutas_investigacion.docx),
   sección G. Se contrastó su XML con la [transcripción derivada](../../docs/archive/import-2026-10-17/RUTAS_INVESTIGACION_texto_extraido.md),
   líneas 241–257: construir P=Φ(P₁,…,P_n) o S=Ψ(S₁,…,S_n), distinguir
   invertibilidad y medir rango/espectro/dimensión efectiva; explorar curvatura
   y profundidad. Son propuestas e hipótesis, sin teorema ni experimento de
   composición demostrado allí. El dato 468/800 del documento está superado.
2. [Contexto/axioma](../../docs/archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md):
   fuente técnica que fija ω, B, admisibilidad y cociente; integra históricos
   anteriores y no sustituye sus datos. Informa controles de cartas históricos,
   no valida la propuesta composicional nueva.
3. [Estado de septiembre](../../docs/archive/import-2026-10-17/originals/Leviathan_RIPG_estado_investigacion_2026-09-23.md):
   síntesis técnica histórica, con fecha de corte interna 24 de septiembre pese
   al nombre 23; no se altera esta discrepancia.
4. [Síntesis vigente](../../docs/research-directions.md) y
   [síntesis previa al import](../../docs/archive/review-before-import/docs/research-directions.md)
   separan composicionalidad y coarse-graining e imponen mapas/observables.
   Son síntesis posteriores, no nuevas fuentes primarias.
5. [Limitaciones de la remesa](../../docs/archive/import-2026-10-17/FALTANTES_Y_LIMITACIONES.md):
   no se localizaron notas autónomas adicionales de estas dos líneas. No se
   inventa definición histórica de Φ ni de Ψ ni un resultado histórico ausente.

Se conservarán hashes de estas fuentes en `results/source_hashes.csv`. No se
invoca acceso a conversaciones ni bibliotecas externas. Los resultados E9/E11
se citan como reportados por las fuentes, no se vuelven a calcular aquí.

## Decisiones

- Métrica SPD declarada antes del caso singular; no Fisher estimada ni regularización.
- Cuatro operaciones separadas; comparar rango con referente explícito.
- No buscar curvatura/radios ni entrenar. Tablas bastan: `figures/` sin imágenes.
- Conservar diseño en commit previo al código/ejecución. Sin ajustes retrospectivos.
- La autorización explícita del usuario para push/PR prevalece sobre la regla
  general de AGENTS.md «no publicar ni hacer push automáticamente».
- T2-A: sólo se consultan índices y contexto documental. Ningún archivo, protocolo,
  predictor, clasificación ni outcome se modifica; ningún script suyo se ejecuta.
