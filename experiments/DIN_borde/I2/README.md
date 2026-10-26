# DIN-I2 · rho_borde v2 con caras completas

Instrumento nuevo; no reemplaza ni modifica v1 congelado.
Entrega por separado rho_vert y rho_caras, con dirección/soporte ganador,
errores y restos explícitos. No son la distancia geodésica al borde.

- [Diseño congelado](DESIGN_FROZEN.md)
- [Demostración I1](THEORY.md)
- [Configuración](config.json)
- [Fuentes permitidas](freeze_manifest.csv)
- [Lectura previa](progress.md)

## API y significado

```python
import importlib.util
spec = importlib.util.spec_from_file_location("i2", "experiments/DIN_borde/I2/rho_borde_v2.py")
i2 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(i2)
r = i2.rho_borde_v2(M, f)  # M PSD n×n; f n×2, rango afín dos; P0=0
if r["status"] == "VALID_NUMERICAL_ESTIMATE":
    print(r["rho_vert"], r["rho_caras"], r["rho_caras_winner"])
```

`rho_vert` estima el ínfimo sobre conos abiertos de vértices geométricos.
`rho_caras` incorpora todas las normales de aristas expuestas completas.
La salida conserva caras, multiplicidades, rejillas, intentos, candidatos,
direcciones racionales, error quad y restos inicial/final hasta infinito.
El valor reportado suma integral y cotas de ambos restos; no incluye como
intervalo certificado el error estimado de quad ni el redondeo PSD.

`direction_rational` permite reproducir empates exactos. Su versión unitaria
float es para visualizar: redondearla puede convertir una cara en un vértice.
Membresía de cara racional EXACTA, tolerancia cero; umbral1e-10 sólo para alertar
sobre puntos casi colineales. Todos los índices exactamente colineales sobre
la arista se incluyen, así como posiciones duplicadas. No se fusionan casi empates.

Un ganador `vertex_limit` tiene `attained=false`: es normal más cola hacia un
vértice de su cono, no la longitud de la normal aislada. No prueba que ningún
rayo interior empate. Los intentos de búsqueda son finitos; no se certifican
ínfimos globales. Si se agota60s o4096 evaluaciones se devuelve
`INCONCLUSIVE_BUDGET` con candidatos parciales y sin valores finales.

La versión pública final es **r3**. [r1](versions/r1/rho_borde_v2.py) y
[r2](versions/r2/rho_borde_v2.py) se preservan bit a bit, junto con sus fallos.
Las enmiendas [r2](AMENDMENT_r2_FROZEN.md) y [r3](AMENDMENT_r3_FROZEN.md)
se comprometieron antes de sus correcciones. Cerca de rango uno, la búsqueda
rápida usa TV del modo dominante; la longitud final usa todos los modos y
quad dividido en ceros. Se registran cota residual y brackets de redondeo.

## Reproducción y archivos

Requiere los arrays propios archivados indicados por SHA en las etapas fuente;
no descarga datos ni lee Wine/T2/C1. En una copia de trabajo nueva con salidas
I2 ausentes, desde la raíz y con dependencias de requirements.txt:

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python experiments/DIN_borde/I2/scripts/run_r3.py --part controls
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python experiments/DIN_borde/I2/scripts/run_r3.py --part cohort
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 python experiments/DIN_borde/I2/scripts/summarize_r3.py
```

El ejecutor escribe exclusivamente archivos nuevos. **No ejecutar esos comandos
sobre las salidas archivadas**: no sobrescribe ni reanuda. r3 reutiliza los102
comparadores v1 de run_v1; para reproducción íntegra, generar primero run_v1 con
el código y commits históricos documentados, o conservar esos comparadores.
Los arrays están fuera de Git (`/workspace/work/din-i2-{v1,r2,r3}-arrays`);
cada JSON de estado registra su SHA. Sin ellos, siguen consultables medidas,
intentos, referencias y comparaciones archivadas; no se promete reproducibilidad
autónoma de los estados G1/D2b desde este PR sin sus arrays fuente.

- [Conclusión y tabla](CONCLUSION.md), [recomendación](RECOMENDACION.md).
- [Resultados finales](results/run_r3/summary.json), [tabla302](results/run_r3/states.csv).
- [Verificación](verification.json), [manifest](manifest.csv).
- Corridas conservadas: [r1](results/run_v1/summary.json), [r2](results/run_r2/summary.json).
