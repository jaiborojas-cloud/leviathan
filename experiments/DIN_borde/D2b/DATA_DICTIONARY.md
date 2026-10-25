# Diccionario y reproducción

`results/run_v2/*_*.json`: un retorno por red, sin sobrescritura.
`metrics`: probabilidades de etiqueta, errores normalizados por max(1,norma
referencia), concentración, espectro, rango y ridge; no son trayectorias.
`native`: retorno intacto rho_borde defaults1440/800. `native_fidelity`: acuerdo
con integral independiente AL MISMO ÁNGULO, no certificado de mínimo.
`coordinate_lower_ratio/upper_ratio`: cotas divididas por sqrt(M00)/27.
`array`: ruta externa y SHA; no contiene ni deriva de estados T2.
`warnings`: todos los avisos capturados. `log_rho=null` en geometría nula.
No se imputan logs ni se reemplazan valores no finitos; estos se conservan
como cadenas explícitas si aparecen en un retorno.

`networks_v3.csv`:86 filas, incluidos casos aligned. `summary_v3.json`:
resumen válido. `summary.json`: JSON PARCIAL del postproceso fallido, excluido
explícitamente de entradas. `statistic_panels.json`: resultados de controles
estadísticos; correlaciones indefinidas como null, conteos explícitos.
`M0_error=null` significa identidad sin ridge no resuelta bajo la condición
previa de rango/condicionamiento, no error ni exclusión del caso completo.

Fuentes permitidas por SHA en freeze_manifest; algoritmo de core/rho/geometry
ejecutado desde sus bytes sin parchear. No ejecutar entry points de esos
scripts, que tienen herramientas de carga fuera del alcance sintético.

Para repetir en OTRO checkout/entorno limpio con Python3.12 y requirements:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 \
  python experiments/DIN_borde/D2b/scripts/run_v2.py
python experiments/DIN_borde/D2b/scripts/summarize_v3.py
```

Las rutas de salida deben estar libres: los scripts rechazan sobrescritura.
Aquí torch se instaló fuera de Git, por lo que se añadió
`PYTHONPATH=/workspace/work/din-d2b-deps`. Las rutas de arrays se fijan en
config y launcher. Reejecutar en este checkout exige una nueva versión
documentada, no borrar los resultados para hacer espacio.

La verificación no ejecuta redes ni rho: lee resultados propios, los arrays
externos preservados y fuentes autorizadas. manifest.csv cubre todos los
archivos de la etapa salvo él mismo y verification.json (evita ciclos de SHA).
El verificador informa su propio SHA y verifica el manifest completo.
