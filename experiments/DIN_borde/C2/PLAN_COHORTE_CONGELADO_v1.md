# DIN-C2: tamaño y universo congelados antes del código de cohorte

Diseño d00abbad…ff80 → potencia dd34a6b/58558b8 → ESTE plan.
**200 splits, cinco inicializaciones, 1.000 trayectorias.**

- [Plan](cohorte/c2_plan.json), SHA `ad320ac9fdf75a80801f2c44a529de467f1c852ed90cdd3d7181a61151b6aed8`.
- SHA de IDs unidos por salto de línea SIN salto final: `3b9c090d2951dbf7a6252e4a11fbc5396374c9a85eb882f32cfb78fd2dba3700`.
- [Lista completa](cohorte/ids_planificados.txt), splits 0..199, k=0..4.
- [Potencia](potencia/RESULTADO_POTENCIA_v1.md): primer N válido, inferior95=.83075
  para D_obj=.012; superior95 nulo=.04857.
- Semillas de datos 611000..611199, pesos 621000..621999,
  lotes 631000..631999. Controles usan bases 641000 y 651000.
- Se conservan las cuatro visitas autorizadas 5,10,30,250: 4.000 estados previstos.
- Generador/red/entrenamiento G3 intactos; sólo s=.8 y semillas nuevas.
- Salidas pesadas: `/workspace/work/din-c2-cohorte-v1-arrays/` fuera de Git.

Todavía no existe código de cohorte C2 ni se ha generado/entrenado una trayectoria C2.
El próximo commit añadirá el código; después se comprometerá la compuerta de reproducción
antes del entrenamiento. Este agente publica y no ejecuta el análisis de C2.
