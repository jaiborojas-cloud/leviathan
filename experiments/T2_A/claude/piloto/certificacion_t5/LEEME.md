# Certificación de T5 (j5, j7; control j8)

- Protocolo: [`PROTOCOLO_certificacion_T5_v1_CONGELADO.md`](PROTOCOLO_certificacion_T5_v1_CONGELADO.md) (SHA-256 `3d2e4882…dbd`). Borrador original sin cambios: `PROTOCOLO_certificacion_T5_BORRADOR_v0.md`.
- Script: `certificar_t5.py`. Su SHA-256 se registra en `MANIFIESTO_scripts_certificacion_T5.sha256` **antes** de correrlo sobre j5, j7 y j8 (sección 9).
- Pruebas previas (no cuentan): `PRUEBAS_previas_certificar_t5.md`.

## Comando (PowerShell, equipo del responsable)
Antes, desactivar la suspensión (el muestreo de K en mpmath puede tardar):
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
```
Descargar `certificar_t5.py` del repositorio y verificar su hash contra el manifiesto (`AFC23C71…B268`). Comprobar también que el venv tiene mpmath:
```powershell
New-Item -ItemType Directory -Force "D:\RIPG_DATA\T2_A\expediente\certificacion_t5" | Out-Null
Invoke-WebRequest "https://raw.githubusercontent.com/jaiborojas-cloud/leviathan/claude/t2a-certificacion-t5/experiments/T2_A/claude/piloto/certificacion_t5/certificar_t5.py" -OutFile "D:\RIPG_DATA\T2_A\expediente\certificacion_t5\certificar_t5.py"
Get-FileHash "D:\RIPG_DATA\T2_A\expediente\certificacion_t5\certificar_t5.py" -Algorithm SHA256
& "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe" -I -c "import mpmath, shapely; print(mpmath.__version__)"
```
Correr (lee los tres estados de `estados_u25`, verifica sus hashes y escribe solo en la carpeta de salida nueva):
```powershell
& "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe" -I "D:\RIPG_DATA\T2_A\expediente\certificacion_t5\certificar_t5.py" --out "D:\RIPG_DATA\T2_A\expediente\certificacion_t5\salida_2026-10-21" *>&1 | Tee-Object -FilePath "D:\RIPG_DATA\T2_A\expediente\certificacion_t5\salida_2026-10-21.log"
```
Requiere `mpmath` en el venv. Si falta, se instala con el `pip` del mismo venv. Si se interrumpe, se relanza el mismo comando: los casos con `resultado.json` completo no se recalculan.

## Salida
- `salida_…/RESUMEN.json`: V1 (los tres casos), V2 (j8), validez del procedimiento y estado por caso (`T5_CERTIFICADA` o `T5_NO_CERTIFICADA` con razones), con U.
- `salida_…/<caso>/resultado.json`, `rayos.csv`, `traza_haz.csv`, `log.txt`.

## Lectura (fijada en el protocolo, secciones 4.5 y 5)
- Un caso queda certificado solo si se cumplen todas estas condiciones:
  - (i) C1–C6;
  - (ii) δ_disc ≤ 10⁻⁵;
  - V3 y V4;
  - muestreo de K convergido;
  - U ≤ 0.0195;
  - **además**, V1 vale en j5, j7 y j8, y V2 vale en j8.
- Si algo falla, el caso queda «T5 no certificado» con la razón. Nada se reajusta después.
- Ningún resultado cambia el estado de j5 ni de j7 (siguen `PAUSED_PENDING_REVIEW` hasta E2) ni asigna Y.
