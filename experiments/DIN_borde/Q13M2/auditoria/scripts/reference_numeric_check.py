"""Diagnóstico del literal LS: misma tabla,funciones originales,punto únicamente."""
import csv
import json
import numpy as np
from support import STAGE,CFG,PROV,LS,sha,write,code_guard,guard,target


def main():
    code_guard();guard(True);assert sha(LS)==PROV['LS_reference']['sha256'];m=target()
    with LS.open(newline='') as f:rows={r['trajectory']:r for r in csv.DictReader(f)}
    val={l:{} for l in range(6)}
    for t in m.DR.universo(200):
        r=rows[t];l=int(t.split('_')[1][1:]);s=int(t.split('_')[2][1:])
        if m.DR.valida(r):val[l].setdefault(s,[]).append(r)
    common=[s for s in range(200) if all(len(val[l].get(s,[]))>=3 for l in range(6))]
    arr={l:m.arreglos(val,common,l,lambda r:int(r['trajectory'].split('_')[2][1:])) for l in range(6)}
    Dq=[];Da=[];c=[]
    for l in range(6):
        a=arr[l];Dq.append(m.Q.D_punto(a['sp'],a['X'],a['L'],a['Y']))
        # One permutation only to expose the original C1 point D; no LS hypothesis is tested.
        Da.append(m.A.primaria(a['sp'],a['X'],a['L'],a['Y'],3,260001,1)['D']);c.append(float(np.median(a['c'])))
    q=m.DR.pendiente(Dq,c);a=m.DR.pendiente(Da,c);expected=0.07692466151365258
    write(STAGE/'results/reference_LS/numeric_comparison.json',dict(Q_D_point=Dq,original_C1_point_D=Da,c=c,
        point_vectors_identical=bool(np.array_equal(Dq,Da)),beta_Q=q,beta_original_C1=a,published_expected=expected,
        absolute_difference_literal=abs(q-expected),within_1e_12=abs(q-expected)<=1e-12,
        scope='Reproducción de la referencia LS autorizada; no nuevo test ni nuevo cierre de Q13DR',old_status_unchanged=True))
    print(json.dumps(dict(beta_Q=q,beta_original_C1=a,difference_literal=abs(q-expected),vectors_identical=np.array_equal(Dq,Da))),flush=True)


if __name__=='__main__':main()
