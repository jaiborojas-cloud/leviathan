#800 basales Wine — descarga y pruebas locales

## Descarga compacta
Extrae Leviathan_T2A_800_basales_compacto.zip. Incluye800 checkpoints de update5,800 iniciales update0, campos M,f exactos, JSON basales, comparadores, predictores sellados, protocolo y fuentes originales. No incluye los grandes arrays de rayos/Jacobi ni testigos de cuadratura: están completos en las16 partes originales.

Windows, desde la carpeta extraída:

    py -3.12 verificar.py
    py -3.12 -m pip install numpy==2.3.5
    py -3.12 inspeccionar.py split8_j5_true

El verificador sólo usa la biblioteca estándar y no deserializa los .pt. La inspección usa NumPy, lee M,f y muestra G(P0) y resultados guardados. No entrena ni calcula outcomes. Si usas un entorno existente con NumPy, no necesitas reinstalarlo.

## Descarga completa
Descarga las16 partes Leviathan_T2A_800_basales_parte_01.zip a _16.zip. Cada parte es un ZIP independiente con50 auditorías originales, sin recomprimir ni alterar sus ZIP internos. Extrae todas en la misma carpeta que el compacto: aparece baselines_originales/ con800 ZIP.

    py -3.12 verificar.py --completo

Los800 ZIP originales incluyen los datos completos de rayos, fases, Jacobi y comparadores. Para trabajar con su árbol original, extrae cada ZIP interior en una carpeta de trabajo separada; los nombres incluyen trajectory/split/init para evitar colisiones. Nunca extraer sobre una copia oficial de producción.

## Integridad y alcance
original_zip_manifest.csv registra SHA256 de cada ZIP y checkpoint basal. compact_manifest.json verifica cada archivo compacto. DESCARGAS_SHA256.txt verifica los paquetes exteriores. La exportación preserva los valores; no vuelve a calcular resultados.
Estos800 basales son160 splits8..167×5 inicializaciones, todos true, update5. No son el panel80 de T1 ni800 outcomes futuros. Se incluyen checkpoints0/5, no visitas25..250. El campo outcome_status del manifest de cohorte es el de su snapshot basal; no describe el progreso futuro actual.

## Reproducción
M,f bastan para evaluar la geometría exacta con las fuentes proporcionadas. Los .pt requieren PyTorch para cargarse; las fuentes originales de entrenamiento/reconstrucción están en sources/. Se conserva su contenido histórico: no ejecutar funciones legacy de entrenamiento como si sustituyeran el protocolo T2-A0. No se ha probado aquí una nueva instalación completa de PyTorch en Windows. La inspección suministrada evita esa dependencia.
Crear resultados en resultados_locales/ y documentar código, versiones y hashes. Las pruebas son exploratorias/instrumentales. No sobrescribir predictors_locked.csv, baseline_cutoff_frozen.json, checkpoints ni tablas selladas. No utilizar estos datos para ajustar y confirmar retrospectivamente un nuevo predictor.
