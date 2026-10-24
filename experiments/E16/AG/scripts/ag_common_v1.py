"""Fuentes intactas y guarda de AF; sólo entradas sintéticas."""
import sys, os, json, csv, time, hashlib, importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
sys.path.insert(0,str(ROOT.parent/'AF/scripts'))
import common_v1 as af
# Al ejecutar este archivo como módulo se importa AF por nombre distinto.
import numpy as np
import mpmath as mp
from scipy.spatial import ConvexHull
CFG=json.loads((ROOT/'config.json').read_text())
sha=af.sha
rows=af.rows
write=af.write
table=af.table

def geometry():
 for key in ['geometry','audit']:
  assert sha(REPO/CFG[key+'_path'])==CFG[key+'_sha256']
 return af.imports()[0]

def inputs():
 assert sha(REPO/CFG['af_inputs'])==CFG['af_inputs_sha256']
 answer=[]
 U=np.column_stack([np.array([1,-1,0])/np.sqrt(2),np.array([1,1,-2])/np.sqrt(6)])
 D=np.repeat(np.eye(3),9,axis=0)
 for i,seed in enumerate(CFG['seeds']):
  beta=np.arange(3)*2*np.pi/3+i*np.pi/30
  F=CFG['feature_radius']*np.column_stack([np.cos(beta),np.sin(beta)])
  psi=(i+1)*np.pi/17;rot=np.array([[np.cos(psi),-np.sin(psi)],[np.sin(psi),np.cos(psi)]])
  C=U@rot@np.diag([1.,.06+.02*i])
  for scale in CFG['length_scales']:
   Q=np.zeros((27,27));Q[:,:2]=scale*np.sqrt(27)*D@C
   eps=scale**2*CFG['epsilon_base'];M=Q@Q.T/27+eps*np.eye(27)
   answer.append({'id':f'triangle/{seed}/a{scale:g}','group':'triangle','seed':seed,'length_scale':scale,'epsilon':eps,'Q':Q.tolist(),'M':M.tolist(),'f':np.repeat(F,9,axis=0).tolist()})
 for st in json.loads((REPO/CFG['af_inputs']).read_text())['states']:
  answer.append({'id':'AF/'+st['id'],'group':'AF','seed':st['seed'],'length_scale':None,'epsilon':st['epsilon'],'M':st['M'],'f':st['f']})
 return answer

def exact_triangle(M):
 E=np.repeat(np.eye(3),9,axis=0)/9 if len(M)==27 else np.eye(3)
 W=E.T@M@E;q0=np.ones(3)/3;verts=np.eye(3)
 distances=[];feet=[]
 for i,j in [(0,1),(1,2),(2,0)]:
  v=verts[j]-verts[i];t=float(np.clip((q0-verts[i])@W@v/(v@W@v),0,1));foot=verts[i]+t*v
  distances.append(float(np.sqrt((q0-foot)@W@(q0-foot))));feet.append(foot)
 candidates=list(verts)+[(verts[i]+verts[j])/2 for i,j in [(0,1),(1,2),(2,0)]]
 rho=min(float(np.sqrt((p-q0)@W@(p-q0))) for p in candidates)
 return W,min(distances),rho,feet[int(np.argmin(distances))]

def special_angles(f):
 points=np.unique(f,axis=0);hull=ConvexHull(points);angles=[]
 for normal in hull.equations[:,:2]:
  for v in [normal,-normal]:
   theta=float(np.arctan2(v[1],v[0])%(2*np.pi))
   if all(abs(np.angle(np.exp(1j*(theta-a))))>1e-10 for a in angles):angles.append(theta)
 return sorted(angles)

def mp_speed(M,f,u,s,special=False):
 with mp.workdps(80):
  mm=mp.matrix([[mp.mpf(float(x)) for x in row] for row in M])
  z=[sum(mp.mpf(float(x))*mp.mpf(float(y)) for x,y in zip(row,u)) for row in f];top=max(z)
  if special:
   z=[top if abs(x-top)<mp.mpf('1e-12')*max(1,max(abs(t) for t in z)) else x for x in z]
  z=[x-max(z) for x in z];aa=[mp.exp(mp.mpf(float(s))*x) for x in z];den=sum(aa);aa=[x/den for x in aa];mu=sum(a*x for a,x in zip(aa,z));b=mp.matrix([a*(x-mu) for a,x in zip(aa,z)])
  return float(mp.sqrt((b.T*mm*b)[0]))

def load_e16(name,path):
 spec=importlib.util.spec_from_file_location(name,path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
