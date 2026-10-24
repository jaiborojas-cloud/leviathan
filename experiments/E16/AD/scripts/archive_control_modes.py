#!/usr/bin/env python3
"""Completa el archivo de controles desde bandas ya medidas, sin calcular Hessianas."""
from common import *
from scipy.linalg import eigh
import argparse

def archive(out):
 destination=out/'control_negative_vectors.csv'
 if destination.exists():raise FileExistsError(destination)
 rs=rows(out/'bands.csv');result=[]
 for case in sorted({r['case'] for r in rs if r['case'].startswith('sphere/')}):
  rr=[r for r in rs if r['case']==case and r['block']=='normal'];n=int(rr[0]['dimension']);H=np.zeros((n,n))
  for r in rr:H[int(r['row']),int(r['column'])]=float(r['value'])
  vals,vec=eigh(H);tau=max(CFG['spectral_absolute'],CFG['spectral_relative']*max(abs(vals)))
  for idx in np.flatnonzero(vals< -tau):
   for j in range(n):result.append({'case':case,'mode_index':int(idx),'node':j+1,'eigenvalue':float(vals[idx]),'threshold':tau,'tangent_fraction':0.,'latitude':float(vec[j,idx]),'longitude':0.})
 table(destination,result,['case','mode_index','node','eigenvalue','threshold','tangent_fraction','latitude','longitude'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=ROOT/'results/part_b_v1');archive(p.parse_args().out)
