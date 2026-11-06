#!/bin/bash
# generado por cribado_llm_azure.ps1 (lanzar seleccion); limite 2026-11-07T23:18:08Z
set -o pipefail
LIMITE=1794093488
LOG=~/q15/etiquetar.log
restante=$(( LIMITE - $(date +%s) ))
if [ "$restante" -le 60 ]; then echo "FIN seleccion codigo=SIN_TIEMPO" >> "$LOG"; exit 0; fi
timeout "$restante" bash -c 'python3 -I ~/q15/cribado_llm.py etiquetar --entrada ~/q15/datos/entrada_seleccion.jsonl --config C1 --datos ~/q15/datos --hasta 2026-11-07T23:18:08Z && python3 -I ~/q15/cribado_llm.py etiquetar --entrada ~/q15/datos/entrada_seleccion.jsonl --config C2 --datos ~/q15/datos --hasta 2026-11-07T23:18:08Z' 2>&1 | tee -a "$LOG"
rc=$?
echo "FIN seleccion codigo=$rc" >> "$LOG"
exit $rc
