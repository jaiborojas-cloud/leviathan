# Cierre de T2-A0 — BORRADOR v0 (2026-10-22)

**Estado:** propuesta para el responsable. **No congelado.** Se congela (SHA-256, manifiesto, commit) solo con su aprobación explícita. No asigna Y, no abre X, no reetiqueta ninguna visita.

## 1. Propuesta
Cerrar T2-A0 con veredicto confirmatorio **INCONCLUSIVE por limitación del instrumento de seguimiento**, sin completar la cohorte. Ninguna evaluación primaria (precision@10 %, criterios 1–6) se calcula. La sección 6 de E1 (sensibilidad por completaciones binarias) **no se aplica**: está definida sobre la cohorte completa.

## 2. Por qué
1. **El veredicto ya está determinado.** Por E2 v1 (`d5bc7565…f955`), una sola visita T5 basta para que la compuerta global sea INCONCLUSIVE. En el piloto, split8_j5/u25 tiene T5 certificado (numérico v1) y split8_j7/u25 sospecha de T5 no certificada. Completar la cohorte no puede cambiar el veredicto.
2. **Cobertura.** En el lote 0 quedó pausado el 59 % de las visitas terminadas (76 de 128), agrupadas por split: split 8, 45 de 45; split 9, 3 de 45; split 10, 28 de 38. Con esa tasa, muchas trayectorias quedarían sin Y y la sección 6 daría cotas tan anchas que no informarían.
3. **Recursos.** ≈ 1.2 GB de disco por visita (hasta ≈ 6 GB) y hasta 54 min por visita con refinamiento: del orden de 10 TB y semanas de cómputo para 7980 visitas, para un resultado ya determinado.
4. **Antecedente del proyecto.** El dominio de área 0.02 no es construible como disco simple en una fracción de estados true: pliegue en C1-A2 (split0 j1, j3), escape en T2-A (split8 j5, j7) y pausas masivas aquí. Es el mismo patrón que E13: el instrumento falla precisamente en los estados que interesan.

Esto **no** es abandonar casos difíciles para declarar completa la cohorte (roadmap): la cohorte se declara **incompleta** y el veredicto INCONCLUSIVE, con todo el registro conservado.

## 3. Qué queda registrado
| elemento | estado |
|---|---|
| Basales (800) y X | sellados por hash; X **sin abrir** (salvo la desviación de Nemotron, `DESVIACION_ACCESO_BASELINE_NEMOTRON_2026-10-21.md`) |
| Piloto (20 visitas u25) | cerrado (`piloto/CIERRE_PILOTO_20_2026-10-21.md`) |
| Lote 0 | 128 visitas, cerrado (`produccion/lote_0/CIERRE_LOTE0_2026-10-22.md`); 52 no iniciadas |
| Splits 12–167 | **ninguna visita futura abierta**; solo basales |
| Split 11 | ninguna visita futura abierta |
| Estados, checkpoints y resultados | se conservan en D (y copia en E al archivar); nada se borra |

## 4. Decisiones que pide al responsable
1. **Aprobar el cierre** INCONCLUSIVE por limitación del instrumento.
2. **¿Se clasifican las 52 visitas evaluadas del lote 0?** Propuesta: no ahora. Sus resultados quedan sellados por hash en el manifiesto y se abren solo como material de desarrollo de T2-A1, si su diseño lo prevé.
3. **¿Cuándo se abre X?** Propuesta: no antes de congelar el instrumento y las reglas de medición de T2-A1, porque T2-A1 podría reutilizar estas trayectorias.
4. **Conservación:** mantener en D o E los checkpoints de las 128 visitas hasta cerrar el diseño de T2-A1. Son regenerables (el ejecutor es determinista desde el update 5), pero no se borran sin decisión.

## 5. Para T2-A1 (fuera de este cierre)
Muestra de desarrollo: splits 8–11 (ya abiertos). Muestra confirmatoria: splits 12–167, intactos en seguimiento. Antecedentes y propuestas, en documento aparte.
