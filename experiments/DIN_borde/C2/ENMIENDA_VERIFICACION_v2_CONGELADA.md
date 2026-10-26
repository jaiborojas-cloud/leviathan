# DIN-C2: enmienda operacional del verificador v2 — CONGELADA antes del código

## Defecto demostrado y preservado

La primera ejecución de verify_v1.py terminó con PermissionError al leer
`C2/state_records_manifest.csv`: la guarda sólo autoriza los directorios propios
`cohorte/` y `cohorte_scripts/`. También escribiría sus salidas en la raíz C2,
fuera de esos directorios. [Log íntegro](cohorte/fallos_v1/verification_console.log)
y [registro del fallo](cohorte/fallos_v1/FAILURE.json). Se preserva verify_v1.py intacto.

## Cambio fijado ANTES de implementar

Crear verify_v2.py como copia del v1 con tres cambios exclusivamente de IO:
1. Cargar las filas del manifiesto de estados propio antes de instalar la guarda;
   después verificar los mismos SHA sobre los mismos registros, bajo la guarda.
2. Escribir el manifiesto de arrays como `cohorte/external_manifest.csv`.
3. Escribir el resultado como `cohorte/verification.json`.

El log de v2 tendrá ruta nueva. Se conserva el fallo v1. No se debilita la guarda
ni se cambian controles, tolerancias, fuentes, semillas, estados, mediciones, valores
de tabla, resumen, diseño o analistas. No se vuelve a entrenar ni a medir rho.
No se ejecuta analisis_C2.py ni se calculan asociaciones. La enmienda corrige la
verificación de integridad, sin efecto sobre el protocolo confirmatorio congelado.

El archivo completo de la cohorte ya está comprometido en bccb549; la tabla tiene
SHA `afd4783c2505251a1456aed9b3f8583d8f98c186908d2611be7f3dedd64eca19`.
El plan conserva SHA `ad320ac9fdf75a80801f2c44a529de467f1c852ed90cdd3d7181a61151b6aed8`.
ESTE commit precede al primer código v2 y a su ejecución. No autoriza cambios científicos.
