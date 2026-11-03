# Q15 v3.1 — ejecutor PC v2.1: rutas Windows corregidas

Esta versión sustituye operacionalmente al [ejecutor v2](../ejecutor_pc_v2/README.md), conservado sin cambios con su manifiesto. Corrige el fallo comunicado por el responsable: **87/91 en Windows**, con cuatro fallos por diferencias entre rutas persistidas con `/` y `\`. Los 91/91 anteriores eran controles en Linux; no demostraban la igualdad de identificadores nativa de Windows.

- **Código, requisitos y suite publicados:** `505e4239e7343bc73dffb838351da56d39039703`.
- **SHA-256 del ejecutor:** `6f05b419dbc3d055a3e155c4bfcf9346ed61ba6d938dad8828e9bfbd9157147b`.
- **SHA-256 de la suite:** `e1782c6da81f33fe68d2e89c24f8d90a9565a98c5131cdb7b6d1d659b03dfeca`.
- **Resultado local:** [98/98 PASS, solo simulaciones](pruebas_simuladas/run_01.json), incluidas siete regresiones que fuerzan `PureWindowsPath`.

Seguir el [procedimiento PowerShell nuevo](PROCEDIMIENTO_WINDOWS.md), con otro clon y carpetas `Q15_v31_1_CONTROLES`, `Q15_v31_1_PREPARACION` y `Q15_v31_1_RED`. Primero **paso 2**; solo si pasa, **paso 3**. Conservar el informe fallido original en `D:\RIPG_DATA\Q15_v31_CONTROLES\pruebas_001.json` y `.log`. No se han leído ni modificado esos archivos desde este entorno; [la incidencia](INCIDENCIA_WINDOWS_v2_REPORTADA.json) distingue el resultado comunicado de la evidencia local y deja sus SHA desconocidos.

## Corrección

Las tres conversiones de `relative_to(...)` del ejecutor —trabajo reanudado, evidencia HTTP reutilizada y dependencia de catálogo— usan ahora `.as_posix()`. La inspección completa encontró además `str(Path(evidence).parent)` en el directorio de rechazos; también usa `.as_posix()`. No quedan conversiones `str(...relative_to(...))` ni `str(Path(...).parent)` en el ejecutor v2.1.

Los identificadores persistidos son POSIX, aunque los archivos se abran con `pathlib` en Windows. Las rutas del sistema mostradas solo en diagnósticos pueden mantener su separador nativo. La versión cambia a `EJECUTOR_PC_v2.1_Q15_v3.1`, de modo que no se reutiliza una salida anterior bajo identidad distinta.

Son cuatro cambios de representación y la etiqueta de versión. No cambian endpoints, expresiones, filtro, orden, N/K, tokens, reintentos ni reglas de cobertura. La [enmienda S2](../ENMIENDA_S2_OPERATIVA_v3_1.md) publicada en `7e668f81…` sigue intacta. Tampoco se reescriben los estados o informes anteriores.

## Validación

La suite conserva las 91 pruebas y agrega siete con E/S temporal real del host y representación relativa `PureWindowsPath`: igualdad de evidencia al reutilizar HTTP; recuperación de HTTP 200 no JSON, Atom y objeto bulk inválido; dependencia de trabajo reutilizado; dependencia de catálogo; y directorio de rechazo forzando `Path` Windows. Se inspeccionan los identificadores serializados para excluir `\`.

El [control negativo](pruebas_simuladas/EVALUACION_CONTROL_NEGATIVO.json) confirma que la v2 anterior no pasa ninguna de esas siete pruebas: un FAIL y seis ERROR al forzar separadores Windows sobre E/S Linux. Esa reproducción léxica no es una nueva ejecución nativa de Windows ni pretende reproducir su tipo exacto de excepción. Se conservan el [JSON original del control](pruebas_simuladas/control_negativo_v2.json) y su log. Su indicador `REVISAR` esperaba siete FAIL y no contaba ERROR; la evaluación adicional explica las siete regresiones sin alterar ese registro.

La preparación local construyó 294 unidades sin HTTP. Los manifiestos anteriores y el nuevo se comprobaron; [verification.json](verification.json) registra SHA, entorno y alcance. No se ejecutaron búsquedas bibliográficas ni experimentos. La prueba nativa de 98 casos en el PC queda pendiente del responsable.
