"""Controles previos de la pérdida y pareado; nunca calcula X/rho/D."""
import hashlib
import numpy as np
from recipe_v1 import initialize,update
from recipe_m2 import update_m2


def controls():
    import torch
    torch.set_num_threads(1)
    g=np.random.default_rng(905001);xt=torch.tensor(g.normal(size=(90,13)),dtype=torch.float64);yt=torch.tensor(np.tile(np.arange(3),30))
    records=[]
    for arm,dose in [('A0',0.),('WD',.2)]:
        a,oa,ha=initialize(905101,arm,dose,torch);b,ob,hb=initialize(905101,arm,dose,torch)
        ba,bb=hashlib.sha256(),hashlib.sha256()
        update(a,oa,xt,yt,np.random.default_rng(905201),ba,arm,dose,torch)
        update_m2(b,ob,xt,yt,np.random.default_rng(905201),bb,arm,dose,torch)
        exact=ha==hb and ba.hexdigest()==bb.hexdigest() and all(torch.equal(x,y) for x,y in zip(a.parameters(),b.parameters()))
        records.append(dict(case=arm+'_delegation',pass_test=exact))
    model,opt,_=initialize(905102,'LP',.003,torch);saved=[]
    def hook(module,args,z):z.retain_grad();saved.append(z)
    handle=model.register_forward_hook(hook);batch=hashlib.sha256()
    update_m2(model,opt,xt,yt,np.random.default_rng(905202),batch,'LP',.003,torch);handle.remove()
    z=saved[0];ids=np.random.default_rng(905202).choice(90,size=64,replace=False)
    onehot=torch.nn.functional.one_hot(yt[ids],3).double()
    expected=(torch.softmax(z.detach(),1)-onehot)/64+2*.003*z.detach()/64
    err=float(torch.max(torch.abs(z.grad-expected)));correct=err<=1e-12 and opt.defaults['weight_decay']==0
    records.append(dict(case='LP_analytic_logit_gradient_and_Adam_no_decay',max_gradient_error=err,pass_test=correct))
    model,opt,_=initialize(905103,'A0',0.,torch);other,op2,_=initialize(905103,'LP',0.,torch)
    update(model,opt,xt,yt,np.random.default_rng(905203),hashlib.sha256(),'A0',0.,torch)
    update_m2(other,op2,xt,yt,np.random.default_rng(905203),hashlib.sha256(),'LP',0.,torch)
    records.append(dict(case='LP_zero_equals_A0',pass_test=all(torch.equal(a,b) for a,b in zip(model.parameters(),other.parameters()))))
    return dict(status='PASS' if all(r['pass_test'] for r in records) else 'FAIL',records=records,
                independent_control_seeds=[905001,905101,905102,905103,905201,905202,905203],calibration_trajectories_measured=0)
