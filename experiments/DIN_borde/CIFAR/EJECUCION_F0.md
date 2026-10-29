# DIN-CIFAR F0 — ejecución en el equipo del responsable (Windows, PowerShell)

Requisitos: el clon `D:\leviathan-q13` (con `core.autocrlf=false`) actualizado a la rama que contiene este archivo, y el venv `D:\RIPG_DATA\venv_q13` (torch 2.9.1+cpu, numpy 2.3.5, scipy 1.17.0, scikit-learn 1.8.0). No hace falta instalar nada más.

```powershell
cd D:\leviathan-q13
git pull

# 1. Datos oficiales (unos 170 MB) y su MD5
New-Item -ItemType Directory -Force D:\RIPG_DATA\DIN_CIFAR_F0 | Out-Null
Invoke-WebRequest -Uri https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz -OutFile D:\RIPG_DATA\cifar-10-python.tar.gz
Get-FileHash -Algorithm MD5 D:\RIPG_DATA\cifar-10-python.tar.gz
# debe decir C58F30108F718F92721AF3B95E74349A

# 2. Compuerta de equivalencia (unos 20 s)
D:\RIPG_DATA\venv_q13\Scripts\python.exe experiments\DIN_borde\CIFAR\compuerta_equivalencia.py --salida D:\RIPG_DATA\DIN_CIFAR_F0\compuerta.json

# 3. F0: 20 splits x 5 inicializaciones (solo si el paso 2 dijo PASA)
D:\RIPG_DATA\venv_q13\Scripts\python.exe experiments\DIN_borde\CIFAR\f0_factibilidad.py --cifar D:\RIPG_DATA\cifar-10-python.tar.gz --compuerta D:\RIPG_DATA\DIN_CIFAR_F0\compuerta.json --salida D:\RIPG_DATA\DIN_CIFAR_F0\corrida --procesos 12
```

- **Duración esperada:** en el contenedor de desarrollo, una trayectoria tardó unos 6–8 s de CPU; con 12 procesos, F0 debería tardar pocos minutos. La cifra real es justamente lo que mide F0.
- **Reanudable:** si se interrumpe, se repite el mismo comando del paso 3. Las trayectorias ya escritas (incluidas las fallidas) se conservan y no se repiten.
- **Qué devolver:** lo que imprime la consola en los pasos 2 y 3, y los archivos `compuerta.json`, `corrida\resumen_F0.json` y `corrida\tabla_F0.csv`.
- **Qué NO contiene la salida:** X10, ρ ni M. F0 no mide la señal temprana.
