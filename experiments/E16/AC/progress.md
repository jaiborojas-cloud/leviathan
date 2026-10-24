# Fase 0 · lectura antes del diseño

Se leyeron D/analytic_mp, analytic_B, P/kernel, T/run.py y los runners y tablas
paths/audits/comparisons/spectra/vertices de Z, AA y AB. No se ejecutaron etapas cerradas.

Métrica: ux=B(e1) chol((F+rho I)^−1), uy=B(e2) chol(...), rho desde D/config.
Cuadrática: U(p)=p1 ux+p2 uy, h=UUᵀ, ∂a h=Ua Uᵀ+U Uaᵀ,
∂ab h=Ua Ubᵀ+Ub Uaᵀ. Suma: h=ux uxᵀ constante. A/B son
perspectives[0/1] de H; z=(t,s) se transforma por A+t(B−A)+s R(B−A).
No se encontró implementación previa de K de Gauss: AC deberá construirla
con Christoffel y sus derivadas exactas, no reutilizar una medida inexistente.
T construye tangentes por cuerda centrada en z, normales euclidianas rotadas,
TᵀHT y NᵀHN (no normal riemanniana continua); Z/AA/AB no archivan esos bloques.
Los testigos de Z/AB son de g⊥ y no se archivaron sus vectores, sólo hashes.
Por tanto normales negativos y tangencialidad de esos testigos son UNKNOWN.

| Etapa/fuente | Método | Malla | KKT final | Testigo MP |
|---|---|---:|---:|---|
| Z/Q0/reference/132 | L-BFGS-B; PHYSICAL_SUSTAINED | 264 | 6.449316499984592e-06 | True |
| Z/Q0/reference/264 | L-BFGS-B; PHYSICAL_SUSTAINED | 528 | 1.9066023294878054e-06 | True |
| Z/Q0/scaled/132 | L-BFGS-B; PHYSICAL_SUSTAINED | 264 | 4.603402182112859e-06 | True |
| Z/Q0/scaled/264 | L-BFGS-B; PHYSICAL_SUSTAINED | 528 | 3.3525091985564526e-06 | True |
| Z/Q1/reference/132 | L-BFGS-B; PHYSICAL_SUSTAINED | 264 | 4.381387456911523e-06 | True |
| Z/Q1/reference/264 | L-BFGS-B; PHYSICAL_SUSTAINED | 528 | 4.886575164397833e-06 | True |
| Z/Q1/scaled/132 | L-BFGS-B; PHYSICAL_SUSTAINED | 264 | 6.001316999765249e-06 | True |
| Z/Q1/scaled/264 | L-BFGS-B; PHYSICAL_SUSTAINED | 528 | 3.6992005213731805e-06 | True |
| Z/C0/reference/132 | L-BFGS-B; NATIVE_CONTROL | 264 | 2.9424485343602065e-36 | False |
| Z/C0/reference/264 | L-BFGS-B; NATIVE_CONTROL | 528 | 1.1769794137440826e-35 | False |
| Z/C0/scaled/132 | L-BFGS-B; NATIVE_CONTROL | 264 | 2.9424485343602065e-36 | False |
| Z/C0/scaled/264 | L-BFGS-B; NATIVE_CONTROL | 528 | 1.1769794137440826e-35 | False |
| AA/Q0/reference/132 | L-BFGS-B; UNVERIFIED_TERMINATION | 264 | 1.3296554310510134e-06 | False |
| AA/Q0/reference/264 | L-BFGS-B; UNVERIFIED_TERMINATION | 528 | 3.022188728871167e-06 | True |
| AA/Q0/scaled/132 | L-BFGS-B; UNVERIFIED_TERMINATION | 264 | 2.623026080172952e-06 | False |
| AA/Q0/scaled/264 | L-BFGS-B; UNVERIFIED_TERMINATION | 528 | 3.937365205625154e-06 | True |
| AA/Q1/reference/132 | L-BFGS-B; UNVERIFIED_TERMINATION | 264 | 7.849933608056192e-06 | False |
| AA/Q1/reference/264 | L-BFGS-B; UNVERIFIED_TERMINATION | 528 | 5.928934053309187e-06 | True |
| AA/Q1/scaled/132 | L-BFGS-B; UNVERIFIED_TERMINATION | 264 | 2.4017656762159723e-06 | False |
| AA/Q1/scaled/264 | L-BFGS-B; UNVERIFIED_TERMINATION | 528 | 3.021678924394755e-06 | True |
| AA/C0/reference/132 | L-BFGS-B; NATIVE_CONTROL | 264 | 2.9424485343602065e-36 | False |
| AA/C0/reference/264 | L-BFGS-B; NATIVE_CONTROL | 528 | 1.1769794137440826e-35 | False |
| AA/C0/scaled/132 | L-BFGS-B; NATIVE_CONTROL | 264 | 2.9424485343602065e-36 | False |
| AA/C0/scaled/264 | L-BFGS-B; NATIVE_CONTROL | 528 | 1.1769794137440826e-35 | False |
| AB/Q0/reference/132 | TRF gradiente; UNVERIFIED_TERMINATION | 264 | 1.2723880316034553e-07 | False |
| AB/Q0/reference/264 | TRF gradiente; PHYSICAL_SUSTAINED | 528 | 4.9156218984158784e-08 | True |
| AB/Q0/scaled/132 | TRF gradiente; UNVERIFIED_TERMINATION | 264 | 1.4796296210484172e-07 | False |
| AB/Q0/scaled/264 | TRF gradiente; PHYSICAL_SUSTAINED | 528 | 8.776794147014044e-08 | True |
| AB/Q1/reference/132 | TRF gradiente; UNVERIFIED_TERMINATION | 264 | 1.0827931462564777e-07 | False |
| AB/Q1/reference/264 | TRF gradiente; PHYSICAL_SUSTAINED | 528 | 9.449209781298151e-08 | True |
| AB/Q1/scaled/132 | TRF gradiente; PHYSICAL_SUSTAINED | 264 | 9.612074247655755e-08 | False |
| AB/Q1/scaled/264 | TRF gradiente; PHYSICAL_SUSTAINED | 528 | 9.013005046465405e-08 | True |
| AB/C0/reference/132 | TRF gradiente; INITIAL_CONTROL | 264 | 2.9424485343602065e-36 | False |
| AB/C0/reference/264 | TRF gradiente; INITIAL_CONTROL | 528 | 1.1769794137440826e-35 | False |
| AB/C0/scaled/132 | TRF gradiente; INITIAL_CONTROL | 264 | 2.9424485343602065e-36 | False |
| AB/C0/scaled/264 | TRF gradiente; INITIAL_CONTROL | 528 | 1.1769794137440826e-35 | False |

AB cubre las doce fuentes. AC usará las doce, incluidos inconclusos y controles.
La falta del comparando normal impide decidir H1/H2 con la regla solicitada;
no se importará el bloque de T como si perteneciera a AB.
