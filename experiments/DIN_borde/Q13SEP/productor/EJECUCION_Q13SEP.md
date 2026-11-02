# DIN-Q13-SEP v2 — ejecución en el equipo del responsable (PowerShell)

Requisitos:
- **Fusionados el PR #134** (diseño congelado) **y el PR de este productor.**
- El venv `D:\RIPG_DATA\venv_q13`, con las versiones fijadas.
- **No hace falta descargar datos:** las gaussianas se generan con las semillas congeladas.

**SHA publicados antes de medir:** [PUBLICACION_PRODUCTOR_v1.sha256](PUBLICACION_PRODUCTOR_v1.sha256).

## 1. Prueba corta (15 entrenamientos de calibración: s0, k0–2, los cinco brazos)

```powershell
cd D:\leviathan-q13
git checkout main
git pull
New-Item -ItemType Directory -Force D:\RIPG_DATA\DIN_Q13SEP | Out-Null
D:\RIPG_DATA\venv_q13\Scripts\python.exe -I experiments\DIN_borde\Q13SEP\productor\productor_q13sep.py --fase cal --salida D:\RIPG_DATA\DIN_Q13SEP\cal --prueba-corta --procesos 12
```

- Imprime los estados, los tiempos (t_train, t_M y latencia), la memoria y la **proyección de las dos fases**. Si la proyección pasa de 90 min, se detiene y decide el responsable.
- También corre los **controles oficiales**: tres reconstrucciones con error 0 y el contraste de rutas T1. Si fallan, la corrida es INVALIDA.
- Estos 15 entrenamientos pertenecen al universo de calibración: el paso 2 no los repite.

## 2. Calibración completa (250 entrenamientos), en la misma carpeta

```powershell
D:\RIPG_DATA\venv_q13\Scripts\python.exe -I experiments\DIN_borde\Q13SEP\productor\productor_q13sep.py --fase cal --salida D:\RIPG_DATA\DIN_Q13SEP\cal --procesos 12
D:\RIPG_DATA\venv_q13\Scripts\python.exe -I experiments\DIN_borde\Q13SEP\productor\analisis_q13sep.py --fase cal --corrida D:\RIPG_DATA\DIN_Q13SEP\cal --salida D:\RIPG_DATA\DIN_Q13SEP\decision_cal
```

El analista escribe `DOSIS_Y_REGLAS_Q13SEP_v2.json` e imprime su SHA. **Ese archivo se publica en el repo (PR) antes de entrenar la validación.** Si la decisión es NO_IDENTIFICABLE, aquí se detiene la vía.

## 3. Validación (200 entrenamientos), solo con DOSIS_APTA publicada

```powershell
D:\RIPG_DATA\venv_q13\Scripts\python.exe -I experiments\DIN_borde\Q13SEP\productor\productor_q13sep.py --fase val --salida D:\RIPG_DATA\DIN_Q13SEP\val --dosis <ruta en el repo>\DOSIS_Y_REGLAS_Q13SEP_v2.json --dosis-sha <SHA publicado> --procesos 12
D:\RIPG_DATA\venv_q13\Scripts\python.exe -I experiments\DIN_borde\Q13SEP\productor\analisis_q13sep.py --fase val --corrida D:\RIPG_DATA\DIN_Q13SEP\val --salida D:\RIPG_DATA\DIN_Q13SEP\veredicto --dosis <misma ruta> --dosis-sha <SHA publicado>
```

Todo es **reanudable**: si se corta, se repite el mismo comando. Lo escrito no se sobrescribe, y una tarea a medias se conserva en `interrumpidas\` y se rehace.
