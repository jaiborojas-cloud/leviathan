# Plan de producción T2-A — v1 (CONGELADO, 2026-10-22)

**Estado:** congelado el 2026-10-22 ≈08:13 America/Mexico_City por decisión del responsable («sí, tal cual»), que adopta las cinco decisiones del borrador v0 (SHA-256 `9bb2cf3873b5064d0bcc0c277a57b4f3611ba59326dc279d346ce099d8880203`, que se conserva). Incorpora la revisión de otra sesión: puntos 2–9 adoptados, punto 1 no adoptado (ver §6). **Autoriza producir una vez cumplidos los pendientes de §7** (lanzador con prueba en seco registrada). No modifica el preregistro, E1 v9, el anexo v1.1 ni E2 v1. No asigna Y.

## 1. Marco vigente
| documento o código | SHA-256 | papel |
|---|---|---|
| Preregistro T2-A0 | `36b41002…7f72` | cohorte, visitas, Y, análisis |
| Enmienda E1 v9 | `824e19a1…72f9` | disposiciones, pausa operativa |
| Anexo operativo E1 v1.1 | `ec17ce3c…67fd` | topes T1–T2, T4′ |
| Enmienda E2 v1 | `d5bc7565…f955` | E2-C; T5 solo diagnóstico; sección 6 exploratoria bloqueada |
| Ejecutor de producción v12 (`produccion/`) | `2381fbcc…3347` | visita de cualquier update programado; validado el 2026-10-22 |
| Dependencias congeladas | driver `e061617e…b7cd`, T4′ `c58eb54b…3360` | — |
| Protocolo T5 v1 y script v4 | `3d2e4882…dbd`, `9e0c12a2…0b7d` | diagnóstico T5 (ver 7.3) |
| Sección 6 | script `d8fceff1…3200` | solo tras completar la cohorte |

## 2. Partición en 7 lotes (fijada por número de split, sin consultar X)
**Paso de updates: 25.** El lote 0 visita 50…250 (9 updates); el update 25 de sus 20 trayectorias ya está en el piloto. Los lotes 1–6 visitan 25…250 (10 updates). Cada split tiene 5 trayectorias (inicializaciones j = 5(S−7) … 5(S−7)+4).

| lote | splits | updates | trayectorias | visitas |
|---|---|---|---|---|
| 0 | 8–11 (piloto) | 50, 75, …, 250 | 20 | 180 |
| 1 | 12–37 | 25, 50, …, 250 | 130 | 1300 |
| 2 | 38–63 | ídem | 130 | 1300 |
| 3 | 64–89 | ídem | 130 | 1300 |
| 4 | 90–115 | ídem | 130 | 1300 |
| 5 | 116–141 | ídem | 130 | 1300 |
| 6 | 142–167 | ídem | 130 | 1300 |
| | | | **800** | **7980** |

- Las 20 trayectorias del lote 0 se visitan **todas**, incluidas split8_j5 y split8_j7, que siguen INCONCLUSIVE en el update 25 y pueden tener evento después.
- **No se omiten visitas posteriores a un positivo** (decisión del 2026-10-22). Y = 1 ya está resuelto por regla, pero completar las 10 visitas evita una regla de parada dependiente del desenlace y conserva el registro completo.
- **Orden dentro de un lote:** la cola se construye **leyendo `cohort_manifest.csv`** de los basales (no generando nombres) y es la lista de (trayectoria, update) ordenada por split, inicialización y update ascendentes. Los procesos en paralelo toman el siguiente elemento de la cola. Como el modelo de cada update se entrena de forma independiente desde el update 5, el orden no afecta a ningún resultado (validación B del ejecutor).

## 3. Ejecución de cada visita
- **Raíz de producción:** `D:\RIPG_DATA\T2_A\produccion`.
- **Comando:** ejecutor v12 con `--case <trayectoria> --step <k> --work D:\RIPG_DATA\T2_A\produccion\lote_<n>\<trayectoria>\u<k>`. Usa los topes por defecto (anexo v1.1), sin `--extra-budget` ni `--forzar-t4prima`.
- **Estados posibles:**
  - `VISIT_EVALUATED` (`VISITA_COMPLETA.json`);
  - `PAUSED_PENDING_REVIEW` (`REVISION_PENDIENTE.json`);
  - `ERROR_DE_EJECUCION`.
- Una visita pausada o con error **no se reintenta automáticamente**. La reanudación sigue las reglas del anexo (mismo directorio, presupuesto adicional solo con decisión registrada). Una pausa por reloj de pared con el equipo suspendido se repite en un directorio nuevo (anexo v1.1, 2.5).
- **Reanudación del lote:** un lote detenido se reanuda desde su último punto de control, con las mismas semillas y sin repetir visitas ya cerradas (con `VISITA_COMPLETA.json`).
- **Repeticiones:** una visita que debe repetirse en un directorio nuevo (pausa por reloj de pared con el equipo suspendido, anexo v1.1 §2.5) usa `u<k>_r2`, `u<k>_r3`, etc. Es **autoritativa** la de número más alto que tenga `VISITA_COMPLETA.json`. Las anteriores se conservan, y el manifiesto las registra todas, marcando cuál cuenta. La omisión al reanudar usa la misma regla.
- **Checkpoint parcial:** el ejecutor reutiliza `checkpoint.pt` y `state.npz` si existen, sin escritura atómica. Si un proceso muere escribiéndolos, la visita reanudada puede terminar en `ERROR_DE_EJECUCION`; el informe operacional lo señala como causa posible. Se repite en `u<k>_r<n>`.

## 4. Paralelismo y recursos
- **Procesos** (decisión del 2026-10-22): el lote 0 usa **8 procesos** para medir la memoria por visita, sobre todo en visitas con refinamiento de 8192–16384 rayos, que no se han medido. Para los lotes 1–6, el número de procesos se fija tras el lote 0, sin pasar de 20 de los 24 núcleos. El ejecutor fija un hilo por proceso, así que los procesos no compiten por hilos.
- **Antes de cada visita:** el lanzador comprueba que haya al menos **50 GB libres en D**. Si no los hay, se detiene limpiamente.
- **Suspensión e hibernación** desactivadas durante toda la producción (`powercfg`).

## 5. Disco
1. Durante el lote, todo se escribe en D (SSD).
2. Al cerrar el lote, los `ode_checkpoints` de las visitas `VISIT_EVALUATED` se **copian** a `E:\RIPG\T2_A\checkpoints_produccion\lote_<n>\…`. La copia se **verifica archivo por archivo con SHA-256 releyendo desde E**, y solo entonces se borran de D.
3. Las visitas pausadas, con error o con diagnóstico T5 pendiente **conservan sus checkpoints en D** hasta resolverse.
4. Los resultados (`states/`, JSON, logs) y los manifiestos se quedan en D. Además se hace una **segunda copia** de los resultados en `E:\RIPG\T2_A\resultados_produccion\lote_<n>\` al cerrar cada lote (unos 10 GB por lote; decisión del 2026-10-22).
5. E es un disco antiguo (unas 65 600 horas, 28 y 319 errores de lectura acumulados): solo guarda copias regenerables o redundantes.

## 6. Entre lotes: solo revisión operacional
- **Informe operacional por lote** (decisión del 2026-10-22): visitas por estado (evaluada, pausada, error), tiempos, memoria, espacio libre en D y en E y defectos de ejecución. **No incluye clasificaciones** (INJECTIVE o NONINJECTIVITY) ni Y, y **no se consulta X**. Las clasificaciones se agregan al terminar los 7 lotes.
- **Nota sobre T5 (punto 1 de la revisión, no adoptado):** una visita que dispara T5 termina en `PAUSED_PENDING_REVIEW`, así que el informe puede dejar inferir pausas compatibles con T5. No se oculta ni se reetiqueta como evaluada, porque eso falsearía el informe y la regla de revisión. No afecta al veredicto de T2-A0, que ya es INCONCLUSIVE por el criterio 1 (split8_j5 y split8_j7, E2 v1), ni al cegamiento de X frente a Y.
- **Regla de parada operativa** (decisión del 2026-10-22), declarada de antemano: no es científica y no se ajusta a resultados.
  - El lote se **detiene de inmediato** ante 20 `ERROR_DE_EJECUCION` consecutivos, **contados por orden de terminación** (fallo de infraestructura).
  - **No se abre el lote siguiente sin revisión** si más del 10 % de las visitas del lote termina en `PAUSED_PENDING_REVIEW` o `ERROR_DE_EJECUCION` después de las reanudaciones permitidas por el anexo v1.1. El denominador son todas las visitas del lote. Una visita `VISIT_EVALUATED` cuenta como registro válido cualquiera que sea su clasificación, incluida INCONCLUSIVE.
- **Manifiesto por lote:** SHA-256 de cada `VISITA_COMPLETA.json`, `result.json` y `nominal.json`, con commit propio en el repo. Contiene hashes, no desenlaces. Los resultados quedan en local hasta el análisis.

## 7. Pendientes antes del lote 0
1. **Congelar este plan**, con las decisiones marcadas resueltas.
2. **Lanzador por lotes**: cola, procesos, omisión de visitas completas, comprobación de disco, regla de parada, informe operacional y manifiesto. Debe pasar una **prueba en seco** sin visitar, que compruebe: rutas y hashes del ejecutor y sus dependencias; `cohort_manifest.csv` con 800 filas, splits 8–167 con 5 inicializaciones cada uno; y conteos por lote 180 y 1300 (el lote 0 sin el update 25). Después se registra su hash.
3. **Adaptador T5 para producción.** El script T5 v4 solo acepta, fuera del modo prueba, los estados de j5, j7 y j8 escritos en el código, y su validez depende de los controles V1 y V2 con j8. Para aplicar T5 a visitas de producción (E2 3 bis) hace falta una versión que tome el `state.npz` de la visita con su hash e incluya a j8 como control en cada corrida, validada y registrada. **No bloquea el lote 0**: hasta tenerla, una visita de producción que dispare T5 queda como «sospecha, diagnóstico no resuelto» y conserva sus checkpoints.
4. **Inventario fechado** (E1 §8): lo genera el lanzador al iniciar el lote 0, con hash.
5. ~~Fusionar los PR abiertos del marco: #36, #37 y #38.~~ **Hecho** (fusionados el 2026-10-22).

## 8. Calendario estimado (grueso; lo corrige el lote 0)
- **Medida del update 25:** unos 2.3 min por visita sin evento (calibración más auditoría) y hasta unos 15 min con evento. No está medido para updates posteriores.
- **Lote 0:** 180 visitas con 8 procesos, entre 1 y 2 horas.
- **Lote grande:** 1300 visitas con unos 20 procesos, entre 3 y 5 horas, más el traslado de checkpoints a E (20–35 min).
- **Total:** del orden de 1 a 2 días de cómputo, repartidos según tu disponibilidad.

## 9. Qué no se afirma
- No se afirma la frecuencia de eventos, pausas ni T5 en updates posteriores, ni que los tiempos del update 25 valgan para ellos.
- Ningún informe entre lotes es un análisis de resultados.
- La producción no cambia la previsión de E2 de que T2-A0 sea INCONCLUSIVE si aparece cualquier T5.
