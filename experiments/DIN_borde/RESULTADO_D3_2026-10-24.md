# DIN-borde D3 — resultado exploratorio (2026-10-24)

**Naturaleza:** exploratorio, según `PLAN_D3_exploratorio.md` (commit `c5698fc`, registrado antes de calcular). Son los mismos 3120 estados de D1. Salidas: `d3/d3_estados.csv` y `d3/d3_resumen.json`. No confirma nada.

## Hallazgos
1. **M es casi diagonal desde el update 5.** El autovector dominante está concentrado en un solo ejemplo del panel: la mediana de max v₁,k² es 0.9996 en el update 5 y > 0.99999999 a partir del 50. El índice coincide con el del mayor M_kk en 99.4 % de los estados del update 5 y en 100 % después. Además, λ_max/tr ≈ M_kk,max/tr (0.0655 frente a 0.0654 en el update 5; 0.9266 en ambos en el 250). En el update 5, el rango efectivo de 24 viene de **muchas entradas diagonales comparables**, no de mezclas entre ejemplos.
2. **El colapso consiste en que una sola entrada diagonal se queda con la traza:** un ejemplo k* del panel concentra M. Encaja con la hipótesis de D2: si M ≈ e_k e_kᵀ, ρ̃ = 1/n.
3. **k* lo fija el split, no la inicialización.**
   - En los updates 50–250, la mediana es de 1 k* distinto entre las 5 trayectorias de un split; en el update 5 era de 3.
   - k* se mantiene igual entre los updates 50, 150 y 250 en 87 % de las trayectorias.
   - Solo en 32 % coincide con el k* dominante del update 5: el ejemplo que termina dominando aparece después del update 5.
4. **k* no tiende a ser vértice de la envolvente de f.** Es vértice en 19 % de los estados, cuando los vértices son 28 % de los puntos del panel. Los ejemplos interiores también producen el piso.
5. **Por encima del piso.** 218 estados del update 250 quedan por encima de log(1/n) + 0.05. Spearman entre log ρ̃ y λ_max/tr: −0.80. Spearman entre log ρ̃ y la concentración: −0.73. Las diferencias de concentración son minúsculas (1 − c ≈ 10⁻⁸ frente a 10⁻⁷), pero importan: una masa residual ε en otras direcciones aporta del orden de √ε a la longitud. Coincide con la pregunta Q4 de D2.

## Lectura (hipótesis)
M = R(F + reg)⁻¹Rᵀ, donde las filas de R son los gradientes de log p(y_n) de cada ejemplo del panel. Si, al entrenar, el modelo gana confianza en casi todos los ejemplos, sus gradientes se apagan y **queda uno, k*, cuyo gradiente sigue vivo**. El candidato natural es el ejemplo de validación que el modelo no logra aprender: mal clasificado o con poca confianza. Entonces:
ρ_borde ≈ √(M_k*k*)/n,
y la distancia al borde quedaría determinada por **un solo ejemplo difícil del panel de validación**. Eso explicaría tres cosas: por qué manda el split (los datos fijan cuál es el ejemplo difícil), por qué la inicialización casi no importa y por qué la precisión en validación se asocia.

**Siguiente paso (D4):** comprobarlo con p(y_n | modelo) en cada estado. Requiere cargar los checkpoints con torch.
