# Enmienda congelada v4 · salida de la verificación

verify_v2 completó los contrastes, pero falló al serializar otro numpy.bool_,
esta vez en la auditoría suplementaria D-M. La corrección v3 del resumen no
se había aplicado a este script independiente. Se conserva el código y el
verification.json parcial en este commit; no hay cambio científico ni redes
nuevas. No se presenta ese archivo parcial como una verificación PASS.

Después de este commit, verify_v3 convertirá escalares NumPy sólo en la
serialización. El parcial se preservará byte por byte como
verification_v2_failed.json y el manifest utilizado como manifest_v2.csv.
Un manifest nuevo enumerará todos los archivos finales y verify_v3 escribirá
un verification.json completo nuevo. No se repite rho, redes ni estadísticas;
sólo se auditan hashes y fórmulas ya especificadas desde las mismas salidas.
Ningún umbral, predicción, veredicto previo ni instrumento se modifica.
