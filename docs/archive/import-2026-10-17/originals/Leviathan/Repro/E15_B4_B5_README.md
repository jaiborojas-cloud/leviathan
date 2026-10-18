# Leviathan RIPG — E15-B4/B5 reproducibility package

This package contains the deterministic Wine states and the core code/configuration needed to reproduce E15-B4/B5 and start E15-B6.

## Contents
- `checkpoints/`: 16 PyTorch checkpoints (8 splits × true/random, init j=0) plus SHA-256 manifest.
- `results/`: B4/B5 CSV outputs.
- `config/protocol.json`: frozen training, geometry, disk and adaptive-integration configuration.
- `src/e15_repro_core.py`: core model, training, reduced-logit geometry, Fisher/Woodbury metric, curvature, geodesic integration, triangle subdivision.

## Dataset
`sklearn.datasets.load_wine`.

## Primary E15-B6 target
Resolve mesh-independence for highly focal true states, especially split 6 true, using multiple source meshes and angular phase offsets.

## Important methodological note
B5 showed that adaptive convergence within one starting mesh does not guarantee convergence across starting meshes. Do not treat a single adaptive estimate as final for highly focal states.

## Checkpoint loading
Each `.pt` contains:
- model state dict
- exact split indices
- scaler mean/scale
- train target labels (including random permutation)
- seeds and stopping step
- validation/test accuracies

Load with PyTorch and reconstruct `WineMLP`, then `load_state_dict`.
