"""Receta G3/C2: únicamente cambia la pérdida o el optimizador por brazo."""
import hashlib
import math
import numpy as np


def network(torch):
    class Network(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.l1 = torch.nn.Linear(13, 64)
            self.l2 = torch.nn.Linear(64, 32)
            self.l3 = torch.nn.Linear(32, 3)
        def forward(self, x):
            return self.l3(torch.relu(self.l2(torch.relu(self.l1(x)))))
    return Network().double()


def dataset(seed):
    from sklearn.preprocessing import StandardScaler
    means = np.zeros((3, 13))
    means[:, :2] = [[2., 0.], [-1., math.sqrt(3)], [-1., -math.sqrt(3)]]
    y = np.repeat(np.arange(3), 39)
    tr = np.array([39*c+i for c in range(3) for i in range(30)], dtype=np.int64)
    va = np.array([39*c+i for c in range(3) for i in range(30, 39)], dtype=np.int64)
    epsilon = np.random.default_rng(seed).normal(size=(117, 13))
    raw = means[y]+.8*epsilon
    scaler = StandardScaler().fit(raw[tr])
    Z = scaler.transform(raw)
    return Z, y, tr, va


def initialize(init_seed, arm, dose, torch):
    torch.manual_seed(init_seed)
    model = network(torch)
    initial = hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in model.parameters())).hexdigest()
    optimizer = (torch.optim.AdamW(model.parameters(), lr=.006, weight_decay=dose) if arm == 'WD'
                 else torch.optim.Adam(model.parameters(), lr=.006))
    return model, optimizer, initial


def update(model, optimizer, xt, yt, rng, batches, arm, dose, torch):
    ids = rng.choice(len(xt), size=64, replace=False)
    batches.update(np.asarray(ids, dtype=np.int64).tobytes())
    optimizer.zero_grad()
    loss = torch.nn.functional.cross_entropy(model(xt[ids]), yt[ids], label_smoothing=dose if arm == 'LS' else 0.)
    if not torch.isfinite(loss):
        raise RuntimeError('Pérdida no finita')
    loss.backward()
    optimizer.step()


def metric(model, Z, y, va, core, torch):
    Rb, Ub, fp = core.make_geom_state(model, torch.tensor(Z[va]), torch.tensor(y[va]))
    M = core.subset_M(Rb, Ub, [0, 1, 2]).numpy()
    f = fp.numpy()
    diag = np.diag(M)
    trace = float(np.trace(M))
    norm = float(np.linalg.norm(M))
    if not np.isfinite(M).all() or trace <= 0 or norm <= 0:
        raise RuntimeError('M inválida')
    c = float(diag.max()/trace)
    q = float(np.linalg.norm(M-np.diag(diag))/norm)
    with torch.no_grad():
        acc = float((model(torch.tensor(Z[va])).argmax(1) == torch.tensor(y[va])).double().mean())
    return c, q, acc, M, f
