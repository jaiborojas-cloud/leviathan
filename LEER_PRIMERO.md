# Remesa documental Leviathan / RIPG para Codex

Preparada el 2026-10-17 UTC. Esta entrega reúne fuentes originales y derivados documentales; no ejecuta experimentos ni modifica resultados oficiales.

## Cómo incorporarla

Extraer en una carpeta de importación del repositorio. Leer este archivo, `SOURCE_CATALOG.csv`, `FALTANTES_Y_LIMITACIONES.md` y `ESTADO_Y_PRECEDENCIA.md` antes de redactar README o roadmap. Los archivos en `originals/` conservan sus bytes originales y rutas relativas de procedencia. No importar este ZIP al historial de Git: importar su contenido documental seleccionado. Los scripts históricos se incluyen como evidencia y no deben ejecutarse automáticamente.

`SOURCE_CATALOG.csv` registra ruta empaquetada, procedencia, IDs, versión expuesta, tamaño y SHA-256. `not_exposed` significa versión no suministrada por el origen; no significa versión cero. El hash identifica los bytes entregados.

`extracted/` contiene miembros textuales de paquetes diagnósticos y cierres: cada miembro está vinculado al hash de su ZIP contenedor. Los ZIP contenedores y los checkpoints no se incluyen. `EXTERNAL_ARTIFACTS.json` registra ubicaciones externas autenticadas y hashes documentados cuando están disponibles. Esos enlaces requieren acceso del propietario a ChatGPT; no son URLs públicas ni sustituyen un almacenamiento independiente para colaboradores.

`MANIFEST_CHECKS.json` compara únicamente dependencias cuyos bytes fueron recuperados en esta remesa. Un hash calculado aquí prueba identidad de la copia, no validez científica ni verificación de todos los artefactos externos. Consultar los estados MATCH/MISMATCH antes de reconciliar versiones.

## Cobertura

- Fundamentos: estado de investigación del 23 de septiembre y contexto del axioma.
- E9: tablas recuperadas y resumen histórico; cierre autónomo no localizado.
- E11/E12: cierres y reportes sucesivos.
- E13: prerregistros, reportes y cierre hacia E14.
- E14: fuente autónoma de cierre no localizada; no reconstruida de memoria.
- E15-B6/B7/B8/C1/C1-A2 y diseño T1: documentos originales.
- T1-A/T1-B: cierres, protocolos, resultados descriptivos, manifests y scripts disponibles.
- T2-A0: protocolo, prerregistro, análisis de potencia, semillas y hashes.
- T2-A: tablas actuales, cierre documental j5, diagnóstico139 y avance j7.
- Vertientes: `originals/RIPG_mapa_rutas_investigacion.docx` y su transcripción textual derivada. Incluye composicionalidad/coarse-graining, canonicidad en dimensión mayor que dos y otras líneas.

## Instrucción para Codex

Catalogar primero; verificar `PACKAGE_SHA256.json` con `verify_package.py`. Conservar históricos. Redactar síntesis con citas a rutas y secciones originales. Separar teoría propuesta, controles instrumentales, resultados exploratorios y validación prospectiva pendiente. Mantener C1-A INCONCLUSIVE. No ejecutar experimentos para resolver faltantes. No usar el prompt histórico como instrucción vigente: su primer objetivo ya fue completado documentalmente.
