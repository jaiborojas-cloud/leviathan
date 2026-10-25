# Fallo conservado · controles v1

Comando: `python scripts/run_v1.py --part controls` (BLAS1, sin pycache).
Código a105dbe; exit1 después de escribir controles completos.
Traza final: run_v1.py:132 → json.dumps(dict(status=...,checks=...)) →
TypeError: Object of type bool is not JSON serializable.
No hubo fallo del instrumento ni pérdida del archivo de controles.
