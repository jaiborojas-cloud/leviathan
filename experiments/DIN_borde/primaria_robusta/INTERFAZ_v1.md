# Interfaz genérica del borrador A1

[Contrato científico](DISENO_ANALISTA_BORRADOR_v1.md). **No usar sobre cohortes reales hasta auditoría y congelación del primer diseño nuevo.** No existe adaptación automática para tablas de C1/C2/Q13/CIFAR; no se reanalizan esas etapas.

## Plan

JSON con exactamente `protocolo`, `estado`, `tipo_datos`, `n_clases` y `universo`. Ejemplo de estructura (no es una cohorte ni un tamaño propuesto):

```json
{
  "protocolo": "DIN-PRIMARIA-ROBUSTA-v1",
  "estado": "BORRADOR",
  "tipo_datos": "PRUEBA_SINTETICA",
  "n_clases": 3,
  "universo": [{"trajectory": "ejemplo_s0_k0", "split": 0}]
}
```

El plan real de un futuro experimento debe enumerar **todos** los IDs, incluidos los que después fallen. Orden del universo = orden de los cálculos, las salidas y los desempates. Cada split es un entero no negativo representable en int64; no se acepta bool. La capa genérica no fija N, cinco inicios, dataset, productor, dosis o arquitectura. Las fracciones de calidad siempre se comparan contra el universo planificado, no contra supervivientes.

CSV UTF-8, una fila por ID, encabezado exacto:

```text
trajectory,split,estado_10,estado_final,error,X10,rho_caras_10,rho_caras_250,acc_train_final
```

Estados MEDIDA/FALLIDA/INVALID_RHO; vacío cuenta como falta de medida. Se conservarán filas fallidas aunque no tengan valores numéricos. X10 finita; rho positivas y finitas; precisión final en [0, 1]. **.5 se admite; menos de .5 es NO_APRENDIO y falta**, sin reescribir el estado original. Las visitas finales son u250 para la primaria adoptada. No se confunde X con probabilidad ni se introducen campos L/Y en el CSV: se calculan los logs tras validar.

## Núcleo y salida

- `analizar(rows, plan, B=5000, gate_reasons=())`: selección, calidad, primaria recortada, influencia y veredicto. B menor se usa solo en pruebas declaradas.
- `primaria(split, X, L, Y, B=5000, recorte=True)`: API numérico sin selección de cohortes. El modo sin recorte es una comprobación de equivalencia, no otra primaria ni una opción de CLI.
- `punto`, `preparar`, `ajustar`: funciones separadas para auditar matrices de cada bloque, pérdidas y residuos.
- `influencia` y `decidir`: contribuciones y regla final. Una omisión degenerada conserva error y bloquea PASS.

Salida: `RESULTADO_ROBUSTA_v1.json`, creación exclusiva. Incluye faltantes y todos sus motivos por ID, NO_APRENDIO, splits, elegibles no usados, primaria con p/pendiente/SSE, límites e IDs de recorte por bloque, residuos/g_i por trayectoria, fracción e ID máximo, D_sin_max y error propio, condiciones original y de influencia por separado, hashes y alcance. Los cuatro veredictos son PASS, NO_ROBUSTO, NOT_MET e INCONCLUSIVE. ABORTA (código 3) indica entrada estructural o de E/S inválida, sin resultado científico.

La fracción no se trunca a [0, 1], y es null si la suma de mejoras no es positiva. No se inventa un umbral de porcentaje dominante. El centrado por split y la prueba de permutación conservan su definición; un PASS mejora a esta base concreta, sin certificar causalidad, tamaño nominal universal o ausencia de cualquier artefacto.

## CLI y vínculos

Argumentos requeridos:

```text
--tabla --tabla-sha --plan --plan-sha --resumen --compuerta --compuerta-sha --productor-sha --out
```

`RESUMEN` debe contener los mismos `tabla_sha256`, `plan_sha256`, `compuerta_sha256` y `productor_sha256` recibidos desde su publicación previa. La compuerta genérica debe tener `PASA: true` y `script_sha256` idéntico al SHA del productor. El diseño de experimento debe especificar qué verifica esa compuerta y archivar su evidencia; esta interfaz no reemplaza una compuerta de geometría.

Los SHA de los archivos de entrada se verifican antes de leer las filas. Los campos extra en un resumen pueden documentar instrumentos y costes. La CLI mantiene 5.000 permutaciones y no tiene banderas para cambiar umbral, semillas, grado, recorte o usar otro veredicto. La configuración de esta entrega está fijada por SHA y **bloquea COHORTE_NUEVA aun con un plan marcado CONGELADO** mientras la implementación esté en BORRADOR. La congelación posterior requiere auditoría y publicación explícita, no cambiar un estado a mano.

Salida existente, directorio donde se esperaba archivo, JSON no finito o con claves repetidas: nunca se sobrescriben ni normalizan silenciosamente. Las pruebas se ejecutan con [requisitos](requirements.txt), Python 3.12 y un hilo BLAS. No hay dependencias de red, torch ni datos externos para el analista.
