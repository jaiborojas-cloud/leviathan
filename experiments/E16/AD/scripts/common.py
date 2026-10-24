"""Fuentes cerradas de sólo lectura; tensores y marcos nodales."""
import sys
sys.dont_write_bytecode=True
import json,csv,hashlib,importlib.util
from pathlib import Path
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];CFG=json.loads((ROOT/'config.json').read_text());E16=ROOT.parent
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def rows(p):return list(csv.DictReader(p.open()))
def table(p,rs,fields=None):
 if rs or fields:
  with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields or list(rs[0]));w.writeheader();w.writerows(rs)
def prepare():
 for p,h in CFG['sources'].items():assert sha(E16/p)==h,p
 d=load('d_ad',E16/'D/scripts/run.py');k=load('k_ad',E16/'P/scripts/kernel.py');ac=load('ac_ad',E16/'AC/scripts/run_v2.py');data=json.loads((E16/'H/data.json').read_text());prepared={}
 for digits in CFG['precisions']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(x)) for x in data['states']['h00']];inputs=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels']['P0']];cv,jc,_,ch=d.analytic_mp(theta,inputs);prepared[digits]={}
   for kind in ['sum','quadratic','product']:
    ux=d.analytic_B(cv,jc,[1,0],kind)[0]*ch;uy=d.analytic_B(cv,jc,[0,1],kind)[0]*ch;metric=ac.Metric('sum' if kind=='sum' else 'quadratic',np.array(ux.tolist(),object),np.array(uy.tolist(),object));prepared[digits][kind]=(ux,uy,metric)
 return data,k,ac,prepared
def float_metric(ac,prepared,kind):
 ux,uy,_=prepared[80][kind];return ac.Metric('sum' if kind=='sum' else 'quadratic',np.array(ux.tolist(),float),np.array(uy.tolist(),float))
def frame(z,J,A,metric):
 n=len(z)-2;T=np.zeros((2*n,n));N=np.zeros_like(T);gs=[]
 for i,(p,chord) in enumerate(zip(z[1:-1],z[2:]-z[:-2])):
  g=J.T@metric.geometry(A+J@p)[0]@J;t=chord/np.sqrt(chord@g@chord);gt=g@t;normal=np.array([-gt[1],gt[0]]);normal/=np.sqrt(normal@g@normal);T[2*i:2*i+2,i]=t;N[2*i:2*i+2,i]=normal;gs.append(g)
 return T,N,gs
