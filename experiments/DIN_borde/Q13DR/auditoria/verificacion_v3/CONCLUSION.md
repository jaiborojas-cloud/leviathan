# Conclusión — verificación independiente v3

**Se confirman las correcciones N01–N05 en sus casos reproducibles, sin regresiones en la matriz F01–F06. No se identificaron nuevos bloqueos en los diffs revisados.** Desde este alcance técnico no queda pendiente una corrección del analista; la decisión de congelar corresponde al responsable.

Referencia exclusiva: commit `a8da9046cf0b5e4ba64ef24e03999591f899c4e2`, analista SHA `cc5524a781b16ac08ef25b86427f8f36bb43c6425d8cf17753c4ae5a9b534b6a`. El diseño científico sigue siendo el borrador v2; no se modifica ni se congela aquí.

- [N01–N05](MATRIZ_N01_N05.md): punto y réplicas constantes dan INCONCLUSIVE; rango común invertido=.3 y margen=.006; eps enorme/entradas ilegibles abortan limpiamente; se guardan todos los fallos de bootstrap.
- [F01–F06](MATRIZ_F01_F06.md):51 casos reejecutados, incluyendo los Aborta esperados por IDs inválidos;27 controles de dominio y cuatro de Spearman pasan.
- [Diffs](REVISION_DIFFS.md):87 planes,720 permutaciones de c distintas y ocho casos adicionales de entrada inválida pasan. Diez comparaciones v2/v3 no degeneradas son exactamente iguales en las estadísticas y decisiones.

En los300 draws del caso original de L constante se conservan116 fallos; en el nuevo caso de c constante se conservan271. Ambas listas de índices coinciden exactamente con la traza independiente, sin sustituciones o redibujos. Son casos adversariales sintéticos, no tasas de error del procedimiento.

No se repite Monte Carlo porque el cálculo válido no cambió y las comparaciones son exactas. Esta verificación no añade evidencia de tamaño/potencia ni implica una certificación de ausencia de fallos. No se entrenó ni se usaron datos Wine, C2 o Q13 reales; no se ejecutaron las pruebas del autor que acceden a su fixture C2.

Solo se añaden archivos en `auditoria/verificacion_v3/`. Los resultados v1/v2, el diseño y el analista permanecen intactos. Fuentes, hashes, casos y salidas se conservan con [verificación](verification.json) y [manifest](manifest.csv). PR separado en borrador, sin fusionar.
