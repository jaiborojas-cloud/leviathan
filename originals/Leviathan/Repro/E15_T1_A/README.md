# Leviathan E15-T1-A

Mapa descriptivo de los 80 estados Wine originales. C1-A permanece INCONCLUSIVE; ninguna exclusión, sustitución, cambio de área o confirmación sobre supervivientes.

## Recuperación

1. Descargar todos los archivos de `/Leviathan/Repro/E15_T1_A/`, conservando la identidad/versiones de los archivos mutables.
2. Extraer cada `split*_j*_*.zip` en esta carpeta: cada uno contiene `states/<estado>/` con checkpoint, campo, radio heredado, reconstrucción, tareas, diagnósticos y `result.json` terminal. Verificar sus SHA con manifest.csv. Los archivos válidos no deben recalcularse.
3. Los insumos base son los ZIP C1 y A2 indicados en input_integrity.json. Colocarlos en `../inputs/Leviathan/Repro/` y extraer en `../unpacked/<nombre_sin_zip>/`. Verificar con verify_inputs.py antes de usar.
4. Instalar requirements.txt; torch CPU desde el índice oficial CPU. `source_core` proviene de A2 y está incluido en common_sources.zip. Extraerlo en esta carpeta. No cambiar geometry.py ni audit.py heredados.
5. Si faltan estados pendientes, setup.py recupera los inputs exactos, sin reentrenamiento. reconstruct.py comprueba M/f contra los checkpoints. No borra result.json. Comprobar protocolo_T1_A_frozen.sha256 antes de cálculos.
6. Ejecutar run_map.py para pendientes. La persistencia usa persist.py y los helpers vigentes de Library; una sesión nueva debe actualizar las identidades/versiones de archivos mutables mediante los metadatos actuales, no adivinarlas. Descargar helpers oficiales a ../helpers/. No copiar credenciales.
7. Estados con result.json pero sin ZIP persistido: primero empaquetar, subir y confirmar ese estado, luego actualizar progress.md; nunca recalcularlo sólo por un fallo de subida.
8. Ejecutar analyze_map.py sólo cuando estén disponibles los resultados que se quieran describir; su resumen indica n y compuerta. No presentar un parcial como cierre.

## Alcance

El radio nominal es el de C1 con área de cuadratura radial 0.02; en positivos no se considera prueba de disco embebido. Los no-eventos están censurados a ese radio. A_embed en positivos es una estimación de la familia inicialmente embebida, no un máximo global certificado; un cut locus anterior puede no detectarse. No se atribuye cota inferior rigurosa a r_inj por ausencia de eventos muestreados. La condición y el determinante se miden en marcos intrínsecos, usando Jacobi j/r sin singularidad polar.

Los diez casos A2 se importan con su matriz más fuerte (hasta16384, ambas fases, RK4 y Jacobi). Se identifica ese origen en cada resultado. Los otros70 reciben el screening congelado y sólo los candidatos pasan a niveles2/3. La resolución es escalonada: prevalencia observada bajo estas pruebas, no teorema global.

Las correlaciones que requieren C_A en dominios C1 inválidos quedan no estimables. Censura no se sustituye por máximos observados; no hay inferencia confirmatoria ni causal.
