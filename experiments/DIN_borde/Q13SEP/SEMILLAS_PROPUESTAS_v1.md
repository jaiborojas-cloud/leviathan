# Q13-SEP · semillas propuestas y cotejo de registros

2026-11-02. **Borrador; no se generan datos ni se autoriza una cohorte.** El [diseño](../DISENO_DIN_Q13SEP_BORRADOR_v1.md) y la configuración proponen estos intervalos cerrados. La repetición entre brazos/T de un mismo (fase,s,k) es intencional para el pareado; entre fases no se reutiliza ninguna semilla.

| Fase/uso | Split | Inicialización | Lote |
|---|---|---|---|
| Calibración, 10 splits × 5 | 71.000.000–71.000.009 | 71.100.000–71.100.049 | 71.200.000–71.200.049 |
| Validación, 20 splits × 5 | 72.000.000–72.000.019 | 72.100.000–72.100.099 | 72.200.000–72.200.099 |
| Reserva futura de señal, hasta 10.000 splits × 5, **sin N elegido** | 73.000.000–73.009.999 | 73.100.000–73.149.999 | 73.200.000–73.249.999 |

Fórmulas: base_split + s, base_init + 5s + k y base_lote + 5s + k. Las fases del piloto usan **330 entradas escalares únicas**; incluyendo la reserva propuesta son 110.330. Ninguna se ha pasado aquí a un PRNG. La prueba corta consume el prefijo de calibración (s0, k0/1/2), no crea una reserva adicional ni repite esos entrenamientos.

## Registros que se evitan

Se evita conservadoramente la banda escalar 0..30.000.000, que contiene las semillas/intervalos históricos revisados: G2/G3, C2, las calibraciones y cohortes Q13, Q13-DR (811000/821000/831000), calibración M2 (901000/902000/903000), cohorte M2 (911000/921000/931000), F0/F0b/F0c (1.010.000..1.090.000), F1 (1.100.000/1.110.000/1.120.000), **reserva CIFAR-F2 1.200.000/1.300.000/1.400.000** con su capacidad completa, y semillas de métodos/auditorías, E16 y fixtures A1 basadas en 2026xxxx. Se incluye el PR #132 aunque aún no esté fusionado: 20.261.102 y el intervalo 20.261.200..20.261.219 no se usan.

Los números anteriores son bases y ejemplos de registros, no el alcance completo del cotejo. La reserva CIFAR-F2 permanece sin usar; no se cambia su estado. Los nuevos intervalos están por encima de esa banda, no se intersectan entre sí y se cotejaron además contra todos los literales numéricos de las fuentes revisadas, no solo contra esta lista abreviada.

## Evidencia estática y límites

Base revisada: main `259fac77c21190c0753fd7087062d1578e58ef0d`, más fuentes del PR #132 en `1faf1b75`; decisión PR #133 en `168352e8`. Se inspeccionaron fuentes `.py`, protocolos `.md` y JSON con nombres de configuración/plan. Se excluyeron tablas/estados/checkpoints, carpetas de resultados y datos: no se ejecutó ningún generador o código de entrenamiento. El [listado con SHA](fuentes/semillas_archivos_revisados.csv) y las [líneas de registros](fuentes/semillas_lineas_main.csv) permiten auditar el alcance. El [resumen](fuentes/semillas_verificacion_estatica.json) diferencia esta comprobación de una corrida.

Método: literales AST de Python sin ejecutar módulos, valores de JSON y tokens numéricos de comentarios/protocolos (incluidos separadores de miles); cotejo con los 110.330 escalares propuestos o reservados, y comprobación de los intervalos/fórmulas. **Sin colisiones literales detectadas.** Los esquemas SeedSequence con listas se revisan como entradas estructuradas; no se confunden con el número formado concatenando sus componentes ni se reutilizan aquí.

Esto documenta disjunción frente a los registros visibles y las fórmulas citadas. No es un certificado de independencia matemática de PRNG ni una evaluación formal de todo programa dinámico. Antes de congelar/publicar el plan de ejecución se repetirá el cotejo con los registros actualizados, incluidos otros PR que se hayan incorporado; no se hará una selección automática de nuevas semillas si apareciera un conflicto. Cualquier conflicto se resolverá en una revisión documental antes de medir.
