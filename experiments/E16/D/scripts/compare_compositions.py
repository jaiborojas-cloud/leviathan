#!/usr/bin/env python3
"""Comparaciones descriptivas previamente declaradas, conservando desconocidos."""
import argparse
import csv
import json
from pathlib import Path


def analyze(folder):
    folder=Path(folder)
    main=[r for r in csv.DictReader((folder/'ranks.csv').open()) if r['point']!='control']
    groups={}
    panels={}
    for r in main:
        groups.setdefault((r['state'],r['panel'],r['point']),{})[r['composition']]=r
        panels.setdefault((r['state'],r['point'],r['composition']),[]).append(r)
    paired=[]
    for (state,panel,point),kinds in groups.items():
        assert set(kinds)=={'sum','product','quadratic'}
        valid=all(r['status']=='PASS_NUMERICAL' for r in kinds.values())
        values={k:int(r['rank_reference']) for k,r in kinds.items()}
        paired.append({'state':state,'panel':panel,'point':point,**{k+'_rank':v for k,v in values.items()},
                       'independent_precision':'PASS' if valid else 'INCONCLUSIVE',
                       'product_changes_rank':int(values['product']!=values['sum']) if valid else '',
                       'quadratic_changes_rank':int(values['quadratic']!=values['sum']) if valid else ''})
    sensitivity=[]
    for (state,point,kind),rows in panels.items():
        assert len(rows)==3
        valid=all(r['status']=='PASS_NUMERICAL' for r in rows)
        values=[int(r['rank_reference']) for r in rows]
        sensitivity.append({'state':state,'point':point,'composition':kind,
                            'ranks_by_panel':json.dumps({r['panel']:int(r['rank_reference']) for r in rows},sort_keys=True),
                            'min_rank':min(values),'max_rank':max(values),
                            'status':('STABLE' if min(values)==max(values) else 'SENSITIVE') if valid else 'INCONCLUSIVE'})
    for name,rows in [('paired_compositions.csv',paired),('panel_sensitivity.csv',sensitivity)]:
        with (folder/name).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    summary={'triples':len(paired),'triples_with_validated_precision':sum(r['independent_precision']=='PASS' for r in paired),
             'product_rank_changes':sum(r['product_changes_rank']==1 for r in paired),
             'quadratic_rank_changes':sum(r['quadratic_changes_rank']==1 for r in paired),
             'triples_with_unknown_comparison':sum(r['independent_precision']!='PASS' for r in paired),
             'panel_groups':len(sensitivity),'panel_groups_stable':sum(r['status']=='STABLE' for r in sensitivity),
             'panel_groups_sensitive':sum(r['status']=='SENSITIVE' for r in sensitivity),
             'statistically_independent_trials':False,'hypothesis_of_learning_tested':False}
    (folder/'secondary_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);a=p.parse_args();print(json.dumps(analyze(a.folder),indent=2))
