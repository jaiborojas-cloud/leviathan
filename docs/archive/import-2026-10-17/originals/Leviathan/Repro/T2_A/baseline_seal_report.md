# T2-A — cierre de fase basal y sellado de predictores

800/800 auditorías basales completas; 800 ZIP y checkpoints verificados.
Elegibles: 800, repartidos en 160 splits. Exclusiones: 0. Compuertas basales y comparadores: PASS.

Predictor primario: κ máximo intrínseco de Dexp en r*=0.05697156262709151, update5. Cola superior congelada: q=10%, 80 trayectorias. Corte X≥1.0005397093666348; todos los empates exactos incluidos. Comparadores del mismo update5 conservados sin cambios.

Tabla, elegibilidad, corte y marcadores de sellado persistidos con SHA-256. Ver baseline_seal_verification.json. Ningún estado futuro ejecutado o abierto. Esto no constituye evidencia predictiva ni PASS de la hipótesis temporal.

Siguiente paso: seguimiento en orden de cohorte, visitas 25,50,…,250, conservando modelo, Adam y RNG. Antes de ejecutar, verificar los hashes del sello y sus recibos; no recalcular basales ni llamar a agregadores basales que sobrescriban este progreso. No detener trayectorias por puntuación, precisión o evento. No tratar visitas pendientes como negativas.
