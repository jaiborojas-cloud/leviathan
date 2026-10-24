"""Familia E12 sobre E16: derivadas de inmersión y geometría extrínseca exactas."""
import sys
sys.dont_write_bytecode=True
import json,csv,hashlib,importlib.util
from pathlib import Path
import numpy as np
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1];E16=ROOT.parent;CFG=json.loads((ROOT/'phase0_config.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
def rows(p):return list(csv.DictReader(p.open()))
def table(p,rs,fields=None):
 if rs or fields:
  with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields or list(rs[0]));w.writeheader();w.writerows(rs)
class Metric:
 def __init__(self,features,scores):self.f=features;self.R=scores
 def immersion(self,p):
  mp_mode=isinstance(p[0],mp.mpf);zz=self.f@p
  if mp_mode:
   a=np.array([mp.exp(x-max(zz)) for x in zz],object);a/=sum(a)
  else:a=np.exp(zz-max(zz));a/=sum(a)
  mean=a@self.f;d=self.f-mean;cov=d.T@(a[:,None]*d);U=d.T@(a[:,None]*self.R);S=np.array([[(a*(d[:,i]*d[:,j]-cov[i,j]))@self.R for j in range(2)] for i in range(2)])
  return a@self.R,U,S,a
 def geometry(self,p):
  _,U,S,a=self.immersion(p);h=U@U.T;det=h[0,0]*h[1,1]-h[0,1]**2
  if h[0,0]<=0 or det<=0:raise ValueError('NON_SPD')
  inv=np.array([[h[1,1],-h[0,1]],[-h[0,1],h[0,0]]])/det;G=(inv@U@S.reshape(4,-1).T).reshape(2,2,2);normal=S-np.array([[G[:,i,j]@U for j in range(2)] for i in range(2)]);K=(normal[0,0]@normal[1,1]-normal[0,1]@normal[0,1])/det
  return h,G,K
 def condition(self,p):return float(np.linalg.cond(np.asarray(self.geometry(p)[0],float)))
def prepare():
 for p,h in CFG['sources'].items():assert sha(E16/p)==h,p
 d=load('d_ae',E16/'D/scripts/run.py');data=json.loads((E16/'H/data.json').read_text());prep={}
 for digits in CFG['mp_digits']:
  with mp.workdps(digits):
   theta=[mp.mpf(str(x)) for x in data['states'][CFG['state']]];inputs=[[mp.mpf(str(x)) for x in data['inputs'][i]] for i in data['panels'][CFG['panel']]];_,_,C,ch=d.analytic_mp(theta,inputs);features=np.array(inputs,object)
   for j in range(2):
    mean=sum(features[:,j])/len(inputs);sd=mp.sqrt(sum((x-mean)**2 for x in features[:,j])/len(inputs));features[:,j]=[(x-mean)/sd for x in features[:,j]]
   scores=[]
   for x,y in inputs:
    u=mp.tanh(theta[0]*x+theta[1]*y+theta[4]);v=mp.tanh(theta[2]*x+theta[3]*y+theta[5]);logit=theta[6]*u+theta[7]*v+theta[8];sig=1/(1+mp.exp(-logit));r=mp.matrix([theta[6]*(1-u*u)*x,theta[6]*(1-u*u)*y,theta[7]*(1-v*v)*x,theta[7]*(1-v*v)*y,theta[6]*(1-u*u),theta[7]*(1-v*v),u,v,1]);row=((int(x+y>0)-sig)*r).T*ch;scores.append(list(row))
   prep[digits]=Metric(features,np.array(scores,object))
 metric=Metric(np.array(prep[80].f,float),np.array(prep[80].R,float));return metric,prep
