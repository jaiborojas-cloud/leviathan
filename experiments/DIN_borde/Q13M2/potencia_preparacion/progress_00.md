# Lectura y cuestión previa al escenario

Se leyó AGENTS.md y se parte de mainac40fcd0. La preparación apunta al borrador v1 y analista del PR#114,commit525c7455. Se archivan snapshots por SHA; no se modifica ni se congela el diseño confirmatorio. La futura congelación obliga a verificar esta potencia contra el SHA congelado o repetirla si cambia el estimando.

Se leyeron los seis puntos D/c del RESULTADO_Q13DR.json publicado(SHA0f74669d…). No se abrió la tabla de Q13-DR ni se calculó D de datos reales. Con pendiente fija.077,el intercepto MCO condicionado a esa pendiente es media(D)−.077·media(c)=−.038434071244996953. Los extremos previstos dan D<0. El método gaussiano Q13-DR usa sqrt(d/(1−d)),por lo que se preguntó al responsable si se conserva la truncación max(0,D) de ese método. No se ejecutarán simulaciones dependientes de esa decisión hasta recibir respuesta.

Solo están autorizados como datos el piloto G3s=.8 y los seis puntos ya publicados para fijar el escenario. No se usan tablas Q13,C2,Q13-DR ni una cohorte nueva. No se generará plan ni entrenará cohorte.
