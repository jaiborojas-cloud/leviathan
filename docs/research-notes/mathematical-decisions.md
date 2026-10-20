# Historia de las decisiones matemáticas

La secuencia se reconstruye desde fuentes del repositorio. Los identificadores
D01–D09 son de esta síntesis; no sustituyen decisiones ni protocolos originales.
Es una historia de motivaciones y consecuencias, no un registro nuevo de resultados.

## D01 — Separar el modelo de la perspectiva

**Motivo:** Fisher describe la estructura estadística identificable, pero no elige
qué observable importa. **Decisión:** especificar $S_p$, $\omega_p=d_\theta S_p$
y mantener distintos los parámetros del modelo y de la familia.
**Consecuencia:** cambiar carta no equivale a cambiar perspectiva.
[Fuente consolidada](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md); A01–A03.

## D02 — Introducir admisibilidad sobre el cociente Fisher

**Motivo:** Fisher puede tener kernel; una relevancia arbitraria puede atribuir
sentido a direcciones no identificables. **Decisión:** exigir anulación del
kernel para $\omega$ y $B$ y definir la geometría ideal en el dual del cociente.
**Consecuencia:** $BF^+B^T$ sólo representa la contracción intrínseca bajo esas
hipótesis. El antecedente autónomo E9 no está plenamente recuperado; se usa la
[síntesis del axioma tras E9-G](../archive/import-2026-10-17/originals/RIPG_contexto_vigente_axioma.md),
sin inventar su historial faltante. A02–A04.

## D03 — Dejar de usar desplazamiento como calidad universal

**Motivo:** E10 no obtuvo anticipación respecto de accuracy ni una ley simple de
corrupción; E11 mostró inversiones de signo según alcance y relevancia.
**Decisión de interpretación:** reportar diferencias geométricas condicionadas,
separadas de utilidad predictiva y causalidad. **Consecuencia:** mayor $D_G$ no
significa automáticamente mejor aprendizaje.
[Cierre E10](../archive/import-2026-10-17/originals/Cierre_E10_RIPG_y_ruta_E11.md),
[estado E11-C](../archive/import-2026-10-17/originals/Estado_hipotesis_RIPG_E11C.md); A16, N01–N03.

## D04 — Transportar una referencia en vez de cortar el espectro crudo

**Motivo:** E11-E cambió la métrica de la misma red al reescalar coordenadas.
**Decisión instrumental:** seleccionar modos con autovalores generalizados de
$(F,H)$, transportando $H$; estudiar después regularización explícita.
**Consecuencia:** un contraste estadístico fuerte no repara la falta de covariancia.
[Prueba E11-E](../archive/import-2026-10-17/originals/E11E_invariancia_de_carta_y_rango_Fisher.md),
[referencias E11-F](../archive/import-2026-10-17/originals/E11F_referencias_y_estado_E11.md); A05–A06.

## D05 — Hacer explícita la regularización y la escala de atribución

**Motivo:** el corte duro es discontinuo; cambiar escala por alcance impide leer
sus diferencias como aportes aditivos. **Decisión:** declarar
$G_\rho=B(F+\rho\lambda_{\max}(F,H)H)^{-1}B^T$ y usar escala común para Schur.
**Consecuencia:** covariancia condicionada, no elección canónica; la aditividad
ocurre en métricas, no en sus distancias.
[E11-J](../archive/import-2026-10-17/originals/E11J_regularizacion_explicita_y_estado_RIPG.md),
[E11-N](../archive/import-2026-10-17/originals/E11N_atribucion_schur_y_estado_RIPG.md); A04, A11.

## D06 — Construir un campo no lineal y usar holonomía como control derivado

**Motivo:** una matriz en un punto no describe curvatura espacial; $d\omega=0$
no implica conexión plana. **Decisión:** familia exponencial admisible, derivadas
del campo y cálculo de Levi-Civita/Riemann; contrastar holonomía con flujo de
curvatura. **Consecuencia:** separar magnitud, expansión de área y signo, sin
contar holonomía como evidencia predictiva independiente.
[E12-B](../archive/import-2026-10-17/originals/E12B_campo_no_lineal_admisible_y_estado_RIPG.md),
[E12-E](../archive/import-2026-10-17/originals/E12E_holonomia_control_derivado_y_cierre_E12.md); A07–A09.

## D07 — Normalizar regiones y conservar fallos de cobertura

**Motivo:** igual tamaño coordenado no implica igual área intrínseca; el jet de
E13 perdió positividad en la réplica externa. **Decisión:** conservar el cierre
INCONCLUSIVE; el desarrollo posterior debe resolver el campo regional sin convertir
supervivientes en confirmación. **Consecuencia:** un estimando regional necesita
un dominio válido; SPD local no garantiza una región admisible.
[Cierre E13](../archive/import-2026-10-17/originals/E13_cierre_y_punto_de_partida_E14.md),
[cierre C1-A2](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-C1-A2_cierre.md); A10, A13.

## D08 — Separar asociación simultánea de predicción temporal

**Motivo:** Jacobi relaciona curvatura y deformación en el mismo estado; los casos
positivos de T1 ya eran conocidos. **Decisión:** T2-A0 define cohorte nueva,
señal basal y evento futuro bajo secuencia ciega y criterios propios.
**Consecuencia:** T1-B es antecedente descriptivo/control; un prerregistro o una
calibración técnica no son resultado predictivo.
[T1-B](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_E15-T1-B_cierre.md),
[T2-A0](../archive/import-2026-10-17/originals/Leviathan/Leviathan_RIPG_T2-A0_preregistro.md); A14–A15.
La documentación nueva específica está en [codex](../../experiments/T2_A/codex/README.md).

## D09 — Distinguir operaciones y cambiar el método, no el outcome antiguo

**Motivo:** «componer» y «agrupar» no son equivalentes; E16-B no alcanzó la
precisión FD exigida para rango. **Decisión:** separar carta, restricción, descenso
y composición; fijar otro protocolo de precisión E16-C antes de ejecutarlo.
**Consecuencia:** la referencia corregida de E16 y el resultado inconcluso de B
se conservan; el método nuevo aporta controles numéricos sobre datos conocidos,
no una confirmación independiente de aprendizaje.
[E16 y errata](../../experiments/E16/ERRATA_v2.md),
[E16-B](../../experiments/E16/B/CONCLUSION.md),
[E16-C, fuente fijada](https://github.com/jaiborojas-cloud/leviathan/blob/4fd7eb5790a7161731e22c238f29138cd66425ac/experiments/E16/C/DESIGN_FROZEN.md); A17–A19.

## Decisiones que este documento no toma

No declara una métrica canónica, un cierre E14 recuperado, un evento T2-A ni
una fase nueva autorizada de entrenamiento. No modifica tiempos, radios,
tolerancias, cohortes o outcomes. Para esas decisiones rige el protocolo de la
etapa y su historial versionado, no esta síntesis retrospectiva.
