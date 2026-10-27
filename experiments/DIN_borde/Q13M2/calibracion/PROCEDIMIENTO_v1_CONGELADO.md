# DIN-Q13-M2: ejecución de calibración v1, previa al código

Rige íntegro el protocolo Q13M2/PROTOCOLO_CALIBRACION_M2_v1.md, SHA en config_v1.json. No se modifica. Solo se añaden archivos en Q13M2/calibracion/. No se eligen dosis confirmatorias.

## Implementación y universo

Receta Q13 recipe_v1.py copiada byte por byte; network,dataset,initialize,metric y update de A0/WD sin cambios. Un adaptador LP copia el flujo de update (mismos lotes/zero_grad/backward/step), con z=model(xt[ids]) y loss=CE(z,y)+lam*(z**2).sum(dim=1).mean(). LP usa initialize original, que selecciona Adam sin decay al no ser WD; WD usa AdamWlr.006 y CE normal. Soporte original conservado por bytes, con soporte de ejecución nuevo para rutas/guarda/IO. No se importa ningún instrumento rho ni analista. core y geometry por SHA intactos.

Universo fijo: A0dosis0; LP[.0001,.0003,.001,.003,.01,.03,.1,.3]; WD[.2,.5,1,2,4]; cada condición100 splits×5 k.7000 IDs m2_{brazo}_d{dosis:g}_s{split:03d}_k{k}. Orden condición→split→k, todas las condiciones. Seeds901000+s,902000+5s+k,903000+5s+k, pareadas.250 updates, mismo generador/red/Adam/lote de Q13. Dos procesos spawn de un hilo; versiones Q13 exactas. Se contrasta igualdad de SHA de datos,pesos iniciales y lotes entre pares sin calcular asociaciones.

## Publicación y fallos

Procedimiento→implementación por commit+push antes de medir. Pruebas de implementación de LP con redes de control y datos sintéticos separados: ecuación y gradiente, igualdad A0/WD, sin X/rho/D. Cualquier defecto publicado exige preservar salidas y enmienda antes de corregir. Ejecuciones fallidas no se repiten ni sustituyen. Salidas exclusivas; sin reanudar una ejecución fallida para convertirla en éxito. Un corte de proceso conserva registros existentes y archiva el fallo; los IDs sin registro aparecen como FAILED/INTERRUPTED al cerrar la tabla. No se inventan mediciones.

Por trayectoria: solo c250,q250,acc_panel250 como medidas; metadata de hashes/tiempos/warnings y arrays/pesos finales fuera de Git permiten auditoría. Tabla completa con diez columnas del encargo y todos los7000 IDs. No se calcula X,rho,D ni asociaciones. Se conserva el código usado y el entorno.

## Resúmenes predefinidos

Por condición completa(500 medidas válidas): medianas de c,q,acc; fracción c≤.70 sobre500; IC95 percentil[.025,.975] de la mediana de c. Bootstrap de100 splits completos con reemplazo,2000 draws de semilla904001; cada split mantiene sus cinco inicializaciones. Los mismos draws se aplican a todas las condiciones. Sin redondeo para decisiones.

Si alguna condición no está completa, sus medianas/IC oficiales y fracción puntual quedan null, con planned/measured/failed y límites de fracción posibles:[n_validas_c≤.70/500,(n_validas_c≤.70+fallidas)/500]. No se convierten supervivientes en una condición completa. Se evalúan criterios con los resultados conocidos: un contraejemplo conocido puede dar false; true requiere evidencia suficiente y ausencia de valores faltantes relevantes; de otro modo null/INCONCLUSIVE. No se cambian umbrales por fallos.

C1: toda mediana en dosis ascendente no creciente; listar todas las inversiones adyacentes. C2: existe dosis de mediana c≤.45 con caída(acc_A0−acc_dosis)≤.10; se reportan testigos, sin elegir dosis del confirmatorio. C3: para cada dosis con mediana c≥.55, diferencia absoluta de medianas de acc frente a A0<.05; se listan violaciones. LP/WD elegibles si C1,C2,C3 true; no elegible si alguno false; desconocido si no hay false y falta información. La referencia es la mediana acc_A0. No se impone un filtro adicional de q ni requisito de alcanzar una dosis no estipulada.

Se informa monotonía como descriptivo de medianas de esta rejilla: no prueba una curva poblacional monótona. Los IC son de la mediana,cumpliendo la unidad split; no se usan para reinterpretar la regla exacta del protocolo. Al terminar: tabla,resúmenes,elegibilidad,manifest,SHA,verificación y PR en borrador; detenerse sin diseñar confirmatorio.
