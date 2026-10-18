# Transcripción textual derivada del DOCX histórico

No reemplaza al original. Conserva propuestas históricas; su estado 468/800 está superado. Las afirmaciones geométricas propuestas requieren revisión, no son teoremas certificados.

LEVIATHAN / RIPG

Mapa de rutas de investigación

Prioridades, dependencias, riesgos y criterios de decisión

Estado de referencia: T2-A en 468/800 auditorías, protocolo congelado.



1. Propósito

Este documento organiza los principales caminos científicos de RIPG después del programa E12–E15 y durante la validación prospectiva T2-A. El objetivo no es maximizar el número de extensiones, sino priorizar aquellas que más reducen incertidumbre sobre la hipótesis central: qué parte de la geometría perspectival es intrínseca, predictiva y estable frente a decisiones de modelado.

El peso estratégico asignado a cada línea es una recomendación de cartera, no una probabilidad de éxito. Los pesos suman 100% y reflejan cuatro factores: valor científico, urgencia como prerrequisito, poder de falsación y costo/riesgo de confusión.

2. Estado científico actual

T2-A está incompleto y permanece ciego respecto de desenlaces futuros; el estado reportado es 468/800 auditorías basales.

La geometría operativa validada es una familia 2D de perspectivas; no existe todavía un espacio ambiente canónico P_m para m>2.

En P₂ hay evidencia fuerte de pérdida de inyectividad en casos concretos, pero conviene separar y certificar formalmente las ramas conjugada y Maxwell/corte.

La curvatura K usada en C1-A2 proviene del campo métrico exacto Gρ y sus derivadas por autodiferenciación, no de diferencias finitas.

Para una futura extensión m>2, las rebanadas geodésicas Σ_Π permiten aislar K(Π) en P₀, pero toda interpretación es relativa a la familia perspectival Φ elegida.

3. Portafolio propuesto

ID

Línea

Peso

Relevancia

Momento

Pregunta que resuelve

A

Completar T2-A prospectivo

20%

Muy alta

Ahora

Prueba si una señal geométrica temprana predice no-inyectividad futura fuera de muestra.

B

Certificación conjugada en P₂

15%

Muy alta

Ahora

Cierra el mecanismo focal con cantidades con signo y dos rutas independientes.

C

Capa Maxwell / colisión del frente en P₂

15%

Muy alta

Después de B

Separa corte global de autointersecciones inducidas por conjugados.

D

Robustez dentro de P₂

8%

Alta

Después de B–C

Controla activación, elecciones instrumentales y estabilidad del fenómeno sin cambiar de familia ambiente.

E

Canonicidad y extensiones P_m

12%

Alta

Tras cerrar P₂

Formaliza que P_m depende de Φ y compara familias admisibles.

F

Tomografía Grassmanniana

10%

Alta

Después de E

Estudia Π↦K^(Φ)(Π), r_conj^(Φ)(Π) y estructura direccional en una familia fija.

G

Composicionalidad y coarse-graining

10%

Alta

Exploratoria controlada

Pregunta si composiciones no invertibles crean estructura y reducen dimensión geométrica efectiva.

H

Benchmarks físicos: PINNs / Boltzmann

7%

Media-alta

Tras cierre básico

Prueba RIPG contra invariantes y estructura física conocida.

I

Puente con teoría de aproximación

3%

Media

Largo plazo

Relaciona dimensión geométrica efectiva con complejidad, generalización y tasas de aproximación.

4. Líneas prioritarias

A. Completar T2-A — validación prospectiva

Peso sugerido: 20%

Hipótesis: Una propiedad geométrica temprana puede anticipar pérdida futura de inyectividad bajo un protocolo preregistrado y sin abrir desenlaces.

Valor: Es la prueba más directa de poder predictivo prospectivo; distingue señal descriptiva de mecanismo útil.

Criterio de salida: PASS / FAIL / INCONCLUSIVE según reglas congeladas de T2-A0, sin redefinir predictor, umbrales ni cohorte.

Dependencias: Ninguna línea nueva debe contaminar la cohorte o alterar el protocolo antes del cierre.

B. Certificación conjugada en P₂

Peso sugerido: 15%

Objetivo: Certificar el primer conjugado con información orientada y no únicamente con σ_min.

Usar det(Dexp) con signo o, equivalentemente en 2D, el signo de J(r)/r.

Exigir un cambio de signo entre radios r₋ y r₊ cuyos valores excedan la barra de error del integrador.

Integrar de forma independiente J'' + K(γ(t))J = 0 y comparar su primer cero con el obtenido desde Dexp.

Usar comparación de Sturm para cotas: límites superiores e inferiores sobre K a lo largo del rayo producen cotas sobre r_conj.

Documentar presupuesto de error: autodiferenciación de G/K, integración DOP853, salida densa y refinamiento de raíz.

Instrumentación: Persistir por rayo: dirección inicial, radios, J(r), det(Dexp), Dexp, σ_max y tangente final de la geodésica.

C. Capa Maxwell / colisión del frente en P₂

Peso sugerido: 15%

Objetivo: Determinar qué ocurre primero: conjugado o colisión global del frente.

Una autointersección del borde no discrimina por sí sola entre Maxwell y una cola/cúspide posterior a un conjugado.

Construir una función de separación mínima del frente M(r) excluyendo vecinos angulares triviales.

Para N rayos, usar un criterio conservador de ausencia de colisión basado en M_N(r) > L(r)·Δθ, con Δθ=2π/N.

Acotar L(r) con información de Dexp, por ejemplo mediante r·σ_max(Dexp) cuando corresponda al parametrizado radial.

Comparar el primer radio Maxwell con r_conj y clasificar la pérdida de inyectividad por orden de eventos.

Resultado esperado: Clasificación conjugada / Maxwell / ambas, con orden radial explícito.

D. Robustez dentro de P₂

Peso sugerido: 8%

Repetir controles clave con activaciones suaves (tanh, GELU o SiLU) frente a ReLU, sin reinterpretar retrospectivamente los umbrales.

Separar fenómenos geométricos genuinos de efectos inducidos por regiones lineales de ReLU.

Comprobar estabilidad frente a elecciones instrumentales ya declaradas: regularización ρ, precisión ODE y parametrización equivalente de la misma familia.

5. Extensiones después de cerrar P₂

E. Canonicidad y construcción de P_m

Peso sugerido: 12%

No debe asumirse que existe un único espacio de perspectivas de dimensión m. Cada familia admisible Φ que extienda la rebanada actual puede inducir una métrica ambiente diferente G_P^(Φ). Por tanto, elegir p³,…,p^m es una decisión de modelado.

Definir varias familias candidatas Φ que contengan la rebanada P₂ actual.

Clasificar resultados como dependientes de Φ, covariantes bajo ciertas extensiones o invariantes respecto de una clase natural.

Evitar lenguaje de 'la geometría de P_m' sin especificar la familia perspectival.

F. Tomografía Grassmanniana relativa a Φ

Peso sugerido: 10%

Para una familia fija Φ, estudiar funciones sobre Gr₂(T_P₀P), usando rebanadas geodésicas Σ_Π = exp_P₀(Π) para eliminar en P₀ el término extrínseco de la ecuación de Gauss.

Perfil local: Π ↦ K^(Φ)(Π).

Perfil focal: Π ↦ r_conj^(Φ)(Π); el radio conjugado ambiente se obtiene como ínfimo/mínimo sobre planos cuando corresponde.

La rama Maxwell no puede inferirse por ausencia en un atlas aleatorio; debe buscarse en el espacio de pares de direcciones y luego identificar span(v₁,v₂).

G. Composicionalidad y coarse-graining perspectival

Peso sugerido: 10%

Hipótesis: Propiedades estructurales pueden emerger de composiciones de perspectivas aunque no estén presentes en cada perspectiva elemental.

Construir P = Φ(P₁,…,P_n) o S_P = Ψ(S_{P₁},…,S_{P_n}) con composiciones controladas.

Separar cambios invertibles de coordenadas de composiciones no invertibles que agregan o colapsan información.

Medir si rank(h), el espectro de h y la dimensión efectiva disminuyen bajo coarse-graining.

Comparar curvatura, radios conjugados y estructura de relevancia antes y después de la composición.

Explorar la interpretación de profundidad como reorganización de qué distinciones siguen siendo geométricamente relevantes.

Conexiones: Composicionalidad profunda, teoría de representación, coarse-graining, renormalización, manifolds efectivos y física estadística.

H. Benchmarks físicos: PINNs y Boltzmann

Peso sugerido: 7%

PINNs: tratar PDE, condiciones de frontera, condiciones iniciales y datos como perspectivas físicas diferentes sobre el mismo modelo.

Boltzmann: usar masa, momento, energía, entropía y operador de colisión como banco de pruebas con estructura analítica conocida.

Preguntar si RIPG recupera invariantes, modos lentos/rápidos, relajación al equilibrio y relaciones de conservación.

Usar la física conocida como falsador: si la geometría no refleja restricciones necesarias, revisar la construcción antes de atribuir contenido físico nuevo.

I. Puente con teoría de aproximación y generalización

Peso sugerido: 3%

Investigar si la dificultad efectiva de aproximación está mejor relacionada con una dimensión intrínseca/espectral del espacio de perspectivas que con la dimensión ambiente. Esta línea es conceptualmente atractiva, pero debe esperar a que la geometría y su canonicidad estén mejor cerradas.

6. Qué más conviene considerar

Consideración

Por qué importa

Definición de dimensión efectiva

Fijar una o varias definiciones preregistrables: rango numérico, participación espectral, entropía espectral o dimensión basada en volumen.

Identificabilidad

Separar degeneraciones de la métrica debidas a redundancia perspectival de degeneraciones debidas al modelo o a Fisher.

Estabilidad bajo reparametrización

Mantener controles explícitos de cambios de carta y transformaciones equivalentes del modelo.

Jerarquía local–global

No mezclar curvatura local, focalización/conjugados y corte/Maxwell; cada fenómeno requiere observables e inferencia diferentes.

Persistencia de datos geométricos

Guardar trayectorias, tangentes finales, J(r), determinantes con signo, Dexp y metadatos de tolerancia para auditorías posteriores.

Controles negativos

Diseñar familias o composiciones que no deberían producir la señal propuesta; son esenciales para atribuir significado a cualquier patrón.

Predicciones antes de cómputo

Convertir cada extensión en una hipótesis falsable antes de abrir resultados, replicando la disciplina de T2-A0.

Generalización entre datasets

Después de Wine, repetir solo resultados ya definidos en dominios diferentes; evitar redefinir observables por dataset.

Escala por capas

Volver a la pregunta mecanística de E15: qué capas contribuyen a cada fenómeno y si la geometría aparece por composición jerárquica.

7. Secuencia recomendada y compuertas

La secuencia recomendada evita que una extensión atractiva introduzca grados de libertad antes de cerrar los fenómenos ya observados.

G0 — Integridad — Completar T2-A sin tocar el protocolo ni abrir desenlaces.

G1 — Conjugados P₂ — Certificación por signo + Jacobi independiente + cotas de Sturm.

G2 — Corte P₂ — Establecer o descartar colisión Maxwell antes de r_conj con una cota de discretización explícita.

G3 — Cierre P₂ — Declarar qué parte del fenómeno es local, focal y global; congelar el instrumental resultante.

G4 — Robustez — Probar activación/representación sin cambiar la pregunta científica.

G5 — Extensiones Φ — Definir familias P_m candidatas y auditar canonicidad relativa.

G6 — Grassmanniana — Caracterizar perfiles direccionales dentro de una familia fija.

G7 — Composición y física — Explorar coarse-graining y benchmarks PINN/Boltzmann con predicciones predefinidas.

8. Lectura estratégica

La cartera queda deliberadamente sesgada hacia validación y cierre antes que hacia expansión. Un 58% del peso se asigna a terminar T2-A, certificar conjugados, resolver Maxwell y robustecer P₂. Un 32% se asigna a extensión geométrica/canonicidad/composición, y solo 10% a aplicaciones y puentes teóricos externos. La razón es metodológica: si P₂ no queda limpio, cualquier estructura en P_m, PINNs o Boltzmann heredará una ambigüedad difícil de interpretar.

La extensión composicional merece un peso alto (10%) porque puede conectar profundidad, reducción de dimensión y estructura emergente; sin embargo, debe diseñarse como una prueba de hipótesis y no como una narrativa posterior a los datos.