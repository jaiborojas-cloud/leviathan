"""Adaptador LP; receta original intacta y A0/WD delegados sin cambios."""
import numpy as np
from recipe_v1 import update as original_update


def update_m2(model,optimizer,xt,yt,rng,batches,arm,dose,torch):
    if arm!='LP':
        return original_update(model,optimizer,xt,yt,rng,batches,arm,dose,torch)
    ids=rng.choice(len(xt),size=64,replace=False)
    batches.update(np.asarray(ids,dtype=np.int64).tobytes())
    optimizer.zero_grad()
    z=model(xt[ids])
    loss=torch.nn.functional.cross_entropy(z,yt[ids])+dose*(z**2).sum(dim=1).mean()
    if not torch.isfinite(loss):raise RuntimeError('Pérdida no finita')
    loss.backward()
    optimizer.step()
