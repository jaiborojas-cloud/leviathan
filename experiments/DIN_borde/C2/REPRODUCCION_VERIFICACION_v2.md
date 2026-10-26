# Nota de reproducción: verificador operacional v2

El [procedimiento v1](REPRODUCCION_COHORTE_v1.md) se preserva. Su último comando,
verify_v1.py, reproduce el fallo de rutas registrado. Para completar la integridad
usar **verify_v2.py** en su lugar, en una ejecución nueva sin salidas v2 existentes:

```bash
python experiments/DIN_borde/C2/cohorte_scripts/verify_v2.py
```

La [enmienda](ENMIENDA_VERIFICACION_v2_CONGELADA.md) se comprometió antes del código.
V2 escribe `cohorte/verification.json` y `cohorte/external_manifest.csv`, conservando
las mismas comprobaciones. No modifica el generador, el publicador ni el analista.
No repetir entrenamiento, mediciones ni publicación para verificar esta entrega.
Las escrituras son exclusivas; preservar cada versión y fallo. No ejecutar el
análisis confirmatorio como parte de la verificación operacional.
