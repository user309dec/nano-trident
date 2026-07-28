"""
The file has a fake data generator

Create N fake images in Trident's h5 format (coords, feat) and have one MIL signal.
In the tumor image, 2% to 8% of the patches were added with a fixed-direction tumor vector.

The labels are only at the patch level.

Param:
    - feat_dir: str; h5 file path
    - epochs: int; number of epochs
    - max_patches: int; number of patches to use; None = all of patches
    - lr: float; Adam learning rate; = 1e-3; I've tried 13-4 but AUC drops
    - seed: int; random seed. The same seed must produce the same split of the training data. Therefore, __main__ can finally reconstruct the train/test exactly the same as during training with split_index(build_index(dir), seed=0). Feed it to mean_pool_baseline for control.
Input:
    - feat_dir: str; h5 file path
    - in each h5 file, there are features (n_pathces, dim) and witness (n_pathces, ) bool and coords (n_pathces, 2)


1. Each n_patches file is different (150-500), and the dim must be consistent. dim is read from the bag of train[0] as load_bag(train[0][0]).shape[1]
2. The witness will not participate in training. It is the answer to "Which patch is the tumor?", and is only used after testing. The only supervisory signal for training is the slide level label in the file name
"""

import copy
import glob
import os
import sys

import h5py
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


sys.path.insert(0, os.path.expanduser("~/trident/learning"))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from nano_trident import NanoABMIL

# ======================================================================================
# Written by Claude
# Scaffolding: Falsifying Data (Deleting the entire piece after the real data is in place)
#
# ⚠️ want to temporarily disable this section? 【 Do not enclose it in triple quotes 】 -- This function comes with its own docstring
# The inner "" will close the outer string in advance, and the subsequent Chinese characters will become code (you just stepped on it).
# Correct approach: Delete the entire block or add # to each line (select it in the editor and click Cmd+/ to complete it with one click).
# In fact, there is no need to disable -- __main__. It is only called when the directory is empty.
# ======================================================================================
def make_fake_dataset(out_dir, n_slides=300, dim=2048, seed=0):
    rng = np.random.default_rng(seed)
    os.makedirs(out_dir, exist_ok=True)

    signal = rng.normal(size=dim)
    signal = (signal / np.linalg.norm(signal)).astype(np.float32)

    for i in range(n_slides):
        is_tumor = (i % 2 == 0)
        n = int(rng.integers(150, 500))
        feats = rng.normal(size=(n, dim)).astype(np.float32)
        wit = np.zeros(n, dtype=bool)

        if is_tumor:

            k = int(rng.integers(1, 4))
            sel = rng.choice(n, k, replace=False)
            feats[sel] += 12.0 * signal
            wit[sel] = True

        name = f"{'tumor' if is_tumor else 'normal'}_{i:03d}.h5"
        with h5py.File(os.path.join(out_dir, name), "w") as f:
            f.create_dataset("features", data=feats)
            f.create_dataset("coords", data=rng.integers(0, 50000, size=(n, 2)))
            f.create_dataset("witness", data=wit)

    print(f"[fake] create {n_slides} fake slides -> {out_dir}  (dim={dim})")


# ======================================================================================
# Create Index of [(path, label), ...] read no features
# ======================================================================================
def build_index(feat_dir):
    items = []
    for path in sorted(glob.glob(os.path.join(feat_dir, "*.h5"))):
        name = os.path.basename(path)
        if name.startswith("tumor"):
            label = 1
        elif name.startswith("normal"):
            label = 0
        else:
            continue
        items.append((path, label))

    n_pos = sum(lab for _, lab in items)
    print(f"Index: {len(items)} Slides:positive {n_pos},negative {len(items) - n_pos}")
    assert n_pos > 0 and n_pos < len(items)
    return items


# ======================================================================================
# Divide the features to three parts
# ======================================================================================
def _shuffled(lst, rng):
    return [lst[i] for i in rng.permutation(len(lst))]


def split_index(items, frac=(0.6, 0.2, 0.2), seed=0):
    rng = np.random.default_rng(seed)
    buckets = [[], [], []]                                    # train / val / test

    for label in (0, 1):                                      # three parts are the same amount
        group = _shuffled([it for it in items if it[1] == label], rng)
        a = int(len(group) * frac[0])
        b = a + int(len(group) * frac[1])
        for bucket, part in zip(buckets, (group[:a], group[a:b], group[b:])):
            bucket.extend(part)

    train, val, test = (_shuffled(b, rng) for b in buckets)
    for name, b in (("train", train), ("val", val), ("test", test)):
        n_pos = sum(lab for _, lab in b)
        print(f"[A'] {name:5s}: {len(b):3d} slides  (pos {n_pos}, neg {len(b) - n_pos})")
    return train, val, test


# ======================================================================================
# load a bag with lazy evaluation. Use the bag as needed
# ======================================================================================
def load_bag(path, max_patches=None, rng=None):
    with h5py.File(path, "r") as f:
        feats = torch.from_numpy(f["features"][:]).float()    # (n_patches, dim)

    # Downsampling for CPU speedup and different subsets drawn in each epoch = data augmentation
    # used only during training. The assessment should use all the patches to be fair.
    if max_patches and feats.shape[0] > max_patches:
        sel = rng.choice(feats.shape[0], max_patches, replace=False)
        feats = feats[sel]
    return feats


# ======================================================================================
# Compute Area Under Curve
# ======================================================================================
def compute_auc(y_true, y_score):
    pos = [s for s, y in zip(y_score, y_true) if y == 1]
    neg = [s for s, y in zip(y_score, y_true) if y == 0]
    if not pos or not neg:
        return float("nan")
    wins = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


@torch.no_grad()
def evaluate(model, items):
    model.eval()
    ys, ps = [], []
    for path, label in items:
        logits, _ = model(load_bag(path))
        # dim=1
        # are different from softmax(dim=0) in NanoABMIL
        ps.append(F.softmax(logits, dim=1)[0, 1].item())
        ys.append(label)
    return compute_auc(ys, ps)


# ======================================================================================
# Training
# ======================================================================================
def train_real(feat_dir, epochs=15, lr=1e-3, seed=0, max_patches=None):
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)

    items = build_index(feat_dir)
    train, val, test = split_index(items, seed=seed)

    dim = load_bag(train[0][0]).shape[1]
    model = NanoABMIL(feature_dim=dim)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    lossf = nn.CrossEntropyLoss()
    print(f"[B ] NanoABMIL(feature_dim={dim}),Adam lr={lr}")

    best_auc, best_state, best_epoch = -1.0, None, -1

    for epoch in range(epochs):
        # training
        model.train()
        total = 0.0
        for path, label in _shuffled(train, rng):             # reshuffle  epoch
            bag = load_bag(path, max_patches, rng)            # (n, dim)
            logits, _ = model(bag)                            # (1, 2)
            loss = lossf(logits, torch.tensor([label]))       # target is (1,); dtype is Long
            opt.zero_grad(); loss.backward(); opt.step()
            total += loss.item()

        # verification + early stopping
        auc = evaluate(model, val)
        flag = ""
        if auc > best_auc:
            best_auc, best_epoch = auc, epoch
            # use deepcopy:state_dict() to return reference; for the next step, opt.step() will opt it
            best_state = copy.deepcopy(model.state_dict())
            flag = "  <- best"
        print(f"[C ] epoch {epoch:2d}  train loss {total / len(train):.4f}   val AUC {auc:.3f}{flag}")

    # return the best result
    model.load_state_dict(best_state)
    print(f"\n Use epoch {best_epoch} 's weight(val AUC {best_auc:.3f})")
    print(f"[D ] === TEST AUC = {evaluate(model, test):.3f} ===")
    return model, test


# ======================================================================================
# Written by Claude
# Is attention really being put on witness?
# (requires data set with instance level labels)
# ======================================================================================
@torch.no_grad()
def witness_check(model, items):
    model.eval()
    ratios = []
    for path, label in items:
        if label == 0:
            continue                                          # negative slides have no witness
        with h5py.File(path, "r") as f:
            feats = torch.from_numpy(f["features"][:]).float()
            wit = f["witness"][:]
        _, attn = model(feats)
        a = attn.numpy()
        ratios.append(a[wit].mean() / (a[~wit].mean() + 1e-9))
    print(f"[E ] On positive slides, witnesses' average attention equals to the rest times {np.mean(ratios):.1f}  "
          f"(>2 shows true learning)")


# ======================================================================================
# Comparing with mean pooling. Calculate the mean of features in a bag to gain the slide embeddings
# ======================================================================================
def mean_pool_baseline(train, test):
    def bagmean(items):
        X, y = [], []
        for p, lab in items:
            with h5py.File(p, "r") as f:
                X.append(f["features"][:].mean(0))
            y.append(lab)
        return np.array(X), np.array(y)

    Xtr, ytr = bagmean(train)
    Xte, yte = bagmean(test)
    w = Xtr[ytr == 1].mean(0) - Xtr[ytr == 0].mean(0)     # class mean difference
    print(f"Comparing mean pooling AUC = {compute_auc(yte, Xte @ w):.3f}")


# ======================================================================================
# Main
# ======================================================================================
if __name__ == "__main__":
    fake_dir = os.path.expanduser("~/trident_lab/bags1") #it's the absolute dir on my mac
    if not glob.glob(os.path.join(fake_dir, "*.h5")):
        make_fake_dataset(fake_dir, n_slides=300, dim=2048, seed=0)

    model, test = train_real(fake_dir, epochs=20, lr=1e-3, seed=0, max_patches=None)
    witness_check(model, test)

    train, _, test2 = split_index(build_index(fake_dir), seed=0)
    mean_pool_baseline(train, test2)
