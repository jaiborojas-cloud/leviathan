# Salidas AG y límites de interpretación

`inputs.json` contiene los 40 M/f triangulares nuevos, sus Q/ε, y los 40 M/f
AF exactos. Es información sintética autorizada; no contiene estados T2.
`states.csv` conserva los 80 estados sin seleccionar por éxito:

- `rho` es el mínimo numérico refinado de semirrectas completas, con los
  empates exactos de logits de las aristas incluidos. `rho_resolutions.csv`
  separa mínimos de rejilla y ampliados, y `rho_attempts.csv` conserva quad y
  búsqueda angular. `MP_speed_error` contrasta la norma direccional en tres
  puntos; no es una integral MP completa ni certificado de óptimo global.
- `d_border_exact` y `rho_exact` sólo existen para los triángulos. Sus
  respuestas analíticas proceden de la inmersión plana y se contrastan en MP80.
  Para AF, la distancia al borde real es UNKNOWN, aun habiendo escape.
- `d_escape` es el mínimo entre los 2048 rayos y el refinamiento angular, con
  evento ||P||∞=150 en la carta ORIGINAL. `coarse_escape` conserva el primer
  valor del haz, y `refinement.csv` todos los intentos individuales. No es un
  certificado de distancia a la frontera al infinito ni un mínimo global.
- `ratio=rho/d_escape`, `ratio_true=rho/d_border_exact` y
  `escape_to_true=d_escape/d_border_exact` no son intercambiables.
- `escape_status` distingue ESCAPE, DRAG_5000, RHO_HORIZON_CENSORED,
  NUMERICAL_FAILURE y BUDGET. Sólo DRAG_5000 cuenta en Q4; un timeout o un
  fallo numérico no se convierte en arrastre. `stop_over_rho` existe también
  para otros estados, sin promoverlos a casos de Q4.
- `steps`, `stop_radius` y `ray_steps.csv` conservan los pasos aceptados y el
  radio del haz. El refinamiento tiene sus propios conteos. La cara y las
  probabilidades corresponden al escape coarse; el mínimo refinado puede
  pertenecer a otra dirección cercana. La tendencia registrada es del rayo
  incidente coarse, no de un límite asintótico demostrado.
- `rho_seconds` incluye las cuatro rejillas/cuadraturas y el refinamiento;
  `exp_seconds`, el haz, sus archivos y el refinamiento. No incluyen controles
  ni generación. Las cartas y los objetos calculados son distintos: Q5 sólo
  describe estos costes, sin afirmar una ventaja universal.

`groups.csv` usa los denominadores completos e informa pares válidos y
unknowns. Correlaciones sin imputación ni p-valores: las escalas están
emparejadas, no son 80 réplicas independientes. Los nuevos usan carta plana
de cara desde el inicio; AF usa la carta natural y el horizonte nuevo1.5ρ.
El grupo AF fue «sin patología» hasta el Rmax=.2 de AF; ese estado histórico
no significa que nunca pueda escapar al prolongar el horizonte en AG.

## Arrays fuera de Git

`arrays.csv` da nombres, formas y SHA256 de los .npy en la ruta de
`resources.json`. Los originales se conservan fuera de Git, conforme a AGENTS.
Los arrays rho contienen ángulo y longitud por dirección; los perfiles de la
exponencial tienen forma(4,n,k), con radios en otro archivo. Para AF son
[P1,P2,v1,v2]; para triángulos son[w0,w1,dw0,dw1]. Se guarda origen, los
primeros pasos, cada20 pasos y el último, no una interpolación continua.
No son .npz ni datos T2. Los verificadores comprueban hashes sin reintegrar.

Los avisos de quad se conservan en `execution.log`, junto al resto de stdout y
stderr. No se descartaron intentos para obtener estados favorables. La
corrección documental de dependencias conserva la declaración inicial en
[ERRATA_ENTORNO.md](ERRATA_ENTORNO.md).
