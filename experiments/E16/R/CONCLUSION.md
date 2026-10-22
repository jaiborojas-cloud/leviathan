# Conclusión E16-R

**INCONCLUSIVE.** Este escalado diagonal mejora el cumplimiento del KKT físico
en los casos de 132, pero no consigue terminar las optimizaciones cuadráticas
bajo la regla congelada. Tampoco demuestra una aceleración global: requiere
más evaluaciones y preparación adicional.

## Qué permite afirmar el contraste

1. Se verifica que ambos métodos minimizan exactamente L en el mismo dominio:
   no se introduce un objetivo energético distinto. Las transformaciones,
   cotas y regla de la cadena pasan los controles independientes.
2. Scaled cumple KKT físico en cuatro de cuatro candidatos cuadráticos;
   reference lo cumple en dos de cuatro. En Q1/264, sin embargo, el residual
   es menor con reference. La mejora es parcial, no uniforme.
3. Los ocho casos cuadráticos agotan iteraciones, incluso seis que cumplen
   la tolerancia física. R conserva INCONCLUSIVE porque también exigía éxito
   del solver. Esto separa cumplimiento del KKT auditado y condición interna
   de terminación; no autoriza a cambiar el requisito después de observarlo.
4. Longitud y Hausdorff presentan acuerdo entre métodos y resoluciones. C0
   conserva la recta y pasa. Ninguno de estos acuerdos sustituye por sí solo
   la terminación y validación del problema cuadrático.

## Límites

Los espectros se obtienen en referencias comunes, no en todos los candidatos
finales. Sus umbrales son relativos y su cálculo float64 no certifica signos
ni condicionamiento exactos. El control recto muestra que escalar una matriz
con modos nulos puede amplificar errores numéricos y alterar su clasificación
al umbral. Esos negativos no son evidencia de curvatura real del control.
No se modifica el precondicionador tras observar esta limitación.

El método sólo usa una diagonal congelada, no un tratamiento completo del
acoplamiento entre nodos. No se ha probado que el condicionamiento sea la
única causa del límite de iteraciones ni que otros precondicionadores fallen.
Las trayectorias de continuación de 264 difieren entre métodos, lo que limita
una atribución causal aislada a la escala.

Los datos siguen siendo sintéticos y sin entrenamiento. No hay confirmación
independiente de una hipótesis descubierta en Q/R. Los gradientes son
numéricamente comprobados, no certificados exactos de estacionariedad.
Hausdorff es euclídea en la carta normalizada, no distancia intrínseca de h.
Dos mallas no demuestran convergencia, unicidad, regularidad, existencia de
una curva límite ni mínimos globales.

La siguiente cuestión útil sería definir prospectivamente un criterio de
parada basado en el KKT físico, auditado de forma independiente, y contrastarlo
con las condiciones internas del solver. Debería aplicarse a todos los casos
con presupuesto y reglas nuevos. No se ejecutó aquí ni se usa para aprobar
retrospectivamente candidatos de R.
