# Cribado de Q15 con modelos abiertos: cómo correrlo

El diseño está en [PREREGISTRO_CRIBADO_LLM.md](PREREGISTRO_CRIBADO_LLM.md). No se corre nada antes de que el preregistro esté congelado en git.

En PowerShell, ajusta la primera línea a la ruta de tu clon de `leviathan`:

```powershell
$R = "C:\Users\jaibo\Documents\GitHubRepos\leviathan\docs\research-notes\Q15\ejecucion\cribado_llm"
$D = "D:\RIPG_DATA\Q15_CRIBADO_LLM"
$L1 = "C:\Users\jaibo\Documents\Codex\2026-09-08\files-mentioned-by-the-user-fundationla\outputs\Q15_C_LOTE01_D01_SemanticScholar_2026-11-05.zip"
$L2 = "C:\Users\jaibo\.gemini\antigravity\brain\65cdfae4-b3b1-4d1c-a52b-e841159ff573\scratch\Q15_C_LOTE02_2026-11-05.zip"
$L3 = "C:\Users\jaibo\.gemini\antigravity\brain\65cdfae4-b3b1-4d1c-a52b-e841159ff573\scratch\Q15_C_LOTE03_2026-11-05.zip"
```

| Paso | Comando | Dónde |
|---|---|---|
| 1. Referencia y partición | `python -I "$R\cribado_llm.py" preparar --lote01 $L1 --lote02 $L2 --lote03 $L3 --datos $D` | tu PC (segundos) |
| 2. Confirmar `particion.json` en git | lo hace Claude con la salida del paso 1 | — |
| 3. VM | `& "$R\cribado_llm_azure.ps1" -Fase cuota`, luego `crear`, `preparar` e `instalar -OllamaVersion <tu versión>` | Azure |
| 4. Registrar versión, IDs y cuantización | pegar la salida de `instalar` en el PR | — |
| 5. Selección, 4 configuraciones | `& "$R\cribado_llm_azure.ps1" -Fase lanzar -Mitad seleccion`; revisar con `-Fase estado` | Azure (horas) |
| 6. Bajar y elegir | `-Fase bajar -Mitad seleccion`, luego `python -I "$R\cribado_llm.py" elegir --datos $D` | tu PC |
| 7. Validación, solo la elegida | `-Fase lanzar -Mitad validacion -Configs <elegida>`, luego `-Fase bajar -Mitad validacion` | Azure |
| 8. Veredicto | `python -I "$R\cribado_llm.py" validar --datos $D` | tu PC |
| 9. Apagar | `& "$R\cribado_llm_azure.ps1" -Fase borrar` | Azure |

Si Azure desaloja la VM, repite el `lanzar` del paso en curso con los mismos argumentos: continúa donde iba. Después de cada `bajar` puedes revisar una salida con `python -I "$R\cribado_llm.py" verificar --salida $D\salida_seleccion_C1.jsonl`.
