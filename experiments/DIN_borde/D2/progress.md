# Fase0 y procedencia

Base main 3798757acde266b43dd22b23ba4ddd12a73bca92. Leídos AGENTS, fuentes autorizadas rho_borde.py
completo, geometría/contexto AG/AH. D1 no estaba en main: se leyeron plan y
cierre del PR68 en cb588738857a8448238d0340cca3ce5b51db3651, con hashes en config. Se inspeccionaron sólo
las claves/escalares publicados de d1_resumen.json, sin estados ni matrices.
No se abrió ningún otro dato T2. [Cierre D1](https://github.com/jaiborojas-cloud/leviathan/blob/cb588738857a8448238d0340cca3ce5b51db3651/experiments/DIN_borde/RESULTADO_D1_2026-10-24.md).
No hay código ni mediciones D2. Las pruebas se obtuvieron antes del diseño:
Q1 necesita controlar caras con más de n/2 índices; interiores sí pueden
alcanzar1/n. Rango1/λmax no bastan; mezcla constante satura la perturbación.
La validación separará el mínimo verdadero y la longitud de la dirección
reportada: una cola tardía omitida puede dar un escalar engañoso.
