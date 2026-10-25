# Datos, referencias y alcance de los veredictos

`inputs.json` contiene los12 paneles sintéticos y210 recetas de matrices.
No son estados de entrenamiento. Cada matriz float normalizada está en un
.npy externo identificado por SHA en arrays.csv; los rasgos y parámetros
permiten reproducirla. Las familias gaussian/near_collinear se relacionan por
una transformación afín invertible exacta en potencias de2. No son cohortes
independientes; no hay pruebas estadísticas ni p-valores.

`states.csv` conserva una fila por caso, incluso si falla o queda inconcluso:

- `native_rho`: escalar devuelto por rho_borde.py original. `native_status`
  distingue retorno, error, valor no finito y presupuesto. El resultado bruto,
  sus diagnósticos, theta, tiempo y avisos están en raw_and_references.json.
- `reference_exact`: mínimo demostrado para los modelos con fórmula cerrada.
  Vacío significa UNKNOWN; no cero. `reference_lower/upper` son las cotas
  para casos sin mínimo conocido, con una curva superior fijada antes de medir.
- `reference_native_direction`: longitud completa de la dirección devuelta,
  por TV exacta en los modelos simples o integración MP80 independiente.
  No se convierte un casi empate en una cara exacta.
- `minimum_check`: compara con valor exacto o intervalo de cotas. Un
  PASS_BRACKET_ONLY no certifica que el mínimo global sea exacto.
- `witness_check`: contrasta la longitud del ángulo publicado. INCONCLUSIVE
  conserva una referencia cuyo contraste GL16/32 no cumple la tolerancia;
  su valor aproximado no se usa como evidencia firme de fallo o éxito.
- `Q5`: FAIL tiene prioridad ante una contradicción estable o error del
  instrumento. Un caso puede tener mínimo FAIL y longitud INCONCLUSIVE;
  por ello los conteos marginales no suman los estados inconclusos globales.
- `matrix_control`: traza/PSD a tolerancia y comparación del CUADRADO de la
  norma con J original/fórmula factorizada. Se comparan cuadrados porque la
  raíz de cancelaciones cerca de cero tiene precisión absoluta diferente.
- `global_reference_control`: comprueba las curvas algebraicas que alcanzan
  los mínimos demostrados, o la coherencia de las cotas conocidas.
- `log_native_over_floor` y `log_native_over_reference` no se calculan para
  valores no positivos. Son diferencias de logaritmos, no déficits absolutos.

`raw_and_references.json` conserva MP_value, raíces, cortes, resto de cola,
convergencia y retornos nativos. Los nan/inf se preservan como texto explícito,
nunca se imputan como valores. La llamada adicional4M verifica homogeneidad
sin normalizar4M de vuelta; no añade un estado a los210 de traza1.

`by_form.csv` separa fallos de mínimo y de longitud. `failures.csv` enlaza los
33 fallos sin sustituirlos. `affine_pairs_descriptive.csv` es diagnóstico
secundario de cartas, no cambia los criterios congelados. `theoretical_scalars.json`
compara sólo el mínimo D1 redondeado y el ejemplo δ=5e-5 con las fórmulas.
La orientación de ningún M entrenado se leyó ni se estimó desde esos escalares.

## Arrays y versiones

Los .npy externos de matrices y contribuciones de referencias MP conservan
forma y SHA; la ruta está en resources.json. Los arrays de contribuciones
contienen[inicio,fin,integral_GL16,integral_GL32] como diagnóstico float;
las sumas y normas se evaluaron a80 dígitos y su valor MP se conserva en JSON.
No se guardan .npz ni checkpoints. No se inventan los arrays internos que la
función pública congelada no devuelve. stdout/stderr están en execution.log.
El verificador opera desde archivos y álgebra, sin volver a llamar a rho_borde
ni reintegrar curvas. Fallos del instrumento bajo prueba quedan en Q5, sin
modificarlo; un defecto de la implementación independiente exigiría enmienda.
