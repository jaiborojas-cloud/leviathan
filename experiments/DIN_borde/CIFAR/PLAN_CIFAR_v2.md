# DIN-CIFAR — plan v2: enmienda tras F0 (2026-10-29)

**Estado:** enmienda al [plan v1](PLAN_CIFAR_v1.md), que se conserva. Todo lo que este documento no cambia sigue como en el v1. La aprobó el responsable el 2026-10-29 («si vamos con la enmienda y 0.003»).

## 1. Motivo
Lo que mostró F0 ([resultado](resultado_F0/RESULTADO_F0_2026-10-28.md)):
- el modelo está **subentrenado**: la precisión mediana de entrenamiento es de 0.75 en u250;
- c sigue subiendo hasta u250 sin estabilizarse, con una mediana de 0.288, por debajo del umbral descriptivo de 0.30.

Así, el «estado final» u250 es todavía un punto a media trayectoria.

**Desviación declarada:** el plan v1 solo permitía ajustes si fallaban la precisión o el costo, y los dos cumplieron, aunque la precisión del panel por un pelo. Esta enmienda se aparta de esa regla por decisión del responsable, con el motivo de arriba.

**No hay contaminación:** F0 no midió X10, ρ ni D, y sus semillas no se reutilizan en ninguna otra fase.

## 2. Cambio
- **Adam con lr = 0.003** (antes 0.001). Se mantienen los 250 updates y las visitas 5, 10, 30 y 250, como en Wine y G3, para que X10 signifique lo mismo en todas las familias.
- Nada más cambia: ni las clases, ni f, ni la red, ni el lote, ni el split, ni el preprocesamiento, ni el instrumento.

## 3. F0b: verificación antes de F1
**Criterios fijados antes de correr:**
- **Muestra:** 20 splits × 5 inicializaciones con semillas nuevas: split 1 040 000 + s, inicialización 1 050 000 + 5s + k y lote 1 060 000 + 5s + k.
- **Qué se mide:** lo mismo que en F0, sin X10, ρ ni D.
- **Criterios descriptivos para pasar a F1 con lr = 0.003:**
  - mediana de la precisión de entrenamiento en u250 ≥ 0.90 (nuevo);
  - mediana de la precisión del panel ≥ 0.55;
  - mediana de c250 en [0.30, 0.97];
  - CPU ≤ 60 s por trayectoria;
  - compuerta PASA y reproducción exacta.
- **Si F0b no cumple algún criterio de precisión** (entrenamiento o panel), se pasa al respaldo declarado aquí:
  - **F0c:** lr = 0.001 y 500 updates, con visitas 5, 10, 30 y 500 (u500 es el estado final);
  - semillas 1 070 000 / 1 080 000 / 1 090 000, mismos criterios;
  - se implementa solo si hace falta.
- **Si solo falla c**, decide el responsable **sin más ajustes de entrenamiento**: c no se usa para afinar.
- **Ninguna otra corrida exploratoria** de configuración entre F0b y F1.

## 4. Corrección del productor
La memoria máxima en Windows salía en 0.0 porque la llamada al sistema fallaba sin avisar (tipos de ctypes sin declarar).
- **Ahora** se usa `K32GetProcessMemoryInfo` con los tipos declarados, y si la medición falla se registra `None`, nunca 0.
- **En F0** la memoria queda **sin medir**.
- La corrección **no se probó en Windows** desde el contenedor; F0b la pondrá a prueba.

El código de F0 sigue reproduciendo F0: en la prueba de desarrollo, la trayectoria (s0, k0) dio parámetros finales y c idénticos a la versión anterior.

## 5. F1 y F2
Sin cambios respecto al v1, salvo que usan la configuración que resulte de F0b o F0c. Los diseña el otro agente.
