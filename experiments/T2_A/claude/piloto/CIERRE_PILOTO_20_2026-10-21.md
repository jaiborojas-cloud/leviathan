# Cierre del piloto de 20 visitas (update 25) — 2026-10-21

**Estado:** **piloto CERRADO** por decisión del responsable (2026-10-21 ≈23:04, sección 6). **No es una decisión de abrir la producción.** No asigna Y, no decide nada confirmatorio y no modifica E1 v9, el anexo v1.1 ni E2 v1. Las disposiciones son las de E2 v1, sección 4 bis.

## 1. Resultado
El piloto visitó en el update 25 las 20 trayectorias de los splits 8–11, en orden de cohorte, sin selección por X ni por facilidad (`PILOTO_20_APERTURA_2026-10-19.md`).

| disposición para T2-A0 | visitas | cuáles |
|---|---|---|
| INJECTIVE_AT_NOMINAL_RADIUS | 16 | 15 en la pasada del piloto, más split8_j8 por la reevaluación D4 (`ensayo_t4p_j8/`), con su pausa original conservada |
| GEOMETRIC_NONINJECTIVITY | 2 | split10_j17 (r_conj 0.0643969 < radio 0.0859956) y split8_j9 (r_conj 0.0774200 < 0.0801025) |
| INCONCLUSIVE | 2 | split8_j5: T5 certificado bajo protocolo numérico v1, no cumple E1 §5.1 (`certificacion_t5/`). split8_j7: sospecha de salida del dominio, T5 no certificado |

**Ningún Y está asignado.** Cada trayectoria necesita sus 10 visitas: una visita negativa no determina Y = 0, y un evento en el update 25 sí resuelve Y = 1 para su trayectoria. Por tanto, split10_j17 y split8_j9 tienen ya, por regla del prerregistro, un positivo confirmado. Su registro como Y = 1 queda para el análisis, no para este cierre.

## 2. Compuerta operacional del piloto
La regla es: más de 5 de 20 sin resolver, o 5 de 5 en un split. Quedan **2 de 20** sin resolver, y **2 de 5** en el split 8. **No se dispara.**

**Esto no resuelve la compuerta confirmatoria global de T2-A0.** Con j5 y j7 sin auditoría completa, T2-A0 ya es INCONCLUSIVE en su criterio 1, como prevé E2 (sección 2).

## 3. Lo aprendido para la operación (descriptivo, 20 visitas, un update, 4 splits)
| aspecto | medida en el piloto |
|---|---|
| Calibración completa | 16 visitas; mediana 47 s (36–63 s) |
| Visita completa sin evento | 15 visitas; mediana 89 s (52–143 s) |
| Visita con evento | split10_j17: 899 s de sesión en la pasada original, 563 s de integración, 3341 intentos, 8192 rayos; dio origen a los topes T1–T2 del anexo v1.1. split8_j9: 165 s de sesión tras la reanudación |
| Recuperación T4′ | 1 caso (j8): la calibración v1.0 se pausó y T4′ recuperó el radio. Visita en 268 s |
| Pausas de calibración por alarma de progreso | 4 de 20, todas en el split 8 (j5, j7, j8, j9) |
| Salidas del dominio (T5) | 1 certificada (numérica) y 1 sospecha, ambas en el split 8, por la misma arista del panel de validación (E2 §1.3) |
| Defectos de implementación corregidos | contabilidad del driver (3 defectos, anexo v1.1 §2.3), T1, T2 y la reanudación determinista de T4′; certificación T5 (3 defectos, cuatro corridas) |
| Riesgo operacional | el tope mide reloj de pared: la hibernación produce pausas falsas (anexo v1.1, D7). Hay que desactivarla en corridas largas |

**Lectura:** el split 8 concentró toda la dificultad (4 de 5 trayectorias problemáticas) y los otros tres splits pasaron sin incidencias (salvo el evento de j17). Con 4 splits no puede estimarse la frecuencia de T5 ni de pausas en la cohorte. La hipótesis H-split (E2 §7) es exploratoria.

## 4. Lo que rige para la producción
| documento o código | SHA-256 |
|---|---|
| Preregistro T2-A0 | `36b41002…7f72` |
| Enmienda E1 v9 | `824e19a1…72f9` |
| Anexo operativo E1 v1.1 (topes T1–T2, T4′) | `ec17ce3c…67fd` |
| Enmienda E2 v1 (E2-C; T5 solo como diagnóstico; sección 6 exploratoria) | `d5bc7565…f955` |
| Visita v1.1 + T4′ (`anexo_implementacion/`) | visita `b7352b23…ceee`, T4′ `c58eb54b…3360`, driver `e061617e…b7cd` |
| Protocolo T5 v1 y script v4 (`certificacion_t5/`) | `3d2e4882…dbd`, `9e0c12a2…0b7d` |
| Sección 6 (`../seccion6/`, PR #36) | script `d8fceff1…3200`, pruebas `839ee314…b9bde` |

## 5. Requisitos previos para abrir la producción
1. **Ejecutor para los updates 50–250.** `visita_completa_instrumentada_v11_t4p.py` **solo admite el update 25** (`assert a.step == 25`; entrena desde `checkpoint_005.pt`). Hace falta un ejecutor que encadene el entrenamiento hasta cada update programado sin tocar la geometría, la calibración ni las auditorías. Es código nuevo, así que debe:
   - **validarse**: reproducir bit a bit una visita del update 25 ya evaluada y verificar el encadenamiento de checkpoints frente a un entrenamiento directo;
   - **registrarse** con su hash antes de producir.
2. **Inventario fechado nuevo** (E1 §8), que distinga clasificadas, abiertas y no iniciadas al corte, con hash. Las 20 del piloto quedan con sus disposiciones.
3. **Orden de visitas fijado de antemano**, solo por la cohorte y el calendario de updates, **sin consultar X**. Hay que elegir y declarar si se avanza por trayectoria (las 10 visitas seguidas) o por update (todas las trayectorias en el 25, luego en el 50…).
4. **Disparador T5 en producción** (E2 3 bis): calibración v1.0 pausada y T4′ sin alcanzar A = 0.02, aplicado a todas las visitas por igual y después de verificar los hashes del protocolo y del script.
5. **Medición de tiempos y espacio en un lote pequeño** antes de comprometer un calendario. Quedan 7980 visitas. Con la mediana del piloto (≈ 2.3 min entre calibración y visita, sin eventos), un solo proceso tardaría del orden de 13 días, y las visitas con evento pesan mucho más (hasta 15 min). En paralelo, con los 24 núcleos del equipo, serían unos pocos días. **No está medido** para updates posteriores: la geometría cambia con el entrenamiento. Tampoco están medidos la memoria y el disco de los checkpoints con 16384 rayos (anexo v1.1, limitaciones).
6. **Suspensión desactivada** durante toda la producción, y reglas de reanudación del anexo (presupuesto adicional solo con decisión registrada).

## 6. Decisión del responsable [DECISIÓN]
- ¿Se da por cerrado el piloto con este documento?
- ¿Se autoriza preparar los requisitos de la sección 5 (ejecutor 50–250, inventario, orden, lote de medición)? Preparar no autoriza producir.
- La apertura de la producción se decidiría después, con el ejecutor validado y el lote medido.

**Decisión registrada (2026-10-21 ≈23:04):** el responsable **da por cerrado el piloto**. Para los requisitos de la sección 5 propone dividir la producción en **7 lotes**. La partición y el orden se fijan en el plan de producción, antes de producir.

## 7. Qué no se afirma
- No se afirma la frecuencia de eventos, de pausas ni de T5 en la cohorte.
- Tampoco que los tiempos del update 25 valgan para updates posteriores, ni que el split 8 sea representativo o anómalo (H-split es exploratoria).
- Ningún resultado del piloto es evidencia predictiva sobre X. Ninguna decisión documentada del piloto usó X, que sigue sellado en los basales.
