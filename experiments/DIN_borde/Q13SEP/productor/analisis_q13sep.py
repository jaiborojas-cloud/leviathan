"""Analista de DIN-Q13-SEP v2: emparejamientos E/C, decisión de calibración y veredicto de validación.

Aplica las reglas congeladas (DISENO_DIN_Q13SEP_v2_CONGELADO.md §4–§6, ESQUEMA_Y_DECISION_v2.md)
a la tabla `q13sep_medidas_v2.csv` del productor. No calcula X, ρ ni D.

  python -I analisis_q13sep.py --fase cal --corrida <carpeta cal> --salida <carpeta>
      → q13sep_emparejamientos_v2.csv, DOSIS_Y_REGLAS_Q13SEP_v2.json
  python -I analisis_q13sep.py --fase val --corrida <carpeta val> --salida <carpeta> \\
      --dosis <DOSIS_Y_REGLAS_Q13SEP_v2.json> --dosis-sha <sha publicado>
      → q13sep_emparejamientos_v2.csv, VEREDICTO_Q13SEP_v2.json
Las salidas se crean de forma exclusiva (no sobrescribe).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parents[3]
CONFIG_REL = 'experiments/DIN_borde/Q13SEP/config_v2_CONGELADO.json'
CONFIG_SHA = 'e8074d509f1e5d22e8463d0d7fc00201eb9d6d35207115e1c4dceb60db1f9bf3'
J_GRID = list(range(-16, 17))
COLS_EMP = ('phase,condition,lambda,split,k,update,pregunta,uso,estado,motivo,c_A0,S_A0,j_C,empates_j,T_LP,c_LP,S_LP,'
            'delta_c,log_ratio_S,error_rel_S_E,orientacion,pasa,procedencia').split(',')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def cargar(corrida):
    corrida = Path(corrida)
    res = json.loads((corrida/'RESUMEN_Q13SEP.json').read_text(encoding='utf-8'))
    tabla = corrida/'q13sep_medidas_v2.csv'
    if sha(tabla) != res['tabla_sha256']:
        raise SystemExit('La tabla no coincide con el SHA del resumen del productor')
    if res.get('config_sha256') != CONFIG_SHA:
        raise SystemExit('La corrida no usa la configuración congelada')
    with open(tabla, encoding='utf-8', newline='') as fh:
        filas = list(csv.DictReader(fh))
    return res, filas, sha(tabla)


def valida(f):
    return f is not None and f['estado_medida'] == 'MEDIDA' and all(
        num(f[k]) is not None for k in ('c', 'S_panel', 'T')) and num(f['S_panel']) > 0


def indexar(filas):
    idx = {}
    for f in filas:
        clave = (f['condition'], int(f['split']), int(f['k']), int(f['update']), f['temperature_role'],
                 int(f['j']) if f['j'] != '' else None)
        if clave in idx:
            raise SystemExit('Fila duplicada: '+f['measure_id'])
        idx[clave] = f
    return idx


def evaluar_unidad(cfg, idx, cond, s, k, v):
    """Emparejamientos E y C de una unidad (A0 frente a LP=cond) en la visita v. No decide la orientación."""
    sep = cfg['separabilidad']
    a0 = idx.get(('A0', s, k, v, 'A0_ANCHOR', None))
    out = {}
    base = dict(c_A0=None, S_A0=None)
    if valida(a0):
        base.update(c_A0=num(a0['c']), S_A0=num(a0['S_panel']))
    # --- E
    e = dict(base, pregunta='E')
    em = idx.get((cond, s, k, v, 'E_MATCH', None))
    if not valida(a0):
        e.update(estado='NO_DEFINIDO', motivo='ancla A0 no válida')
    elif not valida(em):
        e.update(estado='NO_DEFINIDO', motivo='E_MATCH no válida: '+(em['error'] if em else 'ausente'))
    else:
        cl, sl, T = num(em['c']), num(em['S_panel']), num(em['T'])
        err = abs(sl-e['S_A0'])/e['S_A0']
        e.update(T_LP=T, c_LP=cl, S_LP=sl, delta_c=e['c_A0']-cl, log_ratio_S=math.log(e['S_A0'])-math.log(sl),
                 error_rel_S_E=err)
        if not err <= sep['E_misma_S_tolerancia_relativa']:
            e.update(estado='NO_DEFINIDO', motivo='igualdad de S fuera de tolerancia')
        else:
            e.update(estado='DEFINIDO', motivo='', procedencia='ENTRE_BRAZOS_T_FIJA' if T == 1.0 else 'ENTRE_BRAZOS_T_EMPAREJADA')
    out['E'] = e
    # --- C: argmin |Δc| sobre la rejilla completa, clave (|Δc|, |j|, j); S solo después
    c = dict(base, pregunta='C')
    grid = [idx.get((cond, s, k, v, 'GRID', j)) for j in J_GRID]
    if not valida(a0):
        c.update(estado='NO_DEFINIDO', motivo='ancla A0 no válida')
    elif not all(valida(g) for g in grid):
        malos = [j for j, g in zip(J_GRID, grid) if not valida(g)]
        c.update(estado='NO_DEFINIDO', motivo=f'rejilla incompleta: j inválidos {malos}')
    else:
        claves = sorted(((abs(num(g['c'])-c['c_A0']), abs(j), j) for j, g in zip(J_GRID, grid)))
        mejor = claves[0]
        empates = [x[2] for x in claves if x[0] == mejor[0]]
        g = grid[J_GRID.index(mejor[2])]
        cl, sl = num(g['c']), num(g['S_panel'])
        c.update(j_C=mejor[2], empates_j=';'.join(map(str, empates)), T_LP=num(g['T']), c_LP=cl, S_LP=sl,
                 delta_c=c['c_A0']-cl, log_ratio_S=math.log(c['S_A0'])-math.log(sl), estado='DEFINIDO', motivo='',
                 procedencia='ENTRE_BRAZOS_T_FIJA' if mejor[2] == 0 else 'ENTRE_BRAZOS_T_EMPAREJADA')
    out['C'] = c
    return out


def pasa(cfg, p, sigma):
    sep = cfg['separabilidad']
    if p['estado'] != 'DEFINIDO':
        return False
    if p['pregunta'] == 'E':
        return sigma*p['delta_c'] >= sep['distinta_c_min']
    return abs(p['delta_c']) <= sep['misma_c_max'] and sigma*p['log_ratio_S'] >= math.log(sep['distinta_S_factor_min'])


def unidad_completa(cfg, idx, conds, s, k, v=250):
    """Calidad principal (u250): todos los brazos y puntos válidos y ningún NO_APRENDIO en la unidad."""
    filas = [idx.get(('A0', s, k, v, 'A0_ANCHOR', None))]
    for cond in conds:
        filas += [idx.get((cond, s, k, v, 'GRID', j)) for j in J_GRID] + [idx.get((cond, s, k, v, 'E_MATCH', None))]
    if not all(valida(f) for f in filas):
        return False
    return all(f['no_aprendio_final'] == 'false' for f in filas)


def splits_que_pasan(cfg, ev, fc, cond, preg, sigma, v=250):
    sep = cfg['separabilidad']
    n = 0
    detalle = {}
    for s in range(fc['n_splits']):
        u = sum(pasa(cfg, ev[(cond, s, k, v)][preg], sigma) for k in range(fc['n_inits']))
        detalle[s] = u
        n += u >= sep['min_unidades_por_split']
    return n, detalle


def calidad(cfg, idx, fc, conds, fase):
    q = cfg['calidad']
    comp = {(s, k): unidad_completa(cfg, idx, conds, s, k) for s in range(fc['n_splits']) for k in range(fc['n_inits'])}
    n = sum(comp.values())
    sp = sum(sum(comp[(s, k)] for k in range(fc['n_inits'])) >= 3 for s in range(fc['n_splits']))
    if fase == 'cal':
        ok = n >= q['min_unidades_completas_calibracion'] and sp >= q['min_splits_con_tres_completas_calibracion']
    else:
        ok = n >= q['min_unidades_completas_validacion'] and sp >= q['min_splits_con_tres_completas_validacion']
    return dict(unidades_completas=n, splits_con_tres_completas=sp, ok=ok,
                incompletas=[f's{s}_k{k}' for (s, k), c in comp.items() if not c])


def tabla_emparejamientos(path, fase, ev, conds, lams, sigmas):
    buf = io.StringIO(newline='')
    w = csv.DictWriter(buf, fieldnames=COLS_EMP, lineterminator='\n')
    w.writeheader()
    for (cond, s, k, v), d in sorted(ev.items(), key=lambda x: (conds.index(x[0][0]),) + x[0][1:]):
        for preg in ('E', 'C'):
            p = d[preg]
            sg = sigmas.get((cond, preg))
            fila = {c: '' for c in COLS_EMP}
            fila.update({kk: ('' if vv is None else vv) for kk, vv in p.items() if kk in COLS_EMP})
            fila.update(phase=fase, condition=cond, **{'lambda': lams[cond]}, split=s, k=k, update=v,
                        uso='PRINCIPAL_u250' if v == 250 else 'DESCRIPTIVO_u10',
                        orientacion='' if sg is None else sg,
                        pasa='' if sg is None else str(pasa(CFG, p, sg)).lower())
            w.writerow({c: (repr(x) if isinstance(x, float) else x) for c, x in fila.items()})
    with open(path, 'x', encoding='utf-8', newline='') as fh:
        fh.write(buf.getvalue())
    return sha(path)


def solo_temperatura(cfg, idx, fc, conds):
    """Descriptivo: LP(T1) frente a cada GRID T≠1 del mismo LP; no rescata nada."""
    sep = cfg['separabilidad']
    out = {}
    for cond in conds:
        for v in cfg['receta']['visitas']:
            n = 0
            for s in range(fc['n_splits']):
                for k in range(fc['n_inits']):
                    g0 = idx.get((cond, s, k, v, 'GRID', 0))
                    if not valida(g0):
                        continue
                    for j in J_GRID:
                        g = idx.get((cond, s, k, v, 'GRID', j))
                        if j == 0 or not valida(g):
                            continue
                        dc = abs(num(g0['c'])-num(g['c']))
                        lr = abs(math.log(num(g0['S_panel']))-math.log(num(g['S_panel'])))
                        n += dc <= sep['misma_c_max'] and lr >= math.log(sep['distinta_S_factor_min'])
            out[f'{cond}_u{v:03d}_pares_C_solo_temperatura'] = n
    return out


CFG = None


def main():
    global CFG
    ap = argparse.ArgumentParser()
    ap.add_argument('--fase', choices=('cal', 'val'), required=True)
    ap.add_argument('--corrida', required=True)
    ap.add_argument('--salida', required=True)
    ap.add_argument('--dosis')
    ap.add_argument('--dosis-sha')
    a = ap.parse_args()
    p = ROOT/CONFIG_REL
    if sha(p) != CONFIG_SHA:
        raise SystemExit('Configuración congelada modificada')
    CFG = json.loads(p.read_text(encoding='utf-8'))
    res, filas, tsha = cargar(a.corrida)
    fc = CFG['calibracion' if a.fase == 'cal' else 'validacion']
    corrida = Path(a.corrida)
    out = Path(a.salida)
    out.mkdir(parents=True, exist_ok=True)
    idx = indexar(filas)
    if a.fase == 'cal':
        conds = ['LP01', 'LP02', 'LP03', 'LP04']
        lams = dict(zip(conds, CFG['calibracion']['LP_grid']))
        dec_cal = None
    else:
        if not a.dosis or sha(a.dosis) != a.dosis_sha:
            raise SystemExit('Falta la decisión de calibración o su SHA no coincide')
        dec_cal = json.loads(Path(a.dosis).read_text(encoding='utf-8'))
        conds, lams = ['LP'], {'LP': dec_cal['lambda']}
    ev = {(cond, s, k, v): evaluar_unidad(CFG, idx, cond, s, k, v) for cond in conds for s in range(fc['n_splits'])
          for k in range(fc['n_inits']) for v in CFG['receta']['visitas']}
    cal_q = calidad(CFG, idx, fc, conds, a.fase)
    ctl = None
    if a.fase == 'cal':
        ctl = json.loads((corrida/'controles.json').read_text(encoding='utf-8'))
    sep = CFG['separabilidad']
    base = dict(config_sha256=CONFIG_SHA, tabla_sha256=tsha, plan_ids_sha256=res['ids_sha256'],
                productor_sha256=res['productor_sha256'], script_sha256=sha(Path(__file__)), calidad=cal_q,
                solo_temperatura=solo_temperatura(CFG, idx, fc, conds))
    if a.fase == 'cal':
        base['controles_sha256'] = sha(corrida/'controles.json')
        candidatos, sigmas, elegido = {}, {}, None
        min_sp = sep['min_splits_calibracion']
        for cond in conds:
            apta = {}
            for preg in ('E', 'C'):
                for sg in sep['orientaciones_ordenadas']:
                    n, det = splits_que_pasan(CFG, ev, fc, cond, preg, sg)
                    candidatos[f'{cond}_{preg}_{sg:+d}'] = dict(splits=n, unidades_por_split=det)
                    if n >= min_sp and preg not in apta:
                        apta[preg] = sg
            if 'E' in apta and 'C' in apta and elegido is None:
                elegido = cond
                sigmas = {(cond, 'E'): apta['E'], (cond, 'C'): apta['C']}
        if not ctl['controles_ok']:
            dec = dict(decision='NO_IDENTIFICABLE', estado_corrida='INVALIDA', motivo='CONTROL_OFICIAL_FALLIDO')
        elif not cal_q['ok']:
            dec = dict(decision='NO_IDENTIFICABLE', motivo='CALIDAD_INSUFICIENTE')
        elif elegido is None:
            dec = dict(decision='NO_IDENTIFICABLE', motivo='CALIBRACION_SIN_DOSIS')
        else:
            dec = dict(decision='DOSIS_APTA', condicion=elegido, **{'lambda': lams[elegido]},
                       sigma_E=sigmas[(elegido, 'E')], sigma_C=sigmas[(elegido, 'C')])
        emp = tabla_emparejamientos(out/'q13sep_emparejamientos_v2.csv', 'cal', ev, conds, lams, sigmas)
        dec.update(base, emparejamientos_sha256=emp, candidatos=candidatos,
                   reglas=dict(ancla='A0_T1', E='T*=exp(log S_LP(1)-log S_A0(1)) aplicado a LP',
                               C='argmin (|Δc|,|j|,j) sobre T=2^(j/8), j=-16..16; S solo después',
                               umbrales=dict(distinta_c=sep['distinta_c_min'], misma_c=sep['misma_c_max'],
                                             factor_S=sep['distinta_S_factor_min']),
                               orden_orientaciones=sep['orientaciones_ordenadas'], menor_lambda_apta=True))
        destino = out/'DOSIS_Y_REGLAS_Q13SEP_v2.json'
    else:
        sE, sC = dec_cal['sigma_E'], dec_cal['sigma_C']
        sigmas = {('LP', 'E'): sE, ('LP', 'C'): sC}
        nE, detE = splits_que_pasan(CFG, ev, fc, 'LP', 'E', sE)
        nC, detC = splits_que_pasan(CFG, ev, fc, 'LP', 'C', sC)
        u10 = {preg: splits_que_pasan(CFG, ev, fc, 'LP', preg, sg, v=10)[0] for preg, sg in (('E', sE), ('C', sC))}
        ok = cal_q['ok'] and nE >= sep['min_splits_validacion'] and nC >= sep['min_splits_validacion']
        dec = dict(veredicto='SEPARABILIDAD_LOGRADA' if ok else 'NO_IDENTIFICABLE',
                   motivo='' if ok else ('CALIDAD_INSUFICIENTE' if not cal_q['ok'] else 'E_o_C_bajo_el_criterio'),
                   splits_E=nE, splits_C=nC, unidades_por_split_E=detE, unidades_por_split_C=detC,
                   descriptivo_u10_splits=u10, dosis_sha256=a.dosis_sha, **{'lambda': dec_cal['lambda']})
        emp = tabla_emparejamientos(out/'q13sep_emparejamientos_v2.csv', 'val', ev, conds, lams, sigmas)
        dec.update(base, emparejamientos_sha256=emp)
        destino = out/'VEREDICTO_Q13SEP_v2.json'
    texto = json.dumps(dec, indent=1, ensure_ascii=False, allow_nan=False, sort_keys=True)+'\n'
    with open(destino, 'x', encoding='utf-8', newline='\n') as fh:
        fh.write(texto)
    print(json.dumps({k: dec.get(k) for k in ('decision', 'veredicto', 'motivo', 'condicion', 'lambda', 'sigma_E',
                                              'sigma_C', 'splits_E', 'splits_C')}, ensure_ascii=False))
    print('calidad:', {k: cal_q[k] for k in ('unidades_completas', 'splits_con_tres_completas', 'ok')})
    print(destino.name, 'SHA =', sha(destino))
    return 0


if __name__ == '__main__':
    sys.exit(main())
