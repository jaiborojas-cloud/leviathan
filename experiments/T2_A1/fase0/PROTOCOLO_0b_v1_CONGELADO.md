# T2-A1 fase 0b — protocolo de cobertura, v1 CONGELADO (2026-10-23)

**Estado:** **CONGELADO** el 2026-10-23 a las 15:32 (hora de México) por aprobación del responsable («si»). Contenido idéntico a `PROTOCOLO_0b_BORRADOR_v0.md`, que se conserva. Scripts registrados antes de correr: `correr_visitas_0b.py` (ver `MANIFIESTO_0b_2026-10-23.sha256`) e `instrumento_D.py` v2. Marco: diseño v2 (sección 5) y protocolo D v1 congelado (sección 5). Instrumento **congelado** en `instrumento_D.py` v2 (`254ebd83…9663`; `RESULTADO_0a_2026-10-23.md`). **0b solo mide: no ajusta el instrumento.**

## 1. Qué se mide
1. **Cobertura primaria (compuerta):** fracción de visitas con D = ? en las 60 visitas primarias: updates 50, 150 y 250 de los splits 8–11 (20 trayectorias). **Pasa si D = ? en ≤ 3 de 60.**
2. Se reportan también:
   - la fracción de trayectorias con Y = ? de esas 20;
   - el desglose por vía (A, B, C) y por razón de D = ?;
   - U y U₂ de cada visita que llega al paso 3;
   - tiempo y disco por visita.
3. **D0-1 (secundario):** las 4 pausas en auditoría del lote 0 en updates primarios se repiten una vez con `--extra-budget`, en carpetas nuevas. Se mide si se resuelven. **No cambian su D primario**, que es «?» por el paso 2. La regla para la fase confirmatoria se decide en 0c.
4. **Cobertura secundaria (opcional, descriptiva):** las 128 visitas del lote 0 en todos sus updates.

X sigue cerrado. Los desenlaces D de esta muestra de desarrollo se ven: está previsto y se declara.

## 2. Visitas
| grupo | visitas | origen |
|---|---|---|
| primarias existentes | 43: splits 8–10 × updates 50/150/250, salvo split10_j19 u150 y u250 (no iniciadas en el lote 0). Por estado del ejecutor: 16 evaluadas, 23 pausas de calibración (→ paso 3) y 4 pausas en auditoría | `D:\RIPG_DATA\T2_A\produccion\lote_0\` (solo lectura) |
| primarias nuevas | 17: split10_j19 u150 y u250; split11_j20…j24 × u50/u150/u250 | ejecutor v12 sin cambios, `D:\RIPG_DATA\T2_A1\fase0b\visitas\` |
| repeticiones D0-1 | 4: split10_j16 u50, split10_j18 u50, split9_j13 u50 y u150, con `--extra-budget` | `D:\RIPG_DATA\T2_A1\fase0b\repeticiones\<tray>\u<k>_r1\` |

Las visitas nuevas y las repeticiones las corre `correr_visitas_0b.py` (cola fija en el código). Este script verifica el hash del ejecutor (`2381fbcc…3347`) y de cada `checkpoint_005` contra `metadata/cohort_manifest.csv`, exige ≥ 50 GB libres antes de cada visita y no escribe en el lote 0.

## 3. Pasos y comandos (PowerShell, equipo del responsable)
```
$PY = "D:\RIPG_DATA\T2_A\cribado_borde\venv_torch\Scripts\python.exe"
$R  = "C:\Users\jaibo\Documents\GitHubRepos\leviathan\experiments\T2_A1\fase0"
```
1. **Liberar disco** (D tiene ≈ 27 GB libres): archivar el lote 0. Copia a `E:\RIPG\T2_A\` los `ode_checkpoints` de las visitas evaluadas (≈ 73 GB), los verifica releyendo desde E y solo entonces los borra de D. Las visitas pausadas conservan sus checkpoints en D.
   `& $PY -I D:\RIPG_DATA\T2_A\expediente\produccion\lanzar_lote.py --lote 0 --archivar`
2. **Visitas nuevas y repeticiones:** primero en seco, luego en serio (8 procesos; estimación 1–3 h):
   `& $PY -I "$R\correr_visitas_0b.py" --out D:\RIPG_DATA\T2_A1\fase0b --seco`
   `& $PY -I "$R\correr_visitas_0b.py" --out D:\RIPG_DATA\T2_A1\fase0b --procesos 8`
3. **Instrumento D** (cada corrida incluye los controles j5 y j8, ≈ 15 min, si hay casos para el paso 3):
   - I1, lote 0 primario (23 casos al paso 3; ≈ 2–4 h):
     `& $PY -I "$R\instrumento_D.py" --lote D:\RIPG_DATA\T2_A\produccion\lote_0 --updates 50 150 250 --out D:\RIPG_DATA\T2_A1\fase0b\D_lote0`
   - I2, visitas nuevas:
     `& $PY -I "$R\instrumento_D.py" --lote D:\RIPG_DATA\T2_A1\fase0b\visitas --updates 50 150 250 --out D:\RIPG_DATA\T2_A1\fase0b\D_nuevas`
   - I3, repeticiones D0-1:
     `& $PY -I "$R\instrumento_D.py" --lote D:\RIPG_DATA\T2_A1\fase0b\repeticiones --updates 50 150 --out D:\RIPG_DATA\T2_A1\fase0b\D_repeticiones`
   - I4 (opcional, secundario): `--updates 50 75 100 125 150 175 200 225 250` sobre el lote 0, con la misma `--out` que I1, para reutilizar las cotas ya calculadas.

## 4. Combinación y lectura
- **Conjunto primario** = las 43 filas de I1 en updates 50/150/250, sin split10_j19 u150 ni u250, más las 17 filas de I2 de la cola nueva. Las filas NO_INICIADA que el instrumento lista para combinaciones fuera de la cola (por ejemplo, split10_j19 u50 en la carpeta nueva) se descartan, porque esa visita ya está en el lote 0.
- **Validez:** si los controles de una corrida fallan, ninguno de sus casos del paso 3 cuenta: quedan en D = ?, como dice el protocolo D.
- **Compuerta:** D = ? en ≤ 3 de 60 → **pasa** y se sigue a 0c. Si D = ? en > 3 → **falla**. Por el diseño v2, el instrumento no se reajusta con estos datos: se decide entre una versión nueva documentada del instrumento (que repetiría 0a y 0b) y abandonar el diseño. Esa decisión se toma por escrito, con el desglose de razones a la vista.
- Informe: `RESULTADO_0b_<fecha>.md`, con tablas por vía y razón, U y U₂, Y por trayectoria (desarrollo), tiempos y disco. Copias pequeñas (CSV, RESUMEN, D.json) al repo con manifiesto.

## 5. Expectativa declarada antes de correr
Con factores dobles, ni j5 certifica (U₂ = 0.020153). En el lote 0, las visitas primarias de split 8 están todas pausadas en calibración, así que **lo previsible es que la compuerta falle**. Se corre igual: es la medición acordada y el dato que decide el siguiente paso.
