from __future__ import annotations

import argparse
import os

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import h5py
from torch.utils.data import Dataset, DataLoader

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import openslide
import skimage.color as sk_color
import skimage.filters as sk_filters


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Nano end-to-end Trident, on CPU.")
    p.add_argument("--slide", default=os.path.expanduser(
        "~/trident_lab/wsis/CMU-1-Small-Region.svs"))
    p.add_argument("--out_dir", default=os.path.expanduser("~/trident_lab/nano"))
    p.add_argument("--patch_size", type=int, default=256)
    p.add_argument("--tissue_frac", type=float, default=0.10)
    p.add_argument("--train-demo", action="store_true")
    p.add_argument("--seed", type=int, default=0)
    return p.parse_args()


def load_slide(path: str) -> openslide.OpenSlide:
    slide = openslide.OpenSlide(path)
    W, H = slide.dimensions
    mpp = slide.properties.get("openslide.mpp-x", "?")
    print(f"[1] slide loaded: {os.path.basename(path)}")
    print(f"    level-0 size = {W} x {H} px,  mpp = {mpp} um/px")
    return slide


def nano_segment(slide: openslide.OpenSlide, thumb_max: int = 512):
    W, H = slide.dimensions #the first element slide.dimensions output is width, and the second is height
    reduceportion = max(W, H) / thumb_max
    # tw, th = W / reduceportion, H / reduceportion use int cuz python automatically takes /'s result as float, not like C
    tw, th = int(W / reduceportion), int(H / reduceportion)
    slide_numpy_array = np.array(slide.get_thumbnail((tw, th)).convert("RGB")) # use get_thumbnail to get the smaller slide of tw * th, then convert to RGB. Then use np.arrary to generate array.

    #from now, slide_numpy_array is a (th, tw, 3) numpy array(numpy array takes height, width, channel as sequence)
    sat = sk_color.rgb2hsv(slide_numpy_array)[..., 1] #change rgb to hsv to get sat
    threshold = sk_filters.threshold_otsu(sat) # we have the threshold of sat
    tissue = sat > threshold #we have the bool array of whether tissue's saturation is greater than threshold or not. If it's True, then we know it's tissue.

    #from now we have everything needed: sat, tissue, numpy array
    tissue_coverage = tissue.mean() #calculate the ratio of True in this boolean array since True is 1 and False is 0

    print(f"1. slide loaded: {tw} * {th} px"
          f"2. the coverage of tissue in the slide is {tissue_coverage*100:.2f}%"
          )

    # scale = level-0 pixels per thumbnail pixel, so patch code can map between them.
    scale = W / tw #the original float reduceportion

    return tissue, scale


def nano_patch(slide, tissue_mask, mask_scale, patch_size, tissue_frac):
    W, H = slide.dimensions
    coords = []
    for y in range(0, H - patch_size + 1, patch_size):
        for x in range(0, W - patch_size + 1, patch_size):
            x0 = int(x / mask_scale)
            y0 = int(y / mask_scale)
            x1 = int((x + patch_size) / mask_scale) # adding patch size is because x1 will not be taken in the following code
            y1 = int((y + patch_size) / mask_scale) #same reason as above
            cell = tissue_mask[y0:y1, x0:x1] #numpy takes (y,x)
            if cell.size and cell.mean() >= tissue_frac: #size is product of dim length(width * height * ...) which is the sum of elements. short eval. cell mean to calculate the coverage > tissue frac as standard of keeping this grid
                coords.append((x, y)) #save the coords of original wsi to be used for next step of patch encode

    coords = np.array(coords, dtype=np.int64) # list np.arrary to a matrix array of (n,2)
    print(f"3. nano-patch: grid step={patch_size}px, kept {len(coords)} tissue patches"
          f"  ->  coords {coords.shape}")
    return coords


# This part is written by claude since i don't know how to introduce resnet50
def build_encoder():
    from torchvision.models import resnet50, ResNet50_Weights
    try:
        weights = ResNet50_Weights.IMAGENET1K_V1
        net = resnet50(weights=weights)
        preprocess = weights.transforms()
        print("[4] encoder: resnet50, dim = 2048")
    except Exception as e:
        net = resnet50(weights=None)
        preprocess = ResNet50_Weights.IMAGENET1K_V1.transforms()
        print(f"[4] encoder: resnet50 (RANDOM weights, no download: {e}), dim = 2048")
    net.fc = nn.Identity()  # drop the 1000-class head; keep the 2048-d embedding
    net.eval()
    return net, preprocess


@torch.no_grad()                      # don't track gradient
def nano_encode(slide, coords, patch_size, encoder, preprocess, batch_size=32):
    """Encode each patch to a vector with dim = 2048
        Return an (n, 2048) tensor of float32"""
    device = next(encoder.parameters()).device   # encoder.parameters() will iterate over every parameters in the model, then next() will read the first tensor parameter, .device will read the cpu/cuda to see which is processing
    encoder.eval() #recursively set every self.training of encoder to False. Let resnet50 uses BatchNorm accumulated running_mean generated during training. Stop using the current batch statistic
    # If forget 'eval()', the features of a certain patch will depend on which patches it happens to be in the same batch as.
    # Changing 'batch_size' will change the result, and even running the same slide twice may not be consistent.
    # This will affect the downstream MIL because feature bag is no longer deterministic.

    feats = []       # collect each batch's output
    buffer = []      # collect one batch then calculate

    for (x, y) in coords:
        tile = slide.read_region((int(x), int(y)), 0, (patch_size, patch_size))
        tile = tile.convert("RGB")          # RGBA → RGB without alpha
        buffer.append(preprocess(tile))     # (3, 224, 224)

        if len(buffer) == batch_size:
            batch = torch.stack(buffer).to(device)   # (batch_size, 3, 224, 224) send to the same device with weights. Or "Expected all tensors to be on the same device" will be thrown
            out = encoder(batch)                     # (batch_size, 2048)
            feats.append(out)
            buffer = []

    if buffer:                              # if any batch left, repeat
        batch = torch.stack(buffer).to(device)
        out = encoder(batch)
        feats.append(out.cpu())

    features = torch.cat(feats, dim=0).float()   # put all patch together to form tensor (n, 2048) of floats
    print(features.shape) #check
    return features

class NanoABMIL(nn.Module):
    def __init__(self, feature_dim: int, hidden: int = 128, n_classes: int = 2): #feature_dim will be extracted through features.shape[1] since features.Size is ([48,2048]).
        super().__init__() #inherit nn.Module
        self.attn_V = nn.Linear(feature_dim, hidden)
        self.attn_W = nn.Linear(hidden, 1)
        self.classifier = nn.Linear(feature_dim, n_classes)

    def forward(self, feats):
        scores = self.attn_W(torch.tanh(self.attn_V(feats)))    # scores: (n,1) feats: (n, dim)
        a = F.softmax(scores, dim=0) # a: (n, 1)
        z = a * feats # z: (n, 1) * (n, dim) which is (n, dim)
        z = z.sum(dim=0, keepdim=True) # z here collapes n patches into one slide level vector (1, dim)
        logits =  self.classifier(z)
        return logits, a.squeeze(-1) # squeez (n, 1) to (n,) for returning the per-patch attention score

# --------------------------------------------------------------------------------------
# Written by Claude — the payoff: paint each patch's attention weight back onto the slide, so I
# can SEE where the model is looking. (On an untrained model this is just the random
# initial attention — see --train-demo below to make it mean something.)
# --------------------------------------------------------------------------------------
def save_attention_overlay(slide, coords, attn, patch_size, out_path, title):
    W, H = slide.dimensions
    thumb = np.array(slide.get_thumbnail((W // 8, H // 8)).convert("RGB"))
    scale = thumb.shape[1] / W  # thumbnail px per level-0 px

    a = attn.detach().numpy()
    a = (a - a.min()) / (np.ptp(a) + 1e-9)  # normalize to [0,1] for coloring

    fig, ax = plt.subplots(figsize=(6, 8))
    ax.imshow(thumb)
    ps = patch_size * scale
    cmap = plt.cm.jet
    for (x, y), av in zip(coords, a):
        ax.add_patch(plt.Rectangle((x * scale, y * scale), ps, ps,
                     facecolor=cmap(av), edgecolor="none", alpha=0.55))
    ax.set_title(title)
    ax.axis("off")
    sm = plt.cm.ScalarMappable(cmap=cmap)
    sm.set_array([])
    fig.colorbar(sm, ax=ax, fraction=0.046, label="attention (normalized)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    print(f"[6] attention overlay saved -> {out_path}")

def main():
    args = parse_args()
    os.makedirs(args.out_dir, exist_ok=True)   # build the dir if missing; no error if it's already there
    torch.manual_seed(args.seed)               # so the random ABMIL init is reproducible

    slide = load_slide(args.slide)
    tissue, scale = nano_segment(slide)
    coords = nano_patch(slide, tissue, scale, args.patch_size, args.tissue_frac)
    encoder, preprocess = build_encoder()
    feats = nano_encode(slide, coords, args.patch_size, encoder, preprocess)

    # feature_dim is read from the features
    model = NanoABMIL(feature_dim=feats.shape[1])
    logits, attn = model(feats)
    print(f"Untrained NanoABMIL: logits {tuple(logits.shape)}, attention {tuple(attn.shape)},"
          f" attn.sum() = {attn.sum().item():.4f}")

    stem = os.path.splitext(os.path.basename(args.slide))[0]   # "CMU-1-Small-Region.svs" -> "CMU-1-Small-Region"
    save_attention_overlay(slide, coords, attn, args.patch_size,
                           out_path=os.path.join(args.out_dir, f"{stem}_attention_untrained.png"),
                           title=f"{stem}  untrained attention (random init attention)")


if __name__ == '__main__':
    main()
