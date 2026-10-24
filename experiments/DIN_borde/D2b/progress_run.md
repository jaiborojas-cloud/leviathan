# Avance de ejecución y versiones

1. Diseño85fffb4: fuentes leídas, hipótesis,86 estados y controles congelados.
2. Se escribió run_v1 y manifest; diff --check rechazó CRLF. El siguiente
   comando arrancó pese al fallo: incidencia de orquestación propia. Se
   detuvo conservando4 redes completas y paneles estadísticos. run_v1 inválida.
3. Código original guardado73cb83a; enmienda923dbba antes de corregir;
   launcher con guarda1c7a1bf exige que el código esté comprometido.
4. run_v2:86 redes, todas completas. Dos procesos,258.432845s. No se observó
   fallo de las identidades primarias. Fuentes científicas sin cambios.
5. summarize_v2 falló serializando numpy.bool_; se conserva JSON parcial.
   Enmienda7e5f020 antes de corregir; summarize_v3 comprometido885cc40.
   Misma tabla de entrada, sin repetir mediciones. Todos9 controles PASS.
6. Se redactó recomendación al responsable, sin editar el borrador DIN-C1.
   Lema adicional de contracción universal: demostración y auditoría secundaria,
   sin añadir una regla primaria ni cambiar tolerancias.
7. Verificación final desde archivos: SHA, permisos, orden de commits,
   probabilidades, cotas Fisher, fórmulas de pares a60 dígitos y alcance.
   verify_v2 falló al serializar un booleano NumPy de la auditoría adicional;
   se conserva verification_v2_failed.json. Enmienda v4 en3cba70c antes
   de corregir; verify_v3 convierte escalares sólo en la salida JSON.
   manifest_v2.csv conserva el inventario anterior. No se repiten mediciones.

Lecturas empíricas limitadas a documentos escalares publicados D1/D3/D4/D5/D6.
No se cargó dato, tabla ni estado T2; no se llamó load_split/load_wine/train_branch.
Los arrays son de nuestra construcción y se conservan fuera del repositorio.
No se excluyen casos ni se estiman frecuencias empíricas desde estas redes.
