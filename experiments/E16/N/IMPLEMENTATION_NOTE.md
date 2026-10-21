# Acotación adicional antes de medir los caminos

Para evitar subdividir innecesariamente polígonos coincidentes, se toma el
mínimo de la cota Lipschitz congelada y otra cota superior válida: para cada
segmento destino, el máximo de las distancias de ambos extremos del intervalo
fuente a ese segmento; luego el mínimo sobre segmentos destino. La distancia
a un conjunto convexo es convexa, por lo que este máximo acota todo el intervalo.
No cambia la distancia, la tolerancia ni la decisión. Se registra antes de medir
M o de optimizar N. Los controles sintéticos de implementación ya se habían
ejecutado con la cota original, sin medir caminos de M/N.
