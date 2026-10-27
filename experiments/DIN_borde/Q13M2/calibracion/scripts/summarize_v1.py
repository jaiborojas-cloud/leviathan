"""Medianas/bootstrap por split y reglas exactas del §5, sin elegir dosis."""
import numpy as np
from support_m2 import CFG


def summarize(records,conditions):
    n=CFG['splits'];per=n*5;draws=np.random.default_rng(CFG['bootstrap_seed']).choice(n,size=(CFG['bootstrap'],n),replace=True)
    summaries=[]
    for arm,dose in conditions:
        rr=sorted([r for r in records if r['brazo']==arm and r['dosis']==dose],key=lambda r:(r['split'],r['k']))
        assert len(rr)==per
        good=[r for r in rr if r['status']=='MEASURED'];complete=len(good)==per
        yes=sum(r['c250']<=.70 for r in good)
        d=dict(brazo=arm,dosis=dose,planned=per,measured=len(good),failed=per-len(good),complete=complete,
               c250=None,q250=None,acc_panel250=None,IC95_mediana_c250=None,fraccion_c250_le_070=None,
               fraccion_c250_le_070_bounds=[yes/per,(yes+per-len(good))/per])
        if complete:
            for key in ('c250','q250','acc_panel250'):d[key]=float(np.median([r[key] for r in rr]))
            C=np.array([r['c250'] for r in rr]).reshape(n,5)
            boot=np.median(C[draws].reshape(CFG['bootstrap'],per),axis=1)
            d['IC95_mediana_c250']=np.quantile(boot,[.025,.975]).tolist();d['fraccion_c250_le_070']=yes/per
        summaries.append(d)
    acc0=summaries[0]['acc_panel250'];eligibility={}
    for arm in ('LP','WD'):
        rr=[r for r in summaries if r['brazo']==arm];complete=all(r['complete'] for r in rr)
        inversions=[dict(dosis_anterior=a['dosis'],dosis_siguiente=b['dosis'],c_anterior=a['c250'],c_siguiente=b['c250'])
                    for a,b in zip(rr,rr[1:]) if a['complete'] and b['complete'] and b['c250']>a['c250']]
        c1=False if inversions else True if complete else None
        witnesses=[r['dosis'] for r in rr if r['complete'] and acc0 is not None and r['c250']<=.45 and acc0-r['acc_panel250']<=.10]
        c2=True if witnesses else False if complete and acc0 is not None else None
        high=[r for r in rr if r['complete'] and r['c250']>=.55]
        violations=[dict(dosis=r['dosis'],delta_abs_acc=abs(r['acc_panel250']-acc0)) for r in high if acc0 is not None and abs(r['acc_panel250']-acc0)>=.05]
        c3=False if violations else True if complete and acc0 is not None else None
        vals=(c1,c2,c3)
        eligibility[arm]=dict(criterio1_monotona_no_creciente=c1,inversiones=inversions,criterio2_alcanza_c045_y_preserva_acc=c2,
            dosis_testigo_criterio2=witnesses,criterio3_acc_preservada_si_c_ge_055=c3,violaciones_criterio3=violations,
            estado='NO_ELEGIBLE' if False in vals else 'INCONCLUSIVE' if None in vals else 'ELEGIBLE')
    return dict(conditions=summaries,elegibilidad=eligibility,dosis_confirmatorio_elegidas=False,
                bootstrap=dict(replicates=CFG['bootstrap'],seed=CFG['bootstrap_seed'],unit='split con las cinco inicializaciones',method='percentil',shared_draws=True)),draws
