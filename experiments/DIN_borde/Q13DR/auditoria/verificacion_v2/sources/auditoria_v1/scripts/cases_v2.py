"""Extensión congelada: beta singular y clasificación explícita de traceback."""
import json
import traceback
import warnings
import numpy as np
from support import STAGE,write,code_guard,guard,target
import cases_v1 as old


def main():
    code_guard();guard();out=STAGE/'results/cases_v2';out.mkdir(parents=True,exist_ok=False)
    old.R=target();rows=old.fixture(12);heights=[.99,.70,.61,.54,.42,.04]
    for r in rows:
        if r['split']==r['nivel'] and r['k']<3:r['error']='SYNTHETIC_DISJOINT_LOSS'
        r['c250']=.04+.92*((r['split']-6)*5+r['k'])/29 if r['split']>=6 else heights[r['nivel']]
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter('always')
        try:
            res=old.execute(rows,12)
            try:json.dumps(res,allow_nan=False);valid_json=True
            except ValueError:valid_json=False
            record=dict(status='RETURNED',result=res,strict_JSON_finite=valid_json,
                common_c_medians=[float(np.median([r['c250'] for r in rows if r['split']>=6 and r['nivel']==l])) for l in range(6)])
        except BaseException as e:record=dict(status='EXCEPTION',exception=type(e).__name__,traceback=traceback.format_exc())
        record['warnings']=[dict(type=w.category.__name__,message=str(w.message)) for w in captured]
    write(out/'singular_beta_after_common_filter.json',record)
    rows=old.fixture()
    for r in rows:r['X10']=-2.
    answer=old.cli('missing_nivel_explicit_traceback_v2',rows,20,levels=[dict(eps=0.) for _ in range(6)])
    corrected='CRASH' if 'Traceback (most recent call last)' in answer['stderr'] else answer['status']
    write(out/'CLI_traceback_classification.json',dict(raw_helper_status=answer['status'],classification_by_traceback=corrected,
        raw_result=answer,original_results_preserved=True))
    print(json.dumps(dict(singular_beta_case=record['status'],strict_JSON_finite=record.get('strict_JSON_finite'),
        raw_CLI_status=answer['status'],corrected_CLI_status=corrected)),flush=True)


if __name__=='__main__':main()
