# Confirmación prospectiva a tamaño operativo N=200

Sin cambiar el Monte Carlo ni casos previos, repetir los dos defectos de
degeneración dentro de la rejilla operativa N=200, para descartar que dependan de
un ejemplo pequeño. Semilla de fixture910100, B39 y NB16 sólo para aislar lógica.

1. L observado variable sólo por split0; rho10=e allí, 1 en el resto; Y=2X.
   El bootstrap puede omitir el único split distinto y hacer L constante.
2. Por nivel l, invalidar k<3 en los splits16l..16l+15: 48/1000 faltantes (4.8%).
   Quedan104 splits comunes (96..199). Dentro de ellos, c comparte entre niveles
   los520 valores equiespaciados de .04 a .96; fuera, alturas por nivel
   [.99,.70,.61,.54,.42,.04]. Comprobar compuerta y β/JSON finitos, sin imponer
   un desenlace ni cambiar reglas si no aparece el fallo.

Se guardan resultados nuevos, fuentes intactas; no se repiten ni ajustan tasas.
