# Registro E16-Q

- 2026-10-21: base main 908abdb, con P integrado. Se crea rama independiente
  en el checkout existente. T2-A intacto.
- 9d06ad5: protocolo, configuración y hashes congelados antes de medir.
  Energía afín se distingue explícitamente de L²/2; presupuesto 900 s/512 MiB.
- 094bc25: implementación v1. Su comprobación AD/MP detecta una escala errónea
  en el FD local de energía. Se interrumpe después de cuatro caminos Q0,
  durante una comparación Hausdorff. No se completó un resultado global v1.
- 03071d3: v1 parcial y snapshot preservados; errata congelada antes de corregir.
- a3e41b9: factor m_global/m_local corregido, con control analítico nuevo de
  tres segmentos. No cambian optimizador, objetivos, fuentes ni tolerancias.
- a39dfae: v2 completa conservada. Global INCONCLUSIVE: cuatro caminos C0
  pasan y ocho cuadráticos agotan iteraciones. Dieciséis checks inconclusos
  de estacionariedad/terminación, cero FAIL. Nueve puntos de condicionamiento.
- V2: 181,50 s y 93,31 MiB. Las coordenadas, objetivos e iteraciones de los
  cuatro caminos comunes con v1 permanecen idénticos.
- Figura derivada sólo de CSV. Teoría separa equivalencia continua, energía
  discreta, distribución de nodos y condicionamiento.
- Reproducción completada: quince salidas v2 idénticas byte por byte; segunda
  corrida 183,55 s, dentro del presupuesto. Congelación, v1, errata, candidatos
  comunes, objetivos, coordenadas y condicionamiento verificados.
- Enlaces relativos, manifests y whitespace revisados. P y T2-A sin cambios.
