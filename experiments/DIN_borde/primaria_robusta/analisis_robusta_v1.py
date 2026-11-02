"""DIN primaria robusta v1 · BORRADOR genérico para auditoría, sin entrenamiento.

Solo diseños nuevos. La CLI borrador admite exclusivamente pruebas sintéticas.
No importa C1, core, geometry ni productores. No modifica archivos de entrada.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
CONFIG_SHA = 'e841d6c36f01b7f8681d2cee441d4d179c1a7a97d9572f34c2b39098c7f71178'
COLUMNS = 'trajectory,split,estado_10,estado_final,error,X10,rho_caras_10,rho_caras_250,acc_train_final'.split(',')
FOLD_SEED = 260010
PERMUTATION_SEED = 260001


class Aborta(ValueError):
    """Entrada estructural inválida; no hay veredicto científico."""


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def json_read(path):
    def bad(value):
        raise Aborta('JSON no finito: ' + value)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Aborta('Clave JSON duplicada: ' + key)
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=bad, object_pairs_hook=unique)


def number(value):
    if isinstance(value, (bool, np.bool_)):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return result if math.isfinite(result) else None


def integer(value):
    if isinstance(value, bool):
        raise Aborta('Entero booleano')
    if isinstance(value, int):
        result = value
    elif isinstance(value, str) and re.fullmatch('[0-9]{1,19}', value):
        result = int(value)
    else:
        raise Aborta('Split no es entero no negativo')
    if not 0 <= result <= np.iinfo(np.int64).max:
        raise Aborta('Split fuera de capacidad int64')
    return result


def config():
    path = HERE / 'config_BORRADOR_v1.json'
    if sha(path) != CONFIG_SHA:
        raise Aborta('Configuración del borrador modificada')
    return json_read(path)


def validar_plan(plan):
    required = {'protocolo', 'estado', 'tipo_datos', 'n_clases', 'universo'}
    if not isinstance(plan, dict) or set(plan) != required:
        raise Aborta('Esquema de plan distinto del contrato')
    if plan['protocolo'] != 'DIN-PRIMARIA-ROBUSTA-v1':
        raise Aborta('Protocolo distinto')
    if plan['estado'] not in ('BORRADOR', 'CONGELADO'):
        raise Aborta('Estado del plan inválido')
    if plan['tipo_datos'] not in ('PRUEBA_SINTETICA', 'COHORTE_NUEVA'):
        raise Aborta('Tipo de datos inválido')
    if type(plan['n_clases']) is not int or plan['n_clases'] != 3:
        raise Aborta('Este umbral está declarado para tres clases')
    universe = plan['universo']
    if not isinstance(universe, list) or not universe:
        raise Aborta('Universo vacío o inválido')
    seen = set()
    for item in universe:
        if not isinstance(item, dict) or set(item) != {'trajectory', 'split'}:
            raise Aborta('Entrada de universo inválida')
        name = item['trajectory']
        if not isinstance(name, str) or not name.strip() or name in seen:
            raise Aborta('ID vacío o duplicado en el plan')
        if type(item['split']) is not int:
            raise Aborta('Split del plan debe ser entero, no booleano')
        integer(item['split'])
        seen.add(name)
    return plan


def centrar(value, split):
    # Mismas operaciones y orden que C1.cen, aplicado a cada columna por separado.
    value = np.asarray(value, float).copy()
    for s in np.unique(split):
        value[split == s] -= value[split == s].mean()
    return value


def preparar(split, X, L, Y, *, recorte=True, grado=3):
    """Bases por bloque. El modo sin recorte es solo diagnóstico de equivalencia."""
    split = np.asarray(split, dtype=np.int64)
    X, L, Y = (np.asarray(v, dtype=float) for v in (X, L, Y))
    if any(v.ndim != 1 for v in (split, X, L, Y)) or not len(X) or any(len(v) != len(X) for v in (split, L, Y)):
        raise FloatingPointError('Vectores vacíos, dimensiones o longitudes distintas')
    if not all(np.isfinite(v).all() for v in (X, L, Y)):
        raise FloatingPointError('Vectores no finitos')
    us = np.unique(split)
    if len(us) < 2:
        raise FloatingPointError('Menos de dos splits para CV')
    if np.allclose(centrar(X, split), 0, atol=1e-8):
        raise FloatingPointError('X sin variación intra-split: NO_IDENTIFICABLE')
    sd = L.std()
    if not math.isfinite(float(sd)) or sd <= 0:
        raise FloatingPointError('L sin variación o DE inválida')
    z = (L - L.mean()) / sd
    if not np.isfinite(z).all():
        raise FloatingPointError('z no finita')
    permutation = np.random.default_rng(FOLD_SEED).permutation(us)
    fold = {s: i % 10 for i, s in enumerate(permutation)}
    fo = np.array([fold[s] for s in split])
    global_base = np.column_stack([centrar(z ** g, split) for g in range(1, grado + 1)])
    cache, clips = [], []
    for k in range(10):
        tr, te = fo != k, fo == k
        lo, hi = float(z[tr].min()), float(z[tr].max())
        zc = z.copy()
        if recorte:
            zc[te] = np.clip(z[te], lo, hi)
        clipped = np.flatnonzero(te & (zc != z))
        base = np.column_stack([centrar(zc ** g, split) for g in range(1, grado + 1)]) if len(clipped) else global_base
        if not np.isfinite(base).all():
            raise FloatingPointError('Base no finita')
        cache.append((tr, te, base))
        clips.append(dict(bloque=k, n_train=int(tr.sum()), n_test=int(te.sum()), z_train_min=lo, z_train_max=hi,
                          indices=clipped.tolist(), z_antes=z[clipped].tolist(), z_despues=zc[clipped].tolist()))
    return dict(split=split, X=X, L=L, Y=Y, yc=centrar(Y, split), z=z, fo=fo, cache=cache,
                global_base=global_base, recortes=clips, grado=grado, recorte=recorte)


def ajustar(prepared, X, *, residuos=False):
    xc = centrar(X, prepared['split'])
    yc = prepared['yc']
    sb = sf = 0.0
    eb, ef = np.empty(len(xc)), np.empty(len(xc))
    for tr, te, base in prepared['cache']:
        full = np.column_stack([base, xc])
        bb = np.linalg.lstsq(base[tr], yc[tr], rcond=None)[0]
        bf = np.linalg.lstsq(full[tr], yc[tr], rcond=None)[0]
        eb[te] = yc[te] - base[te] @ bb
        ef[te] = yc[te] - full[te] @ bf
        # Acumulación por bloque idéntica a C1, sin reducir todo el vector al final.
        sb += float((eb[te] ** 2).sum())
        sf += float((ef[te] ** 2).sum())
    if not math.isfinite(sb) or not math.isfinite(sf) or sb <= 0:
        raise FloatingPointError('SSE_base <= 0 o pérdidas no finitas')
    D = 1 - sf / sb
    if not math.isfinite(D):
        raise FloatingPointError('D no finito')
    if residuos:
        return dict(D=D, SSE_base=sb, SSE_completo=sf, e_base=eb, e_completo=ef)
    return D


def punto(split, X, L, Y, *, recorte=True):
    prepared = preparar(split, X, L, Y, recorte=recorte)
    result = ajustar(prepared, prepared['X'], residuos=True)
    xc = centrar(prepared['X'], prepared['split'])
    beta = float(np.linalg.lstsq(np.column_stack([prepared['global_base'], xc]), prepared['yc'], rcond=None)[0][-1])
    if not math.isfinite(beta):
        raise FloatingPointError('Pendiente no finita')
    result['pendiente_X'] = beta
    return result, prepared


def primaria(split, X, L, Y, *, B=5000, recorte=True):
    """API numérico; B reducido/sin recorte solo para pruebas declaradas."""
    if type(B) is not int or B < 1:
        raise Aborta('Número de permutaciones inválido')
    result, prepared = punto(split, X, L, Y, recorte=recorte)
    result.update(p=None, D_nulo_q95=None, grado_base=3, permutaciones=B, permutaciones_completadas=0,
                  error_permutacion=None, recorte=recorte)
    rng = np.random.default_rng(PERMUTATION_SEED)
    split = prepared['split']
    X = prepared['X']
    indices = [np.where(split == s)[0] for s in np.unique(split)]
    null = np.empty(B)
    try:
        for b in range(B):
            xp = X.copy()
            for ii in indices:
                xp[ii] = X[rng.permutation(ii)]
            null[b] = ajustar(prepared, xp)
            result['permutaciones_completadas'] += 1
        result.update(p=float((1 + np.sum(null >= result['D'] - 1e-15)) / (1 + B)),
                      D_nulo_q95=float(np.quantile(null, .95)),
                      nulo_mayor_igual=int(np.sum(null >= result['D'] - 1e-15)))
    except (FloatingPointError, ValueError, np.linalg.LinAlgError) as e:
        result['error_permutacion'] = dict(replica=result['permutaciones_completadas'], error=f'{type(e).__name__}: {e}')
    return result, prepared


def decidir(D, p, pendiente, D_sin_max):
    values = [number(v) for v in (D, p, pendiente, D_sin_max)]
    if any(v is None for v in values):
        return 'INCONCLUSIVE'
    D, p, pendiente, D_sin_max = values
    if not 0 <= p <= 1:
        return 'INCONCLUSIVE'
    if p < .05 and D > 0 and pendiente > 0:
        return 'PASS' if D_sin_max > 0 else 'NO_ROBUSTO'
    return 'NOT_MET'


def influencia(ids, prepared, observed):
    gains = observed['e_base'] ** 2 - observed['e_completo'] ** 2
    if not np.isfinite(gains).all():
        raise FloatingPointError('Contribuciones no finitas')
    top = int(np.argmax(gains))  # Primer ID en el orden del universo.
    ties = np.flatnonzero(gains == gains[top]).tolist()
    total = float(gains.sum())
    fraction = float(gains[top] / total) if total > 0 else None
    if fraction is not None and not math.isfinite(fraction):
        raise FloatingPointError('Fracción de influencia no finita')
    keep = np.ones(len(ids), dtype=bool)
    keep[top] = False
    result = dict(id_max=ids[top], ids_empatados=[ids[i] for i in ties], max_g=float(gains[top]), suma_g=total,
                  fraccion_max=fraction, motivo_fraccion=None if total > 0 else 'SUMA_G_NO_POSITIVA',
                  D_sin_max=None, error_sin_max=None, ids_sin_max=[t for i, t in enumerate(ids) if keep[i]],
                  n_sin_max=int(keep.sum()), splits_sin_max=np.unique(prepared['split'][keep]).tolist(),
                  criterio_omision='solo_un_ID_sin_reaplicar_compuertas',
                  contribuciones=[dict(trajectory=t, split=int(prepared['split'][i]), bloque=int(prepared['fo'][i]),
                                      e_base=float(observed['e_base'][i]), e_completo=float(observed['e_completo'][i]), g=float(gains[i]))
                                  for i, t in enumerate(ids)])
    try:
        omit, _ = punto(prepared['split'][keep], prepared['X'][keep], prepared['L'][keep], prepared['Y'][keep])
        result['D_sin_max'] = omit['D']
    except (FloatingPointError, ValueError, np.linalg.LinAlgError) as e:
        result['error_sin_max'] = f'{type(e).__name__}: {e}'
    return result


def seleccionar(rows, plan):
    universe = plan['universo']
    planned = {v['trajectory']: v['split'] for v in universe}
    mapping = {}
    states = {'MEDIDA', 'FALLIDA', 'INVALID_RHO', ''}
    for row in rows:
        if not isinstance(row, dict) or set(row) != set(COLUMNS):
            raise Aborta('Columnas o fila distintas del esquema')
        t = row['trajectory']
        if not isinstance(t, str) or t not in planned or t in mapping:
            raise Aborta('ID ajeno o duplicado en la tabla')
        if integer(row['split']) != planned[t]:
            raise Aborta('Split discordante con el plan: ' + t)
        if row['estado_10'] not in states or row['estado_final'] not in states:
            raise Aborta('Estado no reconocido: ' + t)
        mapping[t] = row
    ledger, eligible, missing = {}, [], []
    for item in universe:
        t = item['trajectory']
        row = mapping.get(t)
        reasons = []
        if row is None:
            reasons.append('AUSENTE')
        else:
            for key in ('estado_10', 'estado_final'):
                if row[key] != 'MEDIDA':
                    reasons.append(key + ': ' + str(row[key]))
            if row['error']:
                reasons.append('ERROR_DECLARADO: ' + str(row['error']))
            acc = number(row['acc_train_final'])
            if acc is None or not 0 <= acc <= 1:
                reasons.append('ACC_TRAIN_FINAL_DOMINIO')
            elif acc < .5:
                reasons.append('NO_APRENDIO')
            if number(row['X10']) is None:
                reasons.append('X10_NO_FINITA')
            for key in ('rho_caras_10', 'rho_caras_250'):
                value = number(row[key])
                if value is None or value <= 0:
                    reasons.append(key + ': NO_POSITIVA_FINITA')
        ledger[t] = dict(split=item['split'], elegible=not reasons, motivos=reasons)
        (missing if reasons else eligible).append(t)
    counts = Counter(planned[t] for t in eligible)
    planned_splits = sorted(set(planned.values()))
    valid_splits = [s for s in planned_splits if counts[s] >= 3]
    used = [t for t in eligible if planned[t] in valid_splits]
    return dict(mapping=mapping, ledger=ledger, eligible=eligible, missing=missing, used=used,
                planned_splits=planned_splits, valid_splits=valid_splits,
                counts={str(s):counts[s] for s in planned_splits},
                unused=[t for t in eligible if t not in set(used)])


def analizar(rows, plan, *, B=5000, gate_reasons=()):
    config()
    validar_plan(plan)
    selected = seleccionar(rows, plan)
    n_plan = len(plan['universo'])
    n_split = len(selected['planned_splits'])
    inc = list(gate_reasons)
    if 20 * len(selected['missing']) > n_plan:
        inc.append('FALTANTES_MAYORES_5_POR_CIENTO')
    if 5 * len(selected['valid_splits']) < 4 * n_split:
        inc.append('SPLITS_VALIDOS_MENORES_80_POR_CIENTO')
    if len(selected['valid_splits']) < 2:
        inc.append('MENOS_DE_DOS_SPLITS_PARA_CV')
    result = dict(modo='BORRADOR_PRIMARIA_ROBUSTA_V1', veredicto='INCONCLUSIVE', motivos_inconclusive=inc,
                  planificadas=n_plan, splits_planificados=n_split, elegibles=len(selected['eligible']),
                  faltantes=len(selected['missing']), ids_faltantes=selected['missing'],
                  no_aprendio=sum('NO_APRENDIO' in r['motivos'] for r in selected['ledger'].values()),
                  libro_motivos=selected['ledger'], splits_validos=len(selected['valid_splits']),
                  conteos_elegibles_por_split=selected['counts'], splits_usados=selected['valid_splits'],
                  ids_usados=selected['used'], ids_elegibles_no_usados=selected['unused'],
                  primaria=None, influencia=None,
                  alcance='Solo diseños nuevos; mejora frente a una base cúbica recortada concreta. No certificado universal de robustez, información condicional o causalidad.')
    if inc:
        return result
    used = selected['used']
    mapping = selected['mapping']
    split_by_id = {r['trajectory']:r['split'] for r in plan['universo']}
    split = np.array([split_by_id[t] for t in used], dtype=np.int64)
    X = np.array([float(mapping[t]['X10']) for t in used])
    # Solo se llega al log después de la selección y la validación de dominio.
    L = np.log([float(mapping[t]['rho_caras_10']) for t in used])
    Y = np.log([float(mapping[t]['rho_caras_250']) for t in used])
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            prim, prepared = primaria(split, X, L, Y, B=B)
            result['primaria'] = {k:v for k, v in prim.items() if k not in ('e_base', 'e_completo')}
            result['bloques'] = {str(s):int(prepared['fo'][np.flatnonzero(split == s)[0]]) for s in np.unique(split)}
            result['max_abs_z_L'] = float(np.abs(prepared['z']).max())
            result['recorte_por_bloque'] = [{k:v for k, v in r.items() if k != 'indices'} | {'ids':[used[i] for i in r['indices']]} for r in prepared['recortes']]
            result['n_recortadas'] = sum(len(r['indices']) for r in prepared['recortes'])
            if prim['error_permutacion']:
                inc.append('PERMUTACION_NO_COMPLETA: ' + str(prim['error_permutacion']))
            inf = influencia(used, prepared, prim)
            result['influencia'] = inf
            if inf['error_sin_max']:
                inc.append('D_SIN_MAX_NO_DEFINIDO: ' + inf['error_sin_max'])
            if not inc:
                result['veredicto'] = decidir(prim['D'], prim['p'], prim['pendiente_X'], inf['D_sin_max'])
                if result['veredicto'] == 'INCONCLUSIVE':
                    inc.append('DECISION_NO_FINITA_O_NO_DEFINIDA')
                result['triple_condicion_original'] = bool(prim['p'] < .05 and prim['D'] > 0 and prim['pendiente_X'] > 0)
                result['compuerta_influencia'] = bool(inf['D_sin_max'] > 0)
    except (FloatingPointError, ValueError, np.linalg.LinAlgError) as e:
        inc.append(f'CALCULO_NO_DEFINIDO: {type(e).__name__}: {e}')
    return result


def enlaces(summary, gate, expected):
    reasons = []
    if not isinstance(summary, dict) or not isinstance(gate, dict):
        return ['RESUMEN_O_COMPUERTA_NO_OBJETO']
    for key, value in expected.items():
        if summary.get(key) != value:
            reasons.append('ENLACE_DISTINTO: ' + key)
    if gate.get('PASA') is not True or gate.get('script_sha256') != expected['productor_sha256']:
        reasons.append('COMPUERTA_NO_PASA_O_PRODUCTOR_DISTINTO')
    return reasons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('tabla', 'tabla-sha', 'plan', 'plan-sha', 'resumen', 'compuerta', 'compuerta-sha', 'productor-sha', 'out'):
        parser.add_argument('--' + key, required=True)
    args = parser.parse_args()
    try:
        target = Path(args.out) / 'RESULTADO_ROBUSTA_v1.json'
        if target.exists() or target.is_symlink():
            raise Aborta('Salida ya existe; nunca sobrescribir')
        cfg = config()
        expected = dict(tabla_sha256=args.tabla_sha, plan_sha256=args.plan_sha,
                        compuerta_sha256=args.compuerta_sha, productor_sha256=args.productor_sha)
        if any(not digest(v) for v in expected.values()):
            raise Aborta('SHA de entrada inválido')
        for path, key in [(args.tabla, 'tabla_sha256'), (args.plan, 'plan_sha256'), (args.compuerta, 'compuerta_sha256')]:
            if sha(path) != expected[key]:
                raise Aborta('SHA distinto: ' + key)
        plan = validar_plan(json_read(args.plan))
        if cfg['estado_implementacion'] == 'BORRADOR' and plan['tipo_datos'] != 'PRUEBA_SINTETICA':
            raise Aborta('Implementación BORRADOR: solo pruebas sintéticas hasta auditoría y congelación')
        if plan['tipo_datos'] != 'PRUEBA_SINTETICA' and plan['estado'] != 'CONGELADO':
            raise Aborta('Datos reales requieren plan CONGELADO')
        summary, gate = json_read(args.resumen), json_read(args.compuerta)
        with Path(args.tabla).open(encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != COLUMNS:
                raise Aborta('Columnas distintas del contrato')
            rows = list(reader)
        result = analizar(rows, plan, B=5000, gate_reasons=enlaces(summary, gate, expected))
        result.update(entradas=expected, config_sha256=CONFIG_SHA, script_sha256=sha(Path(__file__)),
                      estado_plan=plan['estado'], tipo_datos=plan['tipo_datos'])
        value = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('x', encoding='utf-8', newline='\n') as f:
            f.write(value)
        print(json.dumps(dict(veredicto=result['veredicto'], faltantes=result['faltantes'], salida=str(target)), ensure_ascii=False))
    except (Aborta, OSError, ValueError, TypeError, OverflowError) as e:
        print('ABORTA: ' + str(e), file=sys.stderr)
        return 3
    return 0


if __name__ == '__main__':
    sys.exit(main())
