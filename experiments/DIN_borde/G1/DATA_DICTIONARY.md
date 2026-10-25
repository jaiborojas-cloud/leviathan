# Datos, estados y salidas G1

Único dataset cargado: sklearn.load_iris, clase0/1/2,150×4. Se guardan datos
crudos, etiquetas, IDs de train/pool/panel y scaler en NPZ propios externos.
No se carga Wine ni se abre una tabla/checkpoint/estado de T2 o DIN-C1.
Leer informes publicados como contexto no se convierte en reutilización
de sus datos. El import intacto de core define load_wine pero no lo ejecuta.

## Estado y procedencia

`results/run_v1/states/<familia>_s<split>_k<init>_u<update>.json` conserva un
registro por ID previsto, incluso si no se pudo medir. MEASURED significa
retorno obtenido, no calidad aprobada. ERROR_MATRIX y UNMEASURED preservan
motivo/fallo/censura sin imputar números. Se registran avisos de rho y de
cálculo de matrices, tiempo, SHA de NPZ y del checkpoint propio.

`metrics.c`: maxdiag/tr; `q`: fracción Frobenius fuera de diagonal.
`collapsed`: M válida, c≥.8 y q≤.05. `M_valid`: reglas numéricas congeladas,
incluido h0 SPD resuelto. Los autovectores son de M, no una Hessiana de camino.
`k_star/k_hard`: posiciones dentro del panel; `*_id`: índice del ejemplo Iris
original. No se comparan posiciones27 y60 como si fueran el mismo ejemplo.
`py_star` puede redondear a1; `log1m_star` y X se obtienen desde logits.

`rank_F_1e10` es rango numérico con corte relativo1e-10; no es un certificado
de rango del Jacobiano reducido. `gamma_minF` usa el menor autovalor resuelto.
`diagonal_odds_relative_error` compara con n diag(odds); no fuerza a ser0.
`leverage_star` mide Mkk/(n odds_k); valores próximos a1 indican ese régimen,
no una nueva ley empírica por sí solos. `universal_bound_min_eigenvalue`
es auditoría flotante de D−M; no aritmética de intervalos.

## ρ y cuerda

`rho` conserva todos los campos nativos de720/400, sin editar su función.
`rho_valid` aplica criterios previos; no certifica mínimo angular global.
`audit`1440/800 sólo aparece en los120 IDs preseleccionados. Se conservan
errores y no se sustituyen valores de análisis por el auditado. La cuerda
incluye conjuntos completos de índices en caras, con tolerancia declarada.

Un aviso no desaparece del archivo aunque se cumplan las tolerancias.
Valores no finitos se escriben como cadenas explícitas nan/inf; no se
transforman en logs ni se imputan. Un dato no identificable se informa null.
`rho_min_gl` y rho refinada no son necesariamente el mismo valor: las
limitaciones de búsqueda angular del instrumento ya están documentadas.

## Resúmenes y reproducción

`by_update.csv`: cobertura y descriptivos por visita/familia.
`hypotheses.csv`: veredictos, cobertura y magnitudes H1–H5.
`events.csv`: tiempos observados por intervalos, con censura derecha explícita.
`audits.csv`:120 contrastes, incluidos fallidos. Los tiempos de H4 no se
interpolan entre visitas ni se fijan a250 para eventos ausentes.

`summary.json` y los tres resúmenes por familia conservan reglas y resultados;
`states.csv` da la tabla de todos los estados sin reemplazar los JSON nativos.
`trajectories/`:200 entrenamientos físicos; R27/P60 son dos mediciones de
los mismos100, no200 entrenamientos independientes.

`external_manifest.csv`: todos los NPZ fuera de Git, con SHA/tamaño; incluye
pesos y momentos Adam de cada visita, RNG de lotes, matrices y espectros.
`manifest.csv`: archivos de G1 excepto sí mismo y verification.json para
evitar ciclos. El verificador informa su propio SHA. Integridad PASS no
obliga a que una hipótesis APAREZCA.

Para repetir en un checkout independiente del commit de código28c6395,
Python3.12 y requirements, con salidas y ruta externa libres:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python experiments/DIN_borde/G1/scripts/run_v1.py
```

En este entorno torch se instaló fuera de Git, por lo que se añadió
PYTHONPATH=/workspace/work/din-d2b-deps. No borrar resultados existentes para
repetir: se necesita una nueva versión/ruta. Postproceso no entrena ni repite
rho. Verificación reconstruye3 matrices desde nuestros pesos y datos Iris,
sin optimización ni datos ajenos.
