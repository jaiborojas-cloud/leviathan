"""Diccionario B4 copiado literalmente de D9g-b; sólo funciones puras."""
import numpy as np

def center(a,group):
    z=np.array(a,dtype=float,copy=True)
    for s in np.unique(group):z[group==s]-=z[group==s].mean(axis=0)
    return z

def design(cheap,extra,group,train,base):
    mean=cheap[train].mean(0);std=cheap[train].std(0);std=np.where(std==0,1.,std)
    z=(cheap-mean)/std
    columns=[z];names=['q0','q1','q2','q3']
    if base>=2:
        columns.extend([z*z,z*z*z]);names += [f'q{i}^2' for i in range(4)]+[f'q{i}^3' for i in range(4)]
    if base>=3:
        columns.append(np.column_stack([z[:,i]*z[:,j] for i in range(4) for j in range(i+1,4)]));names += [f'q{i}q{j}' for i in range(4) for j in range(i+1,4)]
    emean=estd=None
    if base>=4:
        emean=extra[train].mean(0);estd=extra[train].std(0);estd=np.where(estd==0,1.,estd)
        columns.append((extra-emean)/estd);names+=['margin','entropy','weight_norm']
    matrix=center(np.column_stack(columns),group)
    scale=np.sqrt(np.mean(matrix[train]**2,axis=0));scale=np.where(scale==0,1.,scale);matrix/=scale
    sv=np.linalg.svd(matrix[train],compute_uv=False);tol=np.finfo(float).eps*max(matrix[train].shape)*(sv[0] if len(sv) else 0)
    rank=int(np.sum(sv>tol));cond=float(sv[0]/sv[rank-1]) if rank else None
    metadata=dict(mean=mean,std=std,extra_mean=emean,extra_std=estd,term_scale=scale,columns=names,rank=rank,condition_nonzero=cond,n_train=int(train.sum()))
    return matrix,metadata
