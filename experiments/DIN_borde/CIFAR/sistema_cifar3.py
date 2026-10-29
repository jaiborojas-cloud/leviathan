"""Sistema CIFAR-3 del plan v1 §3: datos, split, preprocesamiento, red y entrenamiento.

No usa torchvision. Lee el archivo oficial `cifar-10-python.tar.gz` con un
desempaquetador restringido (solo admite los tipos de numpy que usa CIFAR).
"""
from __future__ import annotations

import hashlib
import io
import pickle
import tarfile

import numpy as np

MD5_OFICIAL = 'c58f30108f718f92721af3b95e74349a'
CLASES = (3, 4, 5)          # gato, ciervo, perro -> etiquetas 0, 1, 2 (perro es la referencia)
N_TRAIN, N_PANEL, N_TEST = 300, 9, 9
LR, LOTE, UPDATES = 1e-3, 64, 250
VISITAS = (5, 10, 30, 250)


class _Restringido(pickle.Unpickler):
    PERMITIDOS = {('numpy.core.multiarray', '_reconstruct'), ('numpy._core.multiarray', '_reconstruct'),
                  ('numpy', 'ndarray'), ('numpy', 'dtype'),
                  ('_codecs', 'encode')}   # inocuo: reconstruye bytes en pickles de protocolo 2 escritos con Python 3

    def find_class(self, module, name):
        if (module, name) not in self.PERMITIDOS:
            raise pickle.UnpicklingError(f'Tipo no permitido en CIFAR: {module}.{name}')
        if module == 'numpy.core.multiarray':
            module = 'numpy._core.multiarray'
        return super().find_class(module, name)


def cargar_cifar10(ruta_tgz):
    """Devuelve (Xtr uint8 50000×3072, ytr, Xte 10000×3072, yte, md5, sha256)."""
    datos = open(ruta_tgz, 'rb').read()
    md5 = hashlib.md5(datos).hexdigest()
    if md5 != MD5_OFICIAL:
        raise RuntimeError(f'MD5 de CIFAR-10 no coincide: {md5}')
    sha = hashlib.sha256(datos).hexdigest()
    lotes = {}
    with tarfile.open(fileobj=io.BytesIO(datos), mode='r:gz') as tar:
        for m in tar.getmembers():
            base = m.name.rsplit('/', 1)[-1]
            if base in [f'data_batch_{i}' for i in range(1, 6)]+['test_batch']:
                d = _Restringido(tar.extractfile(m), encoding='bytes').load()
                lotes[base] = (np.asarray(d[b'data'], dtype=np.uint8), np.asarray(d[b'labels'], dtype=np.int64))
    if len(lotes) != 6:
        raise RuntimeError('Faltan lotes en el archivo de CIFAR-10')
    Xtr = np.concatenate([lotes[f'data_batch_{i}'][0] for i in range(1, 6)])
    ytr = np.concatenate([lotes[f'data_batch_{i}'][1] for i in range(1, 6)])
    Xte, yte = lotes['test_batch']
    if Xtr.shape != (50000, 3072) or Xte.shape != (10000, 3072):
        raise RuntimeError('Formas inesperadas en CIFAR-10')
    return Xtr, ytr, Xte, yte, md5, sha


def indices_split(ytr, yte, semilla):
    """Orden de extracción fijo: primero entrenamiento (clase 3, 4, 5), luego test (3, 4, 5).

    De cada clase de test se extraen 18 sin reemplazo: los 9 primeros son el
    panel y los 9 siguientes el test. Cada grupo se ordena por clase y luego
    por índice original.
    """
    rng = np.random.default_rng(semilla)
    tr = [np.sort(rng.choice(np.flatnonzero(ytr == c), N_TRAIN, replace=False)) for c in CLASES]
    pa, te = [], []
    for c in CLASES:
        t = rng.choice(np.flatnonzero(yte == c), N_PANEL+N_TEST, replace=False)
        pa.append(np.sort(t[:N_PANEL]))
        te.append(np.sort(t[N_PANEL:]))
    return np.concatenate(tr), np.concatenate(pa), np.concatenate(te)


def preparar(Xtr, ytr, Xte, yte, semilla):
    """Imágenes float64 (N,3,32,32) estandarizadas por canal con el entrenamiento del split."""
    itr, ipa, ite = indices_split(ytr, yte, semilla)
    mapa = {c: i for i, c in enumerate(CLASES)}

    def img(X, idx):
        return X[idx].reshape(-1, 3, 32, 32).astype(np.float64)/255.

    a, p, t = img(Xtr, itr), img(Xte, ipa), img(Xte, ite)
    mu = a.mean(axis=(0, 2, 3), keepdims=True)
    sd = a.std(axis=(0, 2, 3), keepdims=True)
    lab = lambda y, idx: np.array([mapa[int(v)] for v in y[idx]], dtype=np.int64)
    return dict(xtr=(a-mu)/sd, ytr=lab(ytr, itr), xpa=(p-mu)/sd, ypa=lab(yte, ipa),
                xte=(t-mu)/sd, yte=lab(yte, ite), itr=itr, ipa=ipa, ite=ite)


def red(torch):
    """CNN de §3: 26 067 parámetros. `body` y `head` separados para el instrumento."""
    nn = torch.nn

    class CNN3(nn.Module):
        def __init__(self):
            super().__init__()
            self.body = nn.Sequential(
                nn.Conv2d(3, 8, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
                nn.Flatten(), nn.Linear(1024, 24), nn.ReLU())
            self.head = nn.Linear(24, 3)

        def forward(self, x):
            return self.head(self.body(x))
    return CNN3().double()


def iniciar(torch, semilla_init):
    torch.manual_seed(semilla_init)
    modelo = red(torch)
    opt = torch.optim.Adam(modelo.parameters(), lr=LR)
    return modelo, opt


def paso(torch, modelo, opt, xt, yt, rng):
    ids = torch.as_tensor(rng.choice(len(xt), size=LOTE, replace=False), dtype=torch.long)
    opt.zero_grad()
    loss = torch.nn.functional.cross_entropy(modelo(xt[ids]), yt[ids])
    if not torch.isfinite(loss):
        raise RuntimeError('Pérdida no finita')
    loss.backward()
    opt.step()


def precision(torch, modelo, x, y):
    with torch.no_grad():
        return float((modelo(x).argmax(1) == y).double().mean())
