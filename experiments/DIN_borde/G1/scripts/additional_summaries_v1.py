"""Descriptivos de las medidas ya previstas; no añade reglas H1–H5 ni rho."""
import csv
import json
import numpy as np
from support_v1 import RUN, ARRAYS, write


def main():
    rows = [json.loads(p.read_text()) for p in sorted((RUN/'states').glob('*.json'))]
    with np.load(ARRAYS/'dataset_iris.npz', allow_pickle=False) as z:
        labels = z['y']
    out = []
    for family in ['R27', 'P60', 'W27']:
        for update in [5, 10, 20, 30, 50, 150, 250]:
            rr = [r for r in rows if r['family'] == family and r['update'] == update and r.get('metrics', {}).get('M_valid')]
            wrong, ratios, normalised = [], [], []
            for r in rr:
                with np.load(r['array']['path'], allow_pickle=False) as z:
                    k = r['metrics']['k_star']
                    wrong.append(int(z['logits'][k].argmax()) != int(labels[z['panel_ids'][k]]))
                    if r.get('rho_valid'):
                        approx = np.sqrt(z['M'][k, k])/len(z['f'])
                        ratios.append(r['rho']['rho_borde']/approx)
                        normalised.append(r['rho']['rho_borde']/np.sqrt(r['metrics']['trace']))
            def med(values):
                return float(np.median(values)) if len(values) else None
            out.append(dict(family=family, update=update, n=len(rr),
                            median_py_star=med([r['metrics']['py_star'] for r in rr]),
                            dominant_misclassified=sum(wrong),
                            dominant_misclassified_fraction=float(np.mean(wrong)) if wrong else None,
                            median_log1m_star=med([r['metrics']['log1m_star'] for r in rr]),
                            median_leverage_star=med([r['metrics']['leverage_star'] for r in rr]),
                            median_rho_over_coordinate_prediction=med(ratios),
                            median_rho_normalised=med(normalised),
                            median_train_loss=med([r['train']['loss'] for r in rr]),
                            median_validation_loss=med([r['validation']['loss'] for r in rr]),
                            largest_face=max((r['metrics']['chord']['largest_face'] for r in rr), default=None)))
    write(RUN/'additional_descriptives.json', dict(changes_primary_rules=False, data=out))
    with (RUN/'additional_descriptives.csv').open('x') as file:
        writer = csv.DictWriter(file, fieldnames=list(out[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(out)


if __name__ == '__main__':
    main()
