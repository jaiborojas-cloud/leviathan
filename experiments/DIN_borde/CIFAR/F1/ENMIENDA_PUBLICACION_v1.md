# Enmienda de publicación, sin cambios científicos

2026-10-29. Las54 pruebas sintéticas terminaron PASS, sin corrección del analista ni repetición de una medida. Se detectó que un identificador de prueba, generado a partir de un dict de parámetros, produce un nombre de archivo con `:` que no es portable a Windows. Sus valores y resultado son correctos; el problema es el nombre del artefacto local de prueba.

Antes de implementar el exportador se fija: conservar los archivos crudos originales en `pruebas/results_v1/` local, sin sobrescribirlos; publicar copias byte a byte con nombres seguros y sufijo de SHA en `pruebas/publicacion_v1/`, con un índice que conserva el identificador original y el SHA. Summary y manifest externo conservan nombres simples. No modificar el script/analista ya probados para presentar esa corrida como otra versión.

Esto no modifica el diseño científico, resultados ni reglas, ni exige repetir las pruebas. El mapeo es de empaquetado, no una selección de casos. Todos los casos, incluidos identificadores no portables y excepciones esperadas, quedan conservados y versionados mediante sus copias por SHA. Los fixtures CSV y salidas CLI siguen fuera de Git. No se publica ningún nombre de archivo incompatible con Windows.
