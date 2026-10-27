# DIN-Q13-M2: potencia preparatoria N=200

**La preparación terminó: N=200 no cumple la regla de potencia individual para LP ni WD en rho=0.** No se generó plan o cohorte,ni se aumentó N. El estudio confirmatorio sigue sin congelar; esta simulación no autoriza su ejecución.

| Dependencia rho | MODULA LP | MODULA WD | Ambos MODULA |
|---|---:|---:|---:|
|0|77.50 %|75.25 %|68.50 %|
|.3|74.25 %|74.75 %|69.00 %|
|.6|66.75 %|68.75 %|63.00 %|
|.615|66.75 %|68.50 %|63.00 %|

Wilson95 inferior en rho=0:LP .731573,WD .707939; ninguno alcanza .8. La potencia conjunta se cuenta directamente y solo se reporta,no se exige por la regla del borrador. Son400 réplicas por rho,bootstrap500,IC bilateral97.5 % y1999 permutaciones; 11 niveles con un A0 único y remuestreos compartidos.

- [Informe con Wilson95,curva y límites](RESULTADO_v1.md).
- [Potencias completas CSV](potencia.csv), [resumen y conteos](results_v1/summary.json), [objetivos/effectos efectivos](results_v1/scenario.json).
- [Decisión recibida antes de simular](DECISION_TRUNCAMIENTO.md), [procedimiento previo](PROCEDIMIENTO_v1_CONGELADO.md), [configuración](config_v1.json), [implementación por SHA](IMPLEMENTACION_v1.sha256).
- [Controles contra el analista completo](results_v1/controls.json), [verificación OLS independiente](verification.json), [arrays por SHA](external_manifest.csv).
- [Fuentes y SHA](sources/provenance.json), [manifest vigente](manifest.csv), [comprobación SHA](manifest.sha256).

La generadora autorizada es max(0,−.038434071244996953+.077c). LP5 y WD5 se truncan; LP4/WD4=.000065928755 siguen positivos. Pendientes MCO efectivas:LP .064952782620,WD .069950805294. Se reduce la pendiente respecto de.077,pero no se asume conservadurismo universal de potencia. Los D estimados negativos se conservan; no se recorta el estadístico de las réplicas.

Referencia provisional:PR#114,commit525c7455,analista SHA15ca7b428110f0b7bff1520d93587c7438e8ea0959394f98c91ac37653d95332. Al congelar hay que verificar el SHA/estimando o repetir. Solo se usan G3s=.8 como piloto y los seis puntos ya publicados del cierre LS; no se recalcula D de ninguna cohorte real. No se calcula compatibilidad con LS en esta preparación.

El [estado pendiente inicial](escenario_pendiente.json) y su [README original](README_PREPARATORIO_b71c1a12.md) se conservan como historia de b71c1a12. La decisión posterior y los resultados actuales los sustituyen como estado vigente; [alcance del manifiesto inicial](ALCANCE_PUBLICACION_PREPARATORIA.json). No se sobrescribieron salidas anteriores.
