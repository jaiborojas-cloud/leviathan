"""Red y puntuaciones G3 copiadas literalmente; sólo forward, nunca entrenar."""
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

def scores(model, X, y, torch):
    with torch.no_grad():
        logits = model(X)
        logp = torch.log_softmax(logits, 1)
        wrong = logits.clone()
        wrong[torch.arange(len(y)), y] = -torch.inf
        log1m = torch.logsumexp(wrong, 1)-torch.logsumexp(logits, 1)
        logpy = logp[torch.arange(len(y)), y]
        pred = logits.argmax(1)
    return dict(acc=float((pred == y).double().mean()), loss=float(-logpy.mean())), dict(
        logits=logits.numpy(), logpy=logpy.numpy(), log1m=log1m.numpy(), pred=pred.numpy())
