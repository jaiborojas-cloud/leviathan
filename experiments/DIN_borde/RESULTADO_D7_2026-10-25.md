# DIN-borde D7 — ¿por qué predice la señal temprana? Resultado (2026-10-25)

**Naturaleza:** exploratorio, según `PLAN_D7_mecanismo.md`, registrado antes de calcular. Datos de descubrimiento: 780 trayectorias de los splits 12–167, con tablas publicadas. No usa la cohorte de DIN-C1. Salida: `d7/d7_resumen.json`. Los p salen de 2000 permutaciones dentro del split y son descriptivos.

## Hallazgos
1. **X no rastrea a un ejemplo concreto.** El ejemplo menos confiado del update t es el mismo que domina M en el 250 en estas proporciones:

| update t | 5 | 10 | 20 | 30 | 40 | 50 |
|---|---|---|---|---|---|---|
| coincide con k*(250) | 32 % | **45 %** | 66 % | 79 % | 83 % | 88 % |

   Además, el incremento de X es igual de fuerte cuando el ejemplo difícil del update 10 **no** es el dominante final (D = 0.063) que cuando sí lo es (D = 0.059). X funciona como una medida **global** de cuánta incertidumbre le queda al modelo, no como el seguimiento de un ejemplo.
2. **X anticipa la resolución final del dominante.**
   - X frente a R = log(1 − p(y_k*)) en el 250: W = 0.21 (0.17 ajustado por la base cúbica de ρ(10)).
   - X frente a «k* mal clasificado en el 250»: W = 0.29, en los 27 splits donde varía.
   - 47 % de las trayectorias terminan con k* mal clasificado.
3. **R determina casi todo Y:** W(R, Y) = 0.94. Es en buena parte la relación algebraica de D2b tras el colapso.
4. **Mediación descriptiva del estimando de C1:**
   - D_X = 0.078 (sobre la base cúbica de L10);
   - **D_X | R = 0.042**: alrededor del **46 %** del incremento de X pasa por la incertidumbre final del dominante;
   - D_X | Mal = 0.057: solo un 27 % pasa por la clasificación binaria final;
   - el **54 % restante** de la información de X sobre ρ(250) no pasa por R.
5. **Heterogeneidad:** el incremento es mayor cuando el dominante termina mal clasificado (D = 0.091) que cuando se resuelve (D = 0.036).

## Lectura (hipótesis)
- **El mecanismo propuesto se cumple solo en parte.** La incertidumbre temprana anticipa en parte si el ejemplo difícil final queda sin resolver, y eso fija ρ(250) casi algebraicamente.
- **X no apunta al ejemplo final:** más de la mitad de las veces, el ejemplo difícil del update 10 no es el que termina dominando.
- **Más de la mitad de la señal no pasa por la confianza final del dominante.** Candidatos para ese resto:
  - el factor de leverage ℓ_k de D2b;
  - el grado de colapso;
  - la escala de la Fisher.
  No se miden aquí.
- **Encaja con G1:** en Iris, el ejemplo difícil casi siempre termina mal clasificado y la escala crece. La señal podría depender de que haya **variación** en la resolución final entre inicializaciones de un mismo split.
- **Mediador medido al final:** R se mide en el tiempo del desenlace y está ligado a Y casi por identidad. La «mediación» es una descomposición descriptiva, no una prueba causal.
