# Errata previa a v2 — Escala global de la energía en el FD local

La primera corrida se detuvo mediante SIGINT tras completar cuatro caminos de
Q0, mientras calculaba una comparación descriptiva de Hausdorff. Se preservan
el resumen original INCOMPLETE, todas las tablas parciales y ABORTED.json.
El snapshot reproduce el código de implementación de 094bc25.

El gradiente local de longitud suma dos aristas y no depende de m. En energía
E_aff=(m/2) sum A_i, la función de referencia aplicada sólo a esas dos aristas
usa por defecto m_local=2. Sus diferencias finitas deben multiplicarse por
m_global/2. V1 omitió ese factor. Por ello son incorrectos su gradiente MP de
energía, residual KKT de energía y errores/estados derivados. El chequeo AD/MP
lo detectó; no se convierten estas cifras en resultados válidos.

La optimización usa el gradiente AD del objetivo GLOBAL y no ese cálculo FD.
No cambian objetivos, candidatos iniciales, optimizador, datos, tolerancias ni
presupuestos. El Hessiano y sus Rayleigh usan diferencias de objetivos globales
y no sufren esta omisión. No se corrige retrospectivamente ninguna tabla v1.

V2 debe ponderar la contribución local por m_global/m_local al calcular FD de
energía. Añadir antes de ejecutar un control de métrica constante, tres
segmentos no uniformes y gradiente analítico m(2p_j-p_{j-1}-p_{j+1}), en ambas
coordenadas, con error normalizado≤1e-40. El cálculo global de referencia no
se pondera otra vez. Guardar v2 en otro directorio y reproducirla íntegramente.
Cotejar también las coordenadas, iteraciones y objetivos de los caminos comunes
con v1 para comprobar que la corrección no cambió la optimización.
