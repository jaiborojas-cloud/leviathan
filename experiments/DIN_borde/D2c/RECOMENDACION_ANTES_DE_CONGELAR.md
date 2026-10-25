# A5 · cambios recomendados al responsable

**PASS_DESCRIPTIVE. Recomiendo corregir D01–D03 y resolver D04 antes de
congelar.** No se modificó C1 ni su diseño. La decisión sigue siendo del
responsable. Esta auditoría corresponde sólo al sujeto6b17d25.

## Necesarios: defectos demostrados

1. **D01, universo de cohorte y unicidad.** Fijar un manifest de los156 splits
   y780 IDs previstos; comprobar rango, inicializaciones, duplicados y unión
   uno a uno. Usar780 como denominador de faltantes y156 como universo de
   splits, o los IDs exactos declarados por protocolo. c1_cohorte debe entregar
   las filas fallidas además de las exitosas, o análisis debe completar las
   ausencias contra ese manifest. Vincular tabla y resumen operacional por SHA.
   Repetir los casos47 omitidas/47 explícitas,40 splits omitidos y duplicados:
   deben impedir un PASS de una cohorte inválida. Mantener el límite exacto:
   39/780=5% no excede5%;40/780 sí lo excede.
2. **D02, dominio numérico ANTES del log.** Comprobar rho>0 y finita para
   todas las variables logarítmicas; X/Y/L transformados deben ser finitos.
   Clasificar inválidos como faltantes y aplicar los umbrales, o abortar de
   forma controlada si el contrato así lo dispone. Una sola rho inválida no
   exige automáticamente INCONCLUSIVE si se trata como faltante y sigue bajo
   el5%: esa política debe quedar escrita. Lo demostrado es el crash actual.
3. **D03, degeneraciones y orden de las compuertas.** Comprobar elegibilidad
   y condición numérica antes de calcular primaria/secundarias; manejar L
   constante, SSEbase cero y errores de ajuste sin perder el informe. Fijar
   qué estado científico corresponde a una primaria no definida. No imputar
   p, D o variación inexistente; conservar errores y las filas que los causan.
4. **D04, precondición de la cuerda.** Enumerar todos los índices de cada
   cara expuesta, incluidos puntos interiores a aristas, o comprobar y declarar
   la precondición de posición general antes de usar sólo pares de vértices.
   El caso sintético SPD de26 puntos en una cara contradice la cota actual.
   No sabemos si ocurre en el panel Wine. No usar esa cota como auditoría de
   rho sin resolver su dominio de validez. No se necesita leer nuevos estados
   para reproducir el defecto matemático.

Después de las correcciones, versionar código/diseño nuevos, SHA y regresiones
antes de congelar; esta auditoría no certifica un parche futuro. No se propone
cambiar umbrales mirando los outcomes de la futura cohorte.

## Aclaraciones necesarias del contrato científico

- Un PASS de D compara **una base cúbica concreta** con esa base más X.
  No prueba información condicional nueva sobre TODO L. X=h(L), con h escalón,
  log o seno, puede pasar sin contener información nueva, porque amplía la
  clase funcional y mejora de verdad esa base. Limitar la afirmación a ese
  estimando; cambiarlo sería una decisión del responsable, no un arreglo
  mecánico del código.
- Permutar X dentro del split es exacto bajo la intercambiabilidad relevante
  de X condicionada a los demás elementos mantenidos fijos. El nulo amplio
  «ningún incremento condicional dado L» no garantiza esa intercambiabilidad
  cuando X depende de L. Los nulos estudiados no certifican todos esos casos.
- Publicar semillas, orden de filas y generador de las pruebas de §6. Algunas
  magnitudes de control no se reproducen numéricamente con semilla1 y nuestra
  tabla ordenada, aunque se reproducen las clasificaciones esperadas. La
  potencia de un X fabricado con el residuo de Y es retrospectiva y específica
  del generador; no garantiza potencia de un predictor temprano desconocido.

## Opcionales o decisiones del responsable

- Documentar atol1e-8 de np.allclose para X, holgura1e-15 del p primario y
  B2000 de D grado5. Explicitar fórmula de la secundaria de rangos y reglas
  para cualquier resultado secundario no definido.
- Decidir si «mejora» requiere además D>0 o un mínimo práctico. La regla
  actual no exige D>0; no se observó aquí un PASS con D≤0 y no se declara ese
  fallo como demostrado.
- Vincular compuerta con SHA de cohorte v2 y protocolo, exigir PASA booleano,
  conservar identidad de las5 trayectorias y evidencia de tolerancias. La
  guarda PASA aislada no acredita que se repitiera con la versión correcta.
- Publicar las40 IDs de auditoría de rho y comprobar completitud/errores;
  fijar qué hacer si la precisión es insuficiente. Ahora se informa sólo lo
  recibido; no hay regla de consecuencia cuantitativa en §5.
- Si se pretende inferencia condicional general, estudiar una aleatorización
  condicionada a X|L o un estimando predictivo con procedimiento inferencial
  adecuado. No sustituir sin validación por permutar residuos ni añadir
  polinomios después de observar el resultado.
- Confirmar conservadurismo/tamaño y potencia con5000 permutaciones en una
  simulación prospectivamente fijada más amplia si se exige esa precisión.
  Nuestra calibración principal usa199; las15 sensibilidades a5000 mantuvieron
  su clasificación, pero son una comprobación pequeña.

No se recomienda entrenar una cohorte ni congelar automáticamente por el
PASS de A2/A4: A1/A3 contienen defectos reproducibles de entrada/decisión.
