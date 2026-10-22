# Lectura de escalares de NumPy en la corrida v1

La primera verificación se detuvo antes de repetir el experimento: intentó leer
con float(texto) la columna `displacement` de probes.csv. NumPy 2.3.5 escribe
repr(np.float64(x)) como `np.float64(x)`, no como un número desnudo.

Se conserva íntegro probes.csv y el código de la primera corrida. El lector del
verificador admite este envoltorio mediante una expresión regular restringida
al contenido numérico, sin eval. No se modifica el indicador, el marcado, las
curvas, el protocolo, las tolerancias ni ningún resultado. La repetición debe
reproducir también ese texto exactamente. El fallo inicial fue de lectura, no
una discrepancia entre dos ejecuciones científicas.
